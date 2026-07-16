import pygame
import sys
import math
import random
import json
import os

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

SW, SH = 800, 600
FPS = 60
GRAVITY = 0.62
TILE = 32

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (70, 130, 180)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
PURPLE = (150, 50, 200)
CYAN = (0, 220, 220)
PINK = (255, 100, 150)
DARK_BLUE = (20, 20, 50)
LAVA_RED = (220, 60, 20)
LAVA_ORANGE = (255, 140, 30)
LAVA_YELLOW = (255, 200, 50)
BROWN = (139, 90, 43)
DARK_BROWN = (100, 65, 30)

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Platformer Adventure DX")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)
big_font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 16)
title_font = pygame.font.SysFont("arial", 64, bold=True)
boss_font = pygame.font.SysFont("arial", 18, bold=True)
achievement_font = pygame.font.SysFont("arial", 14)

SAVE_PATH = os.path.join(os.path.expanduser("~"), ".platformer_save.json")


def generate_sound(freq, duration, volume=0.25, wave_type="sine", freq_end=None):
    sr = 22050
    n = int(sr * duration)
    buf = bytearray(n * 4)
    for i in range(n):
        t = i / sr
        f = freq + (freq_end - freq) * (i / n) if freq_end else freq
        if wave_type == "sine":
            val = int(volume * 32767 * math.sin(2 * math.pi * f * t))
        elif wave_type == "square":
            val = int(volume * 32767 * (1 if math.sin(2 * math.pi * f * t) > 0 else -1))
        elif wave_type == "saw":
            val = int(volume * 32767 * (2 * (f * t % 1) - 1))
        else:
            val = int(volume * 32767 * (random.random() * 2 - 1))
        env = max(0, 1.0 - (i / n) ** 0.5)
        val = max(-32767, min(32767, int(val * env)))
        buf[i * 4] = val & 0xFF
        buf[i * 4 + 1] = (val >> 8) & 0xFF
        buf[i * 4 + 2] = val & 0xFF
        buf[i * 4 + 3] = (val >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))


SND_JUMP = generate_sound(440, 0.12, 0.2, "sine")
SND_COIN = generate_sound(880, 0.08, 0.15, "sine")
SND_COIN2 = generate_sound(1100, 0.12, 0.15, "sine")
SND_DEATH = generate_sound(200, 0.35, 0.25, "square", 80)
SND_STOMP = generate_sound(300, 0.1, 0.2, "sine")
SND_SPRING = generate_sound(500, 0.2, 0.2, "sine", 900)
SND_POWERUP = generate_sound(523, 0.25, 0.2, "sine", 1047)
SND_CHECKPOINT = generate_sound(523, 0.15, 0.15, "sine")
SND_LEVELWIN = generate_sound(523, 0.5, 0.2, "sine", 1047)
SND_DASH = generate_sound(150, 0.15, 0.2, "saw", 50)
SND_WALLJUMP = generate_sound(350, 0.1, 0.15, "sine", 500)
SND_HURT = generate_sound(250, 0.2, 0.2, "square", 100)
SND_BOSS_HIT = generate_sound(100, 0.15, 0.25, "square")
SND_BOSS_DIE = generate_sound(80, 0.5, 0.3, "square", 30)
SND_ACHIEVE = generate_sound(660, 0.15, 0.15, "sine", 1320)
SND_LAVA = generate_sound(60, 0.3, 0.1, "noise")
SND_STAR = generate_sound(1200, 0.15, 0.15, "sine", 1800)


# ── Save System ──────────────────────────────────────────────
def load_save():
    try:
        with open(SAVE_PATH) as f:
            return json.load(f)
    except Exception:
        return {"best_times": {}, "total_coins": 0, "total_stars": 0,
                "levels_beaten": [], "achievements": [], "deaths": 0,
                "enemies_killed": 0, "best_combo": 0}


def write_save(data):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


save_data = load_save()


# ── Camera ───────────────────────────────────────────────────
class Camera:
    def __init__(self, lw, lh):
        self.offset = pygame.math.Vector2(0, 0)
        self.lw, self.lh = lw, lh
        self.shake_amount = 0
        self.shake_timer = 0

    def update(self, target):
        tx = target.centerx - SW // 2
        ty = target.centery - SH // 2
        self.offset.x += (tx - self.offset.x) * 0.1
        self.offset.y += (ty - self.offset.y) * 0.1
        self.offset.x = max(0, min(self.offset.x, self.lw - SW))
        self.offset.y = max(0, min(self.offset.y, self.lh - SH))
        if self.shake_timer > 0:
            self.shake_timer -= 1
            self.offset.x += random.randint(-self.shake_amount, self.shake_amount)
            self.offset.y += random.randint(-self.shake_amount, self.shake_amount)
            self.shake_amount = max(0, self.shake_amount - 0.5)

    def shake(self, amt=5, dur=15):
        self.shake_amount = amt
        self.shake_timer = dur

    def apply(self, rect):
        return pygame.Rect(rect.x - int(self.offset.x), rect.y - int(self.offset.y), rect.width, rect.height)


# ── Particles ────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=3, grav=0.1, fade=True, rot=False):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = self.max_life = life
        self.size = size
        self.grav = grav
        self.fade = fade
        self.rot = rot
        self.angle = random.uniform(0, 360) if rot else 0
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.grav
        self.life -= 1
        if self.rot:
            self.angle += self.vx * 5
        if self.life <= 0:
            self.alive = False

    def draw(self, surf, cam=None):
        a = int(255 * (self.life / self.max_life)) if self.fade else 255
        a = max(0, min(255, a))
        sz = max(1, int(self.size * (self.life / self.max_life)))
        x = self.x - (cam.offset.x if cam else 0)
        y = self.y - (cam.offset.y if cam else 0)
        s = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        c = (*self.color[:3], a)
        if self.rot:
            pygame.draw.rect(s, c, (0, 0, sz * 2, sz))
        else:
            pygame.draw.circle(s, c, (sz, sz), sz)
        if self.rot:
            s2 = pygame.transform.rotate(s, self.angle)
            surf.blit(s2, (int(x - s2.get_width() // 2), int(y - s2.get_height() // 2)))
        else:
            surf.blit(s, (int(x - sz), int(y - sz)))


class Particles:
    def __init__(self):
        self.list = []

    def emit(self, x, y, count, color, spread=3, life=30, size=3, grav=0.1, colors=None, rot=False):
        for _ in range(count):
            vx = random.uniform(-spread, spread)
            vy = random.uniform(-spread, 0)
            c = random.choice(colors) if colors else color
            self.list.append(Particle(x, y, vx, vy, c, random.randint(life // 2, life), size, grav, rot=rot))

    def trail(self, x, y, color, size=2):
        self.list.append(Particle(x, y, random.uniform(-0.5, 0.5), random.uniform(-1, 0), color, 15, size, 0))

    def update(self):
        for p in self.list:
            p.update()
        self.list = [p for p in self.list if p.alive]

    def draw(self, surf, cam=None):
        for p in self.list:
            p.draw(surf, cam)


particles = Particles()


# ── Achievement System ───────────────────────────────────────
class AchievementPopup:
    def __init__(self):
        self.current = None
        self.timer = 0
        self.alpha = 0

    def show(self, name, desc):
        if name in save_data.get("achievements", []):
            return
        save_data.setdefault("achievements", []).append(name)
        write_save(save_data)
        self.current = (name, desc)
        self.timer = 180
        self.alpha = 0
        SND_ACHIEVE.play()

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer > 150:
                self.alpha = min(255, self.alpha + 15)
            elif self.timer < 30:
                self.alpha = max(0, self.alpha - 8)
        else:
            self.current = None

    def draw(self, surf):
        if not self.current or self.alpha <= 0:
            return
        name, desc = self.current
        bg = pygame.Surface((280, 50), pygame.SRCALPHA)
        bg.fill((30, 30, 60, min(220, self.alpha)))
        pygame.draw.rect(bg, (*YELLOW, min(255, self.alpha)), (0, 0, 280, 50), 2, border_radius=6)
        surf.blit(bg, (SW // 2 - 140, 50))
        star = small_font.render("ACHIEVEMENT!", True, YELLOW)
        surf.blit(star, (SW // 2 - star.get_width() // 2, 54))
        t = achievement_font.render(f"{name}: {desc}", True, WHITE)
        surf.blit(t, (SW // 2 - t.get_width() // 2, 72))


ach_popup = AchievementPopup()


# ── Player ───────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.w, self.h = 28, 44
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x, self.vel_y = 0, 0
        self.speed = 5.2
        self.jump_power = -13.8
        self.on_ground = False
        self.jumping = False
        self.facing_right = True
        self.alive = True
        self.coins = 0
        self.stars = 0
        self.hp = 5
        self.max_hp = 5
        self.lives = 3
        self.walk_frame = 0
        self.walk_timer = 0
        self.inv_timer = 0
        self.squash, self.stretch = 1.0, 1.0
        self.spawn_x, self.spawn_y = x, y
        self.has_shield = False
        self.shield_timer = 0
        self.speed_boost = False
        self.speed_timer = 0
        self.double_jump = False
        self.has_dj = False
        self.coin_magnet = False
        self.magnet_timer = 0
        self.coyote = 0
        self.jump_buffer = 0
        self.trail_timer = 0
        # Dash
        self.can_dash = True
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_dir = 1
        self.is_dashing = False
        self.dash_trail = []
        # Wall slide / wall jump
        self.wall_sliding = False
        self.wall_side = 0
        self.wall_slide_timer = 0
        # Combo
        self.combo = 0
        self.combo_timer = 0
        self.kill_count = 0
        # Health regen
        self.regen_timer = 0

    def spawn(self, x, y):
        self.rect.topleft = (x, y)
        self.vel_x = self.vel_y = 0
        self.alive = True
        self.inv_timer = 90
        self.hp = self.max_hp
        self.has_shield = False
        self.shield_timer = 0
        self.speed_boost = False
        self.speed_timer = 0
        self.has_dj = False
        self.coin_magnet = False
        self.magnet_timer = 0
        self.is_dashing = False
        self.dash_cooldown = 0
        self.can_dash = True
        self.wall_sliding = False
        self.combo = 0
        self.combo_timer = 0

    def take_damage(self, amount=1):
        if self.inv_timer > 0:
            return False
        if self.has_shield:
            self.has_shield = False
            self.shield_timer = 0
            self.inv_timer = 60
            SND_HURT.play()
            particles.emit(self.rect.centerx, self.rect.centery, 15, CYAN, 4, 25, 3, 0.05, [CYAN, WHITE, BLUE])
            return True
        self.hp -= amount
        SND_HURT.play()
        particles.emit(self.rect.centerx, self.rect.centery, 10, RED, 3, 20, 2, 0.1, [RED, ORANGE])
        if self.hp <= 0:
            self.die()
        else:
            self.inv_timer = 60
            # Knockback
            self.vel_y = -6
            self.vel_x = 12 if self.facing_right else -12
        return True

    def die(self):
        self.lives -= 1
        SND_DEATH.play()
        particles.emit(self.rect.centerx, self.rect.centery, 35, RED, 7, 45, 4, 0.05, [RED, ORANGE, YELLOW, WHITE])
        save_data["deaths"] = save_data.get("deaths", 0) + 1
        write_save(save_data)
        if self.lives <= 0:
            self.alive = False
        else:
            self.spawn(self.spawn_x, self.spawn_y)

    def update(self, platforms, moving_plats, hazards, enemies):
        keys = pygame.key.get_pressed()
        spd = self.speed * (1.4 if self.speed_boost else 1.0)

        # ── Dash input ──
        if keys[pygame.K_LSHIFT] or keys[pygame.K_z]:
            if self.can_dash and self.dash_cooldown <= 0 and not self.is_dashing:
                self.is_dashing = True
                self.dash_timer = 8
                self.dash_cooldown = 40
                self.can_dash = False
                self.vel_y = 0
                self.dash_dir = 1 if self.facing_right else -1
                self.vel_x = self.dash_dir * 18
                SND_DASH.play()
                for _ in range(12):
                    particles.emit(self.rect.centerx, self.rect.centery, 1, CYAN, 2, 15, 2, 0, [CYAN, WHITE], rot=True)

        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
            # Dash trail
            self.dash_trail.append((self.rect.copy(), 10))
            particles.trail(self.rect.centerx, self.rect.centery, CYAN, 3)
        else:
            self.vel_x = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -spd
                self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = spd
                self.facing_right = True

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.dash_cooldown <= 0 and self.on_ground:
            self.can_dash = True

        # Coyote
        if self.on_ground:
            self.coyote = 7
            self.has_dj = False
            self.wall_slide_timer = 0
        else:
            self.coyote = max(0, self.coyote - 1)

        jump_pressed = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        if jump_pressed:
            self.jump_buffer = 8
        else:
            self.jump_buffer = max(0, self.jump_buffer - 1)

        jumped = False
        if self.jump_buffer > 0:
            if self.coyote > 0:
                self.vel_y = self.jump_power
                self.on_ground = False
                self.jumping = True
                self.coyote = 0
                self.jump_buffer = 0
                self.squash, self.stretch = 0.7, 1.3
                SND_JUMP.play()
                particles.emit(self.rect.centerx, self.rect.bottom, 6, WHITE, 2, 15, 2, 0.15, [WHITE, (200, 200, 255)])
                jumped = True
            elif self.wall_sliding:
                self.vel_y = self.jump_power * 0.95
                self.vel_x = -self.wall_side * 10
                self.facing_right = self.wall_side < 0
                self.on_ground = False
                self.jump_buffer = 0
                self.squash, self.stretch = 0.7, 1.3
                SND_WALLJUMP.play()
                particles.emit(self.rect.centerx, self.rect.centery, 8, WHITE, 3, 18, 2, 0.1, [WHITE, CYAN])
                jumped = True
            elif self.double_jump and not self.has_dj and not self.on_ground:
                self.vel_y = self.jump_power * 0.88
                self.has_dj = True
                self.jump_buffer = 0
                self.squash, self.stretch = 0.7, 1.3
                SND_JUMP.play()
                particles.emit(self.rect.centerx, self.rect.bottom, 8, PURPLE, 3, 20, 2, 0.1, [PURPLE, WHITE])
                jumped = True

        if not jump_pressed and self.vel_y < -4 and not jumped:
            self.vel_y = -4

        if not self.is_dashing:
            self.vel_y += GRAVITY
        if self.vel_y > 14:
            self.vel_y = 14

        # Move X
        self.rect.x += int(self.vel_x)
        self._collide_h(platforms, moving_plats)

        # Move Y
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        self.wall_sliding = False
        self._collide_v(platforms, moving_plats)

        # Wall sliding
        if not self.on_ground and not self.is_dashing:
            wall_check = pygame.Rect(self.rect.x + (3 if self.vel_x > 0 else -3), self.rect.y, self.rect.w, self.rect.h)
            for p in platforms:
                if wall_check.colliderect(p.rect):
                    if (self.vel_x > 0 and self.rect.right <= p.rect.right) or \
                       (self.vel_x < 0 and self.rect.left >= p.rect.left):
                        self.wall_sliding = True
                        self.wall_side = 1 if self.vel_x > 0 else -1
                        self.vel_y = min(self.vel_y, 2.5)
                        break

        # Hazards
        for h in hazards:
            if self.rect.colliderect(h.rect):
                if hasattr(h, 'hazard_type'):
                    if h.hazard_type == "spike":
                        self.take_damage()
                        self.vel_y = -8
                    elif h.hazard_type == "lava":
                        self.hp = 0
                        self.die()
                elif hasattr(h, 'hurt') and h.hurt:
                    self.hp = 0
                    self.die()

        # Magnet
        if self.coin_magnet and self.magnet_timer > 0:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.coin_magnet = False

        # Regen
        if self.hp < self.max_hp:
            self.regen_timer += 1
            if self.regen_timer >= 300:
                self.hp = min(self.max_hp, self.hp + 1)
                self.regen_timer = 0
        else:
            self.regen_timer = 0

        if self.inv_timer > 0:
            self.inv_timer -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.has_shield = False
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed_boost = False

        if self.rect.top > SH + 300:
            self.hp = 0
            self.die()

        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        # Dash trail decay
        new_trail = []
        for r, t in self.dash_trail:
            t -= 1
            if t > 0:
                new_trail.append((r, t))
        self.dash_trail = new_trail

        if self.vel_x != 0 and self.on_ground and not self.is_dashing:
            self.trail_timer += 1
            if self.trail_timer % 3 == 0:
                particles.trail(self.rect.centerx, self.rect.bottom, (100, 150, 255))
        else:
            self.trail_timer = 0

        self.squash += (1.0 - self.squash) * 0.15
        self.stretch += (1.0 - self.stretch) * 0.15
        if self.vel_y > 2 and not self.on_ground:
            self.squash = 1.1
            self.stretch = 0.9

        self.draw_character()

    def _collide_h(self, platforms, moving_plats):
        all_plats = list(platforms) + list(moving_plats)
        for p in all_plats:
            if self.rect.colliderect(p.rect):
                if hasattr(p, 'breakable') and p.breakable:
                    p.hit()
                    continue
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right

    def _collide_v(self, platforms, moving_plats):
        all_plats = list(platforms) + list(moving_plats)
        for p in all_plats:
            if self.rect.colliderect(p.rect):
                if hasattr(p, 'breakable') and p.breakable:
                    p.hit()
                    continue
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jumping = False
                    if hasattr(p, 'bouncy') and p.bouncy:
                        self.vel_y = -18
                        SND_SPRING.play()
                        particles.emit(self.rect.centerx, self.rect.bottom, 10, YELLOW, 4, 20, 3, 0.1, [YELLOW, ORANGE])
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

    def draw_character(self):
        self.image.fill((0, 0, 0, 0))
        if self.inv_timer > 0 and (self.inv_timer // 4) % 2 == 0:
            return
        s = self.image
        cx = self.w // 2
        sw, sh = self.squash, self.stretch

        # Dashing visual
        if self.is_dashing:
            trail_color = CYAN
            for r, t in self.dash_trail:
                a = int(150 * (t / 10))
                ts = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                pygame.draw.rect(ts, (*trail_color, a), (0, 0, self.w, self.h), border_radius=4)
                screen_rect = pygame.Rect(r.x, r.y, self.w, self.h)
                screen.blit(ts, (screen_rect.x, screen_rect.y))
            # Cyan outline while dashing
            pygame.draw.rect(s, CYAN, (0, 0, self.w, self.h), 2, border_radius=4)

        # Body
        bw, bh = int(18 * sw), int(16 * sh)
        bx = cx - bw // 2
        by = 18
        bc = (50, 130, 220) if not self.speed_boost else (220, 180, 50)
        if self.coin_magnet:
            bc = (100, 200, 100)
        pygame.draw.rect(s, bc, (bx, by, bw, bh), border_radius=4)

        # Belt
        pygame.draw.rect(s, (40, 40, 40), (bx, by + bh - 4, bw, 4), border_radius=1)
        pygame.draw.rect(s, YELLOW, (bx + bw // 2 - 3, by + bh - 5, 6, 6), border_radius=2)

        # Arms
        arm_swing = math.sin(pygame.time.get_ticks() * 0.01) * 5 if abs(self.vel_x) > 0 and self.on_ground else 0
        pygame.draw.line(s, bc, (bx + 2, by + 4), (bx - 5, by + 12 + arm_swing), 3)
        pygame.draw.line(s, bc, (bx + bw - 2, by + 4), (bx + bw + 5, by + 12 - arm_swing), 3)
        # Hands
        pygame.draw.circle(s, (255, 210, 170), (int(bx - 5), int(by + 12 + arm_swing)), 3)
        pygame.draw.circle(s, (255, 210, 170), (int(bx + bw + 5), int(by + 12 - arm_swing)), 3)

        # Head
        hr = int(9 * sw)
        hy = 10
        pygame.draw.circle(s, (255, 210, 170), (cx, hy), hr)

        # Eyes
        eo = 3 if self.facing_right else -3
        # Determine eye expression
        if self.is_dashing:
            # Determined squint
            pygame.draw.line(s, BLACK, (cx + eo - 4, hy - 2), (cx + eo, hy), 2)
            pygame.draw.line(s, BLACK, (cx + eo + 2, hy), (cx + eo + 6, hy - 2), 2)
        elif self.vel_y < -2:
            # Excited open eyes
            pygame.draw.circle(s, WHITE, (cx + eo - 2, hy - 1), 4)
            pygame.draw.circle(s, WHITE, (cx + eo + 4, hy - 1), 4)
            pygame.draw.circle(s, BLACK, (cx + eo - 1, hy - 1), 2)
            pygame.draw.circle(s, BLACK, (cx + eo + 5, hy - 1), 2)
        elif self.hp <= 2:
            # Worried
            pygame.draw.circle(s, WHITE, (cx + eo - 2, hy - 1), 3)
            pygame.draw.circle(s, WHITE, (cx + eo + 4, hy - 1), 3)
            pygame.draw.circle(s, BLACK, (cx + eo - 1, hy), 2)
            pygame.draw.circle(s, BLACK, (cx + eo + 5, hy), 2)
            pygame.draw.line(s, BLACK, (cx + eo - 1, hy - 4), (cx + eo + 1, hy - 3), 1)
            pygame.draw.line(s, BLACK, (cx + eo + 3, hy - 3), (cx + eo + 5, hy - 4), 1)
        else:
            # Normal
            pygame.draw.circle(s, WHITE, (cx + eo - 2, hy - 1), 3)
            pygame.draw.circle(s, WHITE, (cx + eo + 4, hy - 1), 3)
            po = 1 if self.facing_right else -1
            pygame.draw.circle(s, BLACK, (cx + eo - 1 + po, hy - 1), 1)
            pygame.draw.circle(s, BLACK, (cx + eo + 5 + po, hy - 1), 1)

        # Hat
        hh = int(5 * sh)
        pygame.draw.rect(s, RED, (cx - 9, hy - hr - hh + 2, 18, hh), border_radius=2)
        pygame.draw.rect(s, (180, 30, 30), (cx - 12, hy - hr + 1, 24, 4), border_radius=2)
        # Star on hat
        pygame.draw.circle(s, YELLOW, (cx + 6, hy - hr - hh + 4), 2)

        # Legs
        lw, lh = 5, 10
        if not self.on_ground and not self.wall_sliding:
            if self.vel_y < 0:
                pygame.draw.rect(s, (40, 50, 130), (cx - 6, by + bh - 2, lw, lh - 4), border_radius=2)
                pygame.draw.rect(s, (40, 50, 130), (cx + 1, by + bh + 2, lw, lh - 4), border_radius=2)
            else:
                pygame.draw.rect(s, (40, 50, 130), (cx - 7, by + bh - 4, lw, lh), border_radius=2)
                pygame.draw.rect(s, (40, 50, 130), (cx + 2, by + bh - 2, lw, lh + 2), border_radius=2)
        elif self.wall_sliding:
            # Legs tucked against wall
            wo = self.wall_side * 2
            pygame.draw.rect(s, (40, 50, 130), (cx - 6 + wo, by + bh, lw, lh - 3), border_radius=2)
            pygame.draw.rect(s, (40, 50, 130), (cx + 1 + wo, by + bh + 3, lw, lh - 6), border_radius=2)
        else:
            self.walk_frame = self.walk_frame if abs(self.vel_x) > 0 else 0
            if abs(self.vel_x) > 0:
                self.walk_timer += 1
                if self.walk_timer > 5:
                    self.walk_timer = 0
                    self.walk_frame = (self.walk_frame + 1) % 4
            offsets = [(0, 0), (2, -2), (0, 0), (-2, 2)]
            lo = offsets[self.walk_frame]
            pygame.draw.rect(s, (40, 50, 130), (cx - 6 + lo[0], by + bh - 2 + lo[1], lw, lh), border_radius=2)
            pygame.draw.rect(s, (40, 50, 130), (cx + 1 - lo[0], by + bh - 2 - lo[1], lw, lh), border_radius=2)

        # Shield glow
        if self.has_shield:
            shield_surf = pygame.Surface((self.w + 12, self.h + 12), pygame.SRCALPHA)
            a = int(80 + 40 * math.sin(pygame.time.get_ticks() * 0.01))
            pygame.draw.ellipse(shield_surf, (*CYAN, a), (0, 0, self.w + 12, self.h + 12), 2)
            s.blit(shield_surf, (-6, -6))

        # Speed glow
        if self.speed_boost:
            sp = pygame.Surface((self.w + 6, self.h + 6), pygame.SRCALPHA)
            a = int(60 + 30 * math.sin(pygame.time.get_ticks() * 0.015))
            pygame.draw.ellipse(sp, (*ORANGE, a), (0, 0, self.w + 6, self.h + 6), 2)
            s.blit(sp, (-3, -3))

        # Magnet glow
        if self.coin_magnet:
            mg = pygame.Surface((self.w + 20, self.h + 20), pygame.SRCALPHA)
            r = 18 + int(4 * math.sin(pygame.time.get_ticks() * 0.008))
            a = int(30 + 20 * math.sin(pygame.time.get_ticks() * 0.01))
            pygame.draw.circle(mg, (*GREEN, a), (self.w // 2 + 10, self.h // 2 + 10), r, 1)
            s.blit(mg, (-10, -10))


# ── Platforms ────────────────────────────────────────────────
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, ptype="grass"):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.ptype = ptype
        self.breakable = False
        self.bouncy = False
        self.hp = 0
        self.draw_platform()

    def draw_platform(self):
        w, h = self.rect.width, self.rect.height
        if self.ptype == "grass":
            pygame.draw.rect(self.image, DARK_GREEN, (0, 0, w, 6))
            pygame.draw.rect(self.image, GREEN, (0, 6, w, h - 6))
            for i in range(0, w, 16):
                pygame.draw.rect(self.image, DARK_GREEN, (i, 1, 3, 5))
                if i % 32 == 0:
                    pygame.draw.line(self.image, (50, 180, 50), (i + 2, 4), (i + 2, -2), 2)
        elif self.ptype == "dirt":
            pygame.draw.rect(self.image, BROWN, (0, 0, w, h))
            pygame.draw.rect(self.image, DARK_BROWN, (0, 0, w, 4))
            for i in range(0, w, 12):
                for j in range(4, h, 8):
                    pygame.draw.rect(self.image, (120, 75, 35), (i + (j % 16), j, 6, 4))
        elif self.ptype == "stone":
            pygame.draw.rect(self.image, (150, 150, 150), (0, 0, w, h))
            for i in range(0, w, 24):
                for j in range(0, h, 12):
                    off = 6 if (j // 12) % 2 else 0
                    pygame.draw.rect(self.image, (120, 120, 120), (i + off, j, 22, 10), 1)
            pygame.draw.rect(self.image, (130, 130, 130), (0, 0, w, h), 2)
        elif self.ptype == "ice":
            pygame.draw.rect(self.image, (180, 220, 255), (0, 0, w, h))
            pygame.draw.rect(self.image, (220, 240, 255), (2, 2, w - 4, h // 2 - 2))
            for i in range(0, w, 20):
                pygame.draw.line(self.image, (240, 250, 255), (i, 2), (i + 10, h - 2), 1)
        elif self.ptype == "wood":
            pygame.draw.rect(self.image, (160, 110, 60), (0, 0, w, h))
            for i in range(0, h, 8):
                pygame.draw.line(self.image, (140, 95, 50), (0, i), (w, i), 1)
            pygame.draw.rect(self.image, (140, 95, 50), (0, 0, w, h), 2)
        elif self.ptype == "bouncy":
            self.bouncy = True
            pygame.draw.rect(self.image, (220, 50, 80), (0, 0, w, h), border_radius=4)
            pygame.draw.rect(self.image, (255, 100, 130), (4, 2, w - 8, h // 2), border_radius=3)
            for i in range(w // 8):
                pygame.draw.line(self.image, WHITE, (4 + i * 8, h - 4), (8 + i * 8, 2), 1)
        elif self.ptype == "breakable":
            self.breakable = True
            self.hp = 3
            pygame.draw.rect(self.image, (180, 140, 80), (0, 0, w, h))
            pygame.draw.rect(self.image, (150, 110, 60), (0, 0, w, h), 2)
            for i in range(1, 3):
                pygame.draw.line(self.image, (120, 85, 40), (w * i // 3, 0), (w * i // 3, h), 1)

    def hit(self):
        if self.breakable:
            self.hp -= 1
            SND_STOMP.play()
            particles.emit(self.rect.centerx, self.rect.centery, 8, (180, 140, 80), 3, 20, 2)
            if self.hp <= 0:
                particles.emit(self.rect.centerx, self.rect.centery, 15, (180, 140, 80), 4, 30, 3, 0.15,
                               [(180, 140, 80), (140, 100, 60)])
                self.kill()


class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, move_x=0, move_y=0, speed=2, ptype="stone"):
        super().__init__(x, y, w, h, ptype)
        self.sx, self.sy = x, y
        self.move_x, self.move_y = move_x, move_y
        self.speed = speed
        self.vel_x, self.vel_y = 0, 0

    def update(self):
        ox, oy = self.rect.x, self.rect.y
        t = pygame.time.get_ticks() * 0.001 * self.speed
        if self.move_x:
            self.rect.x = int(self.sx + math.sin(t) * self.move_x)
        if self.move_y:
            self.rect.y = int(self.sy + math.sin(t) * self.move_y)
        self.vel_x = self.rect.x - ox
        self.vel_y = self.rect.y - oy


# ── Lava ─────────────────────────────────────────────────────
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h=32):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h))
        self.hazard_type = "lava"
        self.hurt = True
        self.timer = random.uniform(0, 10)

    def update(self):
        self.timer += 0.05
        w, h = self.rect.width, self.rect.height
        self.image.fill(LAVA_RED)
        for i in range(0, w, 12):
            wave_h = int(6 * math.sin(self.timer + i * 0.1))
            pygame.draw.ellipse(self.image, LAVA_ORANGE, (i - 4, wave_h, 20, h // 2))
            wave_h2 = int(4 * math.sin(self.timer * 1.5 + i * 0.15))
            pygame.draw.ellipse(self.image, LAVA_YELLOW, (i, wave_h2 + 4, 14, h // 3))
        # Glow on top
        glow = pygame.Surface((w, 8), pygame.SRCALPHA)
        a = int(80 + 40 * math.sin(self.timer * 2))
        pygame.draw.rect(glow, (*LAVA_ORANGE, a), (0, 0, w, 8))
        self.image.blit(glow, (0, 0))

    def draw(self, surf, cam):
        surf.blit(self.image, cam.apply(self.rect))


# ── Coin ─────────────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, ctype="gold"):
        super().__init__()
        self.ctype = ctype
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.base_y = y
        self.timer = random.uniform(0, 6.28)
        self.draw_coin()

    def draw_coin(self):
        colors = {"gold": (YELLOW, (200, 170, 0), "$"), "star": (CYAN, (0, 150, 150), "*")}
        main, dark, sym = colors.get(self.ctype, colors["gold"])
        self.image.fill((0, 0, 0, 0))
        if self.ctype == "star":
            # Draw star shape
            pts = []
            for i in range(5):
                a = math.radians(-90 + i * 72)
                a2 = math.radians(-90 + i * 72 + 36)
                pts.append((8 + 8 * math.cos(a), 8 + 8 * math.sin(a)))
                pts.append((8 + 4 * math.cos(a2), 8 + 4 * math.sin(a2)))
            pygame.draw.polygon(self.image, main, pts)
            pygame.draw.polygon(self.image, dark, pts, 1)
        else:
            pygame.draw.circle(self.image, main, (8, 8), 8)
            pygame.draw.circle(self.image, dark, (8, 8), 8, 2)
            pygame.draw.circle(self.image, (255, 240, 150), (5, 5), 3)

    def update(self, player_rect=None):
        self.timer += 0.06
        self.rect.centery = int(self.base_y + 4 * math.sin(self.timer))
        # Magnet pull
        if player_rect and hasattr(self, '_magnet') and self._magnet:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 150 and dist > 5:
                speed = 6 * (1 - dist / 150)
                self.rect.x += int(dx / dist * speed)
                self.rect.y += int(dy / dist * speed)
                self.base_y = self.rect.centery


# ── Star (collectible secondary currency) ────────────────────
class StarCollectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.base_y = y
        self.timer = random.uniform(0, 6.28)
        self.draw_star()

    def draw_star(self):
        self.image.fill((0, 0, 0, 0))
        pts = []
        for i in range(5):
            a = math.radians(-90 + i * 72)
            a2 = math.radians(-90 + i * 72 + 36)
            pts.append((10 + 9 * math.cos(a), 10 + 9 * math.sin(a)))
            pts.append((10 + 4 * math.cos(a2), 10 + 4 * math.sin(a2)))
        glow = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(glow, (*YELLOW, 60), [(10, 10)] * 10)  # placeholder
        self.image.blit(glow, (0, 0))
        pygame.draw.polygon(self.image, YELLOW, pts)
        pygame.draw.polygon(self.image, (200, 170, 0), pts, 1)
        # Inner bright
        pts2 = []
        for i in range(5):
            a = math.radians(-90 + i * 72)
            a2 = math.radians(-90 + i * 72 + 36)
            pts2.append((10 + 5 * math.cos(a), 10 + 5 * math.sin(a)))
            pts2.append((10 + 2.5 * math.cos(a2), 10 + 2.5 * math.sin(a2)))
        pygame.draw.polygon(self.image, (255, 240, 180), pts2)

    def update(self):
        self.timer += 0.04
        self.rect.centery = int(self.base_y + 5 * math.sin(self.timer))
        # Sparkle
        if random.random() < 0.05:
            particles.emit(self.rect.centerx, self.rect.centery, 1, YELLOW, 1, 15, 1, -0.05, [YELLOW, WHITE])


# ── Enemy ────────────────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, pl, pr, etype="walker", hp=1):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pl, self.pr = pl, pr
        self.vel_x = 2
        self.etype = etype
        self.hp = hp
        self.max_hp = hp
        self.timer = 0
        self.alive = True
        self.hurt_flash = 0
        self.draw_enemy()

    def take_hit(self):
        self.hp -= 1
        self.hurt_flash = 8
        SND_BOSS_HIT.play()
        if self.hp <= 0:
            self.alive = False
            particles.emit(self.rect.centerx, self.rect.centery, 20, RED, 5, 30, 3, 0.1, [RED, ORANGE, YELLOW])
            return True
        return False

    def draw_enemy(self):
        self.image.fill((0, 0, 0, 0))
        s = self.image
        t = self.timer
        if self.hurt_flash > 0:
            self.hurt_flash -= 1
            pygame.draw.rect(s, WHITE, (0, 0, 32, 32))
            return

        if self.etype == "walker":
            b = int(2 * abs(math.sin(t * 0.1)))
            pygame.draw.ellipse(s, (180, 50, 50), (2, 8 - b, 28, 20 + b))
            pygame.draw.ellipse(s, (140, 30, 30), (2, 8 - b, 28, 20 + b), 2)
            ey = 14 - b
            pygame.draw.circle(s, WHITE, (10, ey), 5)
            pygame.draw.circle(s, WHITE, (22, ey), 5)
            pygame.draw.circle(s, BLACK, (12, ey), 3)
            pygame.draw.circle(s, BLACK, (20, ey), 3)
            pygame.draw.line(s, BLACK, (6, ey - 6), (14, ey - 4), 2)
            pygame.draw.line(s, BLACK, (26, ey - 6), (18, ey - 4), 2)
            for sx in [6, 14, 22]:
                pygame.draw.polygon(s, (200, 80, 80), [(sx - 3, 10 - b), (sx, 2 - b), (sx + 3, 10 - b)])
        elif self.etype == "flyer":
            wo = int(4 * math.sin(t * 0.2))
            pygame.draw.ellipse(s, (140, 50, 160), (4, 10, 24, 16))
            pygame.draw.polygon(s, (160, 70, 180), [(0, 10 + wo), (8, 14), (0, 18 - wo)])
            pygame.draw.polygon(s, (160, 70, 180), [(32, 10 + wo), (24, 14), (32, 18 - wo)])
            pygame.draw.circle(s, WHITE, (12, 16), 4)
            pygame.draw.circle(s, WHITE, (22, 16), 4)
            pygame.draw.circle(s, RED, (13, 16), 2)
            pygame.draw.circle(s, RED, (21, 16), 2)
        elif self.etype == "chaser":
            pygame.draw.ellipse(s, (200, 100, 0), (2, 6, 28, 22))
            pygame.draw.ellipse(s, (160, 80, 0), (2, 6, 28, 22), 2)
            pygame.draw.circle(s, (255, 255, 100), (10, 14), 5)
            pygame.draw.circle(s, (255, 255, 100), (22, 14), 5)
            pygame.draw.circle(s, RED, (10, 14), 3)
            pygame.draw.circle(s, RED, (22, 14), 3)
            for sx in [8, 16, 24]:
                pygame.draw.polygon(s, (220, 120, 20), [(sx - 4, 8), (sx, 0), (sx + 4, 8)])
        elif self.etype == "shooter":
            pygame.draw.ellipse(s, (80, 80, 180), (2, 8, 28, 20))
            pygame.draw.ellipse(s, (60, 60, 140), (2, 8, 28, 20), 2)
            # Gun barrel
            bx = 28 if self.vel_x > 0 else 0
            pygame.draw.rect(s, (60, 60, 60), (bx, 16, 8, 4))
            # Eye
            pygame.draw.circle(s, WHITE, (16, 16), 5)
            pygame.draw.circle(s, RED, (16, 16), 3)

        # HP bar for multi-hp enemies
        if self.max_hp > 1:
            bw = 28
            pygame.draw.rect(s, (40, 40, 40), (2, -6, bw, 4))
            fill = int(bw * self.hp / self.max_hp)
            c = GREEN if self.hp > self.max_hp // 2 else YELLOW if self.hp > 1 else RED
            pygame.draw.rect(s, c, (2, -6, fill, 4))

    def update(self, player_rect=None, platforms=None):
        self.timer += 1
        if self.etype == "chaser" and player_rect and self.alive:
            dx = player_rect.centerx - self.rect.centerx
            if abs(dx) < 300:
                self.vel_x = 3 if dx > 0 else -3
            self.rect.x += self.vel_x
        elif self.etype == "shooter" and self.alive:
            self.rect.x += self.vel_x
            if self.timer % 120 == 0 and player_rect:
                # Shoot
                dx = player_rect.centerx - self.rect.centerx
                self.vel_x = 2 if dx > 0 else -2
        else:
            if self.alive:
                self.rect.x += self.vel_x

        if self.rect.left <= self.pl or self.rect.right >= self.pr:
            self.vel_x *= -1

        if self.etype == "flyer":
            self.rect.y += int(math.sin(self.timer * 0.05) * 1.5)

        self.draw_enemy()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((8, 4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, 8, 4), border_radius=2)
        pygame.draw.rect(self.image, ORANGE, (1, 1, 6, 2))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = direction * 5
        self.life = 180

    def update(self):
        self.rect.x += self.vel_x
        self.life -= 1
        if self.life <= 0 or self.rect.right < 0 or self.rect.left > SW * 3:
            self.kill()
        particles.trail(self.rect.centerx, self.rect.centery, ORANGE, 1)


# ── Boss ─────────────────────────────────────────────────────
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, level_num):
        super().__init__()
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = 20 if level_num < 3 else 30
        self.max_hp = self.hp
        self.level_num = level_num
        self.timer = 0
        self.phase = 0
        self.vel_x = 0
        self.vel_y = 0
        self.alive = True
        self.hurt_flash = 0
        self.attack_timer = 90
        self.projectiles = pygame.sprite.Group()
        self.pl = x - 200
        self.pr = x + 200
        self.spawn_x, self.spawn_y = x, y
        self.defeated = False
        self.defeat_timer = 0

    def take_hit(self):
        if self.hurt_flash > 0:
            return False
        self.hp -= 1
        self.hurt_flash = 12
        SND_BOSS_HIT.play()
        particles.emit(self.rect.centerx, self.rect.centery, 10, YELLOW, 4, 20, 3, 0.1, [YELLOW, WHITE, RED])
        if self.hp <= 0:
            self.defeated = True
            SND_BOSS_DIE.play()
            for _ in range(80):
                particles.emit(self.rect.centerx, self.rect.centery, 1, random.choice([RED, ORANGE, YELLOW, WHITE]),
                               8, 60, 4, 0.05, [RED, ORANGE, YELLOW])
            return True
        return False

    def update(self, player_rect):
        self.timer += 1
        if self.hurt_flash > 0:
            self.hurt_flash -= 1

        if self.defeated:
            self.defeat_timer += 1
            self.vel_y += 0.3
            self.rect.y += int(self.vel_y)
            self.image.set_alpha(max(0, 255 - self.defeat_timer * 3))
            return

        # Phase changes
        if self.hp < self.max_hp * 0.5:
            self.phase = 1

        # Movement
        speed = 2 + self.phase
        if player_rect:
            dx = player_rect.centerx - self.rect.centerx
            self.vel_x = speed if dx > 0 else -speed

        self.rect.x += int(self.vel_x)
        if self.rect.left <= self.pl or self.rect.right >= self.pr:
            self.vel_x *= -1

        # Bob
        self.rect.y = int(self.spawn_y + 10 * math.sin(self.timer * 0.03))

        # Attack
        self.attack_timer -= 1
        if self.attack_timer <= 0 and player_rect:
            self.attack_timer = max(30, 80 - self.phase * 20)
            # Fire projectile
            direction = 1 if player_rect.centerx > self.rect.centerx else -1
            b = EnemyBullet(self.rect.centerx, self.rect.centery, direction)
            self.projectiles.add(b)
            if self.phase >= 1:
                # Extra shot
                b2 = EnemyBullet(self.rect.centerx, self.rect.centery - 10, direction)
                self.projectiles.add(b2)

        self.projectiles.update()

        # Draw boss
        self.draw_boss()

    def draw_boss(self):
        self.image.fill((0, 0, 0, 0))
        s = self.image
        t = self.timer
        flash = self.hurt_flash > 0

        # Body - large armored creature
        body_color = (180, 40, 40) if not flash else WHITE
        if self.level_num == 1:
            # Forest boss - big tree monster
            pygame.draw.ellipse(s, body_color, (4, 12, 56, 48))
            pygame.draw.ellipse(s, (140, 30, 30), (4, 12, 56, 48), 3)
            # Branches
            for bx in [0, 52]:
                pygame.draw.line(s, (100, 70, 30), (bx, 25), (bx + (-10 if bx == 0 else 10), 10), 4)
                pygame.draw.circle(s, GREEN, (bx + (-15 if bx == 0 else 15), 5), 8)
            # Face
            pygame.draw.circle(s, WHITE, (22, 28), 8)
            pygame.draw.circle(s, WHITE, (42, 28), 8)
            pygame.draw.circle(s, (200, 0, 0), (22, 28), 5)
            pygame.draw.circle(s, (200, 0, 0), (42, 28), 5)
            pygame.draw.circle(s, BLACK, (22, 28), 2)
            pygame.draw.circle(s, BLACK, (42, 28), 2)
            # Mouth
            mouth_wave = int(3 * math.sin(t * 0.15))
            pygame.draw.line(s, BLACK, (18, 42 + mouth_wave), (46, 42 - mouth_wave), 3)
            for i in range(18, 48, 6):
                pygame.draw.polygon(s, WHITE, [(i, 42), (i + 3, 48), (i + 6, 42)])
        elif self.level_num == 2:
            # Cave boss - crystal golem
            pygame.draw.ellipse(s, (100, 100, 140), (4, 12, 56, 48))
            pygame.draw.ellipse(s, (80, 80, 120), (4, 12, 56, 48), 3)
            # Crystals on head
            for cx, cy, ch in [(15, 5, 12), (32, 0, 16), (49, 8, 10)]:
                pygame.draw.polygon(s, PURPLE, [(cx - 4, cy + ch), (cx, cy), (cx + 4, cy + ch)])
                pygame.draw.polygon(s, (200, 150, 255), [(cx - 2, cy + ch - 2), (cx, cy + 2), (cx + 2, cy + ch - 2)])
            # Eyes
            pygame.draw.circle(s, (200, 200, 255), (22, 28), 7)
            pygame.draw.circle(s, (200, 200, 255), (42, 28), 7)
            pygame.draw.circle(s, PURPLE, (22, 28), 4)
            pygame.draw.circle(s, PURPLE, (42, 28), 4)
            # Glow
            glow = pygame.Surface((64, 64), pygame.SRCALPHA)
            ga = int(30 + 20 * math.sin(t * 0.05))
            pygame.draw.circle(glow, (*PURPLE, ga), (32, 32), 30)
            s.blit(glow, (0, 0))
        else:
            # Final boss - dark knight
            pygame.draw.rect(s, (40, 40, 60), (8, 10, 48, 50), border_radius=8)
            pygame.draw.rect(s, (60, 60, 80), (8, 10, 48, 50), 3, border_radius=8)
            # Helmet
            pygame.draw.rect(s, (50, 50, 70), (12, 2, 40, 20), border_radius=6)
            pygame.draw.rect(s, (80, 80, 100), (12, 2, 40, 20), 2, border_radius=6)
            # Eyes
            eye_glow = int(180 + 75 * math.sin(t * 0.1))
            pygame.draw.circle(s, (eye_glow, 0, 0), (24, 12), 5)
            pygame.draw.circle(s, (eye_glow, 0, 0), (40, 12), 5)
            pygame.draw.circle(s, WHITE, (24, 12), 2)
            pygame.draw.circle(s, WHITE, (40, 12), 2)
            # Sword
            sword_x = 56 if self.vel_x > 0 else 0
            pygame.draw.rect(s, (180, 180, 200), (sword_x, 20, 6, 30))
            pygame.draw.rect(s, (120, 100, 60), (sword_x - 2, 18, 10, 6))
            # Shield
            sh_x = 0 if self.vel_x > 0 else 50
            pygame.draw.ellipse(s, (100, 80, 40), (sh_x, 25, 14, 20))
            pygame.draw.ellipse(s, (120, 100, 60), (sh_x, 25, 14, 20), 2)
            # Dark aura
            aura = pygame.Surface((70, 70), pygame.SRCALPHA)
            aa = int(40 + 20 * math.sin(t * 0.08))
            pygame.draw.circle(aura, (80, 0, 80, aa), (35, 35), 35, 2)
            s.blit(aura, (-3, -3))


# ── Hazard (spikes) ─────────────────────────────────────────
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, w):
        super().__init__()
        self.image = pygame.Surface((w, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hazard_type = "spike"
        self.hurt = True
        for i in range(0, w, 14):
            pygame.draw.polygon(self.image, GRAY, [(i, 20), (i + 7, 0), (i + 14, 20)])
            pygame.draw.polygon(self.image, (170, 170, 170), [(i + 2, 18), (i + 7, 4), (i + 12, 18)])


class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GRAY, (0, 0, 5, 64))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.timer = 0

    def update(self):
        self.timer += 0.08
        wave = int(3 * math.sin(self.timer))
        self.image = self.base_image.copy()
        pts = [(5, 4 + wave), (5, 28 + wave), (36, 16 + wave // 2)]
        pygame.draw.polygon(self.image, GREEN, pts)
        pygame.draw.polygon(self.image, DARK_GREEN, pts, 1)


class Spring(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((24, 16), pygame.SRCALPHA)
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.compressed = 0
        self.draw_spring()

    def draw_spring(self):
        self.image.fill((0, 0, 0, 0))
        h = 16 - self.compressed * 4
        pygame.draw.rect(self.image, GRAY, (2, 16 - h, 20, h))
        pygame.draw.rect(self.image, (200, 200, 200), (0, 14 - self.compressed * 2, 24, 4), border_radius=2)
        for i in range(0, h, 4):
            pygame.draw.line(self.image, (100, 100, 100), (4, 16 - h + i), (20, 16 - h + i), 1)

    def compress(self):
        self.compressed = 4

    def update(self):
        if self.compressed > 0:
            self.compressed -= 1
            self.draw_spring()


class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 48), pygame.SRCALPHA)
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.activated = False
        self.timer = 0
        self.draw_checkpoint()

    def draw_checkpoint(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, GRAY, (6, 0, 4, 48))
        color = YELLOW if self.activated else (100, 100, 100)
        wave = int(2 * math.sin(self.timer * 0.1)) if self.activated else 0
        pygame.draw.polygon(self.image, color, [(10, 4 + wave), (10, 24 + wave), (2 + wave, 14 + wave)])
        if self.activated:
            glow = pygame.Surface((20, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*YELLOW, 40), (10, 14), 12)
            self.image.blit(glow, (-2, 0))

    def activate(self):
        if not self.activated:
            self.activated = True
            SND_CHECKPOINT.play()
            particles.emit(self.rect.centerx, self.rect.centery, 12, YELLOW, 3, 25, 3, 0.05, [YELLOW, WHITE])

    def update(self):
        self.timer += 1
        self.draw_checkpoint()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype="shield"):
        super().__init__()
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.ptype = ptype
        self.base_y = y
        self.timer = random.uniform(0, 6.28)
        self.draw_powerup()

    def draw_powerup(self):
        self.image.fill((0, 0, 0, 0))
        colors = {"shield": CYAN, "speed": ORANGE, "double_jump": PURPLE, "magnet": GREEN}
        color = colors.get(self.ptype, WHITE)
        pygame.draw.circle(self.image, color, (11, 11), 11)
        pygame.draw.circle(self.image, WHITE, (11, 11), 11, 2)
        symbols = {"shield": "S", "speed": ">>", "double_jump": "2J", "magnet": "M"}
        txt = small_font.render(symbols.get(self.ptype, "?"), True, BLACK)
        self.image.blit(txt, (11 - txt.get_width() // 2, 11 - txt.get_height() // 2))

    def update(self):
        self.timer += 0.05
        self.rect.centery = int(self.base_y + 4 * math.sin(self.timer))


# ── Level definitions ────────────────────────────────────────
LEVEL_W = 3200
LEVEL_H = 800
LEVEL_THEMES = {
    1: {"name": "Whispering Woods", "bg_colors": ((15, 35, 15), (25, 55, 25), (35, 75, 35))},
    2: {"name": "Crystal Caverns", "bg_colors": ((20, 15, 35), (35, 25, 55), (45, 35, 70))},
    3: {"name": "Dark Fortress", "bg_colors": ((35, 10, 10), (50, 15, 15), (65, 25, 25))},
}


def make_level(n):
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    flags = pygame.sprite.Group()
    springs = pygame.sprite.Group()
    moving_plats = pygame.sprite.Group()
    checkpoints = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    star_items = pygame.sprite.Group()
    lavas = pygame.sprite.Group()
    boss = None

    if n == 1:
        pw = [
            (0, 568, 500, 32, "grass"), (580, 568, 400, 32, "grass"), (1060, 568, 400, 32, "grass"),
            (1540, 568, 300, 32, "grass"), (1920, 568, 400, 32, "grass"), (2400, 568, 300, 32, "grass"),
            (280, 450, 100, 20, "grass"), (480, 370, 120, 20, "grass"), (680, 290, 100, 20, "grass"),
            (350, 210, 120, 20, "grass"), (600, 150, 100, 20, "grass"),
            (900, 380, 100, 20, "grass"), (1100, 310, 120, 20, "grass"),
            (1350, 250, 100, 20, "grass"), (1550, 380, 80, 20, "grass"),
            (1750, 310, 100, 20, "grass"), (1950, 230, 120, 20, "grass"),
            (2150, 380, 100, 20, "grass"), (2350, 280, 100, 20, "grass"),
            (2600, 450, 100, 20, "grass"), (2800, 380, 120, 20, "grass"),
            (380, 500, 80, 16, "bouncy"), (1200, 460, 80, 16, "bouncy"),
            (780, 500, 80, 20, "breakable"), (1680, 500, 80, 20, "breakable"),
            (2500, 500, 80, 16, "bouncy"),
        ]
        for x, y, w, h, t in pw:
            platforms.add(Platform(x, y, w, h, t))

        moving_plats.add(MovingPlatform(1000, 420, 100, 16, move_x=120, speed=1.5))
        moving_plats.add(MovingPlatform(1850, 380, 100, 16, move_y=80, speed=1.2))
        moving_plats.add(MovingPlatform(2550, 350, 100, 16, move_x=100, speed=1.0))

        for x, y in [(350, 540), (750, 265), (410, 185), (650, 125),
                      (1000, 355), (1160, 285), (1400, 225), (1800, 285),
                      (2010, 205), (2200, 355), (2400, 255),
                      (120, 540), (1600, 540), (2450, 540), (2900, 355),
                      (2700, 425)]:
            coins.add(Coin(x, y))

        enemies.add(Enemy(600, 536, 580, 980))
        enemies.add(Enemy(1100, 536, 1060, 1460))
        enemies.add(Enemy(1700, 536, 1540, 1840))
        enemies.add(Enemy(2500, 536, 2400, 2700))
        enemies.add(Enemy(910, 348, 900, 1000, "flyer"))
        enemies.add(Enemy(1550, 348, 1500, 1650, "flyer"))
        enemies.add(Enemy(2150, 348, 2100, 2250, "flyer"))
        enemies.add(Enemy(2810, 348, 2800, 2920, "shooter"))

        hazards.add(Spike(500, 578, 80))
        hazards.add(Spike(1200, 578, 200))
        hazards.add(Spike(2200, 578, 100))

        springs.add(Spring(280, 450))
        springs.add(Spring(1200, 460))
        springs.add(Spring(2500, 500))

        checkpoints.add(Checkpoint(1100, 568))
        checkpoints.add(Checkpoint(1950, 568))
        checkpoints.add(Checkpoint(2700, 568))

        powerups.add(PowerUp(1410, 220, "shield"))
        powerups.add(PowerUp(660, 120, "double_jump"))
        powerups.add(PowerUp(2160, 350, "magnet"))

        star_items.add(StarCollectible(360, 180))
        star_items.add(StarCollectible(2010, 175))
        star_items.add(StarCollectible(2860, 350))

        boss = Boss(2900, 500, 1)
        flags.add(Flag(3100, 568))

    elif n == 2:
        pw = [
            (0, 568, 300, 32, "stone"), (380, 568, 200, 32, "stone"),
            (660, 568, 300, 32, "stone"), (1040, 568, 200, 32, "stone"),
            (1320, 568, 300, 32, "stone"), (1700, 568, 200, 32, "stone"),
            (1980, 568, 300, 32, "stone"), (2360, 568, 300, 32, "stone"),
            (2740, 568, 200, 32, "stone"),
            (180, 460, 100, 20, "stone"), (380, 380, 100, 20, "stone"),
            (580, 310, 120, 20, "stone"), (780, 250, 80, 20, "stone"),
            (980, 380, 100, 20, "stone"), (1180, 310, 100, 20, "stone"),
            (1380, 240, 80, 20, "stone"), (1580, 380, 100, 20, "stone"),
            (1780, 310, 100, 20, "stone"), (1980, 230, 80, 20, "stone"),
            (2180, 380, 100, 20, "stone"), (2380, 300, 100, 20, "stone"),
            (2580, 230, 80, 20, "stone"), (2780, 400, 100, 20, "stone"),
            (250, 500, 60, 16, "bouncy"), (880, 500, 60, 16, "bouncy"),
            (1600, 500, 60, 16, "bouncy"), (2280, 500, 60, 16, "bouncy"),
            (580, 440, 80, 20, "breakable"), (1380, 380, 80, 20, "breakable"),
            (2180, 440, 80, 20, "breakable"),
        ]
        for x, y, w, h, t in pw:
            platforms.add(Platform(x, y, w, h, t))

        moving_plats.add(MovingPlatform(480, 320, 80, 16, move_x=100, speed=1.2))
        moving_plats.add(MovingPlatform(1100, 420, 80, 16, move_y=100, speed=1.0))
        moving_plats.add(MovingPlatform(1750, 300, 80, 16, move_x=80, speed=1.5))
        moving_plats.add(MovingPlatform(2500, 350, 80, 16, move_y=120, speed=0.8))
        moving_plats.add(MovingPlatform(2800, 300, 80, 16, move_x=60, speed=1.3))

        for x, y in [(150, 540), (480, 540), (810, 540), (1140, 540),
                      (230, 435), (430, 355), (640, 285), (1030, 355),
                      (1230, 285), (1420, 215), (1630, 355),
                      (1830, 285), (2020, 205), (2230, 355), (2430, 275),
                      (2630, 205), (2830, 375),
                      (1300, 540), (2000, 540), (2800, 540)]:
            coins.add(Coin(x, y))

        enemies.add(Enemy(400, 536, 380, 580))
        enemies.add(Enemy(750, 536, 660, 960))
        enemies.add(Enemy(1400, 536, 1320, 1620))
        enemies.add(Enemy(2000, 536, 1980, 2280))
        enemies.add(Enemy(2500, 536, 2360, 2660))
        enemies.add(Enemy(790, 218, 780, 860, "flyer"))
        enemies.add(Enemy(1390, 208, 1380, 1460, "flyer"))
        enemies.add(Enemy(1990, 198, 1980, 2060, "flyer"))
        enemies.add(Enemy(590, 278, 580, 700, "chaser"))
        enemies.add(Enemy(1790, 278, 1780, 1880, "chaser"))
        enemies.add(Enemy(2590, 198, 2580, 2660, "chaser"))
        enemies.add(Enemy(1050, 536, 1040, 1240, "shooter"))
        enemies.add(Enemy(2750, 536, 2740, 2940, "shooter"))

        hazards.add(Spike(300, 578, 80))
        hazards.add(Spike(860, 578, 180))
        hazards.add(Spike(1240, 578, 80))
        hazards.add(Spike(1900, 578, 80))
        hazards.add(Spike(2660, 578, 80))

        lavas.add(Lava(1520, 568, 180, 32))

        springs.add(Spring(180, 460))
        springs.add(Spring(880, 500))
        springs.add(Spring(1600, 500))
        springs.add(Spring(2280, 500))

        checkpoints.add(Checkpoint(1040, 568))
        checkpoints.add(Checkpoint(1700, 568))
        checkpoints.add(Checkpoint(2360, 568))

        powerups.add(PowerUp(790, 215, "speed"))
        powerups.add(PowerUp(2030, 200, "shield"))
        powerups.add(PowerUp(440, 350, "double_jump"))
        powerups.add(PowerUp(2640, 200, "magnet"))

        star_items.add(StarCollectible(640, 280))
        star_items.add(StarCollectible(1830, 260))
        star_items.add(StarCollectible(2640, 200))

        boss = Boss(2900, 500, 2)
        flags.add(Flag(3100, 568))

    elif n == 3:
        pw = [
            (0, 568, 300, 32, "stone"), (380, 568, 200, 32, "stone"),
            (660, 568, 200, 32, "stone"), (940, 568, 200, 32, "stone"),
            (1220, 568, 300, 32, "stone"), (1600, 568, 200, 32, "stone"),
            (1880, 568, 300, 32, "stone"), (2260, 568, 200, 32, "stone"),
            (2540, 568, 300, 32, "stone"), (2920, 568, 200, 32, "stone"),
            (130, 460, 80, 20, "stone"), (330, 380, 100, 20, "stone"),
            (530, 310, 80, 20, "stone"), (730, 240, 100, 20, "stone"),
            (930, 180, 80, 20, "stone"), (1130, 260, 100, 20, "stone"),
            (1330, 190, 80, 20, "stone"), (1530, 310, 100, 20, "stone"),
            (1730, 240, 80, 20, "stone"), (1930, 170, 100, 20, "stone"),
            (2130, 310, 80, 20, "stone"), (2330, 240, 100, 20, "stone"),
            (2530, 180, 80, 20, "stone"), (2730, 310, 100, 20, "stone"),
            (430, 500, 60, 16, "bouncy"), (1030, 500, 60, 16, "bouncy"),
            (1630, 500, 60, 16, "bouncy"), (2230, 500, 60, 16, "bouncy"),
            (2830, 500, 60, 16, "bouncy"),
            (330, 320, 80, 20, "breakable"), (930, 350, 80, 20, "breakable"),
            (1530, 380, 80, 20, "breakable"), (2130, 360, 80, 20, "breakable"),
            (2730, 360, 80, 20, "breakable"),
        ]
        for x, y, w, h, t in pw:
            platforms.add(Platform(x, y, w, h, t))

        moving_plats.add(MovingPlatform(480, 300, 80, 16, move_x=100, speed=1.5))
        moving_plats.add(MovingPlatform(900, 400, 80, 16, move_y=120, speed=1.0))
        moving_plats.add(MovingPlatform(1300, 300, 80, 16, move_x=100, speed=1.2))
        moving_plats.add(MovingPlatform(1700, 250, 80, 16, move_y=100, speed=1.3))
        moving_plats.add(MovingPlatform(2100, 350, 80, 16, move_x=80, speed=1.1))
        moving_plats.add(MovingPlatform(2500, 280, 80, 16, move_y=90, speed=1.4))

        for x, y in [(180, 435), (380, 355), (580, 285), (780, 215),
                      (980, 155), (1180, 235), (1380, 165),
                      (1580, 285), (1780, 215), (1980, 145),
                      (2180, 285), (2380, 215), (2580, 155),
                      (2780, 285), (2980, 155),
                      (130, 540), (720, 540), (1300, 540),
                      (1880, 540), (2550, 540), (2950, 540)]:
            coins.add(Coin(x, y))

        enemies.add(Enemy(400, 536, 380, 580))
        enemies.add(Enemy(750, 536, 660, 860))
        enemies.add(Enemy(1300, 536, 1220, 1520))
        enemies.add(Enemy(1900, 536, 1880, 2180))
        enemies.add(Enemy(2550, 536, 2540, 2840))
        enemies.add(Enemy(540, 278, 530, 610, "flyer"))
        enemies.add(Enemy(1140, 228, 1130, 1230, "flyer"))
        enemies.add(Enemy(1740, 208, 1730, 1810, "flyer"))
        enemies.add(Enemy(2340, 208, 2330, 2430, "flyer"))
        enemies.add(Enemy(740, 208, 730, 830, "chaser"))
        enemies.add(Enemy(1540, 278, 1530, 1630, "chaser"))
        enemies.add(Enemy(2140, 278, 2130, 2210, "chaser"))
        enemies.add(Enemy(2740, 278, 2730, 2830, "chaser"))
        enemies.add(Enemy(950, 536, 940, 1140, "shooter"))
        enemies.add(Enemy(1610, 536, 1600, 1800, "shooter"))
        enemies.add(Enemy(2270, 536, 2260, 2460, "shooter"))

        hazards.add(Spike(300, 578, 80))
        hazards.add(Spike(580, 578, 80))
        hazards.add(Spike(860, 578, 80))
        hazards.add(Spike(1140, 578, 80))
        hazards.add(Spike(1520, 578, 80))
        hazards.add(Spike(1800, 578, 80))
        hazards.add(Spike(2180, 578, 80))
        hazards.add(Spike(2460, 578, 80))

        lavas.add(Lava(1040, 568, 180, 32))
        lavas.add(Lava(2040, 568, 200, 32))

        springs.add(Spring(130, 460))
        springs.add(Spring(530, 310))
        springs.add(Spring(1130, 260))
        springs.add(Spring(1730, 240))
        springs.add(Spring(2330, 240))
        springs.add(Spring(430, 500))
        springs.add(Spring(1630, 500))
        springs.add(Spring(2830, 500))

        checkpoints.add(Checkpoint(940, 568))
        checkpoints.add(Checkpoint(1600, 568))
        checkpoints.add(Checkpoint(2260, 568))
        checkpoints.add(Checkpoint(2920, 568))

        powerups.add(PowerUp(940, 145, "shield"))
        powerups.add(PowerUp(1540, 145, "speed"))
        powerups.add(PowerUp(1940, 135, "double_jump"))
        powerups.add(PowerUp(2540, 145, "magnet"))

        star_items.add(StarCollectible(980, 150))
        star_items.add(StarCollectible(1980, 140))
        star_items.add(StarCollectible(2580, 150))

        boss = Boss(3000, 500, 3)
        flags.add(Flag(3150, 568))

    return (platforms, coins, enemies, hazards, flags, springs, moving_plats,
            checkpoints, powerups, star_items, lavas, boss)


# ── Drawing helpers ──────────────────────────────────────────
def draw_bg(cam_x, level_num):
    theme = LEVEL_THEMES.get(level_num, LEVEL_THEMES[1])
    bg = theme["bg_colors"]
    screen.fill(bg[0])

    # Stars
    for i in range(80):
        x = (i * 37 + pygame.time.get_ticks() * 0.008) % SW
        y = (i * 23) % (SH // 2)
        a = int(100 + 80 * math.sin(pygame.time.get_ticks() * 0.002 + i))
        s = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (1, 1), 1)
        screen.blit(s, (int(x), int(y)))

    # Moon
    mx = int(650 - cam_x * 0.03) % (SW + 100)
    pygame.draw.circle(screen, (240, 240, 200), (mx, 75), 30)
    pygame.draw.circle(screen, bg[0], (mx + 10, 70), 25)
    pygame.draw.circle(screen, (220, 220, 180), (mx, 75), 30, 2)

    # Far mountains
    for i in range(0, SW + 200, 200):
        x = (i - cam_x * 0.08) % (SW + 200)
        h = 80 + (i * 47) % 60
        pygame.draw.ellipse(screen, bg[1], (int(x) - 40, SH - 120 - h // 3, 220, h))

    # Mid hills
    for i in range(0, SW + 200, 150):
        x = (i - cam_x * 0.2) % (SW + 200)
        h = 50 + (i * 23) % 40
        pygame.draw.ellipse(screen, bg[2], (int(x) - 30, SH - 80 - h // 3, 160, h))

    # Near bushes
    for i in range(0, SW + 100, 100):
        x = (i - cam_x * 0.4) % (SW + 100)
        pygame.draw.ellipse(screen, (bg[2][0] + 15, bg[2][1] + 15, bg[2][2] + 10),
                           (int(x) - 20, SH - 50, 100, 25))


def draw_hud(player, level, total_coins, total_stars, level_timer, boss=None):
    bg = pygame.Surface((SW, 48), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 140))
    screen.blit(bg, (0, 0))

    # HP bar
    hp_w = 120
    pygame.draw.rect(screen, (40, 40, 40), (10, 8, hp_w, 12), border_radius=3)
    hp_fill = int(hp_w * player.hp / player.max_hp)
    hp_color = GREEN if player.hp > 3 else YELLOW if player.hp > 1 else RED
    pygame.draw.rect(screen, hp_color, (10, 8, hp_fill, 12), border_radius=3)
    pygame.draw.rect(screen, (100, 100, 100), (10, 8, hp_w, 12), 1, border_radius=3)
    hp_txt = small_font.render(f"HP", True, WHITE)
    screen.blit(hp_txt, (12, 24))

    # Lives
    for i in range(player.lives):
        pygame.draw.polygon(screen, RED,
            [(90 + i * 18, 12), (95 + i * 18, 6), (100 + i * 18, 12), (95 + i * 18, 20)])

    # Coins
    pygame.draw.circle(screen, YELLOW, (12, 38), 6)
    ct = small_font.render(f"{player.coins}", True, WHITE)
    screen.blit(ct, (20, 30))

    # Stars
    pygame.draw.circle(screen, CYAN, (60, 38), 6)
    st = small_font.render(f"{player.stars}", True, WHITE)
    screen.blit(st, (68, 30))

    # Level name
    name = LEVEL_THEMES.get(level, {}).get("name", f"Level {level}")
    lt = font.render(name, True, WHITE)
    screen.blit(lt, (SW // 2 - lt.get_width() // 2, 10))

    # Timer
    secs = int(level_timer / 60)
    timer = font.render(f"{secs // 60}:{secs % 60:02d}", True, WHITE)
    screen.blit(timer, (SW - 70, 10))

    # Dash cooldown
    dash_w = 40
    pygame.draw.rect(screen, (40, 40, 40), (SW - 80, 32, dash_w, 8), border_radius=2)
    if player.can_dash and player.dash_cooldown <= 0:
        pygame.draw.rect(screen, CYAN, (SW - 80, 32, dash_w, 8), border_radius=2)
    else:
        cd = 1 - (player.dash_cooldown / 40)
        pygame.draw.rect(screen, (80, 80, 80), (SW - 80, 32, int(dash_w * cd), 8), border_radius=2)
    dt = small_font.render("DASH", True, (150, 150, 150))
    screen.blit(dt, (SW - 82, 42))

    # Power-up indicators
    y_off = 52
    if player.has_shield:
        screen.blit(small_font.render("Shield", True, CYAN), (10, y_off)); y_off += 16
    if player.speed_boost:
        screen.blit(small_font.render("Speed", True, ORANGE), (10, y_off)); y_off += 16
    if player.double_jump:
        screen.blit(small_font.render("DJ", True, PURPLE), (10, y_off)); y_off += 16
    if player.coin_magnet:
        screen.blit(small_font.render("Magnet", True, GREEN), (10, y_off)); y_off += 16

    # Combo
    if player.combo > 1:
        ct2 = font.render(f"Combo x{player.combo}!", True, YELLOW)
        pulse = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.01))
        ct2.set_alpha(min(255, pulse))
        screen.blit(ct2, (SW // 2 - ct2.get_width() // 2, SH - 50))

    # Boss HP
    if boss and boss.alive:
        boss_hp_w = 300
        bx = SW // 2 - boss_hp_w // 2
        by = SH - 30
        pygame.draw.rect(screen, (40, 40, 40), (bx, by, boss_hp_w, 16), border_radius=4)
        fill = int(boss_hp_w * boss.hp / boss.max_hp)
        bc = RED if boss.hp > boss.max_hp // 2 else ORANGE if boss.hp > boss.max_hp // 4 else (200, 0, 0)
        pygame.draw.rect(screen, bc, (bx, by, fill, 16), border_radius=4)
        pygame.draw.rect(screen, (100, 100, 100), (bx, by, boss_hp_w, 16), 2, border_radius=4)
        bt = boss_font.render(f"BOSS", True, WHITE)
        screen.blit(bt, (bx + boss_hp_w // 2 - bt.get_width() // 2, by - 1))


def draw_title():
    screen.fill(DARK_BLUE)
    t = pygame.time.get_ticks()

    for i in range(80):
        x = (i * 37 + t * 0.01) % SW
        y = (i * 23 + t * 0.005) % SH
        a = int(100 + 50 * math.sin(t * 0.002 + i))
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (2, 2), 2)
        screen.blit(s, (int(x), int(y)))

    title = title_font.render("PLATFORMER", True, YELLOW)
    sub = big_font.render("ADVENTURE DX", True, CYAN)
    screen.blit(title, (SW // 2 - title.get_width() // 2, 120))
    screen.blit(sub, (SW // 2 - sub.get_width() // 2, 195))

    pulse = int(180 + 75 * math.sin(t * 0.004))
    screen.blit(font.render("ENTER - New Game", True, (pulse, pulse, pulse)), (SW // 2 - 100, 320))
    screen.blit(font.render("L - Level Select", True, (pulse, pulse, pulse)), (SW // 2 - 100, 355))

    ctrl = ["Arrow Keys / WASD - Move", "Space / W / Up - Jump",
            "L-Shift / Z - Dash", "R - Restart", "ESC - Pause"]
    for i, line in enumerate(ctrl):
        screen.blit(small_font.render(line, True, (130, 130, 160)), (SW // 2 - 120, 410 + i * 20))

    # Stats
    screen.blit(small_font.render(f"Deaths: {save_data.get('deaths', 0)}", True, (100, 100, 130)), (SW // 2 - 120, 520))
    screen.blit(small_font.render(f"Enemies defeated: {save_data.get('enemies_killed', 0)}", True, (100, 100, 130)), (SW // 2 - 120, 538))
    ach_count = len(save_data.get("achievements", []))
    screen.blit(small_font.render(f"Achievements: {ach_count}/8", True, (100, 100, 130)), (SW // 2 - 120, 556))


def draw_level_select(unlocked_levels):
    screen.fill(DARK_BLUE)
    screen.blit(big_font.render("SELECT LEVEL", True, WHITE), (SW // 2 - 160, 40))

    for i in range(1, 4):
        theme = LEVEL_THEMES[i]
        beaten = i in save_data.get("levels_beaten", [])
        locked = i > unlocked_levels
        x = SW // 2 - 120
        y = 120 + (i - 1) * 130
        w, h = 240, 100

        if locked:
            color = (50, 50, 60)
        elif beaten:
            color = (20, 60, 20)
        else:
            color = (30, 40, 70)

        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((*color, 200))
        pygame.draw.rect(bg, CYAN if not locked else GRAY, (0, 0, w, h), 2, border_radius=8)
        screen.blit(bg, (x, y))

        if locked:
            screen.blit(font.render(f"Level {i} - LOCKED", True, GRAY), (x + 20, y + 30))
            screen.blit(small_font.render("Complete previous level to unlock", True, (80, 80, 100)), (x + 20, y + 58))
        else:
            screen.blit(font.render(f"Level {i}", True, WHITE), (x + 20, y + 10))
            screen.blit(small_font.render(theme["name"], True, CYAN), (x + 20, y + 35))
            stars_in_level = 3
            screen.blit(small_font.render(f"{'*' * stars_in_level}", True, YELLOW), (x + 20, y + 55))
            if beaten:
                screen.blit(small_font.render("COMPLETE", True, GREEN), (x + 150, y + 55))
            screen.blit(small_font.render("Press ENTER to play", True, (130, 130, 160)), (x + 20, y + 75))

    screen.blit(small_font.render("Press ESC to go back", True, (100, 100, 130)), (SW // 2 - 80, SH - 40))


def draw_pause():
    overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    screen.blit(big_font.render("PAUSED", True, WHITE), (SW // 2 - 110, 200))
    hints = ["ESC - Resume", "R - Restart Level", "Q - Quit to Menu"]
    for i, h in enumerate(hints):
        screen.blit(font.render(h, True, (180, 180, 200)), (SW // 2 - 100, 280 + i * 35))


def draw_transition(alpha):
    if alpha > 0:
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(255, int(alpha))))
        screen.blit(overlay, (0, 0))


# ── Main game loop ───────────────────────────────────────────
def run_game():
    state = "title"
    level = 1
    max_level = 3
    unlocked = max(1, *save_data.get("levels_beaten", [0])) + 1 if save_data.get("levels_beaten") else 1
    unlocked = min(unlocked, 3)

    transition_alpha = 0
    transition_target = None
    select_level = 1

    while True:
        # ── Transition ──
        if transition_target:
            transition_alpha += 12
            if transition_alpha >= 255:
                state = transition_target
                transition_target = None
                transition_alpha = 255
        else:
            transition_alpha = max(0, transition_alpha - 8)

        # ── TITLE ──
        if state == "title":
            draw_title()
            draw_transition(transition_alpha)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    write_save(save_data); pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        transition_target = "playing"
                        level = 1
                    if event.key == pygame.K_l:
                        transition_target = "level_select"
                    if event.key == pygame.K_ESCAPE:
                        write_save(save_data); pygame.quit(); sys.exit()
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ── LEVEL SELECT ──
        if state == "level_select":
            draw_level_select(unlocked)
            draw_transition(transition_alpha)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    write_save(save_data); pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        transition_target = "title"
                    if event.key == pygame.K_RETURN:
                        if select_level <= unlocked:
                            level = select_level
                            transition_target = "playing"
                    if event.key == pygame.K_UP:
                        select_level = max(1, select_level - 1)
                    if event.key == pygame.K_DOWN:
                        select_level = min(unlocked, select_level + 1)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ── PLAYING ──
        if state == "playing":
            data = make_level(level)
            (platforms, coin_sprites, enemy_sprites, hazard_sprites, flag_sprites,
             spring_sprites, moving_sprites, checkpoint_sprites, powerup_sprites,
             star_sprites, lava_sprites, boss) = data

            total_coins = len(coin_sprites)
            total_stars = len(star_sprites)

            spawn_x, spawn_y = 50, 500
            player = Player(spawn_x, spawn_y)

            cam = Camera(LEVEL_W, LEVEL_H)
            level_timer = 0
            game_over = False
            game_won = False
            paused = False
            enemy_bullets = pygame.sprite.Group()
            shooting_enemies = [e for e in enemy_sprites if e.etype == "shooter"]

            while state == "playing":
                clock.tick(FPS)
                level_timer += 1

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        write_save(save_data); pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            paused = not paused
                        if event.key == pygame.K_r and not paused:
                            break
                        if paused:
                            if event.key == pygame.K_r:
                                break
                            if event.key == pygame.K_q:
                                state = "title"
                                paused = False
                                break
                        if game_over and event.key == pygame.K_RETURN:
                            transition_target = "title"
                        if game_won and event.key == pygame.K_RETURN:
                            if level < max_level:
                                level += 1
                                transition_target = "playing"
                            else:
                                transition_target = "title"

                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and not paused:
                    break
                if state != "playing":
                    break

                if paused:
                    draw_bg(int(cam.offset.x), level)
                    for mp in moving_sprites:
                        screen.blit(mp.image, cam.apply(mp.rect))
                    for s in platforms:
                        screen.blit(s.image, cam.apply(s.rect))
                    draw_hud(player, level, total_coins, total_stars, level_timer, boss)
                    draw_pause()
                    draw_transition(transition_alpha)
                    pygame.display.flip()
                    continue

                if not game_over and not game_won:
                    # Magnet check for coins
                    for c in coin_sprites:
                        c._magnet = player.coin_magnet

                    player.update(platforms, moving_sprites, hazard_sprites, enemy_sprites)

                    for mp in moving_sprites:
                        mp.update()

                    for e in enemy_sprites:
                        e.update(player.rect, platforms)
                        # Shooter bullets
                        if e.etype == "shooter" and e.alive and e.timer % 100 == 0:
                            d = 1 if player.rect.centerx > e.rect.centerx else -1
                            b = EnemyBullet(e.rect.centerx + d * 20, e.rect.centery, d)
                            enemy_bullets.add(b)

                    enemy_bullets.update()
                    # Bullet vs player
                    for b in pygame.sprite.spritecollide(player, enemy_bullets, True):
                        player.take_damage()

                    for c in coin_sprites:
                        c.update(player.rect)

                    for cp in checkpoint_sprites:
                        cp.update()
                        if player.rect.colliderect(cp.rect):
                            cp.activate()
                            spawn_x = cp.rect.x
                            spawn_y = cp.rect.y - player.h

                    for sp in spring_sprites:
                        sp.update()
                        if player.rect.colliderect(sp.rect) and player.vel_y > 0:
                            player.vel_y = -18
                            player.on_ground = False
                            sp.compress()
                            SND_SPRING.play()
                            particles.emit(sp.rect.centerx, sp.rect.top, 8, YELLOW, 3, 15, 2, 0.1, [YELLOW, ORANGE])

                    for lv in lava_sprites:
                        lv.update()
                        if player.rect.colliderect(lv.rect):
                            player.hp = 0
                            player.die()
                            cam.shake(8, 20)

                    # Coin collect
                    collected = pygame.sprite.spritecollide(player, coin_sprites, True)
                    for c in collected:
                        player.coins += 1
                        SND_COIN.play()
                        SND_COIN2.play()
                        particles.emit(c.rect.centerx, c.rect.centery, 8, YELLOW, 2, 20, 2, 0.05, [YELLOW, WHITE, ORANGE])

                    # Star collect
                    star_collected = pygame.sprite.spritecollide(player, star_sprites, True)
                    for s in star_collected:
                        player.stars += 1
                        SND_STAR.play()
                        particles.emit(s.rect.centerx, s.rect.centery, 15, CYAN, 4, 25, 3, 0.05, [CYAN, YELLOW, WHITE])

                    # Enemy collision - stomp or damage
                    for e in pygame.sprite.spritecollide(player, enemy_sprites, False):
                        if not e.alive:
                            continue
                        # Check if player is stomping
                        if player.vel_y > 0 and player.rect.bottom < e.rect.centery + 5:
                            if e.take_hit():
                                player.vel_y = -10
                                save_data["enemies_killed"] = save_data.get("enemies_killed", 0) + 1
                                # Combo
                                player.combo += 1
                                player.combo_timer = 120
                                if player.combo > save_data.get("best_combo", 0):
                                    save_data["best_combo"] = player.combo
                                SND_STOMP.play()
                                # Score bonus from combo
                                if player.combo >= 3:
                                    player.coins += player.combo
                            cam.shake(3, 8)
                        else:
                            player.take_damage()
                            cam.shake(4, 10)

                    # Spike hazard collision
                    for h in pygame.sprite.spritecollide(player, hazard_sprites, False):
                        if hasattr(h, 'hazard_type') and h.hazard_type == "spike":
                            if player.take_damage():
                                player.vel_y = -8
                                cam.shake(4, 10)

                    # Boss
                    if boss and boss.alive and not boss.defeated:
                        boss.update(player.rect)
                        # Boss projectiles vs player
                        for b in pygame.sprite.spritecollide(player, boss.projectiles, True):
                            player.take_damage()
                        # Player vs boss
                        if player.rect.colliderect(boss.rect):
                            if player.vel_y > 0 and player.rect.bottom < boss.rect.centery:
                                boss.take_hit()
                                player.vel_y = -10
                                cam.shake(5, 12)
                            else:
                                player.take_damage()
                                cam.shake(4, 10)
                    elif boss and boss.defeated:
                        boss.update(player.rect)
                        if boss.defeat_timer > 120:
                            boss.alive = False

                    # Flag
                    if pygame.sprite.spritecollide(player, flag_sprites, False):
                        game_won = True
                        SND_LEVELWIN.play()
                        save_data.setdefault("levels_beaten", [])
                        if level not in save_data["levels_beaten"]:
                            save_data["levels_beaten"].append(level)
                        save_data["total_coins"] = save_data.get("total_coins", 0) + player.coins
                        save_data["total_stars"] = save_data.get("total_stars", 0) + player.stars
                        save_data["best_times"][str(level)] = min(
                            save_data.get("best_times", {}).get(str(level), 999999), int(level_timer / 60))
                        unlocked = min(3, max(unlocked, level + 1))
                        write_save(save_data)
                        for _ in range(60):
                            particles.emit(player.rect.centerx, player.rect.centery, 1, YELLOW, 8, 60, 4, -0.02,
                                           [YELLOW, GREEN, CYAN, WHITE, RED])

                    # Power-ups
                    pu_collected = pygame.sprite.spritecollide(player, powerup_sprites, True)
                    for pu in pu_collected:
                        SND_POWERUP.play()
                        if pu.ptype == "shield":
                            player.has_shield = True
                            player.shield_timer = 600
                        elif pu.ptype == "speed":
                            player.speed_boost = True
                            player.speed_timer = 480
                        elif pu.ptype == "double_jump":
                            player.double_jump = True
                        elif pu.ptype == "magnet":
                            player.coin_magnet = True
                            player.magnet_timer = 600
                        particles.emit(pu.rect.centerx, pu.rect.centery, 15, CYAN, 4, 25, 3, 0.05, [CYAN, WHITE, PURPLE])

                    if not player.alive:
                        game_over = True
                        cam.shake(8, 25)

                    # Achievements
                    if player.combo >= 5 and "Combo Master" not in save_data.get("achievements", []):
                        ach_popup.show("Combo Master", "Reach a 5x combo")
                    if player.coins >= 30 and "Coin Hoarder" not in save_data.get("achievements", []):
                        ach_popup.show("Coin Hoarder", "Collect 30 coins in a level")
                    if level_timer < 600 and game_won and "Speedrunner" not in save_data.get("achievements", []):
                        ach_popup.show("Speedrunner", "Beat a level in under 10s")
                    if player.stars >= 3 and "Star Collector" not in save_data.get("achievements", []):
                        ach_popup.show("Star Collector", "Collect all 3 stars in a level")

                    particles.update()

                # ── Draw ──
                cam.update(player.rect)
                draw_bg(int(cam.offset.x), level)

                for lv in lava_sprites:
                    lv.draw(screen, cam)
                for mp in moving_sprites:
                    screen.blit(mp.image, cam.apply(mp.rect))
                for s in platforms:
                    screen.blit(s.image, cam.apply(s.rect))
                for s in coin_sprites:
                    screen.blit(s.image, cam.apply(s.rect))
                for s in star_sprites:
                    glow = pygame.Surface((28, 28), pygame.SRCALPHA)
                    ga = int(40 + 30 * math.sin(pygame.time.get_ticks() * 0.005))
                    pygame.draw.circle(glow, (*YELLOW, ga), (14, 14), 14)
                    screen.blit(glow, cam.apply(s.rect).move(-4, -4))
                    screen.blit(s.image, cam.apply(s.rect))
                for s in hazard_sprites:
                    screen.blit(s.image, cam.apply(s.rect))
                for s in spring_sprites:
                    screen.blit(s.image, cam.apply(s.rect))
                for s in checkpoint_sprites:
                    screen.blit(s.image, cam.apply(s.rect))
                for s in powerup_sprites:
                    glow = pygame.Surface((30, 30), pygame.SRCALPHA)
                    ga = int(40 + 30 * math.sin(pygame.time.get_ticks() * 0.005))
                    pygame.draw.circle(glow, (*CYAN, ga), (15, 15), 15)
                    screen.blit(glow, cam.apply(s.rect).move(-4, -4))
                    screen.blit(s.image, cam.apply(s.rect))
                for e in enemy_sprites:
                    if e.alive:
                        screen.blit(e.image, cam.apply(e.rect))
                for b in enemy_bullets:
                    screen.blit(b.image, cam.apply(b.rect))
                if boss and boss.alive:
                    screen.blit(boss.image, cam.apply(boss.rect))
                    for b in boss.projectiles:
                        screen.blit(b.image, cam.apply(b.rect))
                for s in flag_sprites:
                    s.update()
                    screen.blit(s.image, cam.apply(s.rect))

                particles.draw(screen, cam)

                if player.alive:
                    screen.blit(player.image, cam.apply(player.rect))

                draw_hud(player, level, total_coins, total_stars, level_timer, boss)
                ach_popup.update()
                ach_popup.draw(screen)

                if game_over:
                    overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    screen.blit(overlay, (0, 0))
                    gt = big_font.render("GAME OVER", True, RED)
                    screen.blit(gt, (SW // 2 - gt.get_width() // 2, 200))
                    screen.blit(font.render(f"Coins: {player.coins}  Stars: {player.stars}", True, WHITE),
                               (SW // 2 - 120, 270))
                    screen.blit(font.render("ENTER - Menu  |  R - Retry", True, (180, 180, 200)),
                               (SW // 2 - 140, 320))

                if game_won:
                    overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    screen.blit(overlay, (0, 0))
                    wt = big_font.render("LEVEL COMPLETE!", True, YELLOW)
                    screen.blit(wt, (SW // 2 - wt.get_width() // 2, 180))
                    screen.blit(font.render(f"Coins: {player.coins}/{total_coins}", True, WHITE),
                               (SW // 2 - 80, 250))
                    screen.blit(font.render(f"Stars: {player.stars}/{total_stars}", True, CYAN),
                               (SW // 2 - 60, 278))
                    secs = int(level_timer / 60)
                    screen.blit(font.render(f"Time: {secs // 60}:{secs % 60:02d}", True, WHITE),
                               (SW // 2 - 50, 306))
                    if player.combo > 1:
                        screen.blit(font.render(f"Best Combo: {player.combo}x", True, ORANGE),
                                   (SW // 2 - 70, 334))
                    if level < max_level:
                        screen.blit(font.render("ENTER - Next Level", True, (180, 180, 200)),
                                   (SW // 2 - 90, 380))
                    else:
                        vt = big_font.render("YOU WIN!", True, CYAN)
                        screen.blit(vt, (SW // 2 - vt.get_width() // 2, 370))
                        screen.blit(font.render("ENTER - Menu", True, (180, 180, 200)),
                                   (SW // 2 - 70, 430))

                draw_transition(transition_alpha)
                pygame.display.flip()

            if state == "playing":
                if game_won:
                    continue
                elif game_over:
                    state = "title"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    continue
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "title"


if __name__ == "__main__":
    run_game()
