# -*- coding: utf-8 -*-
"""
Interactive Environment and Object Systems for MOMENTUM: Chrono Blade.
Includes walls, raycasting line-of-sight checks, destructible crates, explosive barrels,
breakable glass windows, hackable security turrets, and pickup items.
"""
import math
import random
import pygame
from core.constants import (
    COLOR_WALL, COLOR_WALL_EDGE, COLOR_WHITE, COLOR_RED, COLOR_CYAN,
    COLOR_HOT, COLOR_GOLD, COLOR_GRAY, COLOR_DIM
)
from entities.base import circle_rect_collision

def line_of_sight(walls: list, x1: float, y1: float, x2: float, y2: float) -> bool:
    """Checks if there is an unobstructed line of sight between two coordinates."""
    for w in walls:
        if isinstance(w, Wall) and not w.blocks_los:
            continue
        rect = w.rect if isinstance(w, Wall) else w
        if rect.clipline(x1, y1, x2, y2):
            return False
    return True

def raycast_walls(walls: list, x: float, y: float, angle: float, max_dist: float = 1600.0) -> float:
    """Finds distance to the closest intersecting wall along a given ray angle."""
    x2 = x + math.cos(angle) * max_dist
    y2 = y + math.sin(angle) * max_dist
    closest = max_dist

    for w in walls:
        rect = w.rect if isinstance(w, Wall) else w
        clip = rect.clipline(x, y, x2, y2)
        if clip:
            hit_x, hit_y = clip[0]
            dist = math.hypot(hit_x - x, hit_y - y)
            if dist < closest:
                closest = dist

    return closest

class Wall:
    """A solid or semi-solid obstacle in the world."""
    def __init__(self, x: int, y: int, w: int, h: int, blocks_los: bool = True):
        self.rect = pygame.Rect(x, y, w, h)
        self.blocks_los = blocks_los

    # Forward Rect attributes for compatibility
    @property
    def left(self): return self.rect.left
    @property
    def right(self): return self.rect.right
    @property
    def top(self): return self.rect.top
    @property
    def bottom(self): return self.rect.bottom
    @property
    def center(self): return self.rect.center

    def clipline(self, *args):
        return self.rect.clipline(*args)

    def draw(self, surf: pygame.Surface, camera=None):
        r = camera.apply_rect(self.rect) if camera else self.rect
        pygame.draw.rect(surf, COLOR_WALL, r)
        pygame.draw.rect(surf, COLOR_WALL_EDGE, r, 2)

class DestructibleCrate:
    """A destructible container that yields ammo or chrono cells upon destruction."""
    def __init__(self, x: float, y: float, w: int = 32, h: int = 32, drops: str = 'ammo'):
        self.rect = pygame.Rect(int(x - w // 2), int(y - h // 2), w, h)
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.hp = 1
        self.drops = drops
        self.alive = True

    def take_damage(self, amount: int = 1) -> bool:
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
        return not self.alive

    def draw(self, surf: pygame.Surface, camera=None):
        if not self.alive: return
        r = camera.apply_rect(self.rect) if camera else self.rect
        pygame.draw.rect(surf, (38, 38, 48), r)
        pygame.draw.rect(surf, (95, 95, 115), r, 2)
        # Crate cross-bracing
        pygame.draw.line(surf, (70, 70, 90), r.topleft, r.bottomright, 1)
        pygame.draw.line(surf, (70, 70, 90), r.bottomleft, r.topright, 1)

class ExplosiveBarrel:
    """A volatile red fuel barrel that detonates into a lethal area-of-effect fire blast."""
    def __init__(self, x: float, y: float, radius: float = 14.0):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.hp = 1
        self.alive = True
        self.blast_radius = 150.0

    def take_damage(self, amount: int = 1) -> bool:
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
        return not self.alive

    def draw(self, surf: pygame.Surface, camera=None):
        if not self.alive: return
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        r = int(self.radius * (camera.zoom if camera else 1.0))
        pygame.draw.circle(surf, (80, 15, 20), pos, r)
        pygame.draw.circle(surf, COLOR_RED, pos, r, 2)
        # Hazard stripe
        pygame.draw.circle(surf, COLOR_HOT, pos, max(2, r // 2), 2)

class GlassWindow:
    """A breakable glass partition that allows line-of-sight until shattered by bullets."""
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        self.alive = True
        self.blocks_los = False

    @property
    def left(self): return self.rect.left
    @property
    def right(self): return self.rect.right
    @property
    def top(self): return self.rect.top
    @property
    def bottom(self): return self.rect.bottom

    def clipline(self, *args):
        return self.rect.clipline(*args) if self.alive else ()

    def shatter(self):
        self.alive = False

    def draw(self, surf: pygame.Surface, camera=None):
        if not self.alive: return
        r = camera.apply_rect(self.rect) if camera else self.rect
        glass_s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        glass_s.fill((40, 220, 240, 45))
        pygame.draw.rect(glass_s, (180, 240, 255, 120), glass_s.get_rect(), 1)
        surf.blit(glass_s, r.topleft)

class SecurityTurret:
    """An automated gun turret that can be hacked to fire upon enemies."""
    def __init__(self, x: float, y: float, angle: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.radius = 16.0
        self.hacked = False
        self.alive = True
        self.fire_cd = 0.0
        self.fire_rate = 0.35
        self.range = 500.0

    def hack(self):
        """Switches turret allegiance to player friendly."""
        self.hacked = True

    def draw(self, surf: pygame.Surface, camera=None):
        if not self.alive: return
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        r = int(self.radius * (camera.zoom if camera else 1.0))
        col = COLOR_CYAN if self.hacked else COLOR_RED
        
        # Base
        pygame.draw.circle(surf, (28, 28, 36), pos, r)
        pygame.draw.circle(surf, col, pos, r, 2)
        
        # Barrel
        bx = pos[0] + math.cos(self.angle) * (r + 8)
        by = pos[1] + math.sin(self.angle) * (r + 8)
        pygame.draw.line(surf, col, pos, (bx, by), 3)

class AmmoPack:
    """Floating ammo pickup box."""
    def __init__(self, x: float, y: float, count: int = 4):
        self.x = float(x)
        self.y = float(y)
        self.count = count
        self.anim_t = random.uniform(0.0, 6.0)

    def draw(self, surf: pygame.Surface, dt_anim: float, camera=None):
        self.anim_t += dt_anim * 3.0
        bob = math.sin(self.anim_t) * 3.5
        pos = camera.world_to_screen(self.x, self.y + bob) if camera else (int(self.x), int(self.y + bob))
        
        r = pygame.Rect(pos[0] - 10, pos[1] - 8, 20, 16)
        pygame.draw.rect(surf, (20, 20, 28), r)
        pygame.draw.rect(surf, COLOR_WHITE, r, 2)
        pygame.draw.line(surf, COLOR_RED, (r.left + 4, r.centery), (r.right - 4, r.centery), 2)

class ChronoCell:
    """Floating energy cell that restores Chrono Focus battery."""
    def __init__(self, x: float, y: float, amount: float = 35.0):
        self.x = float(x)
        self.y = float(y)
        self.amount = amount
        self.anim_t = random.uniform(0.0, 6.0)

    def draw(self, surf: pygame.Surface, dt_anim: float, camera=None):
        self.anim_t += dt_anim * 4.0
        bob = math.sin(self.anim_t) * 4.0
        pos = camera.world_to_screen(self.x, self.y + bob) if camera else (int(self.x), int(self.y + bob))
        
        pts = [
            (pos[0], pos[1] - 10),
            (pos[0] + 8, pos[1]),
            (pos[0], pos[1] + 10),
            (pos[0] - 8, pos[1])
        ]
        pygame.draw.polygon(surf, (20, 30, 45), pts)
        pygame.draw.polygon(surf, COLOR_CYAN, pts, 2)
        pygame.draw.circle(surf, COLOR_WHITE, pos, 3)
