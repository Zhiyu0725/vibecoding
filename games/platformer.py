import pygame
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (70, 130, 180)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
SKY = (135, 206, 235)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Adventure")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 48
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.jumping = False
        self.facing_right = True
        self.alive = True
        self.coins = 0
        self.walk_frame = 0
        self.walk_timer = 0

    def draw_character(self):
        self.image.fill((0, 0, 0, 0))
        s = self.image

        # Body
        body_color = (50, 120, 200) if self.facing_right else (40, 100, 180)
        pygame.draw.rect(s, body_color, (6, 16, 20, 20))

        # Head
        pygame.draw.circle(s, (255, 200, 150), (16, 12), 10)

        # Eyes
        eye_offset = 4 if self.facing_right else -4
        pygame.draw.circle(s, BLACK, (16 + eye_offset, 10), 2)

        # Hat
        pygame.draw.rect(s, RED, (8, 0, 16, 6))
        pygame.draw.rect(s, RED, (4, 4, 24, 4))

        # Legs with walking animation
        leg_bob = abs(self.vel_x) > 0 and self.on_ground
        if leg_bob:
            self.walk_timer += 1
            if self.walk_timer > 6:
                self.walk_timer = 0
                self.walk_frame = (self.walk_frame + 1) % 4
            offsets = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            lo = offsets[self.walk_frame]
            pygame.draw.rect(s, (60, 60, 150), (8 + lo[0], 36 + lo[1], 6, 12))
            pygame.draw.rect(s, (60, 60, 150), (18 - lo[0], 36 - lo[1], 6, 12))
        else:
            self.walk_frame = 0
            self.walk_timer = 0
            pygame.draw.rect(s, (60, 60, 150), (8, 36, 6, 12))
            pygame.draw.rect(s, (60, 60, 150), (18, 36, 6, 12))

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -5
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = 5
            self.facing_right = True
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -14
            self.on_ground = False
            self.jumping = True

        self.vel_y += 0.7
        if self.vel_y > 12:
            self.vel_y = 12

        self.rect.x += self.vel_x
        self._collide(platforms, "horizontal")

        self.rect.y += self.vel_y
        self.on_ground = False
        self._collide(platforms, "vertical")

        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0

        if self.rect.top > SCREEN_HEIGHT + 100:
            self.alive = False

        self.draw_character()

    def _collide(self, platforms, direction):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if direction == "horizontal":
                    if self.vel_x > 0:
                        self.rect.right = p.rect.left
                    elif self.vel_x < 0:
                        self.rect.left = p.rect.right
                elif direction == "vertical":
                    if self.vel_y > 0:
                        self.rect.bottom = p.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.jumping = False
                    elif self.vel_y < 0:
                        self.rect.top = p.rect.bottom
                        self.vel_y = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.rect = self.image.get_rect(topleft=(x, y))
        if color == GREEN:
            pygame.draw.rect(self.image, DARK_GREEN, (0, 0, w, 6))
            pygame.draw.rect(self.image, GREEN, (0, 6, w, h - 6))
            for i in range(0, w, 20):
                pygame.draw.rect(self.image, DARK_GREEN, (i, 2, 4, 6))
        else:
            self.image.fill(color)


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (8, 8), 8)
        pygame.draw.circle(self.image, (200, 170, 0), (8, 8), 8, 2)
        font_c = pygame.font.SysFont("arial", 12, bold=True)
        txt = font_c.render("$", True, (180, 140, 0))
        self.image.blit(txt, (3, 1))
        self.rect = self.image.get_rect(center=(x, y))
        self.bob_offset = 0
        self.base_y = y
        self.timer = 0

    def update(self):
        self.timer += 0.05
        self.rect.centery = self.base_y + int(4 * pygame.math.Vector2(1, 0).rotate(self.timer * 57.3).y)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_left, patrol_right):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.vel_x = 2
        self.draw_enemy()

    def draw_enemy(self):
        self.image.fill((0, 0, 0, 0))
        s = self.image
        # Body (angry looking blob)
        pygame.draw.ellipse(s, (180, 50, 50), (2, 8, 28, 20))
        pygame.draw.ellipse(s, (140, 30, 30), (2, 8, 28, 20), 2)
        # Angry eyes
        pygame.draw.circle(s, WHITE, (10, 14), 5)
        pygame.draw.circle(s, WHITE, (22, 14), 5)
        pygame.draw.circle(s, BLACK, (12, 14), 3)
        pygame.draw.circle(s, BLACK, (20, 14), 3)
        # Angry eyebrows
        pygame.draw.line(s, BLACK, (6, 8), (14, 10), 2)
        pygame.draw.line(s, BLACK, (26, 8), (18, 10), 2)
        # Spikes on top
        for sx in [6, 14, 22]:
            pygame.draw.polygon(s, (200, 80, 80), [(sx - 3, 10), (sx, 0), (sx + 3, 10)])

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left <= self.patrol_left or self.rect.right >= self.patrol_right:
            self.vel_x *= -1
        self.draw_enemy()


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, w):
        super().__init__()
        self.image = pygame.Surface((w, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        for i in range(0, w, 16):
            pygame.draw.polygon(self.image, GRAY, [(i, 20), (i + 8, 0), (i + 16, 20)])


class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GRAY, (0, 0, 4, 64))
        pygame.draw.polygon(self.image, GREEN, [(4, 2), (4, 30), (36, 16)])
        self.rect = self.image.get_rect(bottomleft=(x, y))


def make_level_1():
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    flags = pygame.sprite.Group()

    # Ground
    ground_segments = [
        (0, 550, 300, 50),
        (380, 550, 200, 50),
        (660, 550, 140, 50),
    ]
    for x, y, w, h in ground_segments:
        platforms.add(Platform(x, y, w, h))

    # Floating platforms
    floating = [
        (200, 430, 100, 20),
        (400, 350, 120, 20),
        (150, 270, 100, 20),
        (550, 280, 100, 20),
        (350, 200, 120, 20),
        (600, 420, 80, 20),
        (50, 350, 80, 20),
        (650, 150, 100, 20),
    ]
    for x, y, w, h in floating:
        platforms.add(Platform(x, y, w, h))

    # Coins
    coin_positions = [
        (250, 410), (460, 330), (200, 250),
        (600, 260), (410, 180), (700, 400),
        (90, 330), (700, 130), (100, 530),
        (350, 530),
    ]
    for x, y in coin_positions:
        coins.add(Coin(x, y))

    # Enemies
    enemies.add(Enemy(390, 518, 380, 580))
    enemies.add(Enemy(160, 238, 150, 250))
    enemies.add(Enemy(560, 248, 550, 650))

    # Spikes
    spikes.add(Spike(300, 555, 80))

    # Flag at the end
    flags.add(Flag(740, 550))

    return platforms, coins, enemies, spikes, flags


def make_level_2():
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    flags = pygame.sprite.Group()

    ground_segments = [
        (0, 550, 150, 50),
        (220, 550, 100, 50),
        (500, 550, 150, 50),
    ]
    for x, y, w, h in ground_segments:
        platforms.add(Platform(x, y, w, h))

    floating = [
        (300, 450, 80, 20),
        (100, 380, 100, 20),
        (300, 320, 100, 20),
        (500, 380, 80, 20),
        (650, 300, 100, 20),
        (400, 220, 120, 20),
        (150, 180, 80, 20),
        (600, 150, 100, 20),
        (300, 100, 100, 20),
    ]
    for x, y, w, h in floating:
        platforms.add(Platform(x, y, w, h))

    coin_positions = [
        (340, 430), (150, 360), (350, 300),
        (540, 360), (700, 280), (460, 200),
        (190, 160), (650, 130), (350, 80),
        (70, 530), (570, 530),
    ]
    for x, y in coin_positions:
        coins.add(Coin(x, y))

    enemies.add(Enemy(230, 518, 220, 320))
    enemies.add(Enemy(310, 288, 300, 400))
    enemies.add(Enemy(410, 188, 400, 520))
    enemies.add(Enemy(610, 118, 600, 700))

    spikes.add(Spike(150, 555, 70))
    spikes.add(Spike(320, 555, 180))
    spikes.add(Spike(650, 555, 80))

    flags.add(Flag(340, 100))

    return platforms, coins, enemies, spikes, flags


def draw_background(scroll_x):
    screen.fill(SKY)
    for i in range(0, SCREEN_WIDTH + 200, 200):
        offset = (i - scroll_x * 0.3) % (SCREEN_WIDTH + 200)
        pygame.draw.ellipse(screen, (100, 180, 100), (offset - 50, SCREEN_HEIGHT - 180, 160, 80))
    for i in range(0, SCREEN_WIDTH + 300, 300):
        offset = (i - scroll_x * 0.15) % (SCREEN_WIDTH + 300)
        h = 80 + (i * 37) % 40
        pygame.draw.ellipse(screen, (80, 160, 80), (offset - 40, SCREEN_HEIGHT - 140 - h // 3, 200, h))


def run_game():
    level = 1
    levels = {1: make_level_1, 2: make_level_2}
    max_level = 2

    platforms, coin_sprites, enemy_sprites, spike_sprites, flag_sprites = levels[level]()
    player = Player(50, 500)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(*platforms)
    all_sprites.add(*coin_sprites)
    all_sprites.add(*enemy_sprites)
    all_sprites.add(*spike_sprites)
    all_sprites.add(*flag_sprites)

    game_over = False
    game_won = False
    victory = False

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return run_game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if game_over or game_won:
                    if event.key == pygame.K_RETURN:
                        if game_won and level < max_level:
                            level += 1
                            platforms, coin_sprites, enemy_sprites, spike_sprites, flag_sprites = levels[level]()
                            all_sprites.empty()
                            all_sprites.add(player)
                            all_sprites.add(*platforms)
                            all_sprites.add(*coin_sprites)
                            all_sprites.add(*enemy_sprites)
                            all_sprites.add(*spike_sprites)
                            all_sprites.add(*flag_sprites)
                            player.rect.topleft = (50, 500)
                            player.alive = True
                            game_over = False
                            game_won = False
                        else:
                            return run_game()

        if not game_over and not game_won:
            player.update(platforms)

            for enemy in enemy_sprites:
                enemy.update()

            for coin in coin_sprites:
                coin.update()

            # Coin collection
            collected = pygame.sprite.spritecollide(player, coin_sprites, True)
            for c in collected:
                player.coins += 1

            # Enemy collision
            if pygame.sprite.spritecollide(player, enemy_sprites, False):
                player.alive = False

            # Spike collision
            if pygame.sprite.spritecollide(player, spike_sprites, False):
                player.alive = False

            # Flag reached
            if pygame.sprite.spritecollide(player, flag_sprites, False):
                game_won = True

            if not player.alive:
                game_over = True

        # Draw
        draw_background(0)
        all_sprites.draw(screen)

        # HUD
        coin_text = font.render(f"Coins: {player.coins}", True, WHITE)
        level_text = font.render(f"Level {level}", True, WHITE)
        screen.blit(coin_text, (10, 10))
        screen.blit(level_text, (SCREEN_WIDTH - 100, 10))

        # Game Over screen
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            go_text = big_font.render("GAME OVER", True, RED)
            hint = font.render("Press R to restart or ESC to quit", True, WHITE)
            screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 250))
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 320))

        # Win screen
        if game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            win_text = big_font.render("LEVEL COMPLETE!", True, YELLOW)
            coin_info = font.render(f"Coins collected: {player.coins}", True, WHITE)
            if level < max_level:
                hint = font.render("Press ENTER for next level or R to restart", True, WHITE)
            else:
                hint = font.render("YOU BEAT THE GAME! Press ENTER to play again", True, YELLOW)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 220))
            screen.blit(coin_info, (SCREEN_WIDTH // 2 - coin_info.get_width() // 2, 290))
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 340))

        pygame.display.flip()


if __name__ == "__main__":
    run_game()
