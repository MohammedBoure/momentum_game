# -*- coding: utf-8 -*-
"""
Master Engine and State Coordinator for MOMENTUM: Chrono Blade.
Coordinates graphics, procedural audio, save states, camera physics, and mode transitions.
"""
import math
import sys
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS, COLOR_BG, COLOR_WHITE,
    COLOR_RED, COLOR_GRAY, COLOR_DIM, COLOR_DARK, TIME_SCALE_STILL,
    WINDOW_TITLE
)
from core.camera import Camera
from core.save_manager import SaveManager
from audio.sound_effects import SoundLibrary
from audio.music_engine import MusicEngine
from gfx.particles import ParticleManager
from gfx.effects import PostProcessingManager
from gfx.renderer import UIRenderer
from levels.level_data import CAMPAIGN_LEVELS
from levels.level_editor import LevelEditor
from modes.campaign import CampaignMode
from modes.endless import EndlessMode
from modes.menu_system import MenuSystem

class GameEngine:
    """Master game engine managing the update loop, render passes, and subsystem interactions."""
    def __init__(self, screen: pygame.Surface, audio_enabled: bool = True):
        self.screen = screen
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize subsystems
        self.save_manager = SaveManager()
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.sound_lib = SoundLibrary(audio_enabled=audio_enabled)
        self.music_engine = MusicEngine(audio_enabled=audio_enabled)
        self.particles = ParticleManager()
        self.post_processing = PostProcessingManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui = UIRenderer()

        # Apply persistent volume settings
        master_v = self.save_manager.get_setting('master_volume', 0.8)
        sfx_v = self.save_manager.get_setting('sfx_volume', 0.9)
        mus_v = self.save_manager.get_setting('music_volume', 0.6)
        self.sound_lib.update_volume(master_v, sfx_v)
        self.music_engine.update_volume(master_v, mus_v)

        # Game modes
        self.campaign_levels = CAMPAIGN_LEVELS
        self.campaign_mode = CampaignMode(self, self.campaign_levels)
        self.endless_mode = EndlessMode(self)
        self.level_editor = LevelEditor(self.screen, self.save_manager, self.sound_lib, self.ui)
        self.menu_system = MenuSystem(self, self.save_manager, self.sound_lib, self.ui)

        # Master State Machine: 'menu', 'campaign', 'endless', 'editor', 'paused'
        self.state = 'menu'
        self.previous_state = 'menu'
        self.time_scale = 1.0
        self.time_accumulated = 0.0

        # Heartbeat pulse timer during time dilation
        self.heartbeat_timer = 0.0
        self.heartbeat_sub_timer = 0.0
        self.heartbeat_pulse = 0.0

        # Start dynamic soundtrack
        self.music_engine.play_track('main_theme')

    def run(self):
        """Main game execution loop."""
        while self.running:
            raw_dt = min(self.clock.tick(TARGET_FPS) / 1000.0, 0.035)
            self.time_accumulated += raw_dt

            # 1. Input & Event Polling
            self._process_events()

            # 2. Physics & Logic Update
            is_frozen = self.post_processing.update(raw_dt)
            if not is_frozen:
                self._update_subsystems(raw_dt)

            # 3. Layered Render Pipeline
            self._render_pipeline()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _process_events(self):
        """Handles all system, keyboard, and mouse events."""
        mouse_pos = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
                return

            # Music toggle shortcut (Global)
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_m:
                self.music_engine.toggle_music()

            # ----------------------------------------------------
            # State-Specific Event Dispatching
            # ----------------------------------------------------
            if self.state == 'menu':
                action = self.menu_system.handle_event(ev, self.campaign_levels)
                if action == 'start_campaign':
                    unlocked_idx = min(self.save_manager.data.get('unlocked_level', 1) - 1, len(self.campaign_levels) - 1)
                    self.campaign_mode.load_level(unlocked_idx)
                    self.state = 'campaign'
                elif action == 'start_endless':
                    self.endless_mode.start_new_game()
                    self.state = 'endless'
                elif action and action.startswith('play_level_'):
                    lv_num = int(action.replace('play_level_', ''))
                    self.campaign_mode.load_level(lv_num)
                    self.state = 'campaign'
                elif action == 'start_editor':
                    self.state = 'editor'
                elif action == 'quit':
                    self.running = False

            elif self.state == 'editor':
                res = self.level_editor.handle_event(ev)
                if res == 'exit':
                    self.state = 'menu'
                elif res == 'test':
                    # Load editor map into campaign mode
                    custom_data = self.level_editor.export_data()
                    self.campaign_mode.levels = [custom_data]
                    self.campaign_mode.load_level(0)
                    self.state = 'campaign'

            elif self.state == 'campaign':
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        if self.campaign_mode.state == 'play':
                            self.state = 'paused'
                            self.previous_state = 'campaign'
                        elif self.campaign_mode.state in ('clear', 'dead'):
                            self.state = 'menu'
                    elif ev.key == pygame.K_r:
                        self.campaign_mode.load_level(self.campaign_mode.current_level_idx)
                    elif ev.key in (pygame.K_LSHIFT, pygame.K_SPACE):
                        keys = pygame.key.get_pressed()
                        mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
                        my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
                        self.campaign_mode.player.trigger_dash((mx, my), sound_lib=self.sound_lib, time_acc=self.time_accumulated)
                    elif ev.key == pygame.K_1: self.campaign_mode.player.set_weapon('pistol')
                    elif ev.key == pygame.K_2: self.campaign_mode.player.set_weapon('shotgun')
                    elif ev.key == pygame.K_3: self.campaign_mode.player.set_weapon('railgun')
                    elif ev.key == pygame.K_4: self.campaign_mode.player.set_weapon('shuriken')
                    elif ev.key == pygame.K_e:
                        self.campaign_mode.player.focus_active = not self.campaign_mode.player.focus_active
                    elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if self.campaign_mode.state == 'clear':
                            if self.campaign_mode.current_level_idx < len(self.campaign_mode.levels) - 1:
                                self.campaign_mode.load_level(self.campaign_mode.current_level_idx + 1)
                            else:
                                self.state = 'menu'

                elif ev.type == pygame.MOUSEWHEEL:
                    self.campaign_mode.player.switch_weapon(ev.y)

            elif self.state == 'endless':
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                    elif ev.key == pygame.K_r and self.endless_mode.state == 'dead':
                        self.endless_mode.start_new_game()
                    elif self.endless_mode.state == 'perk_select':
                        if ev.key == pygame.K_1 and len(self.endless_mode.perk_choices) >= 1:
                            self.endless_mode.apply_selected_perk(self.endless_mode.perk_choices[0])
                        elif ev.key == pygame.K_2 and len(self.endless_mode.perk_choices) >= 2:
                            self.endless_mode.apply_selected_perk(self.endless_mode.perk_choices[1])
                        elif ev.key == pygame.K_3 and len(self.endless_mode.perk_choices) >= 3:
                            self.endless_mode.apply_selected_perk(self.endless_mode.perk_choices[2])
                    elif ev.key in (pygame.K_LSHIFT, pygame.K_SPACE):
                        keys = pygame.key.get_pressed()
                        mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
                        my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
                        self.endless_mode.player.trigger_dash((mx, my), sound_lib=self.sound_lib, time_acc=self.time_accumulated)

            elif self.state == 'paused':
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        self.state = self.previous_state
                    elif ev.key == pygame.K_r:
                        if self.previous_state == 'campaign':
                            self.campaign_mode.load_level(self.campaign_mode.current_level_idx)
                        self.state = self.previous_state
                    elif ev.key == pygame.K_q:
                        self.state = 'menu'

    def _update_subsystems(self, dt: float):
        """Updates particle systems, camera tracking, and active game modes."""
        self.particles.update(dt)
        self.heartbeat_pulse = max(0.0, self.heartbeat_pulse - dt * 3.0)

        # Heartbeat pulse audio during intense stasis slow-mo
        if self.time_scale < 0.25 and self.state in ('campaign', 'endless'):
            self.heartbeat_timer -= dt
            if self.heartbeat_sub_timer > 0:
                self.heartbeat_sub_timer -= dt
                if self.heartbeat_sub_timer <= 0:
                    self.sound_lib.play('heart2', time_acc=self.time_accumulated, throttle=0.05)
                    self.heartbeat_pulse = 0.7
            if self.heartbeat_timer <= 0:
                self.sound_lib.play('heart1', time_acc=self.time_accumulated, throttle=0.05)
                self.heartbeat_pulse = 1.0
                self.heartbeat_sub_timer = 0.18
                self.heartbeat_timer = 1.15

        # Dynamic music adaptation to time dilation
        self.music_engine.update_dilation(self.time_scale)

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        if self.state == 'menu':
            self.menu_system.update(dt)
            self.camera.x = SCREEN_WIDTH / 2
            self.camera.y = SCREEN_HEIGHT / 2

        elif self.state == 'editor':
            self.level_editor.update(dt)

        elif self.state == 'campaign':
            self.campaign_mode.update(dt, keys, mouse_pos, mouse_buttons, self.time_accumulated)
            target = (self.campaign_mode.player.x, self.campaign_mode.player.y) if self.campaign_mode.player else (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.camera.update(dt, target, mouse_pos)

        elif self.state == 'endless':
            self.endless_mode.update(dt, keys, mouse_pos, mouse_buttons, self.time_accumulated)
            target = (self.endless_mode.player.x, self.endless_mode.player.y) if self.endless_mode.player else (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.camera.update(dt, target, mouse_pos)

    def _render_pipeline(self):
        """Master rendering pipeline with world drawing, post-processing, and HUD overlays."""
        # 1. World Canvas Pass
        if self.state == 'menu':
            self.menu_system.draw(self.screen, self.campaign_levels)
            return
        elif self.state == 'editor':
            self.level_editor.draw()
            return
        elif self.state in ('campaign', 'paused'):
            self.campaign_mode.draw(self.canvas)
        elif self.state == 'endless':
            self.endless_mode.draw(self.canvas)

        # 2. Blit Canvas to Screen (Applying Shake)
        self.screen.blit(self.canvas, (int(self.camera.shake_offset_x), int(self.camera.shake_offset_y)))

        # 3. Post-Processing Overlays (Vignette, CRT scanlines, Stasis pulse, White flash)
        crt_on = self.save_manager.get_setting('crt_filter', True)
        self.post_processing.render_overlays(
            self.screen, self.time_scale, self.heartbeat_pulse, crt_enabled=crt_on
        )

        # 4. Mode HUD & UI Overlays
        if self.state in ('campaign', 'paused'):
            self.campaign_mode.draw_overlays(self.screen)
        elif self.state == 'endless':
            self.endless_mode.draw_overlays(self.screen)

        # 5. Pause Screen Overlay
        if self.state == 'paused':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            self.ui.render_glow_text(self.screen, "PAUSED", 64, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.38), COLOR_WHITE, COLOR_RED)
            self.ui.render_text(self.screen, "ESC: RESUME   •   R: RESTART   •   Q: QUIT TO MENU", 20, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.52), COLOR_GRAY)

        # 6. Custom Sci-Fi Tactical Crosshair
        if self.state in ('campaign', 'endless'):
            p = self.campaign_mode.player if self.state == 'campaign' else self.endless_mode.player
            cfg = p.weapon_config if p else None
            self.ui.draw_crosshair(self.screen, pygame.mouse.get_pos(), cfg)
