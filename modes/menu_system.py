# -*- coding: utf-8 -*-
"""
Menu, Level Select, and Options Management for MOMENTUM: Chrono Blade.
Includes animated cyber-noir main menu, level selection with rank badges, settings configuration, and controls guide.
"""
import math
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_WALL_EDGE, COLOR_WHITE,
    COLOR_RED, COLOR_HOT, COLOR_CYAN, COLOR_GOLD, COLOR_GRAY, COLOR_DIM,
    RANK_COLORS
)

class MenuSystem:
    """Manages main menu navigation, level selection, options, and controls overlays."""
    def __init__(self, engine, save_manager, sound_lib, ui_renderer):
        self.engine = engine
        self.save_manager = save_manager
        self.sound_lib = sound_lib
        self.ui = ui_renderer

        self.current_screen = 'main'  # 'main', 'level_select', 'options', 'controls'
        self.main_options = ['CAMPAIGN', 'ENDLESS SURVIVAL', 'LEVEL SELECT', 'MAP EDITOR', 'OPTIONS', 'CONTROLS', 'QUIT']
        self.main_selected = 0
        self.level_selected = 0
        self.options_selected = 0
        self.anim_t = 0.0

    def handle_event(self, ev: pygame.event.Event, campaign_levels: list) -> str:
        """Processes navigation inputs. Returns an action string if an item is confirmed."""
        if ev.type == pygame.KEYDOWN:
            # ----------------------------------------------------
            # Main Menu Navigation
            # ----------------------------------------------------
            if self.current_screen == 'main':
                if ev.key in (pygame.K_UP, pygame.K_w):
                    self.main_selected = (self.main_selected - 1) % len(self.main_options)
                    self.sound_lib.play('ui_hover', throttle=0.0)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self.main_selected = (self.main_selected + 1) % len(self.main_options)
                    self.sound_lib.play('ui_hover', throttle=0.0)
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self.sound_lib.play('ui_click', throttle=0.0)
                    choice = self.main_options[self.main_selected]
                    if choice == 'CAMPAIGN':
                        return 'start_campaign'
                    elif choice == 'ENDLESS SURVIVAL':
                        return 'start_endless'
                    elif choice == 'LEVEL SELECT':
                        self.current_screen = 'level_select'
                        self.level_selected = min(self.save_manager.data['unlocked_level'] - 1, len(campaign_levels) - 1)
                    elif choice == 'MAP EDITOR':
                        return 'start_editor'
                    elif choice == 'OPTIONS':
                        self.current_screen = 'options'
                    elif choice == 'CONTROLS':
                        self.current_screen = 'controls'
                    elif choice == 'QUIT':
                        return 'quit'

            # ----------------------------------------------------
            # Level Select Navigation
            # ----------------------------------------------------
            elif self.current_screen == 'level_select':
                unlocked = self.save_manager.data.get('unlocked_level', 1)
                if ev.key in (pygame.K_UP, pygame.K_w):
                    self.level_selected = max(0, self.level_selected - 1)
                    self.sound_lib.play('ui_hover', throttle=0.0)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self.level_selected = min(min(unlocked - 1, len(campaign_levels) - 1), self.level_selected + 1)
                    self.sound_lib.play('ui_hover', throttle=0.0)
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self.sound_lib.play('ui_click', throttle=0.0)
                    return f'play_level_{self.level_selected}'
                elif ev.key == pygame.K_ESCAPE:
                    self.current_screen = 'main'
                    self.sound_lib.play('ui_click', throttle=0.0)

            # ----------------------------------------------------
            # Options Navigation
            # ----------------------------------------------------
            elif self.current_screen == 'options':
                if ev.key in (pygame.K_UP, pygame.K_w):
                    self.options_selected = max(0, self.options_selected - 1)
                    self.sound_lib.play('ui_hover', throttle=0.0)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self.options_selected = min(4, self.options_selected + 1)
                    self.sound_lib.play('ui_hover', throttle=0.0)
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    self._adjust_option(-1)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
                    self._adjust_option(1)
                elif ev.key == pygame.K_ESCAPE:
                    self.current_screen = 'main'
                    self.sound_lib.play('ui_click', throttle=0.0)

            # ----------------------------------------------------
            # Controls Navigation
            # ----------------------------------------------------
            elif self.current_screen == 'controls':
                if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    self.current_screen = 'main'
                    self.sound_lib.play('ui_click', throttle=0.0)

        return None

    def _adjust_option(self, delta: int):
        """Adjusts audio and visual options."""
        sm = self.save_manager
        if self.options_selected == 0:  # Master Volume
            cur = sm.get_setting('master_volume', 0.8)
            new_v = max(0.0, min(1.0, round(cur + delta * 0.1, 1)))
            sm.set_setting('master_volume', new_v)
            self.sound_lib.update_volume(new_v, sm.get_setting('sfx_volume', 0.9))
            self.engine.music_engine.update_volume(new_v, sm.get_setting('music_volume', 0.6))
        elif self.options_selected == 1:  # SFX Volume
            cur = sm.get_setting('sfx_volume', 0.9)
            new_v = max(0.0, min(1.0, round(cur + delta * 0.1, 1)))
            sm.set_setting('sfx_volume', new_v)
            self.sound_lib.update_volume(sm.get_setting('master_volume', 0.8), new_v)
        elif self.options_selected == 2:  # Music Volume
            cur = sm.get_setting('music_volume', 0.6)
            new_v = max(0.0, min(1.0, round(cur + delta * 0.1, 1)))
            sm.set_setting('music_volume', new_v)
            self.engine.music_engine.update_volume(sm.get_setting('master_volume', 0.8), new_v)
        elif self.options_selected == 3:  # CRT Filter
            cur = sm.get_setting('crt_filter', True)
            sm.set_setting('crt_filter', not cur)
        elif self.options_selected == 4:  # Screen Shake
            cur = sm.get_setting('screen_shake', 1.0)
            new_v = max(0.0, min(2.0, round(cur + delta * 0.25, 2)))
            sm.set_setting('screen_shake', new_v)

        self.sound_lib.play('ui_click', throttle=0.0)

    def update(self, dt: float):
        self.anim_t += dt

    def draw(self, screen: pygame.Surface, campaign_levels: list):
        """Draws current menu screen."""
        screen.fill(COLOR_BG)
        bob = math.sin(self.anim_t * 1.5) * 4.0

        if self.current_screen == 'main':
            # Background glowing elements
            drift = math.sin(self.anim_t * 0.6) * 12.0
            pygame.draw.line(screen, (80, 20, 30), (SCREEN_WIDTH // 2 - 350, 185 + bob), (SCREEN_WIDTH // 2 + 350, 185 + bob), 2)

            # Master Titles
            self.ui.render_glow_text(screen, "MOMENTUM", 88, (SCREEN_WIDTH // 2, 110 + bob), COLOR_WHITE, COLOR_RED)
            self.ui.render_text(screen, "C H R O N O   B L A D E", 20, (SCREEN_WIDTH // 2, 165 + bob), COLOR_RED)

            # Main Options
            top_y = 230
            for i, opt in enumerate(self.main_options):
                y = top_y + i * 44
                is_sel = (i == self.main_selected)
                col = COLOR_WHITE if is_sel else COLOR_GRAY
                prefix = "► " if is_sel else "  "
                self.ui.render_text(screen, prefix + opt, 22, (SCREEN_WIDTH // 2, y), col)

            # Global Stats & Hints Footer
            total_deaths = self.save_manager.data.get('total_deaths', 0)
            total_kills = self.save_manager.data.get('total_kills', 0)
            total_deflects = self.save_manager.data.get('total_deflects', 0)
            self.ui.render_text(screen, f"KILLS: {total_kills}   •   DEFLECTS: {total_deflects}   •   DEATHS: {total_deaths}", 14, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 38), COLOR_DIM)

        elif self.current_screen == 'level_select':
            self.ui.render_glow_text(screen, "CAMPAIGN MISSIONS", 48, (SCREEN_WIDTH // 2, 60), COLOR_WHITE, COLOR_RED)
            unlocked_count = self.save_manager.data.get('unlocked_level', 1)
            ranks_map = self.save_manager.data.get('ranks', {})
            best_times = self.save_manager.data.get('best_times', {})

            top_y = 130
            for i, lv in enumerate(campaign_levels):
                is_unlocked = (i + 1 <= unlocked_count)
                is_sel = (i == self.level_selected)
                y = top_y + i * 46

                col = COLOR_WHITE if is_sel else (COLOR_GRAY if is_unlocked else (40, 42, 52))
                prefix = "► " if is_sel else "  "
                title = f"{i + 1}. {lv['name'].upper()}" if is_unlocked else f"{i + 1}. [LOCKED]"
                self.ui.render_text(screen, prefix + title, 20, (SCREEN_WIDTH // 2 - 240, y), col, anchor='midleft')

                if is_unlocked:
                    rk = ranks_map.get(str(i), '—')
                    rk_col = RANK_COLORS.get(rk, COLOR_DIM)
                    self.ui.render_text(screen, f"RANK: {rk}", 18, (SCREEN_WIDTH // 2 + 150, y), rk_col)
                    bt = best_times.get(str(i))
                    if bt:
                        self.ui.render_text(screen, f"{bt:.1f}s", 16, (SCREEN_WIDTH // 2 + 270, y), COLOR_GRAY, anchor='midleft')

            self.ui.render_text(screen, "↑/↓ SELECT   •   ENTER PLAY   •   ESC BACK", 16, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 34), COLOR_DIM)

        elif self.current_screen == 'options':
            self.ui.render_glow_text(screen, "SETTINGS", 48, (SCREEN_WIDTH // 2, 70), COLOR_WHITE, COLOR_CYAN)
            opts = [
                ("MASTER VOLUME", f"{int(self.save_manager.get_setting('master_volume', 0.8) * 100)}%"),
                ("SFX VOLUME", f"{int(self.save_manager.get_setting('sfx_volume', 0.9) * 100)}%"),
                ("MUSIC VOLUME", f"{int(self.save_manager.get_setting('music_volume', 0.6) * 100)}%"),
                ("CRT SCANLINES", "ENABLED" if self.save_manager.get_setting('crt_filter', True) else "DISABLED"),
                ("SCREEN SHAKE", f"{int(self.save_manager.get_setting('screen_shake', 1.0) * 100)}%")
            ]

            top_y = 180
            for i, (label, val) in enumerate(opts):
                y = top_y + i * 65
                is_sel = (i == self.options_selected)
                col = COLOR_CYAN if is_sel else COLOR_GRAY
                prefix = "► " if is_sel else "  "
                self.ui.render_text(screen, prefix + label, 20, (SCREEN_WIDTH // 2 - 180, y), col, anchor='midleft')
                self.ui.render_text(screen, f"[{val}]", 20, (SCREEN_WIDTH // 2 + 180, y), COLOR_WHITE, anchor='midright')

            self.ui.render_text(screen, "←/→ ADJUST   •   ESC BACK", 16, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 45), COLOR_DIM)

        elif self.current_screen == 'controls':
            self.ui.render_glow_text(screen, "COMBAT MANUAL", 46, (SCREEN_WIDTH // 2, 60), COLOR_WHITE, COLOR_RED)
            
            instructions = [
                ("WASD / ARROWS", "Move character. Time moves at normal speed only while moving!"),
                ("MOUSE AIM", "Aim crosshair towards targets and incoming bullets."),
                ("LEFT CLICK", "Katana Slash. Cuts enemies and deflects enemy bullets!"),
                ("RIGHT CLICK", "Fire active ranged firearm (Pistol, Shotgun, Railgun)."),
                ("1 / 2 / 3 / 4", "Switch weapons (Kinetic 9mm, Breacher Shotgun, Railgun, Shuriken)."),
                ("SPACE / SHIFT", "Chrono Dash. Invulnerable phase dash through bullet barrages."),
                ("E (HOLD)", "Chrono Focus. Slow down time using temporal battery."),
                ("R KEY", "Restart mission instantly upon defeat or to improve speedrun time."),
                ("M KEY", "Toggle dynamic synth soundtrack.")
            ]

            top_y = 135
            for i, (key_label, desc) in enumerate(instructions):
                y = top_y + i * 46
                self.ui.render_text(screen, key_label, 17, (SCREEN_WIDTH // 2 - 380, y), COLOR_CYAN, anchor='midleft')
                self.ui.render_text(screen, desc, 16, (SCREEN_WIDTH // 2 - 140, y), COLOR_WHITE, anchor='midleft')

            self.ui.render_text(screen, "PRESS ESC OR ENTER TO RETURN", 16, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35), COLOR_GRAY)
