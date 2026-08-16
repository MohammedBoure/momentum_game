# -*- coding: utf-8 -*-
"""
Level Definitions and Campaign Data for MOMENTUM: Chrono Blade.
Defines 10 handcrafted tactical levels with diverse geometries, hazards, crates, turrets, and enemy encounters.
"""

CAMPAIGN_LEVELS = [
    # ----------------------------------------------------
    # Level 1: First Contact
    # ----------------------------------------------------
    {
        "name": "First Contact",
        "description": "Time moves only when you move. Deflect bullets with your Katana.",
        "par_time": 6,
        "player_spawn": (200, 360),
        "walls": [
            # Outer boundary is added automatically by engine
        ],
        "crates": [],
        "barrels": [],
        "turrets": [],
        "ammo_pickups": [],
        "chrono_pickups": [(200, 240, 50)],
        "enemies": [
            ("grunt", 820, 240),
            ("grunt", 860, 480)
        ]
    },

    # ----------------------------------------------------
    # Level 2: The Breach
    # ----------------------------------------------------
    {
        "name": "The Breach",
        "description": "Explosive barrels can clear entire rooms. Aim carefully.",
        "par_time": 9,
        "player_spawn": (180, 360),
        "walls": [
            (520, 100, 32, 220),
            (520, 400, 32, 220)
        ],
        "crates": [(520, 360, 32, 32, 'ammo')],
        "barrels": [(850, 360)],
        "turrets": [],
        "ammo_pickups": [(200, 180, 4)],
        "chrono_pickups": [],
        "enemies": [
            ("grunt", 780, 220),
            ("grunt", 780, 500),
            ("grunt", 940, 360)
        ]
    },

    # ----------------------------------------------------
    # Level 3: Cover Me
    # ----------------------------------------------------
    {
        "name": "Cover Me",
        "description": "Shotgun Enforcers blast wide spreads. Time your deflects.",
        "par_time": 12,
        "player_spawn": (160, 360),
        "walls": [
            (480, 140, 36, 200),
            (480, 420, 36, 200),
            (760, 260, 36, 200)
        ],
        "crates": [(620, 360, 32, 32, 'ammo')],
        "barrels": [(1020, 200)],
        "turrets": [],
        "ammo_pickups": [],
        "chrono_pickups": [(160, 180, 40)],
        "enemies": [
            ("grunt", 880, 180),
            ("shotgun", 960, 360),
            ("grunt", 880, 540)
        ]
    },

    # ----------------------------------------------------
    # Level 4: Patience
    # ----------------------------------------------------
    {
        "name": "Patience",
        "description": "Snipers telegraph with red laser pointers. Dash or parry.",
        "par_time": 14,
        "player_spawn": (150, 580),
        "walls": [
            (540, 260, 180, 180),
            (320, 140, 140, 28)
        ],
        "crates": [(540, 500, 32, 32, 'ammo')],
        "barrels": [(1080, 480)],
        "turrets": [],
        "ammo_pickups": [(150, 200, 4)],
        "chrono_pickups": [(150, 450, 40)],
        "enemies": [
            ("sniper", 1120, 140),
            ("grunt", 780, 580),
            ("grunt", 1020, 580)
        ]
    },

    # ----------------------------------------------------
    # Level 5: Rush Hour
    # ----------------------------------------------------
    {
        "name": "Rush Hour",
        "description": "Cyber Ninjas charge at blinding speed. Strike before they dash.",
        "par_time": 12,
        "player_spawn": (160, 360),
        "walls": [
            (400, 24, 36, 420),
            (820, 276, 36, 420)
        ],
        "crates": [(610, 360, 32, 32, 'ammo')],
        "barrels": [(610, 140)],
        "turrets": [],
        "ammo_pickups": [(610, 580, 6)],
        "chrono_pickups": [],
        "enemies": [
            ("rusher", 650, 360),
            ("grunt", 580, 120),
            ("rusher", 1080, 540),
            ("grunt", 1080, 180)
        ]
    },

    # ----------------------------------------------------
    # Level 6: The Vault
    # ----------------------------------------------------
    {
        "name": "The Vault",
        "description": "Hack defensive turrets to turn security against the enforcers.",
        "par_time": 16,
        "player_spawn": (140, 360),
        "walls": [
            (420, 180, 80, 80),
            (780, 180, 80, 80),
            (420, 460, 80, 80),
            (780, 460, 80, 80)
        ],
        "crates": [(600, 360, 32, 32, 'ammo'), (600, 200, 32, 32, 'ammo')],
        "barrels": [(1080, 180), (1080, 540)],
        "turrets": [(600, 360, 0.0)],
        "ammo_pickups": [(140, 140, 4)],
        "chrono_pickups": [(140, 580, 50)],
        "enemies": [
            ("shotgun", 600, 120),
            ("shield", 920, 360),
            ("grunt", 600, 600),
            ("rusher", 1100, 140),
            ("sniper", 1140, 600)
        ]
    },

    # ----------------------------------------------------
    # Level 7: Crossfire
    # ----------------------------------------------------
    {
        "name": "Crossfire",
        "description": "Twin snipers pin the perimeter. Shield Troopers block frontal fire.",
        "par_time": 18,
        "player_spawn": (150, 360),
        "walls": [
            (260, 230, 680, 24),
            (340, 466, 680, 24)
        ],
        "crates": [(600, 360, 32, 32, 'ammo')],
        "barrels": [(880, 360)],
        "turrets": [],
        "ammo_pickups": [(150, 140, 4)],
        "chrono_pickups": [(150, 580, 50)],
        "enemies": [
            ("sniper", 1140, 120),
            ("sniper", 1140, 600),
            ("shield", 700, 360),
            ("shotgun", 500, 120),
            ("drone", 860, 120)
        ]
    },

    # ----------------------------------------------------
    # Level 8: The Labyrinth
    # ----------------------------------------------------
    {
        "name": "The Labyrinth",
        "description": "Navigate tight corridors with mixed combat squads.",
        "par_time": 22,
        "player_spawn": (120, 360),
        "walls": [
            (260, 24, 28, 440),
            (500, 256, 28, 440),
            (740, 24, 28, 440),
            (980, 256, 28, 440)
        ],
        "crates": [(380, 360, 32, 32, 'ammo'), (860, 360, 32, 32, 'ammo')],
        "barrels": [(620, 580), (1120, 140)],
        "turrets": [],
        "ammo_pickups": [(120, 620, 6)],
        "chrono_pickups": [(120, 140, 60)],
        "enemies": [
            ("rusher", 380, 580),
            ("grunt", 620, 120),
            ("shotgun", 860, 580),
            ("drone", 860, 120),
            ("sniper", 1140, 120),
            ("rusher", 1140, 580)
        ]
    },

    # ----------------------------------------------------
    # Level 9: Citadel Infiltration
    # ----------------------------------------------------
    {
        "name": "Citadel Infiltration",
        "description": "The inner sanctum garrison. Eliminate all hostiles.",
        "par_time": 25,
        "player_spawn": (140, 360),
        "walls": [
            (540, 280, 180, 160),
            (360, 160, 64, 64),
            (840, 160, 64, 64),
            (360, 496, 64, 64),
            (840, 496, 64, 64)
        ],
        "crates": [(630, 200, 32, 32, 'ammo'), (630, 520, 32, 32, 'ammo')],
        "barrels": [(630, 80), (630, 640), (1050, 360)],
        "turrets": [(630, 360, 0.0)],
        "ammo_pickups": [(140, 120, 6), (140, 600, 6)],
        "chrono_pickups": [(630, 360, 80)],
        "enemies": [
            ("sniper", 1150, 110),
            ("sniper", 1150, 610),
            ("shotgun", 680, 160),
            ("shotgun", 680, 560),
            ("shield", 900, 360),
            ("rusher", 980, 180),
            ("drone", 480, 110),
            ("drone", 480, 610)
        ]
    },

    # ----------------------------------------------------
    # Level 10: The Chrono Warden (BOSS FIGHT)
    # ----------------------------------------------------
    {
        "name": "The Chrono Warden",
        "description": "MASTER TIME ITSELF. Defeat the Warden of Temporal Stasis.",
        "par_time": 35,
        "player_spawn": (160, 360),
        "walls": [
            (440, 180, 40, 120),
            (440, 420, 40, 120),
            (840, 180, 40, 120),
            (840, 420, 40, 120)
        ],
        "crates": [(640, 120, 32, 32, 'ammo'), (640, 600, 32, 32, 'ammo')],
        "barrels": [(440, 360), (840, 360)],
        "turrets": [],
        "ammo_pickups": [(160, 120, 6), (160, 600, 6)],
        "chrono_pickups": [(640, 360, 100)],
        "enemies": [
            ("boss", 960, 360)
        ]
    }
]
