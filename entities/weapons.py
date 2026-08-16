# -*- coding: utf-8 -*-
"""
Weapons and Projectile Systems for MOMENTUM: Chrono Blade.
Includes bullets with wall ricochets, shurikens, temporal EMP grenades, and blade slash arc calculations.
"""
import math
import random
import pygame
from core.constants import (
    COLOR_WHITE, COLOR_RED, COLOR_CYAN, COLOR_HOT, COLOR_PINK, COLOR_GRAY,
    SCREEN_WIDTH, SCREEN_HEIGHT
)
from entities.base import circle_rect_collision, angle_difference

class Bullet:
    """A kinetic projectile supporting wall ricochets, bullet deflection, and glowing motion trails."""
    def __init__(self, x: float, y: float, angle: float, speed: float,
                 friendly: bool = True, deflected: bool = False,
                 bounces_left: int = 0, piercing: bool = False, damage: int = 1,
                 color: tuple = None):
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.friendly = friendly
        self.deflected = deflected
        self.bounces_left = bounces_left
        self.piercing = piercing
        self.damage = damage
        self.radius = 4.0
        self.dead = False
        self.trail = []
        self.max_trail = 8
        self.color = color or (COLOR_WHITE if friendly else COLOR_RED)

    @property
    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)

    def update(self, dt: float, walls: list, particle_manager=None, sound_lib=None, time_acc=0.0) -> bool:
        """
        Steps projectile forward with sub-stepping for precision wall and ricochet detection.
        Returns False if bullet dies.
        """
        if self.dead:
            return False

        sp = self.speed
        if sp <= 0.1:
            self.dead = True
            return False

        # Sub-stepping to prevent tunneling through thin walls
        step_dist = 6.0
        total_move = sp * dt
        steps = max(1, int(math.ceil(total_move / step_dist)))
        step_dt = dt / steps

        for _ in range(steps):
            next_x = self.x + self.vx * step_dt
            next_y = self.y + self.vy * step_dt

            # Wall Collision Check
            hit_wall = None
            for w in walls:
                if circle_rect_collision(w, next_x, next_y, self.radius):
                    hit_wall = w
                    break

            if hit_wall:
                if self.bounces_left > 0:
                    self.bounces_left -= 1
                    # Determine collision normal
                    dx_left = abs(next_x - hit_wall.left)
                    dx_right = abs(next_x - hit_wall.right)
                    dy_top = abs(next_y - hit_wall.top)
                    dy_bottom = abs(next_y - hit_wall.bottom)
                    min_dist = min(dx_left, dx_right, dy_top, dy_bottom)

                    if min_dist in (dx_left, dx_right):
                        self.vx = -self.vx
                    else:
                        self.vy = -self.vy

                    # Ricochet sparks & sound
                    if particle_manager:
                        particle_manager.add_sparks(next_x, next_y, amount=5, color=self.color)
                    if sound_lib:
                        sound_lib.play('ricochet', time_acc=time_acc, throttle=0.05)
                else:
                    self.dead = True
                    if particle_manager:
                        particle_manager.add_sparks(next_x, next_y, amount=7, color=COLOR_GRAY)
                    break
            else:
                self.x = next_x
                self.y = next_y

        # Update motion trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        # Boundary checks
        if (self.x < -80 or self.x > SCREEN_WIDTH + 80 or
            self.y < -80 or self.y > SCREEN_HEIGHT + 80):
            self.dead = True

        return not self.dead

    def draw(self, surf: pygame.Surface, camera=None):
        """Draws glowing motion trail and bullet head."""
        if self.dead:
            return

        # Motion trail
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                progress = i / len(self.trail)
                trail_color = tuple(int(v * progress * 0.75) for v in self.color)
                p1 = camera.world_to_screen(*self.trail[i]) if camera else self.trail[i]
                p2 = camera.world_to_screen(*self.trail[i + 1]) if camera else self.trail[i + 1]
                pygame.draw.line(surf, trail_color, p1, p2, max(1, int(3 * progress)))

        # Head core
        head_pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        pygame.draw.circle(surf, self.color, head_pos, int(self.radius))
        pygame.draw.circle(surf, COLOR_WHITE, head_pos, 2)

class Shuriken:
    """High-velocity spinning throwing star that pierces and pins enemies."""
    def __init__(self, x: float, y: float, angle: float, speed: float = 920.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.angle = angle
        self.spin = 0.0
        self.radius = 6.0
        self.dead = False
        self.friendly = True
        self.damage = 2

    def update(self, dt: float, walls: list, particle_manager=None) -> bool:
        self.spin += dt * 35.0
        self.x += self.vx * dt
        self.y += self.vy * dt

        for w in walls:
            if circle_rect_collision(w, self.x, self.y, self.radius):
                self.dead = True
                if particle_manager:
                    particle_manager.add_sparks(self.x, self.y, amount=8, color=COLOR_CYAN)
                break

        if (self.x < -50 or self.x > SCREEN_WIDTH + 50 or
            self.y < -50 or self.y > SCREEN_HEIGHT + 50):
            self.dead = True

        return not self.dead

    def draw(self, surf: pygame.Surface, camera=None):
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        r = int(self.radius * (camera.zoom if camera else 1.0))
        pts = []
        for i in range(4):
            a = self.spin + i * (math.pi / 2.0)
            pts.append((pos[0] + math.cos(a) * r * 1.5, pos[1] + math.sin(a) * r * 1.5))
            a_mid = a + (math.pi / 4.0)
            pts.append((pos[0] + math.cos(a_mid) * r * 0.4, pos[1] + math.sin(a_mid) * r * 0.4))
        pygame.draw.polygon(surf, COLOR_CYAN, pts)
        pygame.draw.circle(surf, COLOR_WHITE, pos, 2)

class TemporalGrenade:
    """Chrono Grenade that creates an expanding stasis distortion zone upon detonation."""
    def __init__(self, x: float, y: float, angle: float, speed: float = 480.0, fuse: float = 1.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.fuse = float(fuse)
        self.radius = 5.0
        self.dead = False
        self.detonated = False
        self.field_radius = 0.0
        self.max_field_radius = 160.0
        self.field_life = 0.0
        self.max_field_life = 2.5

    def update(self, dt: float, walls: list, particle_manager=None, sound_lib=None, time_acc=0.0):
        if not self.detonated:
            self.fuse -= dt
            self.vx *= (0.92 ** (dt * 60.0))
            self.vy *= (0.92 ** (dt * 60.0))
            self.x += self.vx * dt
            self.y += self.vy * dt

            for w in walls:
                if circle_rect_collision(w, self.x, self.y, self.radius):
                    self.vx = -self.vx * 0.6
                    self.vy = -self.vy * 0.6

            if self.fuse <= 0:
                self.detonated = True
                self.field_life = self.max_field_life
                if particle_manager:
                    particle_manager.add_shockwave(self.x, self.y, radius=self.max_field_radius, duration=0.4, color=COLOR_CYAN, width=3)
                if sound_lib:
                    sound_lib.play('explosion', time_acc=time_acc, throttle=0.0)
        else:
            self.field_life -= dt
            self.field_radius = min(self.max_field_radius, self.field_radius + dt * 450.0)
            if self.field_life <= 0:
                self.dead = True

        return not self.dead

    def draw(self, surf: pygame.Surface, camera=None):
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        if not self.detonated:
            pygame.draw.circle(surf, COLOR_CYAN, pos, int(self.radius))
            pygame.draw.circle(surf, COLOR_WHITE, pos, 2)
        else:
            # Draw translucent temporal stasis bubble
            alpha = int(90 * (self.field_life / self.max_field_life))
            r = int(self.field_radius * (camera.zoom if camera else 1.0))
            if r > 0:
                bubble = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(bubble, (40, 220, 240, alpha), (r, r), r)
                pygame.draw.circle(bubble, (240, 240, 255, alpha + 30), (r, r), r, 2)
                surf.blit(bubble, (pos[0] - r, pos[1] - r))
