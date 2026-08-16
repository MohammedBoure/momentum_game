# -*- coding: utf-8 -*-
"""
Post-Processing Effects and Screen Overlays for MOMENTUM: Chrono Blade.
Includes procedural CRT scanlines, dynamic temporal vignettes, chromatic glitch shifts, and hitstop management.
"""
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE

class PostProcessingManager:
    """Renders layered fullscreen visual effects and handles hitstop/screen flashes."""
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        
        # Pre-rendered surface overlays
        self.vignette_surf = self._create_vignette(width, height)
        self.red_vignette_surf = self._create_red_vignette(width, height)
        self.scanline_surf = self._create_scanlines(width, height)
        self.flash_surf = pygame.Surface((width, height))
        
        # State variables
        self.white_flash = 0.0
        self.red_flash = 0.0
        self.freeze_frames = 0.0
        self.chromatic_aberration = 0.0

    def _create_vignette(self, w: int, h: int) -> pygame.Surface:
        """Creates a smooth dark vignette surface."""
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        steps = 28
        for j in range(steps):
            alpha = int(70 * ((steps - j) / steps) ** 2)
            rect = pygame.Rect(0, 0, w, h).inflate(-j * 24, -j * 18)
            pygame.draw.rect(s, (0, 0, 0, alpha), rect, 30)
        return s

    def _create_red_vignette(self, w: int, h: int) -> pygame.Surface:
        """Creates a pulsing crimson vignette for time-freeze stasis."""
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        steps = 22
        for j in range(steps):
            alpha = int(50 * ((steps - j) / steps) ** 2)
            rect = pygame.Rect(0, 0, w, h).inflate(-j * 32, -j * 24)
            pygame.draw.rect(s, (130, 0, 15, alpha), rect, 36)
        return s

    def _create_scanlines(self, w: int, h: int) -> pygame.Surface:
        """Creates subtle retro CRT scanlines."""
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(s, (0, 0, 0, 16), (0, y), (w, y))
        return s

    def trigger_white_flash(self, intensity: float = 0.16):
        """Triggers a bright white screen flash on perfect deflects."""
        self.white_flash = max(self.white_flash, intensity)

    def trigger_red_flash(self, intensity: float = 0.3):
        """Triggers a red vignette pulse on damage."""
        self.red_flash = max(self.red_flash, intensity)

    def trigger_hitstop(self, duration: float = 0.04):
        """Freezes frame execution briefly for intense game feel."""
        self.freeze_frames = max(self.freeze_frames, duration)

    def trigger_chromatic(self, intensity: float = 0.15):
        """Triggers a brief RGB lens split."""
        self.chromatic_aberration = max(self.chromatic_aberration, intensity)

    def update(self, dt: float) -> bool:
        """
        Updates effect decay timers. Returns True if frame is frozen by hitstop.
        """
        if self.freeze_frames > 0:
            self.freeze_frames -= dt
            return True  # Freeze frame active

        self.white_flash = max(0.0, self.white_flash - dt * 3.5)
        self.red_flash = max(0.0, self.red_flash - dt * 2.5)
        self.chromatic_aberration = max(0.0, self.chromatic_aberration - dt * 4.0)
        return False

    def render_overlays(self, screen: pygame.Surface, time_scale: float, heartbeat_pulse: float, crt_enabled: bool = True):
        """Renders all post-processing passes onto the main screen surface."""
        # 1. White Flash (Deflect / Super)
        if self.white_flash > 0:
            self.flash_surf.fill(COLOR_WHITE)
            alpha = int(180 * min(1.0, self.white_flash / 0.16))
            self.flash_surf.set_alpha(alpha)
            screen.blit(self.flash_surf, (0, 0))

        # 2. Stasis Red Vignette (During Time Slowdown)
        if time_scale < 0.6:
            stasis_intensity = (1.0 - time_scale / 0.6)
            alpha = int(stasis_intensity * 180 + heartbeat_pulse * 55)
            self.red_vignette_surf.set_alpha(min(255, alpha))
            screen.blit(self.red_vignette_surf, (0, 0))

        # 3. Retro CRT Scanlines
        if crt_enabled:
            screen.blit(self.scanline_surf, (0, 0))

        # 4. Master Dark Vignette
        screen.blit(self.vignette_surf, (0, 0))
