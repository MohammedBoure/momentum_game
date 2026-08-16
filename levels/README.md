# Level Architecture & Generation Package

This package manages campaign mission definitions, endless arena wave generation, and the interactive map editor for **MOMENTUM: Chrono Blade**.

## Files & Purposes

- [`level_data.py`](file:///C:/Users/moham/Downloads/momentum_game/levels/level_data.py): 10 handcrafted tactical campaign missions featuring progressive mechanics, speedrun par times, cover pillars, explosive hazards, destructible caches, hackable turrets, and the climactic Chrono Warden boss arena.
- [`wave_generator.py`](file:///C:/Users/moham/Downloads/momentum_game/levels/wave_generator.py): Infinite procedural survival wave generator calculating tactical threat compositions, arena pillar structures, and bonus weapon caches.
- [`level_editor.py`](file:///C:/Users/moham/Downloads/momentum_game/levels/level_editor.py): In-game drag-and-drop map creation suite allowing players to draw walls, place enemy encounters, test custom maps instantly, and export JSON scenarios.
- [`__init__.py`](file:///C:/Users/moham/Downloads/momentum_game/levels/__init__.py): Exposes level modules and wave generators.
