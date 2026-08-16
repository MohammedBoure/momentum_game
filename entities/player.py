# -*- coding: utf-8 -*-
"""
Player Entity and Combat Controller for MOMENTUM: Chrono Blade.
Implements kinetic movement, Katana slashes, bullet deflection, charged heavy blade surges,
weapon switching, Chrono Dash with afterimages, and temporal focus overdrive.
"""
import math
import pygame
from core.constants import (
    PLAYER_RADIUS, PLAYER_BASE_SPEED, PLAYER_DASH_SPEED, PLAYER_DASH_DURATION,
    PLAYER_DASH_COOLDOWN, PLAYER_MAX_FOCUS, PLAYER_FOCUS_DRAIN, PLAYER_FOCUS_RECHARGE,
    KATANA_COOLDOWN, KATANA_SLASH_DURATION, KATANA_RANGE, KATANA_ARC_ANGLE,
    WEAPON_PISTOL, WEAPON_SHOTGUN, WEAPON_RAILGUN, WEAPON_SHURIKEN,
    WEAPON_CONFIGS, COLOR_WHITE, COLOR_RED, COLOR_CYAN, COLOR_GRAY, COLOR_BG
)
from entities.base import Entity, angle_difference
from entities.weapons import Bullet, Shuriken, TemporalGrenade

class Player(Entity):
    """
    The protagonist possessing the Chrono Blade and temporal manipulation abilities.
    """
    def __init__(self, x: float, y: float):
        super().__init__(x, y, radius=PLAYER_RADIUS)
        self.aim_angle = 0.0
        self.ammo = 10
        self.max_ammo = 24
        self.focus = PLAYER_MAX_FOCUS
        self.max_focus = PLAYER_MAX_FOCUS
        self.focus_active = False

        # Weapon state
        self.weapons = [WEAPON_PISTOL, WEAPON_SHOTGUN, WEAPON_RAILGUN, WEAPON_SHURIKEN]
        self.current_weapon_idx = 0
        self.weapon_cooldown = 0.0

        # Katana & Melee state
        self.slash_cooldown = 0.0
        self.slash_timer = 0.0
        self.slash_direction = 0.0
        self.charging_heavy = False
        self.heavy_charge_timer = 0.0
        self.shuriken_cooldown = 0.0
        self.grenade_cooldown = 0.0

        # Dash state
        self.dash_cooldown = 0.0
        self.dash_timer = 0.0
        self.dash_dir_x = 0.0
        self.dash_dir_y = 0.0
        self.is_invulnerable = False

        # Visual afterimages
        self.afterimages = []  # [(x, y, alpha, angle), ...]

    @property
    def current_weapon(self) -> str:
        return self.weapons[self.current_weapon_idx]

    @property
    def weapon_config(self) -> dict:
        return WEAPON_CONFIGS.get(self.current_weapon, WEAPON_CONFIGS[WEAPON_PISTOL])

    def switch_weapon(self, delta: int = 1):
        """Cycles through unlocked weapons."""
        self.current_weapon_idx = (self.current_weapon_idx + delta) % len(self.weapons)

    def set_weapon(self, name: str):
        """Selects a specific weapon by identifier."""
        if name in self.weapons:
            self.current_weapon_idx = self.weapons.index(name)

    def trigger_dash(self, move_input: tuple, sound_lib=None, time_acc=0.0):
        """Executes an invulnerable phase dash."""
        if self.dash_cooldown > 0 or not self.alive:
            return

        mx, my = move_input
        if mx == 0 and my == 0:
            mx, my = math.cos(self.aim_angle), math.sin(self.aim_angle)
        else:
            mag = math.hypot(mx, my)
            mx /= mag
            my /= mag

        self.dash_dir_x = mx
        self.dash_dir_y = my
        self.dash_timer = PLAYER_DASH_DURATION
        self.dash_cooldown = PLAYER_DASH_COOLDOWN
        self.vx = self.dash_dir_x * PLAYER_DASH_SPEED
        self.vy = self.dash_dir_y * PLAYER_DASH_SPEED
        self.is_invulnerable = True

        if sound_lib:
            sound_lib.play('dash', time_acc=time_acc, throttle=0.05)

    def trigger_slash(self, is_heavy: bool = False, sound_lib=None, time_acc=0.0):
        """Initiates a Katana slice that deflects bullets and slices enemies."""
        if self.slash_cooldown > 0 or not self.alive:
            return

        self.slash_cooldown = KATANA_COOLDOWN if not is_heavy else (KATANA_COOLDOWN * 1.5)
        self.slash_timer = KATANA_SLASH_DURATION if not is_heavy else (KATANA_SLASH_DURATION * 1.6)
        self.slash_direction = self.aim_angle

        # Forward lunge impulse
        lunge_speed = 180.0 if not is_heavy else 420.0
        self.vx += math.cos(self.aim_angle) * lunge_speed
        self.vy += math.sin(self.aim_angle) * lunge_speed

        if sound_lib:
            sfx = 'heavy_slash' if is_heavy else 'slash'
            sound_lib.play(sfx, time_acc=time_acc, throttle=0.02)

    def trigger_fire(self, sound_lib=None, time_acc=0.0) -> list:
        """Fires the currently equipped weapon. Returns a list of spawned projectiles."""
        if not self.alive or self.weapon_cooldown > 0:
            return []

        cfg = self.weapon_config
        ammo_cost = cfg.get('ammo_per_shot', 1)
        if ammo_cost > 0 and self.ammo < ammo_cost:
            return []

        self.ammo -= ammo_cost
        self.weapon_cooldown = cfg.get('fire_rate', 0.2)
        projectiles = []

        # Recoil kickback
        kick = cfg.get('kickback', 30.0)
        self.vx -= math.cos(self.aim_angle) * kick
        self.vy -= math.sin(self.aim_angle) * kick

        # Spawn offset at barrel tip
        barrel_x = self.x + math.cos(self.aim_angle) * 18.0
        barrel_y = self.y + math.sin(self.aim_angle) * 18.0

        if self.current_weapon == WEAPON_PISTOL:
            projectiles.append(Bullet(
                barrel_x, barrel_y, self.aim_angle, cfg['bullet_speed'],
                friendly=True, bounces_left=cfg['bounces'], damage=cfg['damage'],
                color=cfg['color']
            ))
            if sound_lib:
                sound_lib.play('shoot_pistol', time_acc=time_acc, throttle=0.02)

        elif self.current_weapon == WEAPON_SHOTGUN:
            pellet_count = cfg.get('pellets', 6)
            spread_angle = cfg.get('spread', 0.32)
            for i in range(pellet_count):
                offset = (i - (pellet_count - 1) / 2.0) * (spread_angle / pellet_count)
                offset += (pygame.time.get_ticks() % 5 - 2) * 0.02
                projectiles.append(Bullet(
                    barrel_x, barrel_y, self.aim_angle + offset, cfg['bullet_speed'] * (0.9 + i * 0.03),
                    friendly=True, bounces_left=cfg['bounces'], damage=cfg['damage'],
                    color=cfg['color']
                ))
            if sound_lib:
                sound_lib.play('shoot_shotgun', time_acc=time_acc, throttle=0.03)

        elif self.current_weapon == WEAPON_RAILGUN:
            projectiles.append(Bullet(
                barrel_x, barrel_y, self.aim_angle, cfg['bullet_speed'],
                friendly=True, bounces_left=0, piercing=True, damage=cfg['damage'],
                color=cfg['color']
            ))
            if sound_lib:
                sound_lib.play('shoot_railgun', time_acc=time_acc, throttle=0.05)

        elif self.current_weapon == WEAPON_SHURIKEN:
            projectiles.append(Shuriken(barrel_x, barrel_y, self.aim_angle))
            if sound_lib:
                sound_lib.play('shuriken', time_acc=time_acc, throttle=0.05)

        return projectiles

    def update(self, dt: float, move_input: tuple, mouse_world_pos: tuple, walls: list):
        """Updates player movement, timers, and physics."""
        if not self.alive:
            return

        # Aim towards cursor
        self.aim_angle = math.atan2(mouse_world_pos[1] - self.y, mouse_world_pos[0] - self.x)

        # Timers decay
        self.slash_cooldown = max(0.0, self.slash_cooldown - dt)
        self.weapon_cooldown = max(0.0, self.weapon_cooldown - dt)
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.slash_timer = max(0.0, self.slash_timer - dt)

        # Focus energy management
        if self.focus_active:
            self.focus = max(0.0, self.focus - dt * PLAYER_FOCUS_DRAIN)
            if self.focus <= 0.0:
                self.focus_active = False
        else:
            self.focus = min(self.max_focus, self.focus + dt * PLAYER_FOCUS_RECHARGE)

        # Dash handling
        if self.dash_timer > 0:
            self.dash_timer -= dt
            self.move_and_collide(self.vx * dt, self.vy * dt, walls)
            if self.dash_timer <= 0:
                self.is_invulnerable = False
        else:
            # Standard keyboard movement
            mx, my = move_input
            if mx or my:
                mag = math.hypot(mx, my)
                mx /= mag
                my /= mag

            target_vx = mx * PLAYER_BASE_SPEED
            target_vy = my * PLAYER_BASE_SPEED
            accel = min(1.0, dt * 14.0)
            self.vx += (target_vx - self.vx) * accel
            self.vy += (target_vy - self.vy) * accel

            self.move_and_collide(self.vx * dt, self.vy * dt, walls)

        # Ghost afterimages when moving fast
        speed = math.hypot(self.vx, self.vy)
        if speed > 220.0:
            self.afterimages.append([self.x, self.y, 0.5, self.aim_angle])
            if len(self.afterimages) > 16:
                self.afterimages.pop(0)

        # Decay afterimages
        for ai in self.afterimages:
            ai[2] -= dt * 2.5
        self.afterimages = [ai for ai in self.afterimages if ai[2] > 0]

    def draw(self, surf: pygame.Surface, camera=None):
        """Renders the player, katana blade, slash arc, and phantom afterimages."""
        if not self.alive:
            return

        # 1. Afterimages
        for ai in self.afterimages:
            k = ai[2] / 0.5
            pos = camera.world_to_screen(ai[0], ai[1]) if camera else (int(ai[0]), int(ai[1]))
            col = tuple(int(v * k * 0.45) for v in COLOR_GRAY)
            pygame.draw.circle(surf, col, pos, int(self.radius * (camera.zoom if camera else 1.0)))

        # 2. Main Player Body
        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        r = int(self.radius * (camera.zoom if camera else 1.0))
        
        pygame.draw.circle(surf, COLOR_WHITE, pos, r)
        pygame.draw.circle(surf, COLOR_BG, pos, r, 2)

        # Visor eye indicator
        head_x = pos[0] + math.cos(self.aim_angle) * (r * 0.55)
        head_y = pos[1] + math.sin(self.aim_angle) * (r * 0.55)
        pygame.draw.circle(surf, COLOR_RED, (int(head_x), int(head_y)), max(2, int(3 * (camera.zoom if camera else 1.0))))

        # 3. Katana Blade / Holster
        bx = pos[0] + math.cos(self.aim_angle + 0.7) * (r * 0.8)
        by = pos[1] + math.sin(self.aim_angle + 0.7) * (r * 0.8)
        tx = pos[0] + math.cos(self.aim_angle - 0.5) * (r * 2.4)
        ty = pos[1] + math.sin(self.aim_angle - 0.5) * (r * 2.4)
        pygame.draw.line(surf, COLOR_WHITE, (bx, by), (tx, ty), 2)

        # 4. Animated Slash Arc Ribbon
        if self.slash_timer > 0:
            k = 1.0 - (self.slash_timer / KATANA_SLASH_DURATION)
            arc_r = int((KATANA_RANGE * 0.6 + k * (KATANA_RANGE * 0.5)) * (camera.zoom if camera else 1.0))
            rect = pygame.Rect(pos[0] - arc_r, pos[1] - arc_r, arc_r * 2, arc_r * 2)
            
            # Draw outer blade streak
            pygame.draw.arc(surf, COLOR_WHITE, rect, -(self.slash_direction + KATANA_ARC_ANGLE), -(self.slash_direction - KATANA_ARC_ANGLE), 4)
            # Inner cyan streak
            inner_r = int(arc_r * 0.7)
            inner_rect = pygame.Rect(pos[0] - inner_r, pos[1] - inner_r, inner_r * 2, inner_r * 2)
            pygame.draw.arc(surf, COLOR_CYAN, inner_rect, -(self.slash_direction + KATANA_ARC_ANGLE * 0.8), -(self.slash_direction - KATANA_ARC_ANGLE * 0.8), 2)
