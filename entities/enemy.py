# -*- coding: utf-8 -*-
"""
Enemy AI Hierarchy and Boss System for MOMENTUM: Chrono Blade.
Includes tactical Troopers, Shotgun Enforcers, Snipers, Cyber Ninjas, Shield Wardens,
Hunter Drones, and the Multi-Phase Boss: CHRONO WARDEN.
"""
import math
import random
import pygame
from core.constants import (
    ENEMY_TYPES, COLOR_WHITE, COLOR_RED, COLOR_HOT, COLOR_PINK, COLOR_CYAN,
    COLOR_DARK, COLOR_GRAY, COLOR_DIM
)
from entities.base import Entity, angle_difference
from entities.environment import line_of_sight, raycast_walls
from entities.weapons import Bullet

class Enemy(Entity):
    """Base tactical enemy unit with line-of-sight awareness, state machine, and firing charge-up."""
    def __init__(self, kind: str, x: float, y: float):
        self.kind = kind
        self.cfg = ENEMY_TYPES.get(kind, ENEMY_TYPES['grunt'])
        super().__init__(x, y, radius=self.cfg['radius'])
        
        self.hp = self.cfg.get('hp', 1)
        self.max_hp = self.hp
        self.color = self.cfg.get('color', COLOR_RED)
        self.sight_range = self.cfg.get('sight_range', 650.0)
        self.charge_time = self.cfg.get('charge_time', 0.7)
        self.cooldown_max = self.cfg.get('cooldown', 1.5)
        self.bullet_speed = self.cfg.get('bullet_speed', 340.0)
        self.move_speed = self.cfg.get('move_speed', 100.0)
        self.score_value = self.cfg.get('score_value', 100)

        # AI State
        self.aim_angle = random.uniform(0.0, 2.0 * math.pi)
        self.target_aim = self.aim_angle
        self.charge = 0.0
        self.cooldown = random.uniform(0.5, 1.2)
        self.wander_timer = random.uniform(0.0, 6.0)
        self.damage_flash = 0.0

        # Melee Rusher specifics
        self.dash_timer = 0.0
        self.windup_timer = 0.0
        self.dash_dx = 0.0
        self.dash_dy = 0.0

    def take_damage(self, amount: int = 1) -> bool:
        """Applies damage and triggers hit flash. Returns True if destroyed."""
        self.hp -= amount
        self.damage_flash = 0.12
        if self.hp <= 0:
            self.alive = False
        return not self.alive

    def update_ai(self, dt: float, player, walls: list, sound_lib=None, time_acc: float = 0.0) -> list:
        """
        Updates AI behavior tree. Returns a list of spawned projectiles if firing.
        """
        if not self.alive:
            return []

        self.damage_flash = max(0.0, self.damage_flash - dt)
        self.wander_timer += dt
        spawned_bullets = []

        if not player or not player.alive:
            return []

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy) or 1.0

        # Line of sight check
        can_see = (dist < self.sight_range) and line_of_sight(walls, self.x, self.y, player.x, player.y)

        # ----------------------------------------------------
        # Rusher Melee Logic
        # ----------------------------------------------------
        if self.kind == 'rusher':
            if self.dash_timer > 0:
                self.dash_timer -= dt
                self.move_and_collide(self.dash_dx * self.cfg['dash_speed'] * dt,
                                      self.dash_dy * self.cfg['dash_speed'] * dt, walls)
            elif self.windup_timer > 0:
                self.windup_timer -= dt
                self.aim_angle = math.atan2(dy, dx)
                if self.windup_timer <= 0:
                    self.dash_timer = 0.45
                    self.dash_dx = dx / dist
                    self.dash_dy = dy / dist
                    if sound_lib:
                        sound_lib.play('dash', time_acc=time_acc, throttle=0.1)
            elif can_see:
                if dist < 160.0:
                    self.windup_timer = self.charge_time
                else:
                    move_x = (dx / dist) * self.move_speed
                    move_y = (dy / dist) * self.move_speed
                    self.move_and_collide(move_x * dt, move_y * dt, walls)
                self.aim_angle = math.atan2(dy, dx)

            # Rusher Melee Hit Check
            if dist < (self.radius + player.radius + 3.0) and not player.is_invulnerable:
                player.alive = False

            return []

        # ----------------------------------------------------
        # Standard Ranged AI Logic
        # ----------------------------------------------------
        self.cooldown -= dt

        if can_see:
            # Smooth aim tracking towards player with a slight predictive weave
            target_angle = math.atan2(dy, dx)
            diff = (target_angle - self.aim_angle + math.pi) % (2.0 * math.pi) - math.pi
            self.aim_angle += diff * min(1.0, dt * 7.5)

            if self.cooldown <= 0:
                self.charge = min(1.0, self.charge + dt / self.charge_time)
                if self.charge >= 1.0:
                    spawned_bullets = self._fire(sound_lib, time_acc)
            else:
                self.charge = max(0.0, self.charge - dt * 2.0)

            # Tactical Repositioning
            if self.kind == 'sniper':
                # Snipers back away if player gets too close
                if dist < 320.0:
                    self.move_and_collide((-dx / dist) * self.move_speed * dt,
                                          (-dy / dist) * self.move_speed * dt, walls)
            elif self.kind == 'shield':
                # Shield Troopers advance steadily towards player
                self.move_and_collide((dx / dist) * self.move_speed * dt,
                                      (dy / dist) * self.move_speed * dt, walls)
            else:
                # Troopers and Shotgunners maintain optimal engagement distance
                preferred_dist = 260.0 if self.kind == 'grunt' else 180.0
                if dist > preferred_dist + 50.0:
                    mx = (dx / dist) * self.move_speed + math.sin(self.wander_timer * 2.0) * 30.0
                    my = (dy / dist) * self.move_speed + math.cos(self.wander_timer * 1.8) * 30.0
                    self.move_and_collide(mx * dt, my * dt, walls)
                elif dist < preferred_dist - 40.0:
                    self.move_and_collide((-dx / dist) * self.move_speed * dt,
                                          (-dy / dist) * self.move_speed * dt, walls)
        else:
            self.charge = max(0.0, self.charge - dt * 2.0)
            # Gentle patrol wandering
            if player.alive and self.kind != 'sniper':
                if dist > 350.0:
                    mx = (dx / dist) * (self.move_speed * 0.7) + math.sin(self.wander_timer * 1.5) * 20.0
                    my = (dy / dist) * (self.move_speed * 0.7) + math.cos(self.wander_timer * 1.3) * 20.0
                    self.move_and_collide(mx * dt, my * dt, walls)

        return spawned_bullets

    def _fire(self, sound_lib=None, time_acc: float = 0.0) -> list:
        """Spawns enemy bullets and resets attack cooldown."""
        bullets = []
        spawn_x = self.x + math.cos(self.aim_angle) * (self.radius + 6.0)
        spawn_y = self.y + math.sin(self.aim_angle) * (self.radius + 6.0)

        if self.kind == 'shotgun':
            pellet_count = self.cfg.get('pellets', 4)
            spread = self.cfg.get('spread', 0.28)
            for i in range(pellet_count):
                off = (i - (pellet_count - 1) / 2.0) * (spread / pellet_count)
                bullets.append(Bullet(spawn_x, spawn_y, self.aim_angle + off, self.bullet_speed,
                                      friendly=False, color=self.color))
        elif self.kind == 'drone':
            for i in range(3):
                bullets.append(Bullet(spawn_x, spawn_y, self.aim_angle + (i - 1) * 0.1, self.bullet_speed,
                                      friendly=False, color=COLOR_CYAN))
        else:
            bullets.append(Bullet(spawn_x, spawn_y, self.aim_angle, self.bullet_speed,
                                  friendly=False, color=self.color))

        self.charge = 0.0
        self.cooldown = self.cooldown_max

        if sound_lib:
            sound_lib.play('enemy_shoot', time_acc=time_acc, throttle=0.03)

        return bullets

    def draw(self, surf: pygame.Surface, walls: list, camera=None):
        """Renders enemy body, weapons, charging circle, and laser telegraph lines."""
        if not self.alive:
            return

        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        r = int(self.radius * (camera.zoom if camera else 1.0))
        draw_color = COLOR_WHITE if self.damage_flash > 0 else self.color

        # 1. Body Shapes based on archetype
        if self.kind == 'grunt':
            # Triangle trooper
            pts = [(pos[0] + math.cos(self.aim_angle) * (r + 6), pos[1] + math.sin(self.aim_angle) * (r + 6))]
            for a in (self.aim_angle + 2.4, self.aim_angle - 2.4):
                pts.append((pos[0] + math.cos(a) * r, pos[1] + math.sin(a) * r))
            pygame.draw.polygon(surf, (35, 10, 15), pts)
            pygame.draw.polygon(surf, draw_color, pts, 2)

        elif self.kind == 'shotgun':
            # Hexagonal armored enforcer
            pts = [(pos[0] + math.cos(i * (math.pi / 3.0) + self.aim_angle) * r,
                    pos[1] + math.sin(i * (math.pi / 3.0) + self.aim_angle) * r) for i in range(6)]
            pygame.draw.polygon(surf, (40, 18, 12), pts)
            pygame.draw.polygon(surf, draw_color, pts, 2)
            # Shotgun barrel
            bx = pos[0] + math.cos(self.aim_angle) * (r + 8)
            by = pos[1] + math.sin(self.aim_angle) * (r + 8)
            pygame.draw.line(surf, draw_color, pos, (bx, by), 3)

        elif self.kind == 'sniper':
            # Diamond marksman
            pts = [(pos[0] + math.cos(a) * r, pos[1] + math.sin(a) * r)
                   for a in (self.aim_angle, self.aim_angle + math.pi / 2, self.aim_angle + math.pi, self.aim_angle - math.pi / 2)]
            pygame.draw.polygon(surf, (38, 12, 28), pts)
            pygame.draw.polygon(surf, draw_color, pts, 2)
            # Long sniper barrel
            bx = pos[0] + math.cos(self.aim_angle) * (r + 14)
            by = pos[1] + math.sin(self.aim_angle) * (r + 14)
            pygame.draw.line(surf, draw_color, pos, (bx, by), 2)

        elif self.kind == 'shield':
            # Circle body + Front shield arc
            pygame.draw.circle(surf, (30, 24, 15), pos, r)
            pygame.draw.circle(surf, draw_color, pos, r, 2)
            # Energy shield arc
            shield_r = int(r * 1.5)
            s_rect = pygame.Rect(pos[0] - shield_r, pos[1] - shield_r, shield_r * 2, shield_r * 2)
            pygame.draw.arc(surf, (255, 190, 50), s_rect, -(self.aim_angle + 1.2), -(self.aim_angle - 1.2), 4)

        elif self.kind == 'drone':
            # Hover drone with pulsing core
            pygame.draw.circle(surf, (15, 30, 40), pos, r)
            pygame.draw.circle(surf, draw_color, pos, r, 2)
            pygame.draw.circle(surf, COLOR_WHITE, pos, max(2, int(r * 0.4)))

        else:  # rusher
            # Spiked ninja star
            pulse = 1.0 + 0.15 * math.sin(self.wander_timer * 10.0)
            pts = [(pos[0] + math.cos(self.wander_timer * 3.0 + i * 1.256) * r * pulse,
                    pos[1] + math.sin(self.wander_timer * 3.0 + i * 1.256) * r * pulse) for i in range(5)]
            pygame.draw.polygon(surf, (45, 8, 12), pts)
            pygame.draw.polygon(surf, draw_color, pts, 2)

        # 2. Charge-up Ring
        if self.charge > 0:
            arc_rect = pygame.Rect(pos[0] - r - 6, pos[1] - r - 6, (r + 6) * 2, (r + 6) * 2)
            pygame.draw.arc(surf, draw_color, arc_rect, -math.pi / 2, -math.pi / 2 + self.charge * 2.0 * math.pi, 2)

        # 3. Laser Sight Aim Telegraph
        if self.charge > 0.05 and self.kind != 'rusher':
            ray_len = raycast_walls(walls, self.x, self.y, self.aim_angle, 1600.0)
            end_wx = self.x + math.cos(self.aim_angle) * ray_len
            end_wy = self.y + math.sin(self.aim_angle) * ray_len
            end_pos = camera.world_to_screen(end_wx, end_wy) if camera else (int(end_wx), int(end_wy))
            
            laser_alpha = int((0.2 + 0.8 * self.charge) * 255)
            laser_col = COLOR_WHITE if self.kind == 'sniper' else COLOR_RED
            line_w = 2 if self.kind == 'sniper' else 1
            pygame.draw.line(surf, laser_col, pos, end_pos, line_w)


class BossChronoWarden(Enemy):
    """
    Multi-Phase Epic Boss: The Chrono Warden.
    Possesses temporal dash teleports, spiral bullet hell storm attacks, and stasis shields.
    """
    def __init__(self, x: float, y: float):
        super().__init__('boss', x, y)
        self.phase = 1
        self.attack_timer = 0.0
        self.spiral_angle = 0.0
        self.teleport_timer = 4.0
        self.shield_active = False

    def update_boss(self, dt: float, player, walls: list, sound_lib=None, time_acc: float = 0.0) -> list:
        """Executes multi-phase boss attack routines."""
        if not self.alive or not player or not player.alive:
            return []

        self.damage_flash = max(0.0, self.damage_flash - dt)
        self.wander_timer += dt
        self.attack_timer += dt
        self.teleport_timer -= dt

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy) or 1.0
        self.aim_angle = math.atan2(dy, dx)
        spawned_bullets = []

        # Phase 2 trigger at 50% HP
        if self.hp < (self.max_hp / 2.0) and self.phase == 1:
            self.phase = 2
            self.shield_active = True

        # Boss Teleport
        if self.teleport_timer <= 0:
            self.teleport_timer = random.uniform(3.5, 5.0)
            tele_angle = random.uniform(0, 2.0 * math.pi)
            tele_dist = random.uniform(180, 320)
            target_x = max(100, min(1180, player.x + math.cos(tele_angle) * tele_dist))
            target_y = max(100, min(620, player.y + math.sin(tele_angle) * tele_dist))
            self.x = target_x
            self.y = target_y
            if sound_lib:
                sound_lib.play('dash', time_acc=time_acc, throttle=0.0)

        # Attack Pattern: Spiral Bullet Hell + Direct Aim Barrage
        if self.phase == 1:
            # Steady spiral bullets
            self.spiral_angle += dt * 3.5
            if int(self.attack_timer * 12) % 3 == 0:
                bullets_per_spoke = 3
                for i in range(bullets_per_spoke):
                    a = self.spiral_angle + i * (2.0 * math.pi / bullets_per_spoke)
                    spawned_bullets.append(Bullet(self.x, self.y, a, 320.0, friendly=False, color=COLOR_RED))
        else:
            # Phase 2: Hyper spiral + targeted bursts
            self.spiral_angle += dt * 5.0
            if int(self.attack_timer * 16) % 2 == 0:
                bullets_per_spoke = 5
                for i in range(bullets_per_spoke):
                    a = self.spiral_angle + i * (2.0 * math.pi / bullets_per_spoke)
                    spawned_bullets.append(Bullet(self.x, self.y, a, 360.0, friendly=False, color=COLOR_HOT))

        return spawned_bullets

    def draw(self, surf: pygame.Surface, walls: list, camera=None):
        """Renders boss with pulsating orbital shields and central core."""
        if not self.alive:
            return

        pos = camera.world_to_screen(self.x, self.y) if camera else (int(self.x), int(self.y))
        r = int(self.radius * (camera.zoom if camera else 1.0))
        draw_color = COLOR_WHITE if self.damage_flash > 0 else (255, 20, 80)

        # Boss Core Octagon
        pts = [(pos[0] + math.cos(i * (math.pi / 4.0) + self.wander_timer * 1.5) * r,
                pos[1] + math.sin(i * (math.pi / 4.0) + self.wander_timer * 1.5) * r) for i in range(8)]
        pygame.draw.polygon(surf, (45, 10, 20), pts)
        pygame.draw.polygon(surf, draw_color, pts, 3)

        # Orbiting temporal rings
        orb_r = int(r * 1.7)
        pygame.draw.circle(surf, COLOR_HOT, pos, orb_r, 1)
        for i in range(3):
            oa = self.wander_timer * 3.0 + i * (2.0 * math.pi / 3.0)
            ox = pos[0] + math.cos(oa) * orb_r
            oy = pos[1] + math.sin(oa) * orb_r
            pygame.draw.circle(surf, COLOR_WHITE, (int(ox), int(oy)), 4)
