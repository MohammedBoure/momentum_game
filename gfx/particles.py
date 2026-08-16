# -*- coding: utf-8 -*-
"""
Particle and Visual FX System for MOMENTUM: Chrono Blade.
Handles blood splatters, persistent floor stains, sparks, smoke, floating combat text, and shockwaves.
"""
import math
import random
import pygame
from core.constants import (
    COLOR_WHITE, COLOR_RED, COLOR_HOT, COLOR_PINK, COLOR_BLOOD,
    COLOR_CYAN, COLOR_GOLD, COLOR_GRAY, COLOR_DIM
)

class Particle:
    """A single physics particle with velocity, decay, and color lerping."""
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size', 'friction', 'gravity_y')
    def __init__(self, x, y, vx, vy, life, color, size=3.0, friction=0.88, gravity_y=0.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.life = float(life)
        self.max_life = float(life)
        self.color = color
        self.size = float(size)
        self.friction = float(friction)
        self.gravity_y = float(gravity_y)

    def update(self, dt: float) -> bool:
        """Updates particle physics. Returns False when dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity_y * dt
        damping = self.friction ** (dt * 60.0)
        self.vx *= damping
        self.vy *= damping
        self.life -= dt
        return self.life > 0

    def draw(self, surf: pygame.Surface, camera=None):
        """Renders the particle onto surface."""
        if self.life <= 0:
            return
        ratio = max(0.0, self.life / self.max_life)
        cur_size = max(1, int(self.size * ratio))
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        pygame.draw.circle(surf, self.color, pos, cur_size)

class BloodStain:
    """Persistent splatter mark on the ground."""
    __slots__ = ('x', 'y', 'radius', 'alpha', 'color')
    def __init__(self, x, y, radius, alpha=0.75):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.alpha = float(alpha)
        # Mix blood shade
        shade = random.uniform(0.7, 1.0)
        self.color = (int(COLOR_BLOOD[0] * shade), int(COLOR_BLOOD[1] * shade), int(COLOR_BLOOD[2] * shade))

    def draw(self, surf: pygame.Surface, camera=None):
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        r = int(self.radius * (camera.zoom if camera else 1.0))
        if r > 0:
            pygame.draw.circle(surf, self.color, pos, r)

class FloaterText:
    """Animated floating combat notifications (e.g. 'DEFLECT!', '+4 AMMO', 'x3 COMBO')."""
    def __init__(self, x, y, text, color=COLOR_WHITE, size=20, duration=0.85, vy=-40.0):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.size = size
        self.life = float(duration)
        self.max_life = float(duration)
        self.vy = float(vy)

    def update(self, dt: float) -> bool:
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf: pygame.Surface, font_cache: dict, camera=None):
        if self.life <= 0:
            return
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        f = font_cache.get(self.size)
        if not f:
            f = pygame.font.SysFont("bahnschrift,impact,segoeui,arial", self.size, bold=True)
            font_cache[self.size] = f
        
        alpha = int(255 * min(1.0, max(0.0, self.life / (self.max_life * 0.4))))
        rendered = f.render(self.text, True, self.color)
        rendered.set_alpha(alpha)
        rect = rendered.get_rect(center=pos)
        surf.blit(rendered, rect)

class ShockwaveRing:
    """Expanding neon ring for explosions, parries, and heavy slashes."""
    def __init__(self, x, y, max_radius=80, duration=0.25, color=COLOR_WHITE, width=3):
        self.x = float(x)
        self.y = float(y)
        self.max_radius = float(max_radius)
        self.life = float(duration)
        self.max_life = float(duration)
        self.color = color
        self.width = width

    def update(self, dt: float) -> bool:
        self.life -= dt
        return self.life > 0

    def draw(self, surf: pygame.Surface, camera=None):
        if self.life <= 0:
            return
        progress = 1.0 - (self.life / self.max_life)
        cur_r = int(self.max_radius * progress)
        if cur_r <= 1:
            return
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        pygame.draw.circle(surf, self.color, pos, cur_r, self.width)

class ParticleManager:
    """Manages creation, updates, and rendering for all particle FX and floor stains."""
    def __init__(self):
        self.particles = []
        self.blood_stains = []
        self.floaters = []
        self.shockwaves = []
        self.max_blood_stains = 400

    def add_blood_burst(self, x, y, amount=20, power=1.0):
        """Emits directional blood spray and creates floor splatter."""
        for _ in range(int(amount * power)):
            angle = random.uniform(0, 2.0 * math.pi)
            speed = random.uniform(60.0, 380.0) * power
            color = COLOR_BLOOD if random.random() < 0.65 else COLOR_RED
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(0.3, 0.8),
                color,
                size=random.uniform(2.5, 4.5),
                friction=0.86
            ))

        for _ in range(random.randint(3, 6)):
            self.blood_stains.append(BloodStain(
                x + random.uniform(-16, 16),
                y + random.uniform(-16, 16),
                random.uniform(3.0, 8.5)
            ))

        if len(self.blood_stains) > self.max_blood_stains:
            self.blood_stains = self.blood_stains[-self.max_blood_stains:]

    def add_sparks(self, x, y, amount=8, color=COLOR_WHITE, speed_range=(80, 260)):
        """Emits fiery sparks from bullet wall impacts or metal clangs."""
        for _ in range(amount):
            angle = random.uniform(0, 2.0 * math.pi)
            speed = random.uniform(*speed_range)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(0.12, 0.28),
                color,
                size=random.uniform(1.5, 2.5),
                friction=0.90
            ))

    def add_explosion_fx(self, x, y, radius=100):
        """Creates high-impact explosive shockwaves, fireballs, and smoke."""
        self.shockwaves.append(ShockwaveRing(x, y, max_radius=radius, duration=0.3, color=COLOR_HOT, width=4))
        self.shockwaves.append(ShockwaveRing(x, y, max_radius=radius * 0.7, duration=0.2, color=COLOR_WHITE, width=2))
        
        # Fire and smoke particles
        for _ in range(35):
            angle = random.uniform(0, 2.0 * math.pi)
            speed = random.uniform(100.0, 420.0)
            col = random.choice([COLOR_WHITE, COLOR_HOT, COLOR_RED, COLOR_GRAY])
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(0.2, 0.55),
                col,
                size=random.uniform(3.0, 6.0),
                friction=0.84
            ))

    def add_floater(self, x, y, text, color=COLOR_WHITE, size=20, duration=0.85):
        """Adds a rising notification floater."""
        self.floaters.append(FloaterText(x, y, text, color, size, duration))

    def add_shockwave(self, x, y, radius=70, duration=0.2, color=COLOR_WHITE, width=3):
        """Adds a shockwave ring."""
        self.shockwaves.append(ShockwaveRing(x, y, radius, duration, color, width))

    def update(self, dt: float):
        """Updates all active particles and animations."""
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floaters = [f for f in self.floaters if f.update(dt)]
        self.shockwaves = [s for s in self.shockwaves if s.update(dt)]

    def draw_floor_stains(self, surf: pygame.Surface, camera=None):
        """Draws blood stains below entities."""
        for stain in self.blood_stains:
            stain.draw(surf, camera)

    def draw_particles(self, surf: pygame.Surface, camera=None):
        """Draws physics particles and shockwaves."""
        for shock in self.shockwaves:
            shock.draw(surf, camera)
        for p in self.particles:
            p.draw(surf, camera)

    def draw_floaters(self, surf: pygame.Surface, font_cache: dict, camera=None):
        """Draws floating text badges."""
        for fl in self.floaters:
            fl.draw(surf, font_cache, camera)

    def clear(self):
        """Resets all particles for new level."""
        self.particles.clear()
        self.blood_stains.clear()
        self.floaters.clear()
        self.shockwaves.clear()
