# MOMENTUM: Chrono Blade

> **"Time moves only when you move."**

An intense, highly stylish cyber-noir tactical action game inspired by *SUPERHOT*, *Katana ZERO*, and *Hotline Miami*. Deflect high-speed bullet hells with your katana, execute phase dashes through laser sightlines, wield heavy kinetic firearms with ricochet physics, and master time dilation across handcrafted campaigns and endless survival arenas.

---

## Key Features & Innovations

- **Dynamic Time Dilation (Chrono Engine)**: Time slows down to 2.5% when stationary, accelerating to 100% when moving, slashing, or firing.
- **Katana Deflection & Cleaving**: Slice enemy projectiles out of the air to deflect them back at targets with lethal homing velocity.
- **Expanded Weapon Arsenal**:
  - **Katana**: Rapid light slash (bullet deflection) & charged heavy blade surge.
  - **Kinetic 9mm**: High-accuracy firearm with ricochet mechanics off solid walls.
  - **Breacher-8 Shotgun**: Devastating multi-pellet spread for close-quarters crowd control.
  - **Chrono Railgun**: Instantaneous ion beam piercing through multiple enemies.
  - **Chrono Shuriken**: Rapid throwing blade that pins hostiles.
- **Deep Tactical AI & Boss Encounters**:
  - Tactical Troopers, Shotgun Enforcers, Marksmen with laser telegraphs, Cyber Ninjas, Shield Riot Wardens, Seeker Drones, and the Multi-Phase Boss: **The Chrono Warden**.
- **Interactive & Destructible Environments**:
  - Destructible supply crates, volatile explosive barrels, breakable glass partitions, and hackable automated turrets.
- **Multiple Game Modes**:
  - **10-Stage Tactical Campaign**: Handcrafted missions with speedrun par times, style scores, and letter ranks (`D` to `S+`).
  - **Endless Survival Arena**: Procedural wave generation with between-wave **Roguelike Upgrade Perks** (Overclocked Katana, Ricochet Dynamics, Chrono Battery, Leeching Parry, etc.).
  - **Integrated Map & Level Editor**: Build custom combat maps with drag-box wall placement, entity tools, and instant playtesting.
- **Procedural Audiovisual Suite**:
  - Pure DSP procedural audio synthesizer generating 18+ sound effects and dynamic multi-track cyberpunk music that slows tempo and filters frequencies during temporal stasis.
  - CRT scanlines, trauma screen shake, chromatic aberration, persistent blood stains, and stylized combat floaters.

---

## Directory Architecture

- [`main.py`](file:///C:/Users/moham/Downloads/momentum_game/main.py): Primary executable entry point initializing hardware display and launching the master engine.
- [`core/`](file:///C:/Users/moham/Downloads/momentum_game/core/README.md): Core systems including constants, dynamic camera with screen shake, save data manager, and the central engine state machine.
- [`audio/`](file:///C:/Users/moham/Downloads/momentum_game/audio/README.md): Procedural waveform synthesizer, sound effects library, and adaptive dynamic music sequencer.
- [`entities/`](file:///C:/Users/moham/Downloads/momentum_game/entities/README.md): Actor physics, player controller, enemy AI state machines, weapon projectiles, and interactive environmental objects.
- [`gfx/`](file:///C:/Users/moham/Downloads/momentum_game/gfx/README.md): Particle physics, blood splatters, post-processing overlays (CRT scanlines, vignettes, hitstop), and HUD renderer.
- [`levels/`](file:///C:/Users/moham/Downloads/momentum_game/levels/README.md): Campaign mission layouts, procedural endless wave generators, and the in-game map editor.
- [`modes/`](file:///C:/Users/moham/Downloads/momentum_game/modes/README.md): Mode managers for the story campaign, endless survival arena, and main menu systems.

---

## Controls

| Action | Input |
| :--- | :--- |
| **Movement** | `W`, `A`, `S`, `D` or `Arrow Keys` |
| **Aim / Reticle** | `Mouse Cursor` |
| **Katana Slash / Deflect** | `Left Mouse Button` |
| **Fire Ranged Weapon** | `Right Mouse Button` |
| **Switch Weapon** | `1`, `2`, `3`, `4` or `Mouse Scrollwheel` |
| **Chrono Dash** | `Spacebar` or `Left Shift` |
| **Chrono Focus** | `E` (Hold) |
| **Restart Level** | `R` |
| **Toggle Music** | `M` |
| **Pause / Back** | `ESC` |

---

## Quickstart

Install dependencies and run the game:

```bash
pip install -r requirements.txt
python main.py
```
