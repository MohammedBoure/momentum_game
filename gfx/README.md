# Visual & Graphics Engine Package

This package manages all visual effects, particle physics, blood splatters, screen filters, and HUD rendering for **MOMENTUM: Chrono Blade**.

## Files & Purposes

- [`particles.py`](file:///C:/Users/moham/Downloads/momentum_game/gfx/particles.py): Comprehensive particle simulation containing blood burst sprays, persistent floor stains, fiery impact sparks, animated floating text badges, and expanding shockwave rings.
- [`effects.py`](file:///C:/Users/moham/Downloads/momentum_game/gfx/effects.py): Real-time fullscreen post-processing effects including CRT scanlines, dark vignettes, pulsing crimson stasis overlays, chromatic aberration lens distortions, white screen flash on bullet deflects, and hitstop freeze frames.
- [`renderer.py`](file:///C:/Users/moham/Downloads/momentum_game/gfx/renderer.py): Font caching system, glowing title text renderer, in-game HUD (speedrun timer, par time, ammo counters, Chrono Focus gauge, style rank gauge), boss health bars, and tactical dynamic crosshairs.
- [`__init__.py`](file:///C:/Users/moham/Downloads/momentum_game/gfx/__init__.py): Exposes graphics rendering and VFX modules.
