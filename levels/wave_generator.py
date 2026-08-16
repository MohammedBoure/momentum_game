# -*- coding: utf-8 -*-
"""
Procedural Wave and Endless Arena Generator for MOMENTUM: Chrono Blade.
Generates dynamic combat arenas, threat budgets, enemy waves, and loot caches.
"""
import random
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def generate_arena_layout(seed: int = None) -> dict:
    """Generates procedural pillar, cover, and barrel layouts for Endless Survival arenas."""
    if seed is not None:
        random.seed(seed)

    walls = []
    crates = []
    barrels = []

    # Choose layout pattern archetype
    pattern = random.choice(['four_pillars', 'cross_divider', 'corner_bunkers', 'open_arena'])

    if pattern == 'four_pillars':
        walls = [
            (420, 200, 70, 70),
            (820, 200, 70, 70),
            (420, 450, 70, 70),
            (820, 450, 70, 70)
        ]
        barrels = [(640, 360)]
        crates = [(640, 180, 32, 32, 'ammo'), (640, 540, 32, 32, 'ammo')]

    elif pattern == 'cross_divider':
        walls = [
            (360, 250, 560, 24),
            (628, 120, 24, 480)
        ]
        barrels = [(450, 180), (830, 540)]
        crates = [(450, 540, 32, 32, 'ammo'), (830, 180, 32, 32, 'ammo')]

    elif pattern == 'corner_bunkers':
        walls = [
            (300, 150, 120, 30),
            (300, 150, 30, 120),
            (860, 150, 120, 30),
            (950, 150, 30, 120),
            (300, 540, 120, 30),
            (300, 450, 30, 120),
            (860, 540, 120, 30),
            (950, 450, 30, 120)
        ]
        barrels = [(640, 220), (640, 500)]
        crates = [(640, 360, 32, 32, 'ammo')]

    else:  # open_arena
        walls = [
            (560, 280, 160, 160)
        ]
        barrels = [(400, 200), (880, 520)]
        crates = [(400, 520, 32, 32, 'ammo'), (880, 200, 32, 32, 'ammo')]

    return {
        "walls": walls,
        "crates": crates,
        "barrels": barrels,
        "player_spawn": (180, 360)
    }

def generate_wave_enemies(wave_number: int) -> list:
    """Calculates enemy composition according to wave difficulty budget."""
    threat_budget = 4 + wave_number * 3
    enemies = []

    # Enemy point costs
    costs = {
        'grunt': 2,
        'shotgun': 4,
        'rusher': 4,
        'sniper': 5,
        'shield': 6,
        'drone': 4
    }

    # Every 5 waves, spawn a boss or elite squad
    if wave_number % 5 == 0:
        enemies.append(('boss', 960, 360))
        threat_budget -= 15

    available_types = ['grunt']
    if wave_number >= 2: available_types.append('shotgun')
    if wave_number >= 3: available_types.append('rusher')
    if wave_number >= 4: available_types.append('sniper')
    if wave_number >= 5: available_types.append('drone')
    if wave_number >= 6: available_types.append('shield')

    while threat_budget >= 2:
        kind = random.choice(available_types)
        cost = costs.get(kind, 2)
        if threat_budget >= cost:
            # Spawn in right hemisphere or perimeter
            spawn_x = random.uniform(550, 1150)
            spawn_y = random.uniform(100, 620)
            enemies.append((kind, spawn_x, spawn_y))
            threat_budget -= cost
        else:
            # Fallback to grunt
            enemies.append(('grunt', random.uniform(550, 1150), random.uniform(100, 620)))
            threat_budget -= 2

    return enemies
