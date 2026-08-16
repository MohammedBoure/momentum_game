# -*- coding: utf-8 -*-
"""
Dynamic Camera and Viewport Management.
Handles smooth player tracking, cursor lookahead, trauma-based screenshake, and coordinate transformations.
"""
import math
import random
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    """
    Manages viewport position, zoom, screen shake, and coordinate mappings.
    """
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.x = width / 2.0
        self.y = height / 2.0
        self.target_x = self.x
        self.target_y = self.y
        self.zoom = 1.0
        self.target_zoom = 1.0
        
        # Shake / Trauma system
        self.trauma = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.angle_offset = 0.0

    def add_shake(self, amount: float):
        """Adds trauma for screen shake, capped at 1.0."""
        self.trauma = min(1.0, self.trauma + amount * 0.15)

    def add_directional_kick(self, angle: float, force: float):
        """Applies a directional screen kick impulse."""
        self.shake_offset_x += math.cos(angle) * force
        self.shake_offset_y += math.sin(angle) * force

    def update(self, dt: float, target_pos: tuple, mouse_pos: tuple, lookahead_factor: float = 0.22):
        """
        Smoothly tracks the target with a slight bias toward mouse cursor.
        """
        # Mouse lookahead offset
        if mouse_pos and target_pos:
            mdx = mouse_pos[0] - (self.width / 2)
            mdy = mouse_pos[1] - (self.height / 2)
            self.target_x = target_pos[0] + mdx * lookahead_factor
            self.target_y = target_pos[1] + mdy * lookahead_factor
        elif target_pos:
            self.target_x, self.target_y = target_pos

        # Smooth position lerping
        lerp_speed = min(1.0, dt * 10.0)
        self.x += (self.target_x - self.x) * lerp_speed
        self.y += (self.target_y - self.y) * lerp_speed

        # Smooth zoom lerping
        self.zoom += (self.target_zoom - self.zoom) * min(1.0, dt * 8.0)

        # Shake / Trauma decay
        if self.trauma > 0:
            self.trauma = max(0.0, self.trauma - dt * 1.8)
            shake_mag = (self.trauma ** 2) * 16.0
            self.shake_offset_x = random.uniform(-1.0, 1.0) * shake_mag
            self.shake_offset_y = random.uniform(-1.0, 1.0) * shake_mag
        else:
            self.shake_offset_x *= max(0.0, 1.0 - dt * 20.0)
            self.shake_offset_y *= max(0.0, 1.0 - dt * 20.0)

    def world_to_screen(self, wx: float, wy: float) -> tuple:
        """Converts world coordinates to screen pixel coordinates."""
        sx = (wx - self.x) * self.zoom + (self.width / 2) + self.shake_offset_x
        sy = (wy - self.y) * self.zoom + (self.height / 2) + self.shake_offset_y
        return (int(sx), int(sy))

    def screen_to_world(self, sx: float, sy: float) -> tuple:
        """Converts screen pixel coordinates to world coordinates."""
        wx = (sx - (self.width / 2) - self.shake_offset_x) / self.zoom + self.x
        wy = (sy - (self.height / 2) - self.shake_offset_y) / self.zoom + self.y
        return (wx, wy)

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """Transforms a Pygame Rect from world space to screen space."""
        topleft = self.world_to_screen(rect.left, rect.top)
        w = int(rect.width * self.zoom)
        h = int(rect.height * self.zoom)
        return pygame.Rect(topleft[0], topleft[1], w, h)
