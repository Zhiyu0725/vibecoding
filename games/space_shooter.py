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

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
CYAN = (0, 220, 220)
GREEN = (50, 220, 80)
ORANGE = (255, 165, 0)
PURPLE = (180, 80, 255)
PINK = (255, 100, 150)
BLUE = (80, 140, 255)
DARK_BG = (8, 8, 24)
GOLD = (255, 200, 50)

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Galactic Fury DX")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)
big_font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 16)
title_font = pygame.font.SysFont("arial", 60, bold=True)
score_font = pygame.font.SysFont("consolas", 28, bold=True)
huge_font = pygame.font.SysFont("arial", 72, bold=True)

SAVE_PATH = os.path.join(os.path.expanduser("~"), ".galactic_fury_save.json")


def gen_sound(freq, dur, vol=0.2, wave="sine", f_end=None):
    sr = 22050
    n = int(sr * dur)
    buf = bytearray(n * 4)
    for i in range(n):
        t = i / sr
        f = freq + (f_end - freq) * (i / n) if f_end else freq
        if wave == "sine":
            val = int(vol * 32767 * math.sin(2 * math.pi * f * t))
        elif wave == "square":
            val = int(vol * 32767 * (1 if math.sin(2 * math.pi * f * t) > 0 else -1))
        elif wave == "saw":
            val = int(vol * 32767 * (2 * (f * t % 1) - 1))
        else:
            val = int(vol * 32767 * (random.random() * 2 - 1))
        env = max(0, 1.0 - (i / n) ** 0.4)
        val = max(-32767, min(32767, int(val * env)))
        buf[i * 4] = val & 0xFF
        buf[i * 4 + 1] = (val >> 8) & 0xFF
        buf[i * 4 + 2] = val & 0xFF
        buf[i * 4 + 3] = (val >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))


SND_SHOOT = gen_sound(880, 0.06, 0.12, "square", 440)
SND_HIT = gen_sound(200, 0.08, 0.15, "square")
SND_EXPLODE = gen_sound(100, 0.25, 0.2, "noise")
SND_BIG_EXPLODE = gen_sound(60, 0.5, 0.25, "noise")
SND_POWERUP = gen_sound(660, 0.2, 0.15, "sine", 1320)
SND_PLAYER_HIT = gen_sound(300, 0.3, 0.2, "square", 100)
SND_WAVE = gen_sound(440, 0.3, 0.15, "sine", 880)
SND_BOSS = gen_sound(80, 0.15, 0.2, "square")
SND_LASER = gen_sound(1200, 0.1, 0.1, "sine", 400)
SND_DASH = gen_sound(600, 0.12, 0.15, "saw", 200)
SND_BOMB = gen_sound(80, 0.6, 0.3, "noise")
SND_ACHIEVE = gen_sound(660, 0.15, 0.15, "sine", 1320)
SND_COMBO = gen_sound(523, 0.08, 0.1, "sine", 1047)
SND_MISSILE_LOCK = gen_sound(1000, 0.1, 0.08, "sine", 1400)


# ── Save System ──────────────────────────────────────────────
def load_save():
    try:
        with open(SAVE_PATH) as f:
            return json.load(f)
    except Exception:
        return {"high_score": 0, "max_wave": 0, "total_kills": 0, "achievements": [],
                "unlocked_ships": ["fighter"], "selected_ship": "fighter",
                "total_games": 0, "bosses_killed": 0}


def write_save(data):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


save = load_save()


# ── Camera / Screen Shake ────────────────────────────────────
class Camera:
    def __init__(self):
        self.ox, self.oy = 0, 0
        self.shake_amt = 0
        self.shake_dur = 0

    def shake(self, amt=4, dur=10):
        self.shake_amt = amt
        self.shake_dur = dur

    def update(self):
        if self.shake_dur > 0:
            self.shake_dur -= 1
            self.ox = random.randint(-self.shake_amt, self.shake_amt)
            self.oy = random.randint(-self.shake_amt, self.shake_amt)
            self.shake_amt = max(0, self.shake_amt - 0.4)
        else:
            self.ox, self.oy = 0, 0

    def apply(self, x, y):
        return int(x + self.ox), int(y + self.oy)


cam = Camera()


# ── Slow Motion ──────────────────────────────────────────────
class SlowMo:
    def __init__(self):
        self.timer = 0
        self.scale = 1.0

    def trigger(self, duration=20, scale=0.3):
        self.timer = duration
        self.scale = scale

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            self.scale = min(1.0, self.scale + 0.04)
        else:
            self.scale = 1.0

    def get_dt(self):
        return self.scale


slowmo = SlowMo()


# ── Particles ────────────────────────────────────────────────
class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'max_life', 'size', 'grav', 'alive')

    def __init__(self, x, y, vx, vy, color, life, size=2, grav=0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = self.max_life = life
        self.size = size
        self.grav = grav
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.grav
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surf, cam_off=(0, 0)):
        a = int(255 * self.life / self.max_life)
        sz = max(1, int(self.size * self.life / self.max_life))
        s = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], a), (sz, sz), sz)
        surf.blit(s, (int(self.x - sz - cam_off[0]), int(self.y - sz - cam_off[1])))


class Particles:
    def __init__(self):
        self.list = []

    def emit(self, x, y, count, color, spread=3, life=20, size=2, grav=0, colors=None):
        for _ in range(count):
            vx = random.uniform(-spread, spread)
            vy = random.uniform(-spread, spread)
            c = random.choice(colors) if colors else color
            self.list.append(Particle(x, y, vx, vy, c, random.randint(life // 2, life), size, grav))

    def trail(self, x, y, color, size=2):
        self.list.append(Particle(x + random.uniform(-1, 1), y, random.uniform(-0.3, 0.3),
                                  random.uniform(-1, 0), color, 15, size, 0))

    def update(self, dt=1.0):
        for i in range(len(self.list) - 1, -1, -1):
            p = self.list[i]
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.grav * dt
            p.life -= dt
            if p.life <= 0:
                self.list.pop(i)

    def draw(self, surf):
        for p in self.list:
            a = max(0, min(255, int(255 * p.life / p.max_life)))
            sz = max(1, int(p.size * p.life / p.max_life))
            s = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p.color[:3], a), (sz, sz), sz)
            surf.blit(s, (int(p.x - sz), int(p.y - sz)))

    def clear(self):
        self.list.clear()


particles = Particles()


# ── Screen flash ─────────────────────────────────────────────
class ScreenFlash:
    def __init__(self):
        self.alpha = 0
        self.color = WHITE

    def trigger(self, color=WHITE, alpha=80):
        self.color = color
        self.alpha = alpha

    def update(self):
        self.alpha = max(0, self.alpha - 5)

    def draw(self, surf):
        if self.alpha > 0:
            overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
            overlay.fill((*self.color[:3], min(255, int(self.alpha))))
            surf.blit(overlay, (0, 0))


flash = ScreenFlash()


# ── Floating text ────────────────────────────────────────────
class FloatingText:
    def __init__(self, x, y, text, color=WHITE, size=16):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = 45
        self.max_life = 45
        self.font = pygame.font.SysFont("arial", size, bold=True)
        self.vy = -1.5

    def update(self):
        self.y += self.vy
        self.vy *= 0.96
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        a = int(255 * self.life / self.max_life)
        t = self.font.render(self.text, True, self.color)
        t.set_alpha(a)
        surf.blit(t, (int(self.x - t.get_width() // 2), int(self.y)))


floating_texts = []


# ── Achievement popups ──────────────────────────────────────
class AchievementPopup:
    def __init__(self):
        self.current = None
        self.timer = 0

    def show(self, name, desc):
        if name in save.get("achievements", []):
            return
        save.setdefault("achievements", []).append(name)
        write_save(save)
        self.current = (name, desc)
        self.timer = 180
        SND_ACHIEVE.play()

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.current = None

    def draw(self, surf):
        if not self.current or self.timer <= 0:
            return
        name, desc = self.current
        a = min(255, self.timer * 4) if self.timer > 150 else min(255, self.timer * 8) if self.timer < 30 else 255
        bg = pygame.Surface((300, 50), pygame.SRCALPHA)
        bg.fill((30, 30, 60, min(220, a)))
        pygame.draw.rect(bg, (*GOLD, min(255, a)), (0, 0, 300, 50), 2, border_radius=6)
        surf.blit(bg, (SW // 2 - 150, 60))
        t1 = small_font.render("ACHIEVEMENT!", True, GOLD)
        t1.set_alpha(min(255, a))
        surf.blit(t1, (SW // 2 - t1.get_width() // 2, 64))
        t2 = small_font.render(f"{name}: {desc}", True, WHITE)
        t2.set_alpha(min(255, a))
        surf.blit(t2, (SW // 2 - t2.get_width() // 2, 82))


ach = AchievementPopup()


# ── Star field ──────────────────────────────────────────────
class StarField:
    def __init__(self):
        self.layers = []
        for i in range(4):
            layer = []
            count = [50, 35, 25, 15][i]
            speed = [0.2, 0.5, 0.9, 1.5][i]
            brightness = [(40, 40, 60), (80, 80, 110), (130, 130, 170), (200, 200, 240)][i]
            for _ in range(count):
                layer.append([random.randint(0, SW), random.randint(0, SH), speed, brightness,
                             random.uniform(0.5, 1.8), random.uniform(0, 6.28)])
            self.layers.append(layer)

    def update(self, dt=1):
        for layer in self.layers:
            for s in layer:
                s[1] += s[2] * dt
                s[5] += 0.02
                if s[1] > SH:
                    s[1] = 0
                    s[0] = random.randint(0, SW)

    def draw(self, surf):
        t = pygame.time.get_ticks()
        for layer in self.layers:
            for s in layer:
                twinkle = 0.6 + 0.4 * math.sin(s[5])
                c = tuple(min(255, int(v * twinkle)) for v in s[3])
                sz = max(1, int(s[4] * twinkle))
                pygame.draw.circle(surf, c, (int(s[0]), int(s[1])), sz)


starfield = StarField()


# ── Ship definitions ────────────────────────────────────────
SHIP_DEFS = {
    "fighter": {
        "name": "Fighter", "desc": "Balanced ship",
        "speed": 5, "hp": 5, "fire_rate": 8, "unlock": "Default",
        "color_main": (100, 140, 220), "color_sec": (140, 180, 255),
        "w": 32, "h": 36,
    },
    "speeder": {
        "name": "Speeder", "desc": "Fast but fragile",
        "speed": 7, "hp": 3, "fire_rate": 6, "unlock": "Reach wave 5",
        "color_main": (50, 200, 100), "color_sec": (80, 255, 140),
        "w": 28, "h": 32,
    },
    "tank": {
        "name": "Tank", "desc": "Slow but tough",
        "speed": 3.5, "hp": 8, "fire_rate": 12, "unlock": "Kill 500 enemies",
        "color_main": (180, 100, 40), "color_sec": (220, 140, 60),
        "w": 38, "h": 40,
    },
    "phantom": {
        "name": "Phantom", "desc": "Dodge specialist",
        "speed": 5, "hp": 4, "fire_rate": 8, "unlock": "Dash 100 times",
        "color_main": (140, 60, 180), "color_sec": (180, 100, 220),
        "w": 30, "h": 34,
    },
    "phoenix": {
        "name": "Phoenix", "desc": "Fires twice as fast",
        "speed": 4.5, "hp": 4, "fire_rate": 4, "unlock": "Beat wave 10",
        "color_main": (220, 80, 30), "color_sec": (255, 140, 50),
        "w": 32, "h": 36,
    },
}


# ── Player ──────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self, ship_id="fighter"):
        super().__init__()
        sd = SHIP_DEFS[ship_id]
        self.ship_id = ship_id
        self.w, self.h = sd["w"], sd["h"]
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(centerx=SW // 2, bottom=SH - 40)
        self.speed = sd["speed"]
        self.hp = sd["hp"]
        self.max_hp = sd["hp"]
        self.base_fire_rate = sd["fire_rate"]
        self.fire_rate = sd["fire_rate"]
        self.fire_timer = 0
        self.weapon = "normal"
        self.weapon_timer = 0
        self.alive = True
        self.inv_timer = 0
        self.shield = False
        self.shield_timer = 0
        self.shield_angle = 0
        self.thrust_timer = 0
        self.score_multiplier = 1.0
        # Dash
        self.dash_cooldown = 0
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_trail = []
        self.dash_dir = 0
        self.dash_count = 0
        # Bomb
        self.bombs = 2
        self.max_bombs = 3
        self.bomb_cooldown = 0
        # Combo
        self.combo = 0
        self.combo_timer = 0
        self.max_combo = 0
        self.kills = 0
        # Regen
        self.regen_timer = 0
        # Color
        self.color_main = sd["color_main"]
        self.color_sec = sd["color_sec"]
        self.draw_ship()

    def draw_ship(self):
        self.image.fill((0, 0, 0, 0))
        s = self.image
        cx = self.w // 2

        # Dash trail
        if self.is_dashing:
            for r, t in self.dash_trail:
                a = int(120 * (t / 6))
                ts = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                pygame.draw.rect(ts, (*CYAN, a), (0, 0, self.w, self.h), border_radius=4)
                s.blit(ts, (r[0] - self.rect.x, r[1] - self.rect.y))

        # Engine glow
        thrust = int(4 + 3 * math.sin(self.thrust_timer * 0.3))
        pygame.draw.polygon(s, ORANGE, [(cx - 5, self.h - 4), (cx, self.h + thrust), (cx + 5, self.h - 4)])
        pygame.draw.polygon(s, YELLOW, [(cx - 3, self.h - 4), (cx, self.h + thrust - 2), (cx + 3, self.h - 4)])

        # Wings
        pygame.draw.polygon(s, (60, 60, 120), [(2, self.h - 8), (cx - 4, 10), (cx - 2, self.h - 4)])
        pygame.draw.polygon(s, (60, 60, 120), [(self.w - 2, self.h - 8), (cx + 4, 10), (cx + 2, self.h - 4)])

        # Body
        pygame.draw.polygon(s, self.color_main, [(cx, 2), (cx - 6, self.h - 6), (cx + 6, self.h - 6)])
        pygame.draw.polygon(s, self.color_sec, [(cx, 2), (cx - 4, self.h - 8), (cx + 4, self.h - 8)])

        # Cockpit
        pygame.draw.ellipse(s, CYAN, (cx - 3, 8, 6, 8))
        pygame.draw.ellipse(s, WHITE, (cx - 2, 9, 4, 4))

        # Shield
        if self.shield:
            sa = int(100 + 80 * math.sin(self.shield_angle))
            ss = pygame.Surface((self.w + 16, self.h + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(ss, (*CYAN, sa), (0, 0, self.w + 16, self.h + 16), 2)
            pygame.draw.ellipse(ss, (*CYAN, sa // 2), (2, 2, self.w + 12, self.h + 12), 1)
            self.image.blit(ss, (-8, -8))

    def update(self, keys):
        self.thrust_timer += 1

        if self.is_dashing:
            self.dash_timer -= 1
            self.rect.x += self.dash_dir * 15
            self.dash_trail.append((self.rect.copy(), 6))
            if self.dash_timer <= 0:
                self.is_dashing = False
            particles.trail(self.rect.centerx, self.rect.centery, CYAN, 3)
        else:
            vx, vy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                vx = -self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                vx = self.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                vy = -self.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                vy = self.speed * 0.7
            if vx and vy:
                vx = int(vx * 0.707)
                vy = int(vy * 0.707)
            self.rect.x += vx
            self.rect.y += vy

        self.rect.clamp_ip(pygame.Rect(0, 0, SW, SH))

        # Dash trail decay
        self.dash_trail = [(r, t - 1) for r, t in self.dash_trail if t > 1]

        if self.fire_timer > 0:
            self.fire_timer -= 1
        if self.weapon_timer > 0:
            self.weapon_timer -= 1
            if self.weapon_timer <= 0:
                self.weapon = "normal"
                self.fire_rate = self.base_fire_rate
        if self.inv_timer > 0:
            self.inv_timer -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1
            self.shield_angle += 0.1
            if self.shield_timer <= 0:
                self.shield = False
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0
        if self.hp < self.max_hp:
            self.regen_timer += 1
            if self.regen_timer >= 600:
                self.hp = min(self.max_hp, self.hp + 1)
                self.regen_timer = 0
        else:
            self.regen_timer = 0

        self.draw_ship()

    def dash(self):
        if self.is_dashing or self.dash_cooldown > 0:
            return
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if dx == 0:
            dx = 1 if not self.facing_right else -1 if hasattr(self, 'facing_right') else 1
            dx = 1
        self.is_dashing = True
        self.dash_timer = 6
        self.dash_cooldown = 35
        self.dash_dir = dx
        self.inv_timer = max(self.inv_timer, 8)
        self.dash_count += 1
        SND_DASH.play()
        for _ in range(8):
            particles.emit(self.rect.centerx, self.rect.centery, 1, CYAN, 2, 12, 2)

    def use_bomb(self):
        if self.bombs <= 0 or self.bomb_cooldown > 0:
            return False
        self.bombs -= 1
        self.bomb_cooldown = 60
        SND_BOMB.play()
        slowmo.trigger(30, 0.2)
        flash.trigger(WHITE, 120)
        cam.shake(10, 20)
        particles.emit(self.rect.centerx, self.rect.centery, 50, WHITE, 10, 40, 4, 0, [WHITE, CYAN, YELLOW])
        return True

    def shoot(self):
        if self.fire_timer > 0:
            return []
        self.fire_timer = self.fire_rate
        shots = []
        if self.weapon == "normal":
            shots.append(Bullet(self.rect.centerx, self.rect.top, 0, -10, 1, YELLOW))
            SND_SHOOT.play()
        elif self.weapon == "spread":
            for angle in [-20, -10, 0, 10, 20]:
                rad = math.radians(angle - 90)
                vx, vy = math.cos(rad) * 8, math.sin(rad) * 8
                shots.append(Bullet(self.rect.centerx, self.rect.top, vx, vy, 1, GREEN))
            SND_LASER.play()
        elif self.weapon == "laser":
            shots.append(Laser(self.rect.centerx, self.rect.top - 10))
            SND_LASER.play()
        elif self.weapon == "missile":
            shots.append(Missile(self.rect.centerx - 10, self.rect.centery))
            shots.append(Missile(self.rect.centerx + 10, self.rect.centery))
            SND_MISSILE_LOCK.play()
        return shots

    def add_kill(self, x, y, score_val):
        self.kills += 1
        self.combo += 1
        self.combo_timer = 120
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        multiplier = 1 + self.combo * 0.25
        actual_score = int(score_val * multiplier)
        # Combo text
        if self.combo >= 3:
            colors = {3: WHITE, 5: GREEN, 8: YELLOW, 12: ORANGE, 20: RED}
            c = WHITE
            for threshold in sorted(colors.keys(), reverse=True):
                if self.combo >= threshold:
                    c = colors[threshold]
                    break
            floating_texts.append(FloatingText(x, y, f"{self.combo}x COMBO! +{actual_score}", c, 18))
            SND_COMBO.play()
        else:
            floating_texts.append(FloatingText(x, y, f"+{actual_score}", YELLOW, 14))
        return actual_score

    def take_damage(self, amount=1):
        if self.inv_timer > 0:
            return False
        if self.shield:
            self.shield = False
            self.shield_timer = 0
            self.inv_timer = 45
            SND_PLAYER_HIT.play()
            particles.emit(self.rect.centerx, self.rect.centery, 15, CYAN, 4, 20, 2, 0, [CYAN, WHITE])
            return False
        self.hp -= amount
        self.inv_timer = 90
        self.combo = 0
        SND_PLAYER_HIT.play()
        cam.shake(5, 12)
        flash.trigger(RED, 40)
        particles.emit(self.rect.centerx, self.rect.centery, 15, CYAN, 4, 20, 2, 0, [CYAN, WHITE, BLUE])
        if self.hp <= 0:
            self.alive = False
            SND_BIG_EXPLODE.play()
            cam.shake(10, 25)
            flash.trigger(WHITE, 80)
            slowmo.trigger(25, 0.3)
            for _ in range(50):
                particles.emit(self.rect.centerx, self.rect.centery, 1,
                               random.choice([RED, ORANGE, YELLOW, WHITE]),
                               7, 45, 4, 0.05, [RED, ORANGE, YELLOW])
        return True


# ── Bullets ─────────────────────────────────────────────────
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, dmg=1, color=YELLOW):
        super().__init__()
        self.w, self.h = 4, 12
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, self.w, self.h), border_radius=2)
        glow = pygame.Surface((self.w + 4, self.h + 4), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color, 60), (0, 0, self.w + 4, self.h + 4), border_radius=3)
        self.image.blit(glow, (-2, -2))
        self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy = vx, vy
        self.dmg = dmg

    def update(self, dt=1):
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)
        if self.rect.bottom < 0 or self.rect.top > SH or self.rect.right < 0 or self.rect.left > SW:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, color=RED):
        super().__init__()
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (3, 3), 3)
        pygame.draw.circle(self.image, WHITE, (2, 2), 1)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy = vx, vy

    def update(self, dt=1):
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)
        if self.rect.top > SH or self.rect.bottom < 0 or self.rect.left > SW or self.rect.right < 0:
            self.kill()


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, SH), pygame.SRCALPHA)
        for i in range(SH):
            a = int(255 * (1 - i / SH) * 0.8)
            c = max(0, min(255, a))
            pygame.draw.rect(self.image, (*CYAN, c), (3, i, 2, 1))
            pygame.draw.rect(self.image, (*WHITE, c // 2), (2, i, 4, 1))
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.dmg = 3
        self.life = 10
        self.timer = 0

    def update(self, dt=1):
        self.timer += 1
        self.life -= 1
        if self.life <= 0:
            self.kill()
        if self.timer % 2 == 0:
            self.image.set_alpha(180)
        else:
            self.image.set_alpha(255)


class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 12), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, ORANGE, [(4, 0), (0, 8), (4, 12), (8, 8)])
        pygame.draw.polygon(self.image, YELLOW, [(4, 2), (2, 7), (4, 10), (6, 7)])
        self.rect = self.image.get_rect(center=(x, y))
        self.vx, self.vy = 0, -7
        self.dmg = 2
        self.target = None
        self.turn_speed = 0.07
        self.life = 180

    def find_target(self, enemies):
        best, best_dist = None, 500
        for e in enemies:
            if not e.alive:
                continue
            dx = e.rect.centerx - self.rect.centerx
            dy = e.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < best_dist:
                best_dist = dist
                best = e
        self.target = best

    def update(self, dt=1):
        if self.target and self.target.alive:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy) or 1
            self.vx += (dx / dist) * self.turn_speed * 60 * dt
            self.vy += (dy / dist) * self.turn_speed * 60 * dt
            speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
            if speed > 8:
                self.vx = self.vx / speed * 8
                self.vy = self.vy / speed * 8
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)
        angle = math.degrees(math.atan2(-self.vy, self.vx)) - 90
        orig = pygame.Surface((8, 12), pygame.SRCALPHA)
        pygame.draw.polygon(orig, ORANGE, [(4, 0), (0, 8), (4, 12), (8, 8)])
        pygame.draw.polygon(orig, YELLOW, [(4, 2), (2, 7), (4, 10), (6, 7)])
        self.image = pygame.transform.rotate(orig, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        particles.trail(self.rect.centerx, self.rect.bottom, ORANGE, 1)
        self.life -= 1
        if self.life <= 0 or self.rect.top > SH + 20 or self.rect.bottom < -20 or self.rect.left > SW + 20 or self.rect.right < -20:
            self.kill()


# ── Enemies ─────────────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, etype="basic", hp=2):
        super().__init__()
        self.w, self.h = 28, 28
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.etype = etype
        self.hp = hp
        self.max_hp = hp
        self.timer = random.randint(0, 100)
        self.alive = True
        self.hurt_flash = 0
        self.score_val = {"basic": 100, "fast": 150, "tank": 300, "shooter": 250,
                         "spinner": 350, "sweeper": 200, "bombardier": 400}[etype]
        self.draw_enemy()

    def draw_enemy(self):
        self.image.fill((0, 0, 0, 0))
        s = self.image
        cx, cy = self.w // 2, self.h // 2
        flash = self.hurt_flash > 0
        if self.hurt_flash > 0:
            self.hurt_flash -= 1

        if self.etype == "basic":
            c = WHITE if flash else (180, 60, 60)
            pygame.draw.polygon(s, c, [(cx, self.h - 2), (2, 4), (cx, 0), (self.w - 2, 4)])
            pygame.draw.polygon(s, (120, 30, 30), [(cx, self.h - 2), (2, 4), (cx, 0), (self.w - 2, 4)], 2)
            pygame.draw.circle(s, RED, (cx - 4, 10), 3)
            pygame.draw.circle(s, RED, (cx + 4, 10), 3)
        elif self.etype == "fast":
            c = WHITE if flash else (60, 60, 200)
            pygame.draw.polygon(s, c, [(cx, self.h), (0, cy), (cx, 0), (self.w, cy)])
            pygame.draw.polygon(s, (30, 30, 150), [(cx, self.h), (0, cy), (cx, 0), (self.w, cy)], 2)
            pygame.draw.circle(s, CYAN, (cx, cy), 4)
        elif self.etype == "tank":
            c = WHITE if flash else (80, 120, 80)
            pygame.draw.rect(s, c, (2, 2, self.w - 4, self.h - 4), border_radius=4)
            pygame.draw.rect(s, (50, 80, 50), (2, 2, self.w - 4, self.h - 4), 2, border_radius=4)
            pygame.draw.circle(s, YELLOW, (cx - 5, cy), 4)
            pygame.draw.circle(s, YELLOW, (cx + 5, cy), 4)
            bw = int(24 * self.hp / self.max_hp)
            pygame.draw.rect(s, (40, 40, 40), (2, -4, 24, 3))
            pygame.draw.rect(s, GREEN, (2, -4, bw, 3))
        elif self.etype == "shooter":
            c = WHITE if flash else (180, 100, 40)
            pygame.draw.ellipse(s, c, (0, 4, self.w, self.h - 4))
            pygame.draw.ellipse(s, (140, 70, 20), (0, 4, self.w, self.h - 4), 2)
            pygame.draw.rect(s, (60, 60, 60), (cx - 2, self.h - 2, 4, 6))
            pygame.draw.circle(s, WHITE, (cx - 5, cy), 3)
            pygame.draw.circle(s, WHITE, (cx + 5, cy), 3)
            pygame.draw.circle(s, RED, (cx - 5, cy), 1)
            pygame.draw.circle(s, RED, (cx + 5, cy), 1)
        elif self.etype == "spinner":
            c = WHITE if flash else PURPLE
            angle = self.timer * 3
            for i in range(4):
                a = math.radians(angle + i * 90)
                bx = cx + 10 * math.cos(a)
                by = cy + 10 * math.sin(a)
                pygame.draw.circle(s, c, (int(bx), int(by)), 4)
            pygame.draw.circle(s, WHITE, (cx, cy), 3)
        elif self.etype == "sweeper":
            c = WHITE if flash else PINK
            pygame.draw.polygon(s, c, [(0, cy), (cx, 0), (self.w, cy), (cx, self.h)])
            pygame.draw.polygon(s, (180, 60, 100), [(0, cy), (cx, 0), (self.w, cy), (cx, self.h)], 2)
            pygame.draw.circle(s, WHITE, (cx, cy), 4)
        elif self.etype == "bombardier":
            c = WHITE if flash else (200, 120, 0)
            pygame.draw.rect(s, c, (4, 2, self.w - 8, self.h - 4), border_radius=6)
            pygame.draw.rect(s, (160, 90, 0), (4, 2, self.w - 8, self.h - 4), 2, border_radius=6)
            pygame.draw.circle(s, RED, (cx, cy), 6)
            pygame.draw.circle(s, (255, 200, 0), (cx, cy), 3)

        if self.max_hp > 2:
            bw = 22
            pygame.draw.rect(s, (40, 40, 40), (cx - bw // 2, -4, bw, 3))
            fill = int(bw * self.hp / self.max_hp)
            pygame.draw.rect(s, GREEN if self.hp > self.max_hp // 2 else YELLOW, (cx - bw // 2, -4, fill, 3))

    def update(self, player_pos=None, dt=1):
        self.timer += 1
        spd = dt
        if self.etype == "basic":
            self.rect.y += int(1.5 * spd)
            self.rect.x += int(math.sin(self.timer * 0.05) * 0.8 * spd)
        elif self.etype == "fast":
            self.rect.y += int(3.5 * spd)
            self.rect.x += int(math.sin(self.timer * 0.1) * 1.5 * spd)
        elif self.etype == "tank":
            self.rect.y += int(0.7 * spd)
        elif self.etype == "shooter":
            self.rect.y += int(1.0 * spd)
            if player_pos:
                dx = player_pos[0] - self.rect.centerx
                self.rect.x += int(1.5 * spd) if dx > 0 else int(-1.5 * spd)
        elif self.etype == "spinner":
            self.rect.y += int(1.2 * spd)
            self.rect.x += int(math.cos(self.timer * 0.08) * 2 * spd)
        elif self.etype == "sweeper":
            self.rect.y += int(2.0 * spd)
            self.rect.x += int(math.sin(self.timer * 0.06) * 3 * spd)
        elif self.etype == "bombardier":
            self.rect.y += int(0.8 * spd)
            if player_pos:
                dx = player_pos[0] - self.rect.centerx
                self.rect.x += int(0.8 * spd) if dx > 0 else int(-0.8 * spd)

        if self.rect.top > SH + 30:
            self.kill()
        self.draw_enemy()

    def shoot(self, player_pos):
        bullets = []
        cx, cy = self.rect.centerx, self.rect.bottom
        if self.etype == "shooter":
            dx = player_pos[0] - cx
            dy = player_pos[1] - cy
            dist = math.sqrt(dx * dx + dy * dy) or 1
            bullets.append(EnemyBullet(cx, cy, dx / dist * 4, dy / dist * 4))
        elif self.etype == "spinner":
            for i in range(6):
                a = math.radians(self.timer * 2 + i * 60)
                bullets.append(EnemyBullet(cx, self.rect.centery, math.cos(a) * 3, math.sin(a) * 3))
        elif self.etype == "bombardier":
            for angle in [-20, 0, 20]:
                rad = math.radians(angle + 90)
                bullets.append(EnemyBullet(cx, cy, math.cos(rad) * 2.5, math.sin(rad) * 2.5, ORANGE))
        return bullets

    def take_hit(self, dmg=1):
        self.hp -= dmg
        self.hurt_flash = 5
        SND_HIT.play()
        if self.hp <= 0:
            self.alive = False
            SND_EXPLODE.play()
            particles.emit(self.rect.centerx, self.rect.centery, 20, RED, 5, 25, 3, 0.02,
                          [RED, ORANGE, YELLOW, WHITE])
            return True
        return False


# ── Boss ────────────────────────────────────────────────────
class Boss(pygame.sprite.Sprite):
    def __init__(self, wave_num):
        super().__init__()
        self.w, self.h = 90, 90
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(centerx=SW // 2, top=-100)
        self.hp = 40 + wave_num * 20
        self.max_hp = self.hp
        self.wave = wave_num
        self.timer = 0
        self.phase = 0
        self.vel_x = 1.5
        self.alive = True
        self.hurt_flash = 0
        self.entering = True
        self.target_y = 80
        self.shoot_timer = 60
        self.projectiles = pygame.sprite.Group()
        self.defeated = False
        self.defeat_timer = 0
        self.score_val = 5000 + wave_num * 2000

    def update(self, player_pos, dt=1):
        self.timer += 1
        if self.hurt_flash > 0:
            self.hurt_flash -= 1

        if self.entering:
            self.rect.y += int(2 * dt)
            if self.rect.centery >= self.target_y:
                self.entering = False
            return

        if self.defeated:
            self.defeat_timer += 1
            self.rect.y += int(2 * dt)
            self.image.set_alpha(max(0, 255 - self.defeat_timer * 4))
            return

        if self.hp < self.max_hp * 0.3:
            self.phase = 2
        elif self.hp < self.max_hp * 0.6:
            self.phase = 1

        speed = 1.5 + self.phase * 0.5
        self.rect.x += int(self.vel_x * speed * dt)
        if self.rect.left < 20 or self.rect.right > SW - 20:
            self.vel_x *= -1
        self.rect.y = int(self.target_y + 20 * math.sin(self.timer * 0.02))

        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = max(12, 50 - self.phase * 15)
            self._shoot(player_pos)

        self.projectiles.update(dt)
        self.draw_boss()

    def _shoot(self, player_pos):
        cx, cy = self.rect.centerx, self.rect.bottom
        if self.phase == 0:
            dx = player_pos[0] - cx
            dy = player_pos[1] - cy
            dist = math.sqrt(dx * dx + dy * dy) or 1
            self.projectiles.add(EnemyBullet(cx, cy, dx / dist * 3.5, dy / dist * 3.5, ORANGE))
        elif self.phase == 1:
            for angle in [-30, -15, 0, 15, 30]:
                rad = math.radians(angle + 90)
                self.projectiles.add(EnemyBullet(cx, cy, math.cos(rad) * 3, math.sin(rad) * 3, ORANGE))
        else:
            for i in range(12):
                a = math.radians(i * 30 + self.timer * 1.5)
                self.projectiles.add(EnemyBullet(cx, cy, math.cos(a) * 3, math.sin(a) * 3, PINK))
            dx = player_pos[0] - cx
            dy = player_pos[1] - cy
            dist = math.sqrt(dx * dx + dy * dy) or 1
            self.projectiles.add(EnemyBullet(cx, cy, dx / dist * 4.5, dy / dist * 4.5, RED))
        SND_BOSS.play()

    def take_hit(self, dmg=1):
        if self.hurt_flash > 0 or self.entering or self.defeated:
            return False
        self.hp -= dmg
        self.hurt_flash = 8
        SND_HIT.play()
        particles.emit(self.rect.centerx, self.rect.centery, 10, YELLOW, 4, 18, 2, 0, [YELLOW, WHITE])
        if self.hp <= 0:
            self.defeated = True
            SND_BIG_EXPLODE.play()
            slowmo.trigger(30, 0.15)
            flash.trigger(WHITE, 100)
            cam.shake(12, 25)
            for _ in range(100):
                particles.emit(self.rect.centerx + random.randint(-45, 45),
                              self.rect.centery + random.randint(-45, 45), 1,
                              random.choice([RED, ORANGE, YELLOW, WHITE]), 7, 55, 4, 0.02)
            return True
        return False

    def draw_boss(self):
        self.image.fill((0, 0, 0, 0))
        s = self.image
        cx, cy = self.w // 2, self.h // 2
        t = self.timer
        flash = self.hurt_flash > 0

        if self.wave % 3 == 1:
            bc = WHITE if flash else (180, 40, 40)
            pygame.draw.ellipse(s, bc, (4, 10, self.w - 8, self.h - 14))
            pygame.draw.ellipse(s, (120, 25, 25), (4, 10, self.w - 8, self.h - 14), 3)
            for cx2 in [14, self.w - 14]:
                pygame.draw.rect(s, (80, 80, 80), (cx2 - 5, self.h - 14, 10, 14))
            pygame.draw.circle(s, WHITE, (cx - 14, 30), 9)
            pygame.draw.circle(s, WHITE, (cx + 14, 30), 9)
            pygame.draw.circle(s, RED, (cx - 14, 30), 6)
            pygame.draw.circle(s, RED, (cx + 14, 30), 6)
            pygame.draw.polygon(s, (100, 30, 30), [(cx - 22, 15), (cx - 30, 0), (cx - 12, 10)])
            pygame.draw.polygon(s, (100, 30, 30), [(cx + 22, 15), (cx + 30, 0), (cx + 12, 10)])
            for i in range(4):
                pygame.draw.rect(s, (100, 20, 20), (8 + i * 20, 15, 16, 8), border_radius=2)
        elif self.wave % 3 == 2:
            bc = WHITE if flash else (80, 40, 140)
            pygame.draw.ellipse(s, bc, (6, 8, self.w - 12, self.h - 10))
            pygame.draw.ellipse(s, (60, 30, 100), (6, 8, self.w - 12, self.h - 10), 3)
            for tx in [18, 40, 62]:
                ty = int(12 * math.sin(t * 0.1 + tx * 0.1))
                pygame.draw.line(s, (100, 50, 160), (tx, self.h - 8), (tx + ty, self.h + 10), 3)
            for ex, ey in [(cx - 18, 25), (cx, 20), (cx + 18, 25), (cx - 10, 40), (cx + 10, 40)]:
                pygame.draw.circle(s, PURPLE, (ex, ey), 5)
                pygame.draw.circle(s, WHITE, (ex, ey), 2)
            aura = pygame.Surface((self.w + 20, self.h + 20), pygame.SRCALPHA)
            aa = int(30 + 25 * math.sin(t * 0.05))
            pygame.draw.circle(aura, (*PURPLE, aa), (self.w // 2 + 10, self.h // 2 + 10), 50, 2)
            s.blit(aura, (-10, -10))
        else:
            bc = WHITE if flash else (40, 40, 60)
            pygame.draw.rect(s, bc, (8, 8, self.w - 16, self.h - 12), border_radius=8)
            pygame.draw.rect(s, (60, 60, 80), (8, 8, self.w - 16, self.h - 12), 3, border_radius=8)
            pygame.draw.circle(s, (40, 40, 50), (cx, cy), 20)
            pygame.draw.circle(s, RED, (cx, cy), 16)
            pulse = int(10 + 8 * math.sin(t * 0.1))
            pygame.draw.circle(s, (255, pulse, pulse), (cx, cy), 10)
            pygame.draw.circle(s, WHITE, (cx - 3, cy - 3), 3)
            for wx in [4, self.w - 14]:
                pygame.draw.rect(s, (80, 80, 100), (wx, 20, 10, 45), border_radius=3)
            if self.phase >= 1:
                for i in range(6):
                    a = math.radians(t * 2 + i * 60)
                    sx = cx + 42 * math.cos(a)
                    sy = cy + 42 * math.sin(a)
                    pygame.draw.line(s, (*CYAN, 80), (cx, cy), (int(sx), int(sy)), 1)

        bw = self.w + 10
        pygame.draw.rect(s, (40, 40, 40), (cx - bw // 2, -8, bw, 6))
        fill = int(bw * self.hp / self.max_hp)
        c = GREEN if self.hp > self.max_hp * 0.5 else YELLOW if self.hp > self.max_hp * 0.25 else RED
        pygame.draw.rect(s, c, (cx - bw // 2, -8, fill, 6))


# ── Power-ups ───────────────────────────────────────────────
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype="spread"):
        super().__init__()
        self.w, self.h = 22, 22
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.ptype = ptype
        self.vy = 1.5
        self.timer = 0
        self.draw_powerup()

    def draw_powerup(self):
        self.image.fill((0, 0, 0, 0))
        colors = {"spread": GREEN, "laser": CYAN, "missile": ORANGE, "shield": BLUE,
                  "heal": RED, "bomb": YELLOW, "score": GOLD}
        c = colors.get(self.ptype, WHITE)
        # Outer glow ring
        glow = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*c, 40), (11, 11), 11)
        self.image.blit(glow, (0, 0))
        pygame.draw.circle(self.image, c, (11, 11), 9)
        pygame.draw.circle(self.image, WHITE, (11, 11), 9, 2)
        symbols = {"spread": "S", "laser": "L", "missile": "M", "shield": "D",
                   "heal": "+", "bomb": "B", "score": "$"}
        t = small_font.render(symbols.get(self.ptype, "?"), True, BLACK)
        self.image.blit(t, (11 - t.get_width() // 2, 11 - t.get_height() // 2))

    def update(self, dt=1):
        self.timer += 1
        self.rect.y += int(self.vy * dt)
        if self.rect.top > SH:
            self.kill()
        pulse = 0.8 + 0.2 * math.sin(self.timer * 0.1)
        self.image.set_alpha(int(255 * pulse))

    def apply(self, player):
        SND_POWERUP.play()
        if self.ptype == "spread":
            player.weapon = "spread"
            player.weapon_timer = 600
            player.fire_rate = 10
        elif self.ptype == "laser":
            player.weapon = "laser"
            player.weapon_timer = 480
            player.fire_rate = 18
        elif self.ptype == "missile":
            player.weapon = "missile"
            player.weapon_timer = 600
            player.fire_rate = 14
        elif self.ptype == "shield":
            player.shield = True
            player.shield_timer = 600
        elif self.ptype == "heal":
            player.hp = min(player.max_hp, player.hp + 2)
        elif self.ptype == "bomb":
            player.bombs = min(player.max_bombs, player.bombs + 1)
        elif self.ptype == "score":
            player.score_multiplier = 2.0
            floating_texts.append(FloatingText(player.rect.centerx, player.rect.top, "2x SCORE!", GOLD, 20))
        particles.emit(self.rect.centerx, self.rect.centery, 12, CYAN, 3, 20, 2, 0, [CYAN, WHITE, GREEN])


# ── Wave definitions ────────────────────────────────────────
WAVE_DEFS = [
    [{"type": "basic", "count": 8, "delay": 30, "hp": 1, "interval": 40}],
    [{"type": "basic", "count": 12, "delay": 25, "hp": 1, "interval": 30}],
    [{"type": "basic", "count": 6, "delay": 20, "hp": 1, "interval": 35},
     {"type": "fast", "count": 4, "delay": 80, "hp": 1, "interval": 25}],
    [{"type": "basic", "count": 5, "delay": 15, "hp": 1, "interval": 30},
     {"type": "shooter", "count": 3, "delay": 60, "hp": 2, "interval": 60}],
    [{"type": "boss", "wave": 1}],
    [{"type": "tank", "count": 4, "delay": 30, "hp": 5, "interval": 50},
     {"type": "basic", "count": 8, "delay": 20, "hp": 1, "interval": 25}],
    [{"type": "spinner", "count": 5, "delay": 25, "hp": 3, "interval": 40},
     {"type": "shooter", "count": 3, "delay": 60, "hp": 2, "interval": 50}],
    [{"type": "sweeper", "count": 6, "delay": 15, "hp": 2, "interval": 25},
     {"type": "bombardier", "count": 3, "delay": 60, "hp": 4, "interval": 50}],
    [{"type": "basic", "count": 10, "delay": 12, "hp": 2, "interval": 20},
     {"type": "fast", "count": 6, "delay": 35, "hp": 1, "interval": 18},
     {"type": "shooter", "count": 4, "delay": 70, "hp": 3, "interval": 35}],
    [{"type": "tank", "count": 5, "delay": 20, "hp": 6, "interval": 40},
     {"type": "spinner", "count": 4, "delay": 45, "hp": 4, "interval": 35},
     {"type": "sweeper", "count": 4, "delay": 20, "hp": 2, "interval": 20}],
    [{"type": "boss", "wave": 2}],
    [{"type": "bombardier", "count": 5, "delay": 20, "hp": 5, "interval": 40},
     {"type": "tank", "count": 4, "delay": 40, "hp": 7, "interval": 50}],
]


def get_wave(n):
    if n <= len(WAVE_DEFS):
        return WAVE_DEFS[n - 1]
    scale = 1 + (n - len(WAVE_DEFS)) * 0.25
    types = ["basic", "fast", "tank", "shooter", "spinner", "sweeper", "bombardier"]
    wave = []
    for _ in range(2 + n // 3):
        et = random.choice(types)
        hp_base = {"basic": 1, "fast": 1, "tank": 5, "shooter": 3, "spinner": 3, "sweeper": 2, "bombardier": 4}[et]
        count = max(2, int((4 + n) * scale * 0.4))
        wave.append({"type": et, "count": count, "delay": 12, "hp": int(hp_base * scale), "interval": 22})
    if n % 5 == 0:
        wave.append({"type": "boss", "wave": min(3, 1 + n // 5)})
    return wave


# ── Drawing helpers ─────────────────────────────────────────
def draw_hud(player, wave, score, wave_timer):
    bg = pygame.Surface((SW, 55), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 140))
    screen.blit(bg, (0, 0))

    st = score_font.render(f"{score:08d}", True, YELLOW)
    screen.blit(st, (SW // 2 - st.get_width() // 2, 6))

    wt = font.render(f"WAVE {wave}", True, WHITE)
    screen.blit(wt, (10, 6))

    # HP
    hp_w = 130
    pygame.draw.rect(screen, (40, 40, 40), (10, 32, hp_w, 10), border_radius=3)
    fill = int(hp_w * player.hp / player.max_hp)
    c = GREEN if player.hp > player.max_hp * 0.5 else YELLOW if player.hp > 1 else RED
    pygame.draw.rect(screen, c, (10, 32, max(0, fill), 10), border_radius=3)
    pygame.draw.rect(screen, (80, 80, 80), (10, 32, hp_w, 10), 1, border_radius=3)
    screen.blit(small_font.render(f"HP {player.hp}/{player.max_hp}", True, WHITE), (10, 44))

    # Weapon
    if player.weapon != "normal":
        # Weapon timer bar
        if player.weapon_timer > 0:
            pw_w = 80
            pygame.draw.rect(screen, (40, 40, 40), (SW - 90, 32, pw_w, 6), border_radius=2)
            fill_w = int(pw_w * player.weapon_timer / 600)
            pygame.draw.rect(screen, GREEN, (SW - 90, 32, max(0, fill_w), 6), border_radius=2)
        screen.blit(small_font.render(f"[{player.weapon.upper()}]", True, GREEN), (SW - 90, 40))

    # Shield
    if player.shield:
        sw_w = 80
        pygame.draw.rect(screen, (40, 40, 40), (SW - 90, 52, sw_w, 6), border_radius=2)
        fill_s = int(sw_w * player.shield_timer / 600)
        pygame.draw.rect(screen, CYAN, (SW - 90, 52, max(0, fill_s), 6), border_radius=2)

    # Bombs
    bx = 10
    for i in range(player.max_bombs):
        color = YELLOW if i < player.bombs else (40, 40, 40)
        pygame.draw.circle(screen, color, (bx + 8, SH - 18), 7)
        pygame.draw.circle(screen, (200, 170, 0) if i < player.bombs else (30, 30, 30), (bx + 8, SH - 18), 7, 1)
        bx += 20

    # Combo
    if player.combo > 1:
        colors = {3: WHITE, 5: GREEN, 8: YELLOW, 12: ORANGE, 20: RED}
        c = WHITE
        for threshold in sorted(colors.keys(), reverse=True):
            if player.combo >= threshold:
                c = colors[threshold]
                break
        ct = font.render(f"{player.combo}x", True, c)
        pulse = int(220 + 35 * math.sin(pygame.time.get_ticks() * 0.01))
        ct.set_alpha(min(255, pulse))
        screen.blit(ct, (SW - 40, 8))

    # Multiplier
    if player.score_multiplier > 1.0:
        screen.blit(small_font.render(f"x{player.score_multiplier:.0f} SCORE", True, GOLD), (10, 60))


def draw_title():
    screen.fill(DARK_BG)
    t = pygame.time.get_ticks()
    starfield.draw(screen)

    # Animated logo
    for i, ch in enumerate("GALACTIC"):
        x = SW // 2 - 150 + i * 40
        y = 90 + int(5 * math.sin(t * 0.004 + i * 0.5))
        c = CYAN
        s = font.render(ch, True, c)
        screen.blit(s, (x, y))
    for i, ch in enumerate("FURY"):
        x = SW // 2 - 75 + i * 42
        y = 145 + int(5 * math.sin(t * 0.004 + i * 0.5 + 2))
        s = font.render(ch, True, YELLOW)
        screen.blit(s, (x, y))
    screen.blit(small_font.render("DX", True, ORANGE), (SW // 2 + 75, 140))

    # Ship showcase
    sx = SW // 2 + int(120 * math.sin(t * 0.002))
    sy = 240 + int(15 * math.cos(t * 0.003))
    ship = pygame.Surface((32, 36), pygame.SRCALPHA)
    pygame.draw.polygon(ship, ORANGE, [(11, 30), (16, 36), (21, 30)])
    pygame.draw.polygon(ship, (60, 60, 120), [(2, 28), (12, 10), (14, 28)])
    pygame.draw.polygon(ship, (60, 60, 120), [(30, 28), (20, 10), (18, 28)])
    pygame.draw.polygon(ship, (100, 140, 220), [(16, 2), (10, 26), (22, 26)])
    pygame.draw.polygon(ship, (140, 180, 255), [(16, 2), (12, 24), (20, 24)])
    screen.blit(ship, (sx - 16, sy))

    pulse = int(180 + 75 * math.sin(t * 0.004))
    screen.blit(font.render("CLICK - Start", True, (pulse, pulse, pulse)), (SW // 2 - 85, 310))
    screen.blit(font.render("H - Hangar (Ships)", True, (pulse, pulse, pulse)), (SW // 2 - 95, 345))

    controls = ["WASD/Arrows - Move", "SPACE - Shoot", "SHIFT/Z - Dash (i-frames)",
                "X - Bomb (screen clear)", "ESC - Pause"]
    for i, c in enumerate(controls):
        screen.blit(small_font.render(c, True, (100, 100, 130)), (SW // 2 - 120, 395 + i * 20))

    # High score
    hs = save.get("high_score", 0)
    if hs > 0:
        screen.blit(small_font.render(f"High Score: {hs}", True, GOLD), (SW // 2 - 60, SH - 30))


def draw_hangar():
    screen.fill(DARK_BG)
    starfield.draw(screen)
    screen.blit(big_font.render("HANGAR", True, CYAN), (SW // 2 - 100, 20))

    selected = save.get("selected_ship", "fighter")
    unlocked = save.get("unlocked_ships", ["fighter"])

    y = 90
    for sid, sd in SHIP_DEFS.items():
        is_unlocked = sid in unlocked
        is_selected = sid == selected
        x = 80
        w, h = 640, 75

        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        if is_selected:
            bg.fill((30, 50, 80, 200))
            pygame.draw.rect(bg, CYAN, (0, 0, w, h), 2, border_radius=6)
        elif is_unlocked:
            bg.fill((20, 25, 40, 180))
            pygame.draw.rect(bg, (80, 80, 100), (0, 0, w, h), 1, border_radius=6)
        else:
            bg.fill((15, 15, 20, 160))
            pygame.draw.rect(bg, (50, 50, 60), (0, 0, w, h), 1, border_radius=6)
        screen.blit(bg, (x, y))

        # Ship icon
        icon = pygame.Surface((24, 28), pygame.SRCALPHA)
        pygame.draw.polygon(icon, sd["color_main"], [(12, 0), (4, 20), (20, 20)])
        pygame.draw.polygon(icon, sd["color_sec"], [(12, 2), (6, 18), (18, 18)])
        screen.blit(icon, (x + 10, y + 22))

        name = font.render(sd["name"], True, WHITE if is_unlocked else GRAY)
        screen.blit(name, (x + 45, y + 8))

        desc = small_font.render(sd["desc"], True, (150, 150, 170) if is_unlocked else (70, 70, 80))
        screen.blit(desc, (x + 45, y + 32))

        stats = f"SPD:{sd['speed']}  HP:{sd['hp']}  RATE:{sd['fire_rate']}"
        screen.blit(small_font.render(stats, True, (120, 120, 140) if is_unlocked else (50, 50, 60)), (x + 45, y + 50))

        if not is_unlocked:
            lock = small_font.render(f"UNLOCK: {sd['unlock']}", True, (180, 60, 60))
            screen.blit(lock, (x + w - lock.get_width() - 15, y + 10))
        elif is_selected:
            screen.blit(small_font.render("SELECTED", True, CYAN), (x + w - 75, y + 10))

        y += 85

    screen.blit(small_font.render("UP/DOWN to select  |  ENTER to choose  |  ESC back", True, (100, 100, 130)),
               (SW // 2 - 180, SH - 30))


def draw_game_over(score, wave, kills, max_combo):
    overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    go = big_font.render("GAME OVER", True, RED)
    screen.blit(go, (SW // 2 - go.get_width() // 2, 130))

    lines = [
        (f"Score: {score}", YELLOW),
        (f"Reached Wave {wave}", WHITE),
        (f"Enemies: {kills}", GREEN),
        (f"Max Combo: {max_combo}x", ORANGE),
    ]
    for i, (text, color) in enumerate(lines):
        t = font.render(text, True, color)
        screen.blit(t, (SW // 2 - t.get_width() // 2, 200 + i * 32))

    if score > save.get("high_score", 0):
        nh = big_font.render("NEW HIGH SCORE!", True, GOLD)
        pulse = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.006))
        nh.set_alpha(pulse)
        screen.blit(nh, (SW // 2 - nh.get_width() // 2, 340))

    pulse = int(180 + 75 * math.sin(pygame.time.get_ticks() * 0.004))
    screen.blit(font.render("ENTER - Menu  |  R - Retry", True, (pulse, pulse, pulse)),
               (SW // 2 - 140, 400))


def draw_pause():
    overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    screen.blit(big_font.render("PAUSED", True, WHITE), (SW // 2 - 110, 220))
    hints = ["ESC - Resume", "R - Restart", "Q - Quit"]
    for i, h in enumerate(hints):
        screen.blit(font.render(h, True, (180, 180, 200)), (SW // 2 - 80, 290 + i * 30))


def draw_wave_announce(wave, timer):
    if timer <= 0:
        return
    alpha = min(255, timer * 8) if timer > 60 else min(255, timer * 4)
    t = big_font.render(f"WAVE {wave}", True, WHITE)
    t.set_alpha(alpha)
    screen.blit(t, (SW // 2 - t.get_width() // 2, SH // 2 - 30))
    wd = get_wave(wave)
    if any(w.get("type") == "boss" for w in wd):
        bt = font.render("BOSS INCOMING!", True, RED)
        bt.set_alpha(alpha)
        screen.blit(bt, (SW // 2 - bt.get_width() // 2, SH // 2 + 20))


def draw_game_screen(player, pb, enemies, eb, pups, boss, score, wave, at):
    screen.fill(DARK_BG)
    starfield.draw(screen)

    for b in pb:
        screen.blit(b.image, b.rect)
    for b in eb:
        screen.blit(b.image, b.rect)
    for e in enemies:
        if e.alive:
            screen.blit(e.image, e.rect)
    for pu in pups:
        screen.blit(pu.image, pu.rect)
    if boss and boss.alive:
        screen.blit(boss.image, boss.rect)
        for b in boss.projectiles:
            screen.blit(b.image, b.rect)

    if player.alive:
        if player.inv_timer > 0 and (player.inv_timer // 4) % 2 == 0:
            pass
        else:
            screen.blit(player.image, player.rect)

    particles.draw(screen)
    for ft in floating_texts:
        ft.draw(screen)

    draw_hud(player, wave, score, 0)
    draw_wave_announce(wave, at)
    flash.draw(screen)
    ach.draw(screen)


# ── Main ────────────────────────────────────────────────────
def run_game():
    state = "title"
    hangar_selected = list(SHIP_DEFS.keys()).index(save.get("selected_ship", "fighter"))

    while True:
        if state == "title":
            starfield.update()
            draw_title()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    state = "playing"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        state = "hangar"
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if state == "hangar":
            starfield.update()
            keys = pygame.key.get_pressed()
            draw_hangar()
            ship_ids = list(SHIP_DEFS.keys())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "title"
                    if event.key == pygame.K_UP:
                        hangar_selected = max(0, hangar_selected - 1)
                    if event.key == pygame.K_DOWN:
                        hangar_selected = min(len(ship_ids) - 1, hangar_selected + 1)
                    if event.key == pygame.K_RETURN:
                        sid = ship_ids[hangar_selected]
                        if sid in save.get("unlocked_ships", ["fighter"]):
                            save["selected_ship"] = sid
                            write_save(save)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if state == "playing":
            ship_id = save.get("selected_ship", "fighter")
            player = Player(ship_id)
            pb = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            eb = pygame.sprite.Group()
            pups = pygame.sprite.Group()
            boss = None

            spawn_queue = []
            spawn_timer = 0
            wave_active = True
            wave_num = 1
            wave_timer = 0
            at = 90
            paused = False
            game_over = False
            score = 0
            particles.clear()
            floating_texts.clear()

            while state == "playing":
                dt_raw = clock.tick(FPS) / (1000 / FPS)
                slowmo.update()
                dt = slowmo.get_dt()
                cam.update()
                flash.update()
                ach.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            paused = not paused
                        if paused and event.key == pygame.K_q:
                            state = "title"; break
                        if paused and event.key == pygame.K_r:
                            state = "playing"; break
                        if game_over:
                            if event.key == pygame.K_RETURN:
                                state = "title"
                            if event.key == pygame.K_r:
                                state = "playing"
                        if not paused and not game_over:
                            if event.key in (pygame.K_LSHIFT, pygame.K_z):
                                player.dash()
                            if event.key == pygame.K_x:
                                if player.use_bomb():
                                    # Destroy all enemies and bullets
                                    for e in enemies:
                                        score += player.add_kill(e.rect.centerx, e.rect.centery, e.score_val)
                                        particles.emit(e.rect.centerx, e.rect.centery, 25, YELLOW, 6, 30, 3)
                                        e.kill()
                                    eb.empty()
                                    if boss and boss.alive and not boss.entering:
                                        boss.hp -= 10
                                        boss.hurt_flash = 15
                                        particles.emit(boss.rect.centerx, boss.rect.centery, 30, WHITE, 5, 25, 3)

                if state != "playing":
                    break

                if paused:
                    draw_game_screen(player, pb, enemies, eb, pups, boss, score, wave_num, at)
                    draw_pause()
                    pygame.display.flip()
                    continue

                if game_over:
                    draw_game_screen(player, pb, enemies, eb, pups, boss, score, wave_num, at)
                    draw_game_over(score, wave_num, player.kills, player.max_combo)
                    pygame.display.flip()
                    continue

                keys = pygame.key.get_pressed()
                player.update(keys)

                # Auto-fire
                if keys[pygame.K_SPACE] or keys[pygame.K_z]:
                    for s in player.shoot():
                        if isinstance(s, Missile):
                            s.find_target(enemies)
                        pb.add(s)

                starfield.update(dt)
                particles.update(dt)
                pb.update(dt)
                eb.update(dt)
                enemies.update(player.rect.center, dt)
                pups.update(dt)
                for ft in floating_texts[:]:
                    if not ft.update():
                        floating_texts.remove(ft)

                # Score multiplier decay
                if player.score_multiplier > 1.0:
                    # Temporary multiplier fades
                    pass

                if boss and boss.alive:
                    boss.update(player.rect.center, dt)
                    for b in pygame.sprite.spritecollide(player, boss.projectiles, True):
                        player.take_damage()
                    for b in pygame.sprite.spritecollide(boss, pb, True):
                        if boss.take_hit(b.dmg if hasattr(b, 'dmg') else 1):
                            score += player.add_kill(boss.rect.centerx, boss.rect.centery, boss.score_val)
                            save["bosses_killed"] = save.get("bosses_killed", 0) + 1
                            write_save(save)
                            for _ in range(3):
                                ptype = random.choice(list(SHIP_DEFS.keys()) if random.random() < 0.3 else
                                                      ["spread", "laser", "missile", "shield", "heal", "bomb", "score"])
                                pups.add(PowerUp(boss.rect.centerx + random.randint(-35, 35),
                                               boss.rect.centery + random.randint(-25, 25), ptype))

                # Bullet vs enemies
                hit_en = pygame.sprite.groupcollide(enemies, pb, False, True)
                for enemy, bullets in hit_en.items():
                    for b in bullets:
                        dmg = b.dmg if hasattr(b, 'dmg') else 1
                        if enemy.take_hit(dmg):
                            score += player.add_kill(enemy.rect.centerx, enemy.rect.centery, enemy.score_val)
                            save["total_kills"] = save.get("total_kills", 0) + 1
                            if random.random() < 0.14:
                                ptype = random.choice(["spread", "laser", "missile", "shield", "heal", "bomb", "score"])
                                pups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery, ptype))
                            cam.shake(2, 5)

                # Enemy bullets vs player
                for b in pygame.sprite.spritecollide(player, eb, True):
                    player.take_damage()

                # Enemy body collision
                for e in pygame.sprite.spritecollide(player, enemies, False):
                    if e.alive:
                        player.take_damage()
                        e.take_hit(1)

                # Player vs powerups
                for pu in pygame.sprite.spritecollide(player, pups, True):
                    pu.apply(player)

                # Off-screen enemies
                for e in list(enemies):
                    if e.rect.top > SH + 50:
                        e.kill()

                # Enemy shooting
                for e in enemies:
                    if e.alive and random.random() < 0.015 * (1 + e.etype in ("shooter", "spinner", "bombardier")):
                        eb.add(e.shoot(player.rect.center))

                # ── Wave spawning ──
                if wave_active:
                    wd = get_wave(wave_num)
                    if not spawn_queue:
                        for entry in wd:
                            if entry["type"] == "boss":
                                if not boss or not boss.alive:
                                    boss = Boss(entry["wave"])
                            else:
                                for i in range(entry["count"]):
                                    spawn_queue.append({
                                        "type": entry["type"], "hp": entry["hp"],
                                        "delay": entry.get("delay", 20) + i * entry.get("interval", 30)
                                    })
                        spawn_queue.sort(key=lambda x: x["delay"])
                        if spawn_queue:
                            mn = spawn_queue[0]["delay"]
                            for s in spawn_queue:
                                s["delay"] -= mn

                    if spawn_queue:
                        spawn_timer += dt
                        while spawn_queue and spawn_timer >= spawn_queue[0]["delay"]:
                            e = spawn_queue.pop(0)
                            enemies.add(Enemy(random.randint(40, SW - 40), -30, e["type"], e["hp"]))
                    else:
                        all_dead = all(not e.alive for e in enemies)
                        boss_done = (not boss) or (not boss.alive and not boss.entering) or (boss and boss.defeated and boss.defeat_timer > 60)
                        if all_dead and boss_done:
                            wave_active = False
                            wave_timer = 0
                            SND_WAVE.play()
                else:
                    if wave_timer > 120:
                        wave_num += 1
                        wave_active = True
                        spawn_queue = []
                        spawn_timer = 0
                        boss = None
                        at = 90
                        SND_WAVE.play()
                        score += wave_num * 500

                if at > 0:
                    at -= 1

                if not player.alive:
                    game_over = True
                    # Update save
                    save["total_games"] = save.get("total_games", 0) + 1
                    if score > save.get("high_score", 0):
                        save["high_score"] = score
                    if wave_num > save.get("max_wave", 0):
                        save["max_wave"] = wave_num
                    if save.get("total_kills", 0) >= 500 and "tank" not in save.get("unlocked_ships", []):
                        save.setdefault("unlocked_ships", []).append("tank")
                    if wave_num >= 5 and "speeder" not in save.get("unlocked_ships", []):
                        save.setdefault("unlocked_ships", []).append("speeder")
                    if player.dash_count >= 100 and "phantom" not in save.get("unlocked_ships", []):
                        save.setdefault("unlocked_ships", []).append("phantom")
                    if wave_num >= 10 and "phoenix" not in save.get("unlocked_ships", []):
                        save.setdefault("unlocked_ships", []).append("phoenix")
                    write_save(save)

                # Achievements
                if wave_num == 1 and "First Steps" not in save.get("achievements", []):
                    ach.show("First Steps", "Start your first game")
                if score >= 10000 and "10K Club" not in save.get("achievements", []):
                    ach.show("10K Club", "Score 10,000 points")
                if player.max_combo >= 10 and "Combo King" not in save.get("achievements", []):
                    ach.show("Combo King", "Reach a 10x combo")
                if player.kills >= 100 and "Century" not in save.get("achievements", []):
                    ach.show("Century", "Kill 100 enemies in one game")

                draw_game_screen(player, pb, enemies, eb, pups, boss, score, wave_num, at)
                pygame.display.flip()


if __name__ == "__main__":
    run_game()
