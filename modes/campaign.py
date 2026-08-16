# -*- coding: utf-8 -*-
"""
Campaign Mode Manager for MOMENTUM: Chrono Blade.
Executes handcrafted story missions, combat resolution, bullet deflections, killcams,
speedrun time tracking, and style ranking calculations.
"""
import math
import random
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_WHITE, COLOR_RED,
    COLOR_HOT, COLOR_PINK, COLOR_CYAN, COLOR_GOLD, COLOR_GRAY, COLOR_DIM,
    TIME_SCALE_STILL, TIME_SCALE_MOVE, TIME_SCALE_FOCUS, TIME_SCALE_KILLCAM,
    TIME_SCALE_ACCEL, RANK_COLORS
)
from entities.environment import (
    Wall, DestructibleCrate, ExplosiveBarrel, GlassWindow, SecurityTurret,
    AmmoPack, ChronoCell
)
from entities.player import Player
from entities.enemy import Enemy, BossChronoWarden
from entities.base import circle_rect_collision, angle_difference

class CampaignMode:
    """Manages the lifecycle, combat interactions, and scoring of campaign missions."""
    def __init__(self, engine, levels_data):
        self.engine = engine
        self.levels = levels_data
        self.current_level_idx = 0
        
        # State tracking
        self.state = 'play'  # 'play', 'killcam', 'clear', 'dead', 'victory'
        self.level_time = 0.0
        self.phase_timer = 0.0
        self.style_score = 0
        self.kills = 0
        self.deflect_count = 0
        self.combo_count = 0
        self.combo_timer = 0.0
        self.killcam_focus = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.boss_entity = None
        
        # World lists
        self.walls = []
        self.crates = []
        self.barrels = []
        self.windows = []
        self.turrets = []
        self.ammo_packs = []
        self.chrono_cells = []
        self.bullets = []
        self.projectiles = []
        self.enemies = []
        self.player = None

    def load_level(self, idx: int):
        """Initializes a specific campaign stage."""
        self.current_level_idx = idx % len(self.levels)
        lv = self.levels[self.current_level_idx]

        # Reset world boundaries
        border_thickness = 24
        self.walls = [
            Wall(0, 0, SCREEN_WIDTH, border_thickness),
            Wall(0, SCREEN_HEIGHT - border_thickness, SCREEN_WIDTH, border_thickness),
            Wall(0, 0, border_thickness, SCREEN_HEIGHT),
            Wall(SCREEN_WIDTH - border_thickness, 0, border_thickness, SCREEN_HEIGHT)
        ]
        self.walls += [Wall(*w) for w in lv.get('walls', [])]

        # Entities & Objects
        self.crates = [DestructibleCrate(*c) for c in lv.get('crates', [])]
        self.barrels = [ExplosiveBarrel(*b) for b in lv.get('barrels', [])]
        self.windows = [GlassWindow(*gw) for gw in lv.get('windows', [])]
        self.turrets = [SecurityTurret(*t) for t in lv.get('turrets', [])]
        self.ammo_packs = [AmmoPack(x, y, n) for x, y, n in lv.get('ammo_pickups', [])]
        self.chrono_cells = [ChronoCell(x, y, a) for x, y, a in lv.get('chrono_pickups', [])]

        # Player & Enemies
        spawn_x, spawn_y = lv.get('player_spawn', (200, 360))
        self.player = Player(spawn_x, spawn_y)
        
        self.enemies = []
        self.boss_entity = None
        for kind, ex, ey in lv.get('enemies', []):
            if kind == 'boss':
                boss = BossChronoWarden(ex, ey)
                self.enemies.append(boss)
                self.boss_entity = boss
            else:
                self.enemies.append(Enemy(kind, ex, ey))

        self.total_initial_enemies = len(self.enemies)
        self.bullets.clear()
        self.projectiles.clear()
        self.engine.particles.clear()

        # Mode variables
        self.state = 'play'
        self.level_time = 0.0
        self.phase_timer = 0.0
        self.style_score = 0
        self.kills = 0
        self.deflect_count = 0
        self.combo_count = 0
        self.combo_timer = 0.0

        # Announce level name
        self.engine.particles.add_floater(
            SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.28,
            f"LEVEL {self.current_level_idx + 1} — {lv['name'].upper()}",
            COLOR_WHITE, size=36, duration=1.8
        )
        self.engine.sound_lib.play('ui_click', throttle=0.0)

    def compute_rank(self) -> str:
        """Calculates performance rank based on speed, deflects, and combos."""
        lv = self.levels[self.current_level_idx]
        par = lv.get('par_time', 15)
        enemies_count = max(1, self.total_initial_enemies)
        
        # Style score target
        target = enemies_count * 200
        score = self.style_score
        if self.level_time <= par:
            score += 300  # Par bonus

        if score >= target * 1.8: return 'S+'
        if score >= target * 1.3: return 'S'
        if score >= target * 1.0: return 'A'
        if score >= target * 0.7: return 'B'
        if score >= target * 0.4: return 'C'
        return 'D'

    def update(self, dt: float, keys: dict, mouse_pos: tuple, mouse_buttons: tuple, time_acc: float):
        """Updates combat mechanics, physics, and enemy AI."""
        if self.state in ('clear', 'victory'):
            return

        p = self.player
        sound = self.engine.sound_lib
        vfx = self.engine.particles
        post = self.engine.post_processing

        # ----------------------------------------------------
        # Time Dilation Calculation
        # ----------------------------------------------------
        if self.state == 'play':
            player_speed = math.hypot(p.vx, p.vy) if p.alive else 0.0
            if p.focus_active:
                target_scale = TIME_SCALE_FOCUS
            elif player_speed > 30.0 or mouse_buttons[0] or mouse_buttons[2]:
                target_scale = TIME_SCALE_MOVE
            else:
                target_scale = TIME_SCALE_STILL
        elif self.state == 'killcam':
            target_scale = TIME_SCALE_KILLCAM
        else:  # 'dead'
            target_scale = 0.25

        # Smooth time scale interpolation
        self.engine.time_scale += (target_scale - self.engine.time_scale) * min(1.0, dt * TIME_SCALE_ACCEL)
        world_dt = dt * self.engine.time_scale

        # ----------------------------------------------------
        # Player Input & Movement
        # ----------------------------------------------------
        if self.state == 'play' and p.alive:
            self.level_time += dt
            self.combo_timer = max(0.0, self.combo_timer - dt)

            # Movement input
            move_x = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            move_y = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
            
            # Convert screen mouse to world coordinates
            mouse_world = self.engine.camera.screen_to_world(*mouse_pos)
            p.update(dt, (move_x, move_y), mouse_world, self.walls)

            # Katana Slash (LMB)
            if mouse_buttons[0]:
                if not p.charging_heavy:
                    p.trigger_slash(is_heavy=False, sound_lib=sound, time_acc=time_acc)
                    self._resolve_katana_slash(is_heavy=False)

            # Fire Gun (RMB)
            if mouse_buttons[2]:
                new_projectiles = p.trigger_fire(sound_lib=sound, time_acc=time_acc)
                if new_projectiles:
                    self.bullets.extend(new_projectiles)
                    cfg = p.weapon_config
                    self.engine.camera.add_shake(cfg.get('shake', 2.0))

        # ----------------------------------------------------
        # Katana Slash & Bullet Deflection Physics
        # ----------------------------------------------------
        # Update enemy AI
        all_walls = self.walls + [w.rect for w in self.windows if w.alive]
        for e in self.enemies:
            if isinstance(e, BossChronoWarden):
                spawned = e.update_boss(world_dt, p, all_walls, sound, time_acc)
            else:
                spawned = e.update_ai(world_dt, p, all_walls, sound, time_acc)
            if spawned:
                self.bullets.extend(spawned)

        # ----------------------------------------------------
        # Projectile Physics & Collisions
        # ----------------------------------------------------
        for b in self.bullets[:]:
            alive = b.update(world_dt, self.walls, vfx, sound, time_acc)
            if not alive:
                self.bullets.remove(b)
                continue

            # Friendly Bullet vs Enemies
            if b.friendly:
                for e in self.enemies[:]:
                    if circle_rect_collision(pygame.Rect(e.x - e.radius, e.y - e.radius, e.radius * 2, e.radius * 2), b.x, b.y, b.radius):
                        self._hit_enemy(e, b.damage, by_deflect=b.deflected)
                        if not b.piercing:
                            b.dead = True
                        break
            # Enemy Bullet vs Player
            else:
                if p.alive and not p.is_invulnerable:
                    if math.hypot(p.x - b.x, p.y - b.y) < (p.radius + b.radius):
                        self._kill_player()
                        b.dead = True

            # Bullet vs Barrels
            for brl in self.barrels[:]:
                if brl.alive and math.hypot(brl.x - b.x, brl.y - b.y) < (brl.radius + b.radius):
                    self._detonate_barrel(brl)
                    b.dead = True

            # Bullet vs Crates
            for crate in self.crates[:]:
                if crate.alive and crate.rect.collidepoint(b.x, b.y):
                    crate.take_damage(1)
                    if not crate.alive:
                        self._break_crate(crate)
                    b.dead = True

        # ----------------------------------------------------
        # Pickups Collision
        # ----------------------------------------------------
        if p.alive:
            for ap in self.ammo_packs[:]:
                if math.hypot(ap.x - p.x, ap.y - p.y) < 26:
                    p.ammo = min(p.max_ammo, p.ammo + ap.count)
                    sound.play('pickup_ammo', time_acc=time_acc, throttle=0.05)
                    vfx.add_floater(ap.x, ap.y - 18, f"+{ap.count} AMMO", COLOR_WHITE, 18)
                    self.ammo_packs.remove(ap)

            for cp in self.chrono_cells[:]:
                if math.hypot(cp.x - p.x, cp.y - p.y) < 26:
                    p.focus = min(p.max_focus, p.focus + cp.amount)
                    sound.play('pickup_chrono', time_acc=time_acc, throttle=0.05)
                    vfx.add_floater(cp.x, cp.y - 18, "+FOCUS", COLOR_CYAN, 18)
                    self.chrono_cells.remove(cp)

        # ----------------------------------------------------
        # Killcam & State Transitions
        # ----------------------------------------------------
        if self.state == 'killcam':
            self.phase_timer += dt
            if self.phase_timer > 1.1:
                self.state = 'clear'
                self.phase_timer = 0.0
                rank = self.compute_rank()
                self.engine.save_manager.record_level_clear(
                    self.current_level_idx, rank, self.level_time,
                    self.style_score, len(self.levels)
                )

        elif self.state == 'dead':
            self.phase_timer += dt
            if self.phase_timer > 1.4:
                self.load_level(self.current_level_idx)

    def _resolve_katana_slash(self, is_heavy: bool = False):
        """Calculates melee damage, enemy cleaving, and bullet deflections."""
        p = self.player
        vfx = self.engine.particles
        sound = self.engine.sound_lib
        slash_range = 95.0 if not is_heavy else 140.0
        slash_arc = 1.35 if not is_heavy else 1.8

        # 1. Deflect Enemy Bullets
        deflected_count = 0
        for b in self.bullets:
            if b.friendly or b.dead:
                continue
            dist = math.hypot(b.x - p.x, b.y - p.y)
            if dist < slash_range:
                bullet_angle = math.atan2(b.y - p.y, b.x - p.x)
                if angle_difference(bullet_angle, p.aim_angle) < slash_arc:
                    # Convert to friendly high-speed deflected projectile!
                    b.friendly = True
                    b.deflected = True
                    b.color = COLOR_WHITE
                    speed = max(b.speed, 880.0)
                    b.vx = math.cos(p.aim_angle) * speed
                    b.vy = math.sin(p.aim_angle) * speed
                    deflected_count += 1

        if deflected_count > 0:
            sound.play('deflect', throttle=0.02)
            self.engine.post_processing.trigger_white_flash(0.18)
            self.engine.post_processing.trigger_hitstop(0.04)
            self.engine.camera.add_shake(4.0)
            self.deflect_count += deflected_count
            self.style_score += deflected_count * 150
            vfx.add_floater(p.x, p.y - 30, "DEFLECT!", COLOR_WHITE, 22)
            self.engine.save_manager.record_deflect(deflected_count)

        # 2. Slice Enemies in Arc
        for e in self.enemies[:]:
            dist = math.hypot(e.x - p.x, e.y - p.y)
            if dist < (slash_range + e.radius):
                enemy_angle = math.atan2(e.y - p.y, e.x - p.x)
                if angle_difference(enemy_angle, p.aim_angle) < slash_arc:
                    damage = 3 if is_heavy else 1
                    self._hit_enemy(e, damage, by_deflect=False)

    def _hit_enemy(self, e: Enemy, damage: int, by_deflect: bool = False):
        """Applies damage to an enemy and manages kill rewards."""
        killed = e.take_damage(damage)
        sound = self.engine.sound_lib
        vfx = self.engine.particles
        
        sound.play('thud', throttle=0.02)
        vfx.add_blood_burst(e.x, e.y, amount=18, power=1.2)
        self.engine.camera.add_shake(3.5)

        if killed:
            self.enemies.remove(e)
            self.kills += 1
            self.engine.save_manager.record_kills(1)

            # Style scoring & combo chain
            if self.combo_timer > 0:
                self.combo_count += 1
                combo_bonus = self.combo_count * 50
                vfx.add_floater(e.x, e.y - 36, f"x{self.combo_count} COMBO", COLOR_HOT, 22)
            else:
                self.combo_count = 1
                combo_bonus = 0

            self.combo_timer = 1.8
            base_score = e.score_value * (3 if by_deflect else 1)
            self.style_score += base_score + combo_bonus

            # Drops
            if e.kind in ('grunt', 'shotgun', 'shield'):
                self.ammo_packs.append(AmmoPack(e.x, e.y, 2))
            elif e.kind == 'sniper':
                self.ammo_packs.append(AmmoPack(e.x, e.y, 4))
            elif e.kind == 'drone':
                self.chrono_cells.append(ChronoCell(e.x, e.y, 25))

            # Final Killcam Trigger
            if not self.enemies and self.state == 'play':
                self.state = 'killcam'
                self.phase_timer = 0.0
                self.killcam_focus = (e.x, e.y)
                sound.play('level_clear', throttle=0.1)

    def _kill_player(self):
        """Kills the player and triggers death VFX."""
        p = self.player
        if not p.alive or self.state != 'play':
            return
        p.alive = False
        self.state = 'dead'
        self.phase_timer = 0.0

        self.engine.sound_lib.play('death', throttle=0.0)
        self.engine.particles.add_blood_burst(p.x, p.y, amount=30, power=1.8)
        self.engine.post_processing.trigger_red_flash(0.4)
        self.engine.camera.add_shake(12.0)
        self.engine.save_manager.record_death()

    def _detonate_barrel(self, barrel: ExplosiveBarrel):
        """Detonates an explosive barrel with area-of-effect damage."""
        barrel.alive = False
        self.barrels.remove(barrel)
        self.engine.sound_lib.play('explosion', throttle=0.0)
        self.engine.particles.add_explosion_fx(barrel.x, barrel.y, radius=barrel.blast_radius)
        self.engine.camera.add_shake(8.0)

        # Damage entities in blast radius
        for e in self.enemies[:]:
            dist = math.hypot(e.x - barrel.x, e.y - barrel.y)
            if dist < barrel.blast_radius:
                self._hit_enemy(e, damage=5, by_deflect=False)

        if self.player.alive:
            p_dist = math.hypot(self.player.x - barrel.x, self.player.y - barrel.y)
            if p_dist < (barrel.blast_radius * 0.75) and not self.player.is_invulnerable:
                self._kill_player()

    def _break_crate(self, crate: DestructibleCrate):
        """Breaks crate and drops item."""
        self.crates.remove(crate)
        self.engine.particles.add_sparks(crate.x, crate.y, amount=12, color=(140, 110, 80))
        if crate.drops == 'ammo':
            self.ammo_packs.append(AmmoPack(crate.x, crate.y, 4))
        else:
            self.chrono_cells.append(ChronoCell(crate.x, crate.y, 35))

    def draw(self, canvas: pygame.Surface):
        """Renders world environment, entities, and HUD."""
        cam = self.engine.camera
        canvas.fill(COLOR_BG)

        # 1. Floor blood stains
        self.engine.particles.draw_floor_stains(canvas, cam)

        # 2. Interactive Objects & Pickups
        for w in self.windows:
            w.draw(canvas, cam)
        for w in self.walls:
            w.draw(canvas, cam)
        for c in self.crates:
            c.draw(canvas, cam)
        for b in self.barrels:
            b.draw(canvas, cam)
        for t in self.turrets:
            t.draw(canvas, cam)
        for ap in self.ammo_packs:
            ap.draw(canvas, 0.016, cam)
        for cp in self.chrono_cells:
            cp.draw(canvas, 0.016, cam)

        # 3. Actors & Bullets
        for e in self.enemies:
            all_walls = self.walls + [w.rect for w in self.windows if w.alive]
            e.draw(canvas, all_walls, cam)

        self.player.draw(canvas, cam)

        for b in self.bullets:
            b.draw(canvas, cam)

        # 4. Particles and Floaters
        self.engine.particles.draw_particles(canvas, cam)
        self.engine.particles.draw_floaters(canvas, self.engine.ui.font_cache, cam)

    def draw_overlays(self, screen: pygame.Surface):
        """Renders HUD, Clear, Dead, and Victory overlays."""
        lv = self.levels[self.current_level_idx]
        rank = self.compute_rank()
        
        # 1. Standard HUD
        if self.state in ('play', 'killcam'):
            self.engine.ui.draw_hud(
                screen, lv['name'], self.current_level_idx,
                self.level_time, lv.get('par_time', 15),
                len(self.enemies), self.player, self.style_score,
                max(1, self.total_initial_enemies * 200),
                rank, self.boss_entity
            )

        # 2. Death Screen
        if self.state == 'dead':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((65, 0, 8, int(160 * min(1.0, self.phase_timer / 0.5))))
            screen.blit(overlay, (0, 0))
            if self.phase_timer > 0.35:
                self.engine.ui.render_glow_text(screen, "ELIMINATED", 72, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.42), COLOR_RED, (120, 10, 20))
                self.engine.ui.render_text(screen, "R: RESTART INSTANTLY", 20, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.56), COLOR_GRAY)

        # 3. Level Clear Screen
        elif self.state == 'clear':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            self.engine.ui.render_glow_text(screen, "LEVEL CLEAR", 64, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.30), COLOR_WHITE, COLOR_RED)
            rank_col = RANK_COLORS.get(rank, COLOR_WHITE)
            self.engine.ui.render_glow_text(screen, rank, 110, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.50), rank_col, (120, 10, 20))
            par = lv.get('par_time', 15)
            self.engine.ui.render_text(
                screen, f"TIME {self.level_time:.2f}s   •   PAR {par}s   •   STYLE {self.style_score}",
                22, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.66), COLOR_GRAY
            )
            if self.current_level_idx == len(self.levels) - 1:
                self.engine.ui.render_text(screen, "PRESS ENTER: FINISH CAMPAIGN", 22, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.76), COLOR_WHITE)
            else:
                self.engine.ui.render_text(screen, "PRESS ENTER: NEXT MISSION", 22, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.76), COLOR_WHITE)
