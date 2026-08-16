# -*- coding: utf-8 -*-
"""
MOMENTUM: Chrono Blade
Main Executable Entry Point.

Time moves only when you move.
Master the Katana, deflect enemy bullet storms, execute temporal dashes,
and conquer handcrafted tactical campaigns and endless survival arenas.
"""
import os
import sys
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, AUDIO_SAMPLE_RATE,
    AUDIO_CHANNELS, AUDIO_BUFFER_SIZE, COLOR_BG, COLOR_RED, COLOR_WHITE
)
from core.engine import GameEngine

def create_window_icon() -> pygame.Surface:
    """Generates an embedded tactical icon for the window."""
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    icon.fill((12, 12, 18))
    # Katana blade line
    pygame.draw.line(icon, COLOR_WHITE, (4, 28), (24, 6), 3)
    # Glowing tip
    pygame.draw.line(icon, COLOR_RED, (24, 6), (28, 2), 4)
    # Cross guard
    pygame.draw.line(icon, COLOR_RED, (8, 20), (14, 26), 2)
    return icon

def main():
    """Initializes Pygame, hardware mixer, window, and starts engine loop."""
    # Pre-init audio for low-latency DSP synthesis
    audio_enabled = False
    try:
        pygame.mixer.pre_init(AUDIO_SAMPLE_RATE, -16, 1, AUDIO_BUFFER_SIZE)
    except Exception as e:
        print(f"[Init] Mixer pre-init warning: {e}")

    pygame.init()

    try:
        pygame.mixer.set_num_channels(AUDIO_CHANNELS)
        audio_enabled = pygame.mixer.get_init() is not None
    except Exception as e:
        print(f"[Init] Mixer init warning: {e}")
        audio_enabled = False

    # Initialize Scaled Display Surface
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
    pygame.display.set_caption(WINDOW_TITLE)
    pygame.display.set_icon(create_window_icon())

    print("\n" + "=" * 60)
    print("  MOMENTUM: Chrono Blade")
    print("  Time moves only when you move!")
    print("=" * 60)
    print("  • WASD / Arrows : Movement")
    print("  • Mouse Cursor  : Aim & Crosshair")
    print("  • Left Click    : Katana Slash (Deflects enemy bullets!)")
    print("  • Right Click   : Fire Gun (Kinetic Pistol / Shotgun / Railgun)")
    print("  • 1 / 2 / 3 / 4 : Switch Weapons (Pistol, Shotgun, Railgun, Shuriken)")
    print("  • Space / Shift : Chrono Dash (Invulnerable phase shift)")
    print("  • E (Hold)      : Chrono Focus (Slow-motion stasis battery)")
    print("  • R Key         : Instant Restart Level")
    print("  • M Key         : Dynamic Cyberpunk Music Toggle")
    print("  • ESC Key       : Pause / Back to Menu")
    print("=" * 60 + "\n")

    # Launch Master Engine
    engine = GameEngine(screen, audio_enabled=audio_enabled)
    engine.run()

if __name__ == "__main__":
    main()
