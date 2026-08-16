# Game Modes & Menus Package

This package manages all primary gameplay states, level transitions, survival wave defense, roguelike perk drafting, and interface menus for **MOMENTUM: Chrono Blade**.

## Files & Purposes

- [`campaign.py`](file:///C:/Users/moham/Downloads/momentum_game/modes/campaign.py): Tactical story mission mode tracking level completion, bullet deflections, speedrun split timers, style combos, cinematic slow-motion killcams, and performance ranks (D to S+).
- [`endless.py`](file:///C:/Users/moham/Downloads/momentum_game/modes/endless.py): Infinite wave survival mode featuring dynamic threat budget scaling, boss wave encounters, and between-wave roguelike perk selections (e.g. Overclocked Katana, Ricochet Dynamics, Chrono Battery, Leeching Parry).
- [`menu_system.py`](file:///C:/Users/moham/Downloads/momentum_game/modes/menu_system.py): Animated cyber-noir main menu, interactive level selection with rank medals and records, audio/visual options sliders (SFX, Music, CRT scanlines, screen shake), and combat manual guide.
- [`__init__.py`](file:///C:/Users/moham/Downloads/momentum_game/modes/__init__.py): Exposes game modes and menu controllers.
