# -*- coding: utf-8 -*-
"""
UI and Scene Renderer for MOMENTUM: Chrono Blade.
Renders text, glows, HUD components, crosshairs, and style rank meters.
"""
import math
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GRAY, COLOR_DIM,
    COLOR_DARK, COLOR_RED, COLOR_HOT, COLOR_CYAN, COLOR_GOLD, RANK_COLORS
)

class UIRenderer:
    """Renders all game UI, HUD elements, glowing text, and crosshairs."""
    def __init__(self):
        self.font_cache = {}

    def get_font(self, size: int, bold: bool = True) -> pygame.font.Font:
        """Retrieves or creates a cached system font."""
        key = (size, bold)
        if key not in self.font_cache:
            try:
                self.font_cache[key] = pygame.font.SysFont("bahnschrift,impact,segoeui,arial", size, bold=bold)
            except Exception:
                self.font_cache[key] = pygame.font.Font(None, size)
        return self.font_cache[key]

    def render_text(self, surf: pygame.Surface, txt: str, size: int, pos: tuple,
                    color: tuple = COLOR_WHITE, anchor: str = 'center', bold: bool = True) -> pygame.Rect:
        """Renders standard crisp text with an anchor."""
        f = self.get_font(size, bold)
        ts = f.render(txt, True, color)
        rect = ts.get_rect(**{anchor: pos})
        surf.blit(ts, rect)
        return rect

    def render_glow_text(self, surf: pygame.Surface, txt: str, size: int, pos: tuple,
                         color: tuple = COLOR_WHITE, glow_color: tuple = COLOR_RED,
                         anchor: str = 'center', bold: bool = True) -> pygame.Rect:
        """Renders text with a smooth gaussian-style glow halo."""
        f = self.get_font(size, bold)
        ts = f.render(txt, True, color)
        gs = f.render(txt, True, glow_color)
        rect = ts.get_rect(**{anchor: pos})
        
        # Smoothscaled glow layer
        w, h = gs.get_size()
        if w > 0 and h > 0:
            sm = pygame.transform.smoothscale(gs, (max(1, w // 3), max(1, h // 3)))
            glow_surf = pygame.transform.smoothscale(sm, (int(w * 1.3), int(h * 1.5)))
            glow_surf.set_alpha(140)
            surf.blit(glow_surf, glow_surf.get_rect(center=rect.center))

        surf.blit(ts, rect)
        return rect

    def draw_hud(self, screen: pygame.Surface, level_title: str, level_idx: int,
                 elapsed_time: float, par_time: int, enemies_left: int,
                 player, style_score: int, max_style_target: int,
                 current_rank: str, boss_entity=None):
        """Draws the complete stylish in-game HUD."""
        # 1. Level Title & Mission Header
        self.render_text(screen, f"LEVEL {level_idx + 1} — {level_title.upper()}", 16, (SCREEN_WIDTH // 2, 36), COLOR_DIM)

        # 2. Speedrun Time & Par
        self.render_text(screen, f"TIME {elapsed_time:.1f}s", 18, (SCREEN_WIDTH - 32, 34), COLOR_GRAY, anchor='topright')
        par_col = COLOR_GOLD if elapsed_time <= par_time else COLOR_DIM
        self.render_text(screen, f"PAR {par_time}s", 14, (SCREEN_WIDTH - 32, 58), par_col, anchor='topright')

        # 3. Enemy Threat Indicators (Top Left)
        if not boss_entity:
            self.render_text(screen, "THREATS", 12, (32, 28), COLOR_DIM, anchor='topleft')
            for i in range(min(16, enemies_left)):
                x = 32 + i * 20
                pygame.draw.polygon(screen, COLOR_RED, [(x, 56), (x - 6, 44), (x + 6, 44)])
            if enemies_left > 16:
                self.render_text(screen, f"+{enemies_left - 16}", 14, (32 + 16 * 20 + 8, 48), COLOR_RED, anchor='midleft')

        # 4. Boss Health Bar (if active)
        if boss_entity and boss_entity.alive:
            bw = 480
            bh = 12
            bx = SCREEN_WIDTH // 2 - bw // 2
            by = 64
            ratio = max(0.0, boss_entity.hp / boss_entity.max_hp)
            pygame.draw.rect(screen, (20, 20, 28), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=4)
            pygame.draw.rect(screen, COLOR_RED, (bx, by, int(bw * ratio), bh), border_radius=3)
            self.render_text(screen, f"CHRONO WARDEN — {int(boss_entity.hp)} HP", 14, (SCREEN_WIDTH // 2, by - 12), COLOR_RED)

        # 5. Bottom Left: Weapon, Ammo & Chrono Focus
        if player:
            # Ammo Bars
            self.render_text(screen, f"AMMO [{player.current_weapon.upper()}]", 13, (32, SCREEN_HEIGHT - 64), COLOR_DIM, anchor='topleft')
            max_ammo_display = min(12, player.ammo)
            for i in range(max_ammo_display):
                pygame.draw.rect(screen, COLOR_WHITE, (32 + i * 14, SCREEN_HEIGHT - 44, 8, 18))
            if player.ammo > 12:
                self.render_text(screen, f"+{player.ammo - 12}", 14, (32 + 12 * 14 + 6, SCREEN_HEIGHT - 35), COLOR_WHITE, anchor='midleft')

            # Chrono Focus Gauge (Right of Ammo)
            focus_bw = 140
            focus_ratio = max(0.0, min(1.0, player.focus / player.max_focus))
            focus_col = COLOR_CYAN if focus_ratio > 0.3 else COLOR_PINK
            self.render_text(screen, "CHRONO FOCUS", 11, (240, SCREEN_HEIGHT - 64), COLOR_DIM, anchor='topleft')
            pygame.draw.rect(screen, (22, 24, 32), (240, SCREEN_HEIGHT - 44, focus_bw, 14), border_radius=3)
            pygame.draw.rect(screen, focus_col, (240, SCREEN_HEIGHT - 44, int(focus_bw * focus_ratio), 14), border_radius=3)

        # 6. Bottom Center: Style Ranking Meter
        style_bw = 260
        style_bh = 8
        style_ratio = min(1.0, style_score / max(1, max_style_target))
        sx = SCREEN_WIDTH // 2 - style_bw // 2
        sy = SCREEN_HEIGHT - 38
        
        # Rank letter & bar
        rank_color = RANK_COLORS.get(current_rank, COLOR_WHITE)
        pygame.draw.rect(screen, (24, 24, 32), (sx, sy, style_bw, style_bh), border_radius=4)
        pygame.draw.rect(screen, rank_color, (sx, sy, int(style_bw * style_ratio), style_bh), border_radius=4)
        self.render_text(screen, f"STYLE  [{current_rank}]", 13, (SCREEN_WIDTH // 2, sy - 14), rank_color)

    def draw_crosshair(self, screen: pygame.Surface, mouse_pos: tuple, weapon_config: dict):
        """Draws a crisp sci-fi tactical crosshair at the mouse position."""
        mx, my = mouse_pos
        col = weapon_config.get('color', COLOR_RED) if weapon_config else COLOR_RED
        
        # Reticle ring
        pygame.draw.circle(screen, col, (mx, my), 9, 1)
        pygame.draw.circle(screen, col, (mx, my), 2)
        
        # Reticle ticks
        pygame.draw.line(screen, col, (mx - 15, my), (mx - 10, my), 1)
        pygame.draw.line(screen, col, (mx + 10, my), (mx + 15, my), 1)
        pygame.draw.line(screen, col, (mx, my - 15), (mx, my - 10), 1)
        pygame.draw.line(screen, col, (mx, my + 10), (mx, my + 15), 1)
