# -*- coding: utf-8 -*-
"""
Endless Survival Mode with Roguelike Perks for MOMENTUM: Chrono Blade.
Features infinite procedural wave defense, boss waves, score multipliers, and between-wave upgrade choices.
"""
import math
import random
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_WHITE, COLOR_RED,
    COLOR_CYAN, COLOR_GOLD, COLOR_HOT, COLOR_GRAY, COLOR_DIM,
    TIME_SCALE_STILL, TIME_SCALE_MOVE, TIME_SCALE_FOCUS, TIME_SCALE_ACCEL
)
from entities.environment import Wall, DestructibleCrate, ExplosiveBarrel, AmmoPack, ChronoCell
from entities.player import Player
from entities.enemy import Enemy, BossChronoWarden
from entities.base import circle_rect_collision, angle_difference
from levels.wave_generator import generate_arena_layout, generate_wave_enemies

PERK_POOL = [
    {
        "id": "katana_range",
        "name": "OVERCLOCKED KATANA",
        "desc": "+30% Blade Deflect Arc & Melee Range",
        "icon": "⚔"
    },
    {
        "id": "ricochet_bounce",
        "name": "RICOCHET DYNAMICS",
        "desc": "+2 Bullet Bounces & Shrapnel Sparks",
        "icon": "✦"
    },
    {
        "id": "chrono_focus",
        "name": "CHRONO BATTERY",
        "desc": "+50% Focus Duration & Faster Recharge",
        "icon": "⏳"
    },
    {
        "id": "vampiric_parry",
        "name": "LEECHING PARRY",
        "desc": "Deflecting bullets restores +2 Ammo & Focus",
        "icon": "🩸"
    },
    {
        "id": "dash_shockwave",
        "name": "KINETIC DASH",
        "desc": "Dashing releases a stun shockwave ring",
        "icon": "💥"
    },
    {
        "id": "ammo_hoarder",
        "name": "EXTENDED MAGS",
        "desc": "+8 Maximum Ammo Capacity & Instant Refill",
        "icon": "📦"
    }
]

class EndlessMode:
    """Manages wave-based endless survival combat and roguelike perk drafting."""
    def __init__(self, engine):
        self.engine = engine
        self.wave = 1
        self.score = 0
        self.kills = 0
        self.state = 'play'  # 'play', 'perk_select', 'dead'
        self.perk_choices = []
        self.active_perks = []

        self.walls = []
        self.crates = []
        self.barrels = []
        self.ammo_packs = []
        self.chrono_cells = []
        self.enemies = []
        self.bullets = []
        self.player = None
        self.phase_timer = 0.0
        self.selected_perk_idx = 0

    def start_new_game(self):
        """Initializes endless run."""
        self.wave = 1
        self.score = 0
        self.kills = 0
        self.active_perks.clear()
        self._load_wave(self.wave)

    def _load_wave(self, wave_num: int):
        """Generates procedural arena and spawns wave hostiles."""
        arena = generate_arena_layout(seed=wave_num * 137)
        border = 24
        self.walls = [
            Wall(0, 0, SCREEN_WIDTH, border),
            Wall(0, SCREEN_HEIGHT - border, SCREEN_WIDTH, border),
            Wall(0, 0, border, SCREEN_HEIGHT),
            Wall(SCREEN_WIDTH - border, 0, border, SCREEN_HEIGHT)
        ] + [Wall(*w) for w in arena['walls']]

        self.crates = [DestructibleCrate(*c) for c in arena.get('crates', [])]
        self.barrels = [ExplosiveBarrel(*b) for b in arena.get('barrels', [])]
        self.ammo_packs.clear()
        self.chrono_cells.clear()
        self.bullets.clear()

        # Preserve player health/ammo if already exists
        if not self.player:
            self.player = Player(*arena['player_spawn'])
        else:
            self.player.x, self.player.y = arena['player_spawn']
            self.player.vx = self.player.vy = 0

        # Apply active perk buffs
        if "ammo_hoarder" in self.active_perks:
            self.player.max_ammo = 32
            self.player.ammo = self.player.max_ammo

        # Spawn enemies
        enemy_defs = generate_wave_enemies(wave_num)
        self.enemies = []
        for kind, ex, ey in enemy_defs:
            if kind == 'boss':
                self.enemies.append(BossChronoWarden(ex, ey))
            else:
                self.enemies.append(Enemy(kind, ex, ey))

        self.state = 'play'
        self.engine.particles.add_floater(
            SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.28,
            f"WAVE {wave_num} — SURVIVE", COLOR_GOLD, size=40, duration=2.0
        )

    def trigger_perk_selection(self):
        """Prepares 3 random upgrade choices between waves."""
        self.state = 'perk_select'
        self.selected_perk_idx = 0
        available = [p for p in PERK_POOL if p['id'] not in self.active_perks]
        if not available:
            available = PERK_POOL
        self.perk_choices = random.sample(available, min(3, len(available)))
        self.engine.sound_lib.play('level_clear', throttle=0.0)

    def apply_selected_perk(self, perk_dict: dict):
        """Applies chosen perk buff."""
        perk_id = perk_dict['id']
        self.active_perks.append(perk_id)
        if perk_id == "ammo_hoarder":
            self.player.max_ammo += 8
            self.player.ammo = self.player.max_ammo

        self.wave += 1
        self._load_wave(self.wave)

    def update(self, dt: float, keys: dict, mouse_pos: tuple, mouse_buttons: tuple, time_acc: float):
        if self.state == 'perk_select':
            return

        p = self.player
        sound = self.engine.sound_lib
        vfx = self.engine.particles

        if self.state == 'play':
            player_speed = math.hypot(p.vx, p.vy) if p.alive else 0.0
            target_scale = TIME_SCALE_MOVE if player_speed > 30.0 or mouse_buttons[0] or mouse_buttons[2] else TIME_SCALE_STILL
            self.engine.time_scale += (target_scale - self.engine.time_scale) * min(1.0, dt * TIME_SCALE_ACCEL)
            world_dt = dt * self.engine.time_scale

            if p.alive:
                # Controls
                mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
                my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
                mouse_world = self.engine.camera.screen_to_world(*mouse_pos)
                p.update(dt, (mx, my), mouse_world, self.walls)

                if mouse_buttons[0]:
                    p.trigger_slash(sound_lib=sound, time_acc=time_acc)
                    self._resolve_slash()

                if mouse_buttons[2]:
                    new_b = p.trigger_fire(sound_lib=sound, time_acc=time_acc)
                    if new_b:
                        self.bullets.extend(new_b)

            # Update enemies
            for e in self.enemies:
                if isinstance(e, BossChronoWarden):
                    spawned = e.update_boss(world_dt, p, self.walls, sound, time_acc)
                else:
                    spawned = e.update_ai(world_dt, p, self.walls, sound, time_acc)
                if spawned:
                    self.bullets.extend(spawned)

            # Update projectiles
            for b in self.bullets[:]:
                if not b.update(world_dt, self.walls, vfx, sound, time_acc):
                    self.bullets.remove(b)
                    continue

                if b.friendly:
                    for e in self.enemies[:]:
                        if circle_rect_collision(pygame.Rect(e.x - e.radius, e.y - e.radius, e.radius * 2, e.radius * 2), b.x, b.y, b.radius):
                            self._hit_enemy(e, b.damage, b.deflected)
                            if not b.piercing:
                                b.dead = True
                            break
                else:
                    if p.alive and not p.is_invulnerable:
                        if math.hypot(p.x - b.x, p.y - b.y) < (p.radius + b.radius):
                            self._kill_player()
                            b.dead = True

            # Check Wave Clear
            if not self.enemies and self.state == 'play':
                self.trigger_perk_selection()

        elif self.state == 'dead':
            self.phase_timer += dt

    def _resolve_slash(self):
        p = self.player
        sound = self.engine.sound_lib
        vfx = self.engine.particles
        slash_range = 115.0 if "katana_range" in self.active_perks else 90.0

        for b in self.bullets:
            if not b.friendly and not b.dead:
                if math.hypot(b.x - p.x, b.y - p.y) < slash_range:
                    if angle_difference(math.atan2(b.y - p.y, b.x - p.x), p.aim_angle) < 1.35:
                        b.friendly = True
                        b.deflected = True
                        b.color = COLOR_WHITE
                        b.vx = math.cos(p.aim_angle) * 880.0
                        b.vy = math.sin(p.aim_angle) * 880.0
                        sound.play('deflect', throttle=0.02)
                        self.score += 150
                        vfx.add_floater(p.x, p.y - 25, "DEFLECT!", COLOR_WHITE, 20)
                        if "vampiric_parry" in self.active_perks:
                            p.ammo = min(p.max_ammo, p.ammo + 2)

        for e in self.enemies[:]:
            if math.hypot(e.x - p.x, e.y - p.y) < (slash_range + e.radius):
                if angle_difference(math.atan2(e.y - p.y, e.x - p.x), p.aim_angle) < 1.35:
                    self._hit_enemy(e, 1, by_deflect=False)

    def _hit_enemy(self, e: Enemy, damage: int, by_deflect: bool):
        if e.take_damage(damage):
            self.enemies.remove(e)
            self.kills += 1
            self.score += e.score_value * (3 if by_deflect else 1)
            self.engine.particles.add_blood_burst(e.x, e.y, amount=18)
            self.engine.sound_lib.play('thud', throttle=0.02)
            self.ammo_packs.append(AmmoPack(e.x, e.y, 2))

    def _kill_player(self):
        self.player.alive = False
        self.state = 'dead'
        self.phase_timer = 0.0
        self.engine.sound_lib.play('death', throttle=0.0)
        self.engine.particles.add_blood_burst(self.player.x, self.player.y, amount=30)
        self.engine.post_processing.trigger_red_flash(0.4)
        self.engine.save_manager.record_endless(self.wave, self.score)

    def draw(self, canvas: pygame.Surface):
        cam = self.engine.camera
        canvas.fill(COLOR_BG)
        self.engine.particles.draw_floor_stains(canvas, cam)

        for w in self.walls: w.draw(canvas, cam)
        for c in self.crates: c.draw(canvas, cam)
        for b in self.barrels: b.draw(canvas, cam)
        for ap in self.ammo_packs: ap.draw(canvas, 0.016, cam)
        for e in self.enemies: e.draw(canvas, self.walls, cam)
        if self.player: self.player.draw(canvas, cam)
        for b in self.bullets: b.draw(canvas, cam)

        self.engine.particles.draw_particles(canvas, cam)
        self.engine.particles.draw_floaters(canvas, self.engine.ui.font_cache, cam)

    def draw_overlays(self, screen: pygame.Surface):
        ui = self.engine.ui
        if self.state == 'play':
            ui.render_text(screen, f"ENDLESS WAVE {self.wave}", 18, (SCREEN_WIDTH // 2, 34), COLOR_GOLD)
            ui.render_text(screen, f"SCORE: {self.score}", 18, (SCREEN_WIDTH - 30, 34), COLOR_WHITE, anchor='topright')
            ui.render_text(screen, f"ENEMIES: {len(self.enemies)}", 14, (30, 34), COLOR_RED, anchor='topleft')

        elif self.state == 'perk_select':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 15, 210))
            screen.blit(overlay, (0, 0))

            ui.render_glow_text(screen, f"WAVE {self.wave} CLEARED", 52, (SCREEN_WIDTH // 2, 130), COLOR_GOLD, (140, 90, 20))
            ui.render_text(screen, "CHOOSE AN UPGRADE (1, 2, OR 3):", 20, (SCREEN_WIDTH // 2, 210), COLOR_WHITE)

            card_w, card_h = 320, 240
            total_w = len(self.perk_choices) * (card_w + 30) - 30
            start_x = SCREEN_WIDTH // 2 - total_w // 2

            for i, perk in enumerate(self.perk_choices):
                cx = start_x + i * (card_w + 30)
                cy = 280
                rect = pygame.Rect(cx, cy, card_w, card_h)
                
                is_hover = (i == self.selected_perk_idx)
                border_col = COLOR_GOLD if is_hover else COLOR_DIM
                pygame.draw.rect(screen, (22, 24, 34), rect, border_radius=8)
                pygame.draw.rect(screen, border_col, rect, 2, border_radius=8)

                ui.render_text(screen, f"[{i + 1}]", 22, (cx + card_w // 2, cy + 35), COLOR_CYAN)
                ui.render_text(screen, perk['name'], 18, (cx + card_w // 2, cy + 85), COLOR_WHITE)
                ui.render_text(screen, perk['desc'], 14, (cx + card_w // 2, cy + 145), COLOR_GRAY)

        elif self.state == 'dead':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((60, 0, 8, 180))
            screen.blit(overlay, (0, 0))
            ui.render_glow_text(screen, "SURVIVAL TERMINATED", 64, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.38), COLOR_RED, (120, 10, 20))
            ui.render_text(screen, f"SURVIVED UNTIL WAVE {self.wave}   •   FINAL SCORE: {self.score}", 22, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.52), COLOR_WHITE)
            ui.render_text(screen, "R: RETRY ENDLESS      ESC: MAIN MENU", 18, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.65), COLOR_GRAY)
