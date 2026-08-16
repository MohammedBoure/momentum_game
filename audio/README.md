# Audio Engine Package

This package manages pure procedural waveform synthesis, dynamic sound effects, and adaptive cyberpunk music loops without requiring external audio files.

## Files & Purposes

- [`synthesizer.py`](file:///C:/Users/moham/Downloads/momentum_game/audio/synthesizer.py): Low-level mathematical DSP audio generator supporting sine, square, triangle, saw waves, ADR envelopes, frequency sweeps, low-pass filtered noise, and buffer conversion to Pygame Sound objects.
- [`sound_effects.py`](file:///C:/Users/moham/Downloads/momentum_game/audio/sound_effects.py): Rich library of 18+ synthesized sound effects including katana slashes, heavy cleaves, bullet deflections, shotgun blasts, railgun piercers, explosions, heartbeats, and UI chimes.
- [`music_engine.py`](file:///C:/Users/moham/Downloads/momentum_game/audio/music_engine.py): Multi-track procedural music sequencer featuring dynamic time dilation volume and low-pass adaptation when time freezes.
- [`__init__.py`](file:///C:/Users/moham/Downloads/momentum_game/audio/__init__.py): Exposes procedural synthesis and audio systems.
