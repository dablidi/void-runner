import pygame
import random
import math
import os

pygame.init()

# ============================================================
# WINDOW
# ============================================================

fullscreen = True

screen = pygame.display.set_mode(
    (0, 0),
    pygame.FULLSCREEN
)

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

pygame.display.set_caption("VOID RUNNER")

clock = pygame.time.Clock()


# ============================================================
# COLORS
# ============================================================

BG = (20, 20, 25)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CYAN = (50, 200, 255)
RED = (255, 60, 60)
PURPLE = (170, 70, 220)
YELLOW = (255, 220, 50)
GREEN = (50, 220, 80)
PINK = (255, 80, 220)

GRAY = (90, 90, 100)
LIGHT_GRAY = (140, 140, 150)

ORANGE = (255, 130, 30)


# ============================================================
# FONTS
# ============================================================

title_font = pygame.font.Font(None, 110)
big_font = pygame.font.Font(None, 80)
button_font = pygame.font.Font(None, 45)
small_font = pygame.font.Font(None, 30)
tiny_font = pygame.font.Font(None, 24)


# ============================================================
# SAVE
# ============================================================

SAVE_FILE = "void_runner_save.txt"


def tutorial_completed():

    if not os.path.exists(SAVE_FILE):
        return False

    try:

        with open(SAVE_FILE, "r") as file:

            return (
                file.read().strip()
                == "tutorial_complete"
            )

    except:

        return False


def mark_tutorial_complete():

    try:

        with open(
            SAVE_FILE,
            "w"
        ) as file:

            file.write(
                "tutorial_complete"
            )

    except:

        pass


# ============================================================
# GAME STATE
# ============================================================

game_state = "menu"

# menu
# game
# tutorial
# tutorial_pause
# pause
# shop
# next_level
# game_over


# ============================================================
# PLAYER
# ============================================================

player = pygame.Rect(
    WIDTH // 2 - 25,
    HEIGHT // 2 - 25,
    50,
    50
)

player_speed = 5


# ============================================================
# HEALTH
# ============================================================

max_health = 100

health = max_health

damage_cooldown = 500

last_damage = 0

red_flash_until = 0

flash_duration = 150


# ============================================================
# LEVEL / SCORE
# ============================================================

level = 1

kills = 0

credits = 0


def get_kill_reward():

    return 20 + (
        (level - 1)
        * 5
    )


# ============================================================
# WALLS
# ============================================================

walls = []

wall_thickness = 30


def create_walls():

    walls.clear()

    wall_count = random.randint(
        6,
        10
    )

    attempts = 0

    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    while (
        len(walls) < wall_count
        and attempts < 1000
    ):

        attempts += 1

        horizontal = random.choice(
            [True, False]
        )

        if horizontal:

            wall_width = random.randint(
                120,
                300
            )

            wall_height = wall_thickness

        else:

            wall_width = wall_thickness

            wall_height = random.randint(
                120,
                300
            )

        x = random.randint(
            50,
            max(
                51,
                WIDTH - wall_width - 50
            )
        )

        y = random.randint(
            120,
            max(
                121,
                HEIGHT - wall_height - 50
            )
        )

        new_wall = pygame.Rect(
            x,
            y,
            wall_width,
            wall_height
        )

        if new_wall.colliderect(
            player.inflate(
                350,
                350
            )
        ):

            continue

        if horizontal:

            if (
                new_wall.top
                <= center_y + 90
                and
                new_wall.bottom
                >= center_y - 90
            ):

                continue

        else:

            if (
                new_wall.left
                <= center_x + 90
                and
                new_wall.right
                >= center_x - 90
            ):

                continue

        overlap = False

        for wall in walls:

            if new_wall.inflate(
                25,
                25
            ).colliderect(wall):

                overlap = True
                break

        if overlap:
            continue

        walls.append(
            new_wall
        )


# ============================================================
# MOVEMENT
# ============================================================

def move_with_walls(
    rect,
    dx,
    dy
):

    rect.x += int(dx)

    for wall in walls:

        if rect.colliderect(wall):

            if dx > 0:

                rect.right = wall.left

            elif dx < 0:

                rect.left = wall.right


    rect.y += int(dy)

    for wall in walls:

        if rect.colliderect(wall):

            if dy > 0:

                rect.bottom = wall.top

            elif dy < 0:

                rect.top = wall.bottom


    if rect.left < 0:
        rect.left = 0

    if rect.right > WIDTH:
        rect.right = WIDTH

    if rect.top < 0:
        rect.top = 0

    if rect.bottom > HEIGHT:
        rect.bottom = HEIGHT


def update_player():

    keys = pygame.key.get_pressed()

    dx = 0
    dy = 0

    if keys[pygame.K_w]:
        dy -= player_speed

    if keys[pygame.K_s]:
        dy += player_speed

    if keys[pygame.K_a]:
        dx -= player_speed

    if keys[pygame.K_d]:
        dx += player_speed

    if dx != 0 and dy != 0:

        dx /= math.sqrt(2)
        dy /= math.sqrt(2)

    move_with_walls(
        player,
        dx,
        dy
    )


# ============================================================
# ENEMY PATHFINDING
# ============================================================

PATH_CELL_SIZE = 40

PATH_RECALCULATE_TIME = 400


def position_to_cell(
    x,
    y
):

    return (
        int(x // PATH_CELL_SIZE),
        int(y // PATH_CELL_SIZE)
    )


def cell_to_position(
    cell
):

    return (
        cell[0] * PATH_CELL_SIZE
        + PATH_CELL_SIZE // 2,

        cell[1] * PATH_CELL_SIZE
        + PATH_CELL_SIZE // 2
    )


def cell_is_walkable(
    cell
):

    cell_x, cell_y = cell

    x, y = cell_to_position(
        cell
    )

    # Keep enemy completely on screen

    if (
        x < enemy_size // 2
        or
        x > WIDTH - enemy_size // 2
        or
        y < enemy_size // 2
        or
        y > HEIGHT - enemy_size // 2
    ):

        return False

    test_rect = pygame.Rect(

        int(
            x - enemy_size // 2
        ),

        int(
            y - enemy_size // 2
        ),

        enemy_size,

        enemy_size

    )

    for wall in walls:

        if test_rect.colliderect(
            wall
        ):

            return False

    return True


def get_neighbors(
    cell
):

    x, y = cell

    neighbors = [

        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),

        (x + 1, y + 1),
        (x - 1, y - 1),
        (x + 1, y - 1),
        (x - 1, y + 1)

    ]

    valid_neighbors = []

    for neighbor in neighbors:

        if not cell_is_walkable(
            neighbor
        ):
            continue

        # Prevent diagonal movement
        # through the corner of a wall.

        if (
            neighbor[0] != cell[0]
            and
            neighbor[1] != cell[1]
        ):

            side_a = (
                neighbor[0],
                cell[1]
            )

            side_b = (
                cell[0],
                neighbor[1]
            )

            if (
                not cell_is_walkable(
                    side_a
                )
                or
                not cell_is_walkable(
                    side_b
                )
            ):

                continue

        valid_neighbors.append(
            neighbor
        )

    return valid_neighbors


def find_enemy_path(
    start_pos,
    target_pos
):

    start = position_to_cell(
        *start_pos
    )

    target = position_to_cell(
        *target_pos
    )

    if not cell_is_walkable(start):

        return []

    # Find a walkable target around
    # the player if the player's cell
    # is occupied.

    if not cell_is_walkable(target):

        possible_targets = []

        for radius in range(
            1,
            6
        ):

            for dx in range(
                -radius,
                radius + 1
            ):

                for dy in range(
                    -radius,
                    radius + 1
                ):

                    candidate = (

                        target[0] + dx,

                        target[1] + dy

                    )

                    if cell_is_walkable(
                        candidate
                    ):

                        possible_targets.append(
                            candidate
                        )

            if possible_targets:
                break

        if not possible_targets:

            return []

        target = min(

            possible_targets,

            key=lambda cell:

                math.hypot(

                    cell[0] - start[0],

                    cell[1] - start[1]

                )

        )

    # --------------------------------------------------------
    # A* PATHFINDING
    # --------------------------------------------------------

    open_set = [start]

    came_from = {}

    g_score = {
        start: 0
    }

    f_score = {

        start:

        math.hypot(

            target[0] - start[0],

            target[1] - start[1]

        )

    }

    while open_set:

        current = min(

            open_set,

            key=lambda cell:
                f_score.get(
                    cell,
                    float("inf")
                )

        )

        if current == target:

            path = []

            while current in came_from:

                path.append(
                    current
                )

                current = came_from[
                    current
                ]

            path.append(start)

            path.reverse()

            return path

        open_set.remove(
            current
        )

        for neighbor in get_neighbors(
            current
        ):

            if (
                neighbor[0]
                != current[0]
                and
                neighbor[1]
                != current[1]
            ):

                movement_cost = 1.414

            else:

                movement_cost = 1

            tentative_g = (
                g_score[current]
                + movement_cost
            )

            if tentative_g < g_score.get(
                neighbor,
                float("inf")
            ):

                came_from[
                    neighbor
                ] = current

                g_score[
                    neighbor
                ] = tentative_g

                f_score[
                    neighbor
                ] = (
                    tentative_g
                    +
                    math.hypot(

                        target[0]
                        - neighbor[0],

                        target[1]
                        - neighbor[1]

                    )
                )

                if neighbor not in open_set:

                    open_set.append(
                        neighbor
                    )

    return []


# ============================================================
# ENEMIES
# ============================================================

enemies = []

enemy_size = 50

enemy_speed = 2

normal_enemy_hp = 3

armed_enemy_hp = 2


# ============================================================
# ENEMY REACTION
# ============================================================

enemy_reaction_delay = 250

enemy_awake_time = 0


# ============================================================
# ARMED ENEMIES
# ============================================================

armed_enemy_min_level = 5

armed_enemy_shoot_cooldown = 1200

armed_enemy_bullet_speed = 5

armed_enemy_bullet_size = 8

enemy_bullets = []


# ============================================================
# PLAYER BULLETS
# ============================================================

bullets = []

bullet_speed = 10

bullet_size = 6

shoot_cooldown = 250

last_shot = 0


# ============================================================
# AUTO GUN
# ============================================================

auto_gun = False

auto_gun_cooldown = 100

last_auto_shot = 0


# ============================================================
# EXPLOSIVES
# ============================================================

explosives = 0

explosive_cost = 100

explosive_radius = 130

last_explosive = 0

explosive_cooldown = 500


# ============================================================
# EXPLOSION EFFECTS
# ============================================================

explosions = []


def create_explosion(
    x,
    y
):

    explosions.append({

        "x": x,

        "y": y,

        "radius": 0,

        "max_radius": explosive_radius,

        "timer": 0,

        "duration": 250

    })


def update_explosions():

    for explosion in explosions:

        explosion["timer"] += (
            clock.get_time()
        )

        progress = (
            explosion["timer"]
            / explosion["duration"]
        )

        progress = min(
            1,
            progress
        )

        explosion["radius"] = (
            explosion["max_radius"]
            * progress
        )

    explosions[:] = [

        explosion

        for explosion in explosions

        if explosion["timer"]
        < explosion["duration"]

    ]


def draw_explosions():

    for explosion in explosions:

        radius = int(
            explosion["radius"]
        )

        if radius <= 0:
            continue

        alpha = int(

            180
            *
            (
                1
                -
                explosion["timer"]
                / explosion["duration"]
            )

        )

        surface = pygame.Surface(
            (
                radius * 2,
                radius * 2
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(

            surface,

            (
                255,
                150,
                20,
                alpha
            ),

            (
                radius,
                radius
            ),

            radius

        )

        pygame.draw.circle(

            surface,

            (
                255,
                230,
                80,
                min(
                    255,
                    alpha + 50
                )
            ),

            (
                radius,
                radius
            ),

            max(
                1,
                radius // 3
            )

        )

        screen.blit(

            surface,

            (
                int(
                    explosion["x"]
                    - radius
                ),

                int(
                    explosion["y"]
                    - radius
                )
            )

        )


# ============================================================
# BUTTONS
# ============================================================

def make_buttons():

    global play_button
    global tutorial_button
    global exit_button

    global pause_resume_button
    global pause_tutorial_button
    global pause_shop_button
    global pause_menu_button

    global tutorial_pause_resume_button
    global tutorial_pause_restart_button
    global tutorial_pause_menu_button

    global shop_auto_button
    global shop_explosive_button
    global shop_back_button

    global restart_button
    global menu_button

    cx = WIDTH // 2

    play_button = pygame.Rect(
        cx - 180,
        HEIGHT // 2 - 60,
        360,
        65
    )

    tutorial_button = pygame.Rect(
        cx - 180,
        HEIGHT // 2 + 20,
        360,
        65
    )

    exit_button = pygame.Rect(
        cx - 180,
        HEIGHT // 2 + 100,
        360,
        65
    )

    pause_resume_button = pygame.Rect(
        cx - 180,
        220,
        360,
        60
    )

    pause_tutorial_button = pygame.Rect(
        cx - 180,
        295,
        360,
        60
    )

    pause_shop_button = pygame.Rect(
        cx - 180,
        370,
        360,
        60
    )

    pause_menu_button = pygame.Rect(
        cx - 180,
        445,
        360,
        60
    )

    tutorial_pause_resume_button = pygame.Rect(
        cx - 180,
        250,
        360,
        60
    )

    tutorial_pause_restart_button = pygame.Rect(
        cx - 180,
        325,
        360,
        60
    )

    tutorial_pause_menu_button = pygame.Rect(
        cx - 180,
        400,
        360,
        60
    )

    shop_auto_button = pygame.Rect(
        cx - 180,
        250,
        360,
        65
    )

    shop_explosive_button = pygame.Rect(
        cx - 180,
        330,
        360,
        65
    )

    shop_back_button = pygame.Rect(
        cx - 180,
        410,
        360,
        65
    )

    restart_button = pygame.Rect(
        cx - 120,
        HEIGHT // 2 + 90,
        240,
        60
    )

    menu_button = pygame.Rect(
        cx - 120,
        HEIGHT // 2 + 165,
        240,
        60
    )


make_buttons()


# ============================================================
# BUTTON DRAW
# ============================================================

def draw_button(
    rect,
    text,
    color
):

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        WHITE,
        rect,
        2,
        border_radius=8
    )

    surface = button_font.render(
        text,
        True,
        WHITE
    )

    screen.blit(
        surface,
        surface.get_rect(
            center=rect.center
        )
    )


# ============================================================
# SPAWN ENEMY
# ============================================================

def spawn_enemy(
    armed=False
):

    enemy = pygame.Rect(
        0,
        0,
        enemy_size,
        enemy_size
    )

    attempts = 0

    while attempts < 500:

        attempts += 1

        enemy.x = random.randint(
            50,
            max(
                51,
                WIDTH - enemy.width - 50
            )
        )

        enemy.y = random.randint(
            120,
            max(
                121,
                HEIGHT - enemy.height - 50
            )
        )

        valid = True

        if enemy.colliderect(
            player.inflate(
                350,
                350
            )
        ):

            valid = False

        if valid:

            for wall in walls:

                if enemy.colliderect(
                    wall
                ):

                    valid = False
                    break

        if valid:

            for other in enemies:

                if enemy.colliderect(
                    other["rect"].inflate(
                        20,
                        20
                    )
                ):

                    valid = False
                    break

        if valid:
            break

    hp = (

        armed_enemy_hp

        if armed

        else normal_enemy_hp

    )

    enemies.append({

        "rect": enemy,

        "armed": armed,

        "hp": hp,

        "max_hp": hp,

        "last_shot":
            pygame.time.get_ticks(),

        "path": [],

        "last_path_update": 0

    })


# ============================================================
# START LEVEL
# ============================================================

def start_level():

    global enemy_awake_time

    enemies.clear()

    bullets.clear()

    enemy_bullets.clear()

    explosions.clear()

    player.center = (
        WIDTH // 2,
        HEIGHT // 2
    )

    create_walls()

    enemy_awake_time = (

        pygame.time.get_ticks()

        + enemy_reaction_delay

    )

    for _ in range(level):

        spawn_enemy(False)

    if level >= armed_enemy_min_level:

        armed_count = (

            1
            +
            (
                (level - 5)
                // 3
            )

        )

        for _ in range(
            armed_count
        ):

            spawn_enemy(True)


# ============================================================
# RESET GAME
# ============================================================

def reset_game():

    global health
    global level
    global kills
    global credits
    global auto_gun
    global explosives
    global game_state

    global last_shot
    global last_auto_shot
    global last_damage
    global red_flash_until
    global last_explosive

    health = max_health

    level = 1

    kills = 0

    credits = 0

    auto_gun = False

    explosives = 0

    last_shot = 0

    last_auto_shot = 0

    last_damage = 0

    red_flash_until = 0

    last_explosive = 0

    bullets.clear()

    enemy_bullets.clear()

    explosions.clear()

    player.center = (
        WIDTH // 2,
        HEIGHT // 2
    )

    game_state = "game"

    start_level()


# ============================================================
# SHOOT
# ============================================================

def shoot():

    mouse_x, mouse_y = (
        pygame.mouse.get_pos()
    )

    dx = (
        mouse_x
        - player.centerx
    )

    dy = (
        mouse_y
        - player.centery
    )

    distance = math.hypot(
        dx,
        dy
    )

    if distance == 0:
        return

    dx /= distance
    dy /= distance

    bullets.append({

        "x": float(
            player.centerx
        ),

        "y": float(
            player.centery
        ),

        "dx": dx,

        "dy": dy

    })


# ============================================================
# ENEMY SHOOT
# ============================================================

def enemy_shoot(
    enemy
):

    dx = (
        player.centerx
        - enemy["rect"].centerx
    )

    dy = (
        player.centery
        - enemy["rect"].centery
    )

    distance = math.hypot(
        dx,
        dy
    )

    if distance == 0:
        return

    dx /= distance
    dy /= distance

    enemy_bullets.append({

        "x": float(
            enemy["rect"].centerx
        ),

        "y": float(
            enemy["rect"].centery
        ),

        "dx": dx,

        "dy": dy

    })


# ============================================================
# EXPLOSIVE
# ============================================================

def use_explosive():

    global explosives
    global last_explosive
    global kills
    global credits

    current_time = (
        pygame.time.get_ticks()
    )

    if explosives <= 0:
        return

    if (
        current_time
        - last_explosive
        < explosive_cooldown
    ):

        return

    mouse_x, mouse_y = (
        pygame.mouse.get_pos()
    )

    create_explosion(
        mouse_x,
        mouse_y
    )

    killed_enemies = []

    for enemy in enemies:

        distance = math.hypot(

            enemy["rect"].centerx
            - mouse_x,

            enemy["rect"].centery
            - mouse_y

        )

        if distance <= explosive_radius:

            killed_enemies.append(
                enemy
            )

    for enemy in killed_enemies:

        if enemy in enemies:

            enemies.remove(
                enemy
            )

            kills += 1

            credits += (
                get_kill_reward()
            )

    explosives -= 1

    last_explosive = (
        current_time
    )


# ============================================================
# DAMAGE PLAYER
# ============================================================

def damage_player(
    amount,
    current_time
):

    global health
    global last_damage
    global red_flash_until

    if (
        current_time
        - last_damage
        < damage_cooldown
    ):

        return

    health -= amount

    last_damage = current_time

    red_flash_until = (
        current_time
        + flash_duration
    )


# ============================================================
# UPDATE ENEMIES
# ============================================================

def update_enemies(
    current_time
):

    enemies_awake = (
        current_time
        >= enemy_awake_time
    )

    for enemy in enemies:

        rect = enemy["rect"]

        # ====================================================
        # ARMED ENEMIES
        # ====================================================

        if enemy["armed"]:

            if enemies_awake:

                if (
                    current_time
                    - enemy["last_shot"]
                    >=
                    armed_enemy_shoot_cooldown
                ):

                    enemy_shoot(
                        enemy
                    )

                    enemy["last_shot"] = (
                        current_time
                    )

            continue

        # ====================================================
        # NORMAL ENEMIES
        # ====================================================

        if not enemies_awake:
            continue

        # Recalculate their route regularly.

        if (

            current_time
            - enemy["last_path_update"]
            >= PATH_RECALCULATE_TIME

            or

            not enemy["path"]

        ):

            enemy["path"] = (
                find_enemy_path(

                    rect.center,

                    player.center

                )
            )

            enemy["last_path_update"] = (
                current_time
            )

        # ====================================================
        # FOLLOW PATH
        # ====================================================

        if enemy["path"]:

            # Remove waypoints we've reached.

            while (
                len(enemy["path"]) > 1
            ):

                next_x, next_y = (
                    cell_to_position(
                        enemy["path"][1]
                    )
                )

                distance = math.hypot(

                    next_x
                    - rect.centerx,

                    next_y
                    - rect.centery

                )

                if distance < 15:

                    enemy["path"].pop(
                        0
                    )

                else:

                    break

            if len(enemy["path"]) > 1:

                target_x, target_y = (
                    cell_to_position(
                        enemy["path"][1]
                    )
                )

            else:

                target_x = (
                    player.centerx
                )

                target_y = (
                    player.centery
                )

            dx = (
                target_x
                - rect.centerx
            )

            dy = (
                target_y
                - rect.centery
            )

            distance = math.hypot(
                dx,
                dy
            )

            if distance > 2:

                dx /= distance
                dy /= distance

                move_with_walls(

                    rect,

                    dx * enemy_speed,

                    dy * enemy_speed

                )

        else:

            # Fallback if no route exists.

            dx = (
                player.centerx
                - rect.centerx
            )

            dy = (
                player.centery
                - rect.centery
            )

            distance = math.hypot(
                dx,
                dy
            )

            if distance > 0:

                dx /= distance
                dy /= distance

                move_with_walls(

                    rect,

                    dx * enemy_speed,

                    dy * enemy_speed

                )


# ============================================================
# UPDATE PLAYER BULLETS
# ============================================================

def update_player_bullets():

    global tutorial_enemy_killed
    global kills
    global credits

    bullets_to_remove = []

    enemies_to_remove = []

    for bullet in bullets:

        bullet["x"] += (
            bullet["dx"]
            * bullet_speed
        )

        bullet["y"] += (
            bullet["dy"]
            * bullet_speed
        )

        if (

            bullet["x"] < 0

            or

            bullet["x"] > WIDTH

            or

            bullet["y"] < 0

            or

            bullet["y"] > HEIGHT

        ):

            bullets_to_remove.append(
                bullet
            )

            continue

        bullet_rect = pygame.Rect(

            int(
                bullet["x"]
                - bullet_size / 2
            ),

            int(
                bullet["y"]
                - bullet_size / 2
            ),

            bullet_size,

            bullet_size

        )

        wall_hit = False

        for wall in walls:

            if bullet_rect.colliderect(
                wall
            ):

                wall_hit = True

                break

        if wall_hit:

            bullets_to_remove.append(
                bullet
            )

            continue

        for enemy in enemies:

            if enemy in enemies_to_remove:
                continue

            if bullet_rect.colliderect(
                enemy["rect"]
            ):

                bullets_to_remove.append(
                    bullet
                )

                enemy["hp"] -= 1

                if enemy["hp"] <= 0:

                    enemies_to_remove.append(
                        enemy
                    )

                break

    for bullet in bullets_to_remove:

        if bullet in bullets:

            bullets.remove(
                bullet
            )

    for enemy in enemies_to_remove:

        if enemy in enemies:

            enemies.remove(
                enemy
            )

            if game_state == "tutorial":

                tutorial_enemy_killed = True

            else:

                kills += 1

                credits += (
                    get_kill_reward()
                )


# ============================================================
# UPDATE ENEMY BULLETS
# ============================================================

def update_enemy_bullets(
    current_time
):

    bullets_to_remove = []

    for bullet in enemy_bullets:

        bullet["x"] += (
            bullet["dx"]
            * armed_enemy_bullet_speed
        )

        bullet["y"] += (
            bullet["dy"]
            * armed_enemy_bullet_speed
        )

        if (

            bullet["x"] < 0

            or

            bullet["x"] > WIDTH

            or

            bullet["y"] < 0

            or

            bullet["y"] > HEIGHT

        ):

            bullets_to_remove.append(
                bullet
            )

            continue

        bullet_rect = pygame.Rect(

            int(
                bullet["x"]
                - armed_enemy_bullet_size / 2
            ),

            int(
                bullet["y"]
                - armed_enemy_bullet_size / 2
            ),

            armed_enemy_bullet_size,

            armed_enemy_bullet_size

        )

        wall_hit = False

        for wall in walls:

            if bullet_rect.colliderect(
                wall
            ):

                wall_hit = True

                break

        if wall_hit:

            bullets_to_remove.append(
                bullet
            )

            continue

        if bullet_rect.colliderect(
            player
        ):

            bullets_to_remove.append(
                bullet
            )

            damage_player(
                10,
                current_time
            )

    for bullet in bullets_to_remove:

        if bullet in enemy_bullets:

            enemy_bullets.remove(
                bullet
            )


# ============================================================
# PLAYER / ENEMY COLLISION
# ============================================================

def check_enemy_collisions(
    current_time
):

    for enemy in enemies:

        if player.colliderect(
            enemy["rect"]
        ):

            damage_player(
                10,
                current_time
            )


# ============================================================
# TUTORIAL
# ============================================================

tutorial_step = 0

tutorial_enemy_moving = False

tutorial_enemy_killed = False

tutorial_finished = False


tutorial_messages = [

    (
        "WELCOME TO VOID RUNNER",
        "Let's get you ready for the run."
    ),

    (
        "MOVEMENT",
        "Use W A S D to move around."
    ),

    (
        "AIM",
        "Move your mouse to aim your weapon."
    ),

    (
        "SHOOTING",
        "LEFT CLICK to shoot the enemy."
    ),

    (
        "MOVING ENEMY",
        "Now it moves. Keep shooting and dodging."
    ),

    (
        "WALLS",
        "Walls block you AND bullets. Use them as cover."
    ),

    (
        "HEALTH",
        "Your HP is shown in the top-left corner."
    ),

    (
        "CREDITS",
        "Killing enemies gives you credits."
    ),

    (
        "LEVELS",
        "Kill every enemy to clear the level."
    ),

    (
        "ARMED ENEMIES",
        "From Level 5, armed enemies start appearing."
    ),

    (
        "ARMED ENEMIES",
        "They stay in place and fire pink projectiles."
    ),

    (
        "EXPLOSIVES",
        "Press E to use an explosive at your mouse."
    ),

    (
        "SHOP",
        "Press ESC to pause and open the Shop."
    ),

    (
        "AUTO GUN",
        "The Auto Gun costs $250 and fires while holding LEFT CLICK."
    ),

    (
        "EXPLOSIVES",
        "Explosives cost $100 each."
    ),

    (
        "PAUSE",
        "Press ESC anytime to pause the game."
    ),

    (
        "FULLSCREEN",
        "Press F11 to switch fullscreen/windowed mode."
    ),

    (
        "YOU'RE READY",
        "You've learned everything. Press ENTER to finish."
    )

]


def setup_tutorial():

    global tutorial_step
    global tutorial_enemy_moving
    global tutorial_enemy_killed
    global tutorial_finished

    enemies.clear()

    bullets.clear()

    enemy_bullets.clear()

    explosions.clear()

    walls.clear()

    tutorial_step = 0

    tutorial_enemy_moving = False

    tutorial_enemy_killed = False

    tutorial_finished = False

    player.center = (
        WIDTH // 2,
        HEIGHT // 2 + 120
    )


def start_tutorial():

    global game_state

    setup_tutorial()

    game_state = "tutorial"


def spawn_tutorial_enemy(
    moving
):

    global tutorial_enemy_moving
    global tutorial_enemy_killed

    enemies.clear()

    bullets.clear()

    tutorial_enemy_moving = moving

    tutorial_enemy_killed = False

    enemy = pygame.Rect(

        WIDTH // 2 - 25,

        HEIGHT // 2 - 100,

        50,

        50

    )

    enemies.append({

        "rect": enemy,

        "armed": False,

        "hp": 3,

        "max_hp": 3,

        "last_shot":
            pygame.time.get_ticks(),

        "path": [],

        "last_path_update": 0

    })


def advance_tutorial():

    global tutorial_step
    global tutorial_enemy_moving
    global tutorial_finished

    if tutorial_step == 0:

        tutorial_step = 1

    elif tutorial_step == 1:

        tutorial_step = 2

    elif tutorial_step == 2:

        spawn_tutorial_enemy(
            False
        )

        tutorial_step = 3

    elif tutorial_step == 3:

        if not tutorial_enemy_killed:

            return

        spawn_tutorial_enemy(
            True
        )

        tutorial_step = 4

    elif tutorial_step == 4:

        if not tutorial_enemy_killed:

            return

        enemies.clear()

        bullets.clear()

        walls.clear()

        walls.append(
            pygame.Rect(
                WIDTH // 2 - 250,
                HEIGHT // 2,
                180,
                30
            )
        )

        walls.append(
            pygame.Rect(
                WIDTH // 2 + 70,
                HEIGHT // 2,
                180,
                30
            )
        )

        tutorial_step = 5

    elif tutorial_step == 5:

        walls.clear()

        tutorial_step = 6

    elif tutorial_step == 6:

        tutorial_step = 7

    elif tutorial_step == 7:

        tutorial_step = 8

    elif tutorial_step == 8:

        tutorial_step = 9

    elif tutorial_step == 9:

        enemies.clear()

        enemy = pygame.Rect(

            WIDTH // 2 - 25,

            HEIGHT // 2 - 100,

            50,

            50

        )

        enemies.append({

            "rect": enemy,

            "armed": True,

            "hp": 2,

            "max_hp": 2,

            "last_shot":
                pygame.time.get_ticks()
                + 999999,

            "path": [],

            "last_path_update": 0

        })

        tutorial_step = 10

    elif tutorial_step == 10:

        enemies.clear()

        tutorial_step = 11

    elif tutorial_step == 11:

        tutorial_step = 12

    elif tutorial_step == 12:

        tutorial_step = 13

    elif tutorial_step == 13:

        tutorial_step = 14

    elif tutorial_step == 14:

        tutorial_step = 15

    elif tutorial_step == 15:

        tutorial_step = 16

    elif tutorial_step == 16:

        tutorial_step = 17

    elif tutorial_step == 17:

        tutorial_finished = True


def update_tutorial():

    update_player()

    if tutorial_step in [
        3,
        4
    ]:

        if tutorial_enemy_moving:

            for enemy in enemies:

                rect = enemy["rect"]

                dx = (
                    player.centerx
                    - rect.centerx
                )

                dy = (
                    player.centery
                    - rect.centery
                )

                distance = math.hypot(
                    dx,
                    dy
                )

                if distance != 0:

                    dx /= distance
                    dy /= distance

                    move_with_walls(

                        rect,

                        dx * enemy_speed,

                        dy * enemy_speed

                    )

        update_player_bullets()


# ============================================================
# DRAW WALLS
# ============================================================

def draw_walls():

    for wall in walls:

        pygame.draw.rect(
            screen,
            GRAY,
            wall
        )

        pygame.draw.rect(
            screen,
            LIGHT_GRAY,
            wall,
            3
        )


# ============================================================
# DRAW PLAYER
# ============================================================

def draw_player():

    pygame.draw.rect(
        screen,
        CYAN,
        player
    )


# ============================================================
# DRAW ENEMIES
# ============================================================

def draw_enemies():

    for enemy in enemies:

        rect = enemy["rect"]

        if enemy["armed"]:

            pygame.draw.rect(
                screen,
                PURPLE,
                rect
            )

            pygame.draw.circle(
                screen,
                YELLOW,
                rect.center,
                10
            )

        else:

            pygame.draw.rect(
                screen,
                RED,
                rect
            )

        ratio = max(
            0,
            enemy["hp"]
            / enemy["max_hp"]
        )

        pygame.draw.rect(

            screen,

            (50, 50, 50),

            (
                rect.x,
                rect.y - 10,
                rect.width,
                6
            )

        )

        pygame.draw.rect(

            screen,

            GREEN,

            (
                rect.x,
                rect.y - 10,
                int(
                    rect.width
                    * ratio
                ),
                6
            )

        )


# ============================================================
# DRAW BULLETS
# ============================================================

def draw_bullets():

    for bullet in bullets:

        pygame.draw.circle(

            screen,

            YELLOW,

            (
                int(
                    bullet["x"]
                ),
                int(
                    bullet["y"]
                )
            ),

            bullet_size // 2

        )

    for bullet in enemy_bullets:

        pygame.draw.circle(

            screen,

            PINK,

            (
                int(
                    bullet["x"]
                ),
                int(
                    bullet["y"]
                )
            ),

            armed_enemy_bullet_size // 2

        )


# ============================================================
# DRAW HUD
# ============================================================

def draw_hud():

    pygame.draw.rect(

        screen,

        (60, 60, 60),

        (
            20,
            20,
            300,
            30
        )

    )

    hp_width = int(

        300
        *
        max(
            0,
            health
            / max_health
        )

    )

    pygame.draw.rect(

        screen,

        GREEN,

        (
            20,
            20,
            hp_width,
            30
        )

    )

    hp_text = small_font.render(

        f"HP: {health}/{max_health}",

        True,

        WHITE

    )

    screen.blit(

        hp_text,

        (
            25,
            23
        )

    )

    level_text = small_font.render(

        f"LEVEL: {level}",

        True,

        WHITE

    )

    screen.blit(

        level_text,

        level_text.get_rect(

            center=(

                WIDTH // 2,

                35

            )

        )

    )

    kills_text = small_font.render(

        f"KILLS: {kills}",

        True,

        WHITE

    )

    screen.blit(

        kills_text,

        (
            WIDTH - 150,
            23
        )

    )

    credits_text = small_font.render(

        f"CREDITS: ${credits}",

        True,

        YELLOW

    )

    screen.blit(

        credits_text,

        (
            20,
            65
        )

    )

    explosive_text = small_font.render(

        f"EXPLOSIVES: {explosives} [E]",

        True,

        ORANGE

    )

    screen.blit(

        explosive_text,

        (
            20,
            95
        )

    )

    if auto_gun:

        auto_text = small_font.render(

            "AUTO GUN: ACTIVE",

            True,

            CYAN

        )

        screen.blit(

            auto_text,

            (
                WIDTH - 220,
                65
            )

        )


# ============================================================
# DRAW MENU
# ============================================================

def draw_menu():

    screen.fill(BG)

    pygame.draw.circle(

        screen,

        (25, 45, 55),

        (
            WIDTH // 2,
            HEIGHT // 2
        ),

        330

    )

    pygame.draw.circle(

        screen,

        (20, 35, 45),

        (
            WIDTH // 2,
            HEIGHT // 2
        ),

        240

    )

    title = title_font.render(

        "VOID RUNNER",

        True,

        CYAN

    )

    screen.blit(

        title,

        title.get_rect(

            center=(

                WIDTH // 2,

                120

            )

        )

    )

    subtitle = small_font.render(

        "SURVIVE. SHOOT. ESCAPE.",

        True,

        LIGHT_GRAY

    )

    screen.blit(

        subtitle,

        subtitle.get_rect(

            center=(

                WIDTH // 2,

                185

            )

        )

    )

    draw_button(

        play_button,

        "PLAY",

        (40, 130, 200)

    )

    draw_button(

        tutorial_button,

        "TUTORIAL",

        (80, 80, 160)

    )

    draw_button(

        exit_button,

        "EXIT",

        (170, 50, 50)

    )


# ============================================================
# DRAW TUTORIAL
# ============================================================

def draw_tutorial():

    screen.fill(BG)

    draw_walls()

    draw_player()

    draw_enemies()

    draw_bullets()

    draw_explosions()

    title, message = tutorial_messages[
        tutorial_step
    ]

    panel = pygame.Rect(

        WIDTH // 2 - 450,

        25,

        900,

        165

    )

    pygame.draw.rect(

        screen,

        (8, 8, 15),

        panel,

        border_radius=12

    )

    pygame.draw.rect(

        screen,

        CYAN,

        panel,

        3,

        border_radius=12

    )

    title_surface = button_font.render(

        title,

        True,

        YELLOW

    )

    screen.blit(

        title_surface,

        title_surface.get_rect(

            center=(

                WIDTH // 2,

                65

            )

        )

    )

    message_surface = small_font.render(

        message,

        True,

        WHITE

    )

    screen.blit(

        message_surface,

        message_surface.get_rect(

            center=(

                WIDTH // 2,

                110

            )

        )

    )

    if tutorial_step == 3:

        if tutorial_enemy_killed:

            instruction = (
                "Enemy destroyed! Press ENTER."
            )

        else:

            instruction = (
                "LEFT CLICK to shoot it."
            )

    elif tutorial_step == 4:

        if tutorial_enemy_killed:

            instruction = (
                "Nice! Press ENTER."
            )

        else:

            instruction = (
                "Shoot the moving enemy."
            )

    elif tutorial_step == 17:

        instruction = (
            "Press ENTER to return to the main menu."
        )

    else:

        instruction = (
            "Press ENTER to continue."
        )

    instruction_surface = tiny_font.render(

        instruction,

        True,

        LIGHT_GRAY

    )

    screen.blit(

        instruction_surface,

        instruction_surface.get_rect(

            center=(

                WIDTH // 2,

                150

            )

        )

    )


# ============================================================
# DRAW PAUSE
# ============================================================

def draw_pause():

    overlay = pygame.Surface(

        (
            WIDTH,
            HEIGHT
        ),

        pygame.SRCALPHA

    )

    overlay.fill(

        (
            0,
            0,
            0,
            210
        )

    )

    screen.blit(

        overlay,

        (0, 0)

    )

    title = big_font.render(

        "PAUSED",

        True,

        WHITE

    )

    screen.blit(

        title,

        title.get_rect(

            center=(

                WIDTH // 2,

                135

            )

        )

    )

    draw_button(

        pause_resume_button,

        "RESUME",

        (50, 150, 80)

    )

    draw_button(

        pause_tutorial_button,

        "TUTORIAL",

        (70, 80, 170)

    )

    draw_button(

        pause_shop_button,

        "SHOP",

        (150, 110, 40)

    )

    draw_button(

        pause_menu_button,

        "MAIN MENU",

        (150, 50, 50)

    )


# ============================================================
# DRAW TUTORIAL PAUSE
# ============================================================

def draw_tutorial_pause():

    overlay = pygame.Surface(

        (
            WIDTH,
            HEIGHT
        ),

        pygame.SRCALPHA

    )

    overlay.fill(

        (
            0,
            0,
            0,
            210
        )

    )

    screen.blit(

        overlay,

        (0, 0)

    )

    title = big_font.render(

        "TUTORIAL PAUSED",

        True,

        WHITE

    )

    screen.blit(

        title,

        title.get_rect(

            center=(

                WIDTH // 2,

                150

            )

        )

    )

    draw_button(

        tutorial_pause_resume_button,

        "RESUME",

        (50, 150, 80)

    )

    draw_button(

        tutorial_pause_restart_button,

        "RESTART TUTORIAL",

        (70, 80, 170)

    )

    draw_button(

        tutorial_pause_menu_button,

        "MAIN MENU",

        (150, 50, 50)

    )


# ============================================================
# DRAW SHOP
# ============================================================

def draw_shop():

    overlay = pygame.Surface(

        (
            WIDTH,
            HEIGHT
        ),

        pygame.SRCALPHA

    )

    overlay.fill(

        (
            5,
            5,
            15,
            240
        )

    )

    screen.blit(

        overlay,

        (0, 0)

    )

    title = big_font.render(

        "SHOP",

        True,

        WHITE

    )

    screen.blit(

        title,

        title.get_rect(

            center=(

                WIDTH // 2,

                100

            )

        )

    )

    money = button_font.render(

        f"CREDITS: ${credits}",

        True,

        YELLOW

    )

    screen.blit(

        money,

        money.get_rect(

            center=(

                WIDTH // 2,

                175

            )

        )

    )

    if auto_gun:

        draw_button(

            shop_auto_button,

            "AUTO GUN: OWNED",

            (60, 120, 60)

        )

    else:

        draw_button(

            shop_auto_button,

            "AUTO GUN - $250",

            (50, 120, 200)

        )

    draw_button(

        shop_explosive_button,

        "EXPLOSIVE - $100",

        (180, 80, 40)

    )

    draw_button(

        shop_back_button,

        "BACK",

        (90, 90, 90)

    )


# ============================================================
# DRAW NEXT LEVEL
# ============================================================

def draw_next_level():

    overlay = pygame.Surface(

        (
            WIDTH,
            HEIGHT
        ),

        pygame.SRCALPHA

    )

    overlay.fill(

        (
            0,
            0,
            0,
            190
        )

    )

    screen.blit(

        overlay,

        (0, 0)

    )

    title = big_font.render(

        "LEVEL COMPLETE",

        True,

        WHITE

    )

    screen.blit(

        title,

        title.get_rect(

            center=(

                WIDTH // 2,

                220

            )

        )

    )

    level_text = button_font.render(

        f"LEVEL {level} READY",

        True,

        CYAN

    )

    screen.blit(

        level_text,

        level_text.get_rect(

            center=(

                WIDTH // 2,

                300

            )

        )

    )

    continue_text = button_font.render(

        "PRESS ENTER TO CONTINUE",

        True,

        WHITE

    )

    screen.blit(

        continue_text,

        continue_text.get_rect(

            center=(

                WIDTH // 2,

                370

            )

        )

    )


# ============================================================
# DRAW GAME OVER
# ============================================================

def draw_game_over():

    overlay = pygame.Surface(

        (
            WIDTH,
            HEIGHT
        ),

        pygame.SRCALPHA

    )

    overlay.fill(

        (
            120,
            0,
            0,
            170
        )

    )

    screen.blit(

        overlay,

        (0, 0)

    )

    title = big_font.render(

        "GAME OVER",

        True,

        WHITE

    )

    screen.blit(

        title,

        title.get_rect(

            center=(

                WIDTH // 2,

                HEIGHT // 2 - 100

            )

        )

    )

    level_text = small_font.render(

        f"LEVEL REACHED: {level}",

        True,

        WHITE

    )

    screen.blit(

        level_text,

        level_text.get_rect(

            center=(

                WIDTH // 2,

                HEIGHT // 2 - 20

            )

        )

    )

    kills_text = small_font.render(

        f"KILLS: {kills}",

        True,

        WHITE

    )

    screen.blit(

        kills_text,

        kills_text.get_rect(

            center=(

                WIDTH // 2,

                HEIGHT // 2 + 20

            )

        )

    )

    draw_button(

        restart_button,

        "RESTART",

        (180, 40, 40)

    )

    draw_button(

        menu_button,

        "MAIN MENU",

        (70, 70, 100)

    )


# ============================================================
# UPDATE GAME
# ============================================================

def update_game(
    current_time
):

    global game_state
    global health
    global level
    global last_auto_shot

    update_player()

    update_enemies(
        current_time
    )

    check_enemy_collisions(
        current_time
    )

    mouse_buttons = (
        pygame.mouse.get_pressed()
    )

    if (

        auto_gun

        and

        mouse_buttons[0]

    ):

        if (

            current_time
            - last_auto_shot
            >= auto_gun_cooldown

        ):

            shoot()

            last_auto_shot = (
                current_time
            )

    update_player_bullets()

    update_enemy_bullets(
        current_time
    )

    if health <= 0:

        health = 0

        game_state = "game_over"

        return

    if len(enemies) == 0:

        level += 1

        health = max_health

        game_state = "next_level"

        return


# ============================================================
# MAIN LOOP
# ============================================================

running = True


# ============================================================
# FIRST LAUNCH
# ============================================================

if not tutorial_completed():

    start_tutorial()


# ============================================================
# LOOP
# ============================================================

while running:

    current_time = (
        pygame.time.get_ticks()
    )

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # F11
            # ------------------------------------------------

            if event.key == pygame.K_F11:

                fullscreen = not fullscreen

                if fullscreen:

                    screen = pygame.display.set_mode(

                        (
                            0,
                            0
                        ),

                        pygame.FULLSCREEN

                    )

                else:

                    screen = pygame.display.set_mode(

                        (
                            1100,
                            750
                        )

                    )

                WIDTH = screen.get_width()

                HEIGHT = screen.get_height()

                make_buttons()

                player.centerx = max(

                    25,

                    min(

                        WIDTH - 25,

                        player.centerx

                    )

                )

                player.centery = max(

                    25,

                    min(

                        HEIGHT - 25,

                        player.centery

                    )

                )

            # ------------------------------------------------
            # ESC
            # ------------------------------------------------

            elif event.key == pygame.K_ESCAPE:

                if game_state == "game":

                    game_state = "pause"

                elif game_state == "pause":

                    game_state = "game"

                elif game_state == "shop":

                    game_state = "pause"

                elif game_state == "tutorial":

                    game_state = "tutorial_pause"

                elif game_state == "tutorial_pause":

                    game_state = "tutorial"

            # ------------------------------------------------
            # ENTER
            # ------------------------------------------------

            elif event.key == pygame.K_RETURN:

                if game_state == "tutorial":

                    if tutorial_finished:

                        mark_tutorial_complete()

                        game_state = "menu"

                    else:

                        advance_tutorial()

                elif game_state == "next_level":

                    start_level()

                    game_state = "game"

            # ------------------------------------------------
            # EXPLOSIVE
            # ------------------------------------------------

            elif event.key == pygame.K_e:

                if game_state == "game":

                    use_explosive()

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = event.pos

            # ------------------------------------------------
            # MENU
            # ------------------------------------------------

            if game_state == "menu":

                if play_button.collidepoint(
                    mouse_pos
                ):

                    reset_game()

                elif tutorial_button.collidepoint(
                    mouse_pos
                ):

                    start_tutorial()

                elif exit_button.collidepoint(
                    mouse_pos
                ):

                    running = False

            # ------------------------------------------------
            # GAME
            # ------------------------------------------------

            elif game_state == "game":

                if event.button == 1:

                    if not auto_gun:

                        if (

                            current_time
                            - last_shot
                            >= shoot_cooldown

                        ):

                            shoot()

                            last_shot = (
                                current_time
                            )

            # ------------------------------------------------
            # PAUSE
            # ------------------------------------------------

            elif game_state == "pause":

                if pause_resume_button.collidepoint(
                    mouse_pos
                ):

                    game_state = "game"

                elif pause_tutorial_button.collidepoint(
                    mouse_pos
                ):

                    start_tutorial()

                elif pause_shop_button.collidepoint(
                    mouse_pos
                ):

                    game_state = "shop"

                elif pause_menu_button.collidepoint(
                    mouse_pos
                ):

                    game_state = "menu"

            # ------------------------------------------------
            # TUTORIAL PAUSE
            # ------------------------------------------------

            elif game_state == "tutorial_pause":

                if tutorial_pause_resume_button.collidepoint(
                    mouse_pos
                ):

                    game_state = "tutorial"

                elif tutorial_pause_restart_button.collidepoint(
                    mouse_pos
                ):

                    start_tutorial()

                elif tutorial_pause_menu_button.collidepoint(
                    mouse_pos
                ):

                    game_state = "menu"

            # ------------------------------------------------
            # SHOP
            # ------------------------------------------------

            elif game_state == "shop":

                if shop_auto_button.collidepoint(
                    mouse_pos
                ):

                    if (

                        not auto_gun

                        and

                        credits >= 250

                    ):

                        credits -= 250

                        auto_gun = True

                elif shop_explosive_button.collidepoint(
                    mouse_pos
                ):

                    if credits >= explosive_cost:

                        credits -= (
                            explosive_cost
                        )

                        explosives += 1

                elif shop_back_button.collidepoint(
                    mouse_pos
                ):

                    game_state = "pause"

            # ------------------------------------------------
            # GAME OVER
            # ------------------------------------------------

            elif game_state == "game_over":

                if restart_button.collidepoint(
                    mouse_pos
                ):

                    reset_game()

                elif menu_button.collidepoint(
                    mouse_pos
                ):

                    game_state = "menu"

            # ------------------------------------------------
            # TUTORIAL
            # ------------------------------------------------

            elif game_state == "tutorial":

                if event.button == 1:

                    if tutorial_step in [
                        3,
                        4
                    ]:

                        shoot()

    # ========================================================
    # UPDATE
    # ========================================================

    if game_state == "game":

        update_game(
            current_time
        )

    elif game_state == "tutorial":

        update_tutorial()

    update_explosions()

    # ========================================================
    # DRAW
    # ========================================================

    if game_state == "menu":

        draw_menu()

    elif game_state == "game":

        screen.fill(BG)

        draw_walls()

        draw_player()

        draw_enemies()

        draw_bullets()

        draw_explosions()

        draw_hud()

        if current_time < enemy_awake_time:

            warning = tiny_font.render(

                "ENEMIES WAKING...",

                True,

                YELLOW

            )

            screen.blit(

                warning,

                warning.get_rect(

                    center=(

                        WIDTH // 2,

                        90

                    )

                )

            )

        if current_time < red_flash_until:

            flash = pygame.Surface(

                (
                    WIDTH,
                    HEIGHT
                ),

                pygame.SRCALPHA

            )

            flash.fill(

                (
                    255,
                    0,
                    0,
                    90
                )

            )

            screen.blit(

                flash,

                (0, 0)

            )

    elif game_state == "tutorial":

        draw_tutorial()

    elif game_state == "tutorial_pause":

        draw_tutorial()

        draw_tutorial_pause()

    elif game_state == "pause":

        screen.fill(BG)

        draw_walls()

        draw_player()

        draw_enemies()

        draw_bullets()

        draw_explosions()

        draw_hud()

        draw_pause()

    elif game_state == "shop":

        screen.fill(BG)

        draw_shop()

    elif game_state == "next_level":

        screen.fill(BG)

        draw_walls()

        draw_player()

        draw_enemies()

        draw_hud()

        draw_next_level()

    elif game_state == "game_over":

        screen.fill(BG)

        draw_walls()

        draw_player()

        draw_enemies()

        draw_bullets()

        draw_explosions()

        draw_hud()

        draw_game_over()

    pygame.display.flip()

    clock.tick(60)


pygame.quit()