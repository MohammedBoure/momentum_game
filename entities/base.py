# -*- coding: utf-8 -*-
"""
Entity Base Classes for MOMENTUM: Chrono Blade.
Defines foundational physics, geometry, collision resolvers, and lifecycle management.
"""
import math
import pygame

def clamp_val(val, min_v, max_v):
    """Clamps a numeric value between min_v and max_v."""
    return min_v if val < min_v else max_v if val > max_v else val

def circle_rect_collision(rect: pygame.Rect, cx: float, cy: float, radius: float) -> bool:
    """Checks if a circle intersects with an axis-aligned rectangle."""
    closest_x = clamp_val(cx, rect.left, rect.right)
    closest_y = clamp_val(cy, rect.top, rect.bottom)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) < (radius * radius)

def angle_difference(angle1: float, angle2: float) -> float:
    """Calculates the absolute shortest angular distance between two radians."""
    return abs((angle1 - angle2 + math.pi) % (2.0 * math.pi) - math.pi)

class Entity:
    """Base game entity with position, velocity, radius, and collision physics."""
    def __init__(self, x: float, y: float, radius: float = 12.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = float(radius)
        self.alive = True

    @property
    def pos(self) -> tuple:
        return (self.x, self.y)

    def move_and_collide(self, dx: float, dy: float, walls: list):
        """
        Moves entity along dx and dy while smoothly sliding along colliding walls.
        """
        # Horizontal pass
        self.x += dx
        for w in walls:
            if circle_rect_collision(w, self.x, self.y, self.radius):
                if dx > 0:
                    self.x = w.left - self.radius
                elif dx < 0:
                    self.x = w.right + self.radius

        # Vertical pass
        self.y += dy
        for w in walls:
            if circle_rect_collision(w, self.x, self.y, self.radius):
                if dy > 0:
                    self.y = w.top - self.radius
                elif dy < 0:
                    self.y = w.bottom + self.radius

    def distance_to(self, other) -> float:
        """Returns Euclidean distance to another entity or coordinate tuple."""
        ox, oy = (other.x, other.y) if hasattr(other, 'x') else other
        return math.hypot(self.x - ox, self.y - oy)

    def angle_to(self, other) -> float:
        """Returns angle (in radians) towards another entity or coordinate tuple."""
        ox, oy = (other.x, other.y) if hasattr(other, 'x') else other
        return math.atan2(oy - self.y, ox - self.x)
