import pygame
import random
import os
import functions_starcall as func


surface_width = 160
surface_height = 240
window_scale = 4
surface = pygame.Surface((surface_width, surface_height))
window_size = (surface_width * window_scale, surface_height * window_scale)

window = pygame.display.set_mode(window_size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
pygame.display.set_caption("StarCall")

pygame.font.init()

# Sprites
spr_PLAYER_IDLE = pygame.image.load(os.path.join("starcall/assets", "player", "protagonist_slowfall.png"))
spr_PLAYER_DOWN = pygame.image.load(os.path.join("starcall/assets", "player", "protagonist_freefall.png"))
spr_PLAYER_DEATH = [pygame.image.load(os.path.join("starcall/assets", "player", "protagonist_death.png")),
                    pygame.image.load(os.path.join("starcall/assets", "player", "protagonist_death_umbrella.png"))]

spr_ROOM_WALL = pygame.image.load(os.path.join("starcall/assets", "room", "cloud_tile.png"))
spr_ENEMY_EYEBAT = func.load_animation_sprites(os.path.join("starcall/assets", "enemies", "EyeBat"), "EyeBat", 5)

spr_MENU_BG = func.load_animation_sprites(os.path.join("starcall/assets", "menu"), "Menu_background_jump", 23)

# colors
col_BACKGROUND = (50, 61, 127)
col_WHITE = (255, 255, 255)
col_RED = (255, 0, 0)

# fonts
font_PRIMARY = pygame.font.Font(os.path.join("starcall/assets", "fonts", "visitor1.ttf"), 12)
font_PRIMARY_BIG = pygame.font.Font(os.path.join("starcall/assets", "fonts", "visitor1.ttf"), 24)

# Constants
LEFT = -1
RIGHT = 1
UP = -1
DOWN = 1
TILE_SIZE = 16

# Menu


# Game initialization variables
scroll_speed = 1
enemy_spawn_chance = 0.1
upwards_draft_strength = 3
stable_altitude = 50
gravity = 0.05

enemies = []
walls = []
particles = []
target_enemy_count_start = 3
target_enemy_count = target_enemy_count_start


class Creature:
    def __init__(self, x, y):
        self.dead = False
        self.x = x
        self.y = y
        self.angle = 0
        self.facing = RIGHT
        self.hspd = 0
        self.vspd = 0
        self.hitbox = None
        self.hitbox_rect = None

        self.active_image = None
        self.rect = None

    def draw_self(self, draw_surface):
        if self.active_image is not None:
            img = self.active_image
            if self.facing == LEFT:
                img = pygame.transform.flip(self.active_image, True, False)
            img, self.rect = func.rot_center(img, self.angle, self.x, self.y)
            draw_surface.blit(img, self.rect)

    def get_width(self):
        return self.active_image.get_width()

    def get_height(self):
        return self.active_image.get_height()

    def get_hitbox_width(self):
        return self.hitbox[2]

    def get_hitbox_height(self):
        return self.hitbox[3]

    def change_sprite(self, sprite):
        if self.active_image != sprite:
            self.active_image = sprite

    def update_hitbox_rect(self, hitbox):
        return pygame.Rect(self.x + hitbox[0], self.y + hitbox[1], hitbox[2], hitbox[3])


class Player(Creature):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image_idle = spr_PLAYER_IDLE
        self.image_down = spr_PLAYER_DOWN
        self.active_image = self.image_idle
        self.mask = pygame.mask.from_surface(self.active_image)
        self.max_vspd = 1
        self.max_hspd = 2
        self.spd_buildup_h = 0.2
        self.spd_buildup_v = 0.5
        self.horizontal_resistance = 0.075
        self.facing = RIGHT
        self.max_angle = 35
        self.rotation_spd = 1.5
        self.hitbox = (-4, -2, 9, 9)
        self.hitbox_rect = self.update_hitbox_rect(self.hitbox)
        self.hitbox_attack = (-1, 21, 3, 3)
        self.hitbox_attack_rect = self.update_hitbox_rect(self.hitbox_attack)

    def accelerate_horizontally(self, direction):
        if self.vspd > 0:
            self.hspd = func.approach(self.hspd, self.max_hspd / 2  * direction, self.spd_buildup_h)
        else:
            self.hspd = func.approach(self.hspd, self.max_hspd * direction, self.spd_buildup_h)
            self.angle = func.approach(self.angle, self.max_angle*direction*-1, self.rotation_spd)
        self.facing = direction

    def accelerate_vertically(self, direction):
        if direction == DOWN:
            self.angle = 0
            self.vspd = func.approach(self.vspd, self.max_vspd, self.spd_buildup_v)
        else:
            self.vspd = func.approach(self.vspd, -(self.max_vspd+upwards_draft_strength), self.spd_buildup_v*upwards_draft_strength)

    def move_and_collide(self):
        if self.hspd != 0:
            predicted_pos = self.x + self.hspd + self.get_hitbox_width()/2 * self.facing
            if predicted_pos > surface_width - TILE_SIZE or predicted_pos < TILE_SIZE:
                self.hspd = 0
            self.x += self.hspd
        if self.vspd != 0:
            predicted_pos = self.y + self.vspd + self.get_hitbox_height()/2
            if predicted_pos > surface_height - self.hitbox[3] or predicted_pos < stable_altitude:
                self.vspd = 0
            self.y += self.vspd


class Enemy(Creature):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vspd = scroll_speed
        self.sprite = spr_ENEMY_EYEBAT
        self.frame = random.randint(0, len(self.sprite) - 1)
        self.active_image = spr_ENEMY_EYEBAT[self.frame]
        self.facing = random.choice([LEFT, RIGHT])
        self.hspd = 1 * self.facing
        self.anim_clock = 0
        self.anim_speed = 6
        self.hitbox = (-6, -8, 13, 17)
        self.hitbox_rect = self.update_hitbox_rect(self.hitbox)

    def move_and_collide(self):
        if not self.dead:
            predicted_pos = self.x + self.hspd + self.get_hitbox_width()/2 * self.facing
            if predicted_pos > surface_width - TILE_SIZE or predicted_pos < TILE_SIZE:
                self.hspd *= -1
                self.facing *= -1
        else:
            self.vspd -= gravity
        self.x += self.hspd
        self.y -= self.vspd

    def animate(self):
        if self.anim_clock <= 0:
            self.anim_clock = self.anim_speed
            if self.frame+1 > len(self.sprite)-1:
                self.frame = 0
            else:
                self.frame += 1
            self.change_sprite(self.sprite[self.frame])
        self.anim_clock -= 1


class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active_image = spr_ROOM_WALL
        self.vspd = scroll_speed
        if x > surface_width/2:
            self.active_image = pygame.transform.flip(self.active_image, True, False)
            self.rect = self.active_image.get_rect(topright=(x, y))
        else:
            self.rect = self.active_image.get_rect(topleft=(x, y))

    def draw_self(self, draw_surface):
        if self.active_image is not None:
            if self.x > surface_width / 2:
                self.rect = self.active_image.get_rect(topright=(self.x, self.y))
            else:
                self.rect = self.active_image.get_rect(topleft=(self.x, self.y))
            draw_surface.blit(self.active_image, self.rect)

    def move(self):
        self.y -= self.vspd
        if self.y <= -TILE_SIZE:
            self.y = surface_height-1
            multiplier = (target_enemy_count-len(enemies))*enemy_spawn_chance
            if random.randint(0, 100) < (enemy_spawn_chance+multiplier) * 100:
                enemy = Enemy(random.randrange(TILE_SIZE, surface_width-TILE_SIZE), self.y+TILE_SIZE)
                enemies.append(enemy)


class Particle:
    def __init__(self, x, y, hspd, vspd, sprite, frame=-1, lifespan=-1, horizontal_resistance=0, gravity=0, rotation=0):
        self.x = x
        self.y = y
        self.angle = 0
        self.facing = RIGHT
        self.hspd = hspd
        self.vspd = vspd
        self.rotation = rotation
        self.hitbox = None
        self.hitbox_rect = None
        self.lifespan = lifespan
        self.gravity = gravity
        self.horizontal_resistance = horizontal_resistance

        self.sprite = sprite
        self.frame = frame
        if frame != -1:
            self.active_image = sprite[frame]
        else:
            self.active_image = sprite
        self.rect = None
        self.hitbox = (-self.get_width()/2, -self.get_height()/2, self.get_width(), self.get_height())
        self.hitbox_rect = self.update_hitbox_rect(self.hitbox)

    def draw_self(self, draw_surface):
        if self.active_image is not None:
            img = self.active_image
            if self.facing == LEFT:
                img = pygame.transform.flip(self.active_image, True, False)
            img, self.rect = func.rot_center(img, self.angle, self.x, self.y)
            draw_surface.blit(img, self.rect)

    def move(self):
        self.x += self.hspd
        self.y += self.vspd
        self.hspd = func.approach(self.hspd, 0, self.horizontal_resistance)
        self.vspd += self.gravity
        self.angle += self.rotation

    def update_hitbox_rect(self, hitbox):
        return pygame.Rect(self.x + hitbox[0], self.y + hitbox[1], hitbox[2], hitbox[3])

    def get_width(self):
        return self.active_image.get_width()

    def get_height(self):
        return self.active_image.get_height()


def main():
    running = True
    fps = 60
    clock = pygame.time.Clock()

    debug_mode = False
    score = 0
    game_file_path = os.getenv('APPDATA') + r"\starcall"

    if not os.path.exists(game_file_path):
        os.makedirs(game_file_path)

    if not os.path.isfile(game_file_path + r"\highscores.txt"):
        with open(game_file_path + r"\highscores.txt", 'w') as file:
            file.write("0")
            hscore = 0
    else:
        with open(game_file_path + r"\highscores.txt", 'r') as file:
            hscore = int(file.readline())

    for i in range(int(surface_height / TILE_SIZE) + 1):
        wall = Wall(0, TILE_SIZE * i)
        wall2 = Wall(surface_width, TILE_SIZE * i)
        walls.append(wall)
        walls.append(wall2)

    player = Player(surface_width/2, stable_altitude)

    def draw_window():
        surface.fill(col_BACKGROUND)

        for wall in walls:
            wall.draw_self(surface)

        for enemy in enemies:
            enemy.draw_self(surface)
            if debug_mode:
                pygame.draw.rect(surface, col_WHITE, enemy.hitbox_rect)

        for particle in particles:
            particle.draw_self(surface)
            if debug_mode:
                pygame.draw.rect(surface, col_WHITE, particle.hitbox_rect)

        if not player.dead:
            player.draw_self(surface)
        if debug_mode:
            pygame.draw.rect(surface, col_WHITE, player.hitbox_rect)
            if player.hitbox_attack_rect is not None:
                pygame.draw.rect(surface, col_RED, player.hitbox_attack_rect)

        text = font_PRIMARY_BIG.render(f"{score//10}", False, col_WHITE)
        text_rect = text.get_rect(center=(surface_width/2, 10))
        surface.blit(text, text_rect)

        text = font_PRIMARY.render(f"to beat: {hscore // 10}", False, col_WHITE)
        text_rect = text.get_rect(center=(surface_width / 2, 10 + font_PRIMARY.get_height()))
        surface.blit(text, text_rect)

        if player.dead:
            text = font_PRIMARY_BIG.render("GAME OVER", False, col_WHITE)
            text_rect = text.get_rect(center=(surface_width / 2, surface_height / 2))
            surface.blit(text, text_rect)
            text = font_PRIMARY.render("Press ESC", False, col_WHITE)
            text_rect = text.get_rect(center=(surface_width / 2, surface_height / 2 + font_PRIMARY_BIG.get_height() ))
            surface.blit(text, text_rect)

        scaled_surface = pygame.transform.scale(surface, window_size)
        window.blit(scaled_surface, (0, 0))

        pygame.display.update()

    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    debug_mode = not debug_mode
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not player.dead:
            score += 1
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                player.accelerate_horizontally(LEFT)
            if keys[pygame.K_d]:
                player.accelerate_horizontally(RIGHT)
            if keys[pygame.K_s]:
                player.accelerate_vertically(DOWN)
                player.change_sprite(spr_PLAYER_DOWN)
                player.hitbox_attack_rect = player.update_hitbox_rect(player.hitbox_attack)
            else:
                player.accelerate_vertically(UP)

                player.change_sprite(spr_PLAYER_IDLE)
                player.hitbox_attack_rect = None

            if (not keys[pygame.K_d] and not keys[pygame.K_a]) or (keys[pygame.K_d] and keys[pygame.K_a]):
                if player.hspd != 0:
                    player.hspd = func.approach(player.hspd, 0, player.horizontal_resistance)
                if player.angle != 0:
                    player.angle = func.approach(player.angle, 0, player.rotation_spd)

            player.move_and_collide()

            player.hitbox_rect = player.update_hitbox_rect(player.hitbox)

        for wall in walls[:]:
            wall.move()

        for particle in particles[:]:
            if particle.lifespan > 0:
                particle.lifespan -= 1
            elif particle.lifespan == 0 or (func.outside_surface(surface, particle) and particle.lifespan < 0):
                particles.remove(particle)
            particle.move()
            particle.hitbox_rect = particle.update_hitbox_rect(particle.hitbox)

        for enemy in enemies[:]:
            enemy.move_and_collide()
            if not enemy.dead:
                if enemy.y <= -TILE_SIZE:
                    enemies.remove(enemy)
                enemy.animate()
                enemy.hitbox_rect = enemy.update_hitbox_rect(enemy.hitbox)
                if not player.dead and player.hitbox_attack_rect is not None:
                    if enemy.hitbox_rect.colliderect(player.hitbox_attack_rect):
                        enemy.dead = True
                        enemy.vspd *= 2
                        player.vspd -= 6
                        score += 100
                if enemy.hitbox_rect.colliderect(player.hitbox_rect) and not player.dead:
                    player.dead = True
                    for i in range(2):
                        p_hspd = 0.2 * random.randint(-6, 6)
                        p_vspd = 0.5 * random.randint(-5, 0)
                        p_rot = random.randint(-10, 10)
                        part = Particle(player.x, player.y, p_hspd, p_vspd, spr_PLAYER_DEATH[i], -1, -1, 0, gravity, p_rot)
                        particles.append(part)

                        with open(game_file_path + r"\highscores.txt", 'r') as file:
                            hscore = int(file.readline())
                        if score > hscore:
                            with open(game_file_path + r"\highscores.txt", 'w') as file:
                                file.write(str(score))

            else:
                enemy.hitbox_rect = enemy.update_hitbox_rect(enemy.hitbox)
                if func.outside_surface(surface, enemy):
                    enemies.remove(enemy)

        draw_window()


main()
