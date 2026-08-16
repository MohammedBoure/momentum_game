# -*- coding: utf-8 -*-
"""
Sound Effects Engine and SFX Library for MOMENTUM: Chrono Blade.
Synthesizes all weapon fire, bullet deflections, katana strikes, explosions, and UI feedback.
"""
import pygame
from audio.synthesizer import (
    generate_tone, generate_noise, mix_tracks, samples_to_sound, DummySound
)

class SoundLibrary:
    """Stores and plays synthesized sound effects with rate throttling and volume scaling."""
    def __init__(self, audio_enabled: bool = True):
        self.audio_enabled = audio_enabled
        self.sounds = {}
        self.last_played = {}
        self.master_volume = 0.8
        self.sfx_volume = 0.9

        if self.audio_enabled:
            self._build_all_sfx()

    def _build_all_sfx(self):
        """Generates all in-game sound effect waveforms."""
        # 1. Katana Light Slash
        slash_layers = [
            (0.00, generate_noise(0.08, volume=0.45, lowpass_factor=0.85, decay_exp=2.5)),
            (0.01, generate_tone(0.07, freq_start=680, freq_end=220, wave_type='triangle', volume=0.25))
        ]
        self.sounds['slash'] = samples_to_sound(mix_tracks(slash_layers), self.audio_enabled)

        # 2. Katana Heavy Slash / Blade Surge
        heavy_slash_layers = [
            (0.00, generate_noise(0.16, volume=0.7, lowpass_factor=0.9, decay_exp=1.8)),
            (0.02, generate_tone(0.18, freq_start=450, freq_end=80, wave_type='saw', volume=0.45)),
            (0.00, generate_tone(0.14, freq_start=120, freq_end=40, wave_type='sine', volume=0.7))
        ]
        self.sounds['heavy_slash'] = samples_to_sound(mix_tracks(heavy_slash_layers), self.audio_enabled)

        # 3. Bullet Deflect / Blade Parry
        deflect_layers = [
            (0.00, generate_tone(0.18, freq_start=1520, freq_end=1080, wave_type='sine', volume=0.45)),
            (0.00, generate_tone(0.10, freq_start=2280, freq_end=1980, wave_type='square', volume=0.15)),
            (0.00, generate_noise(0.04, volume=0.35, lowpass_factor=0.95))
        ]
        self.sounds['deflect'] = samples_to_sound(mix_tracks(deflect_layers), self.audio_enabled)

        # 4. Perfect Parry Surge
        perfect_parry_layers = [
            (0.00, generate_tone(0.35, freq_start=880, freq_end=1760, wave_type='sine', volume=0.5)),
            (0.05, generate_tone(0.25, freq_start=2640, freq_end=1320, wave_type='triangle', volume=0.3)),
            (0.00, generate_noise(0.20, volume=0.5, lowpass_factor=0.6))
        ]
        self.sounds['perfect_parry'] = samples_to_sound(mix_tracks(perfect_parry_layers), self.audio_enabled)

        # 5. Pistol Shoot
        pistol_layers = [
            (0.00, generate_noise(0.09, volume=0.6, lowpass_factor=0.4, decay_exp=3.0)),
            (0.00, generate_tone(0.08, freq_start=180, freq_end=60, wave_type='sine', volume=0.55))
        ]
        self.sounds['shoot_pistol'] = samples_to_sound(mix_tracks(pistol_layers), self.audio_enabled)

        # 6. Shotgun Blast
        shotgun_layers = [
            (0.00, generate_noise(0.22, volume=0.85, lowpass_factor=0.35, decay_exp=1.5)),
            (0.00, generate_tone(0.16, freq_start=220, freq_end=35, wave_type='sine', volume=0.75)),
            (0.08, generate_noise(0.06, volume=0.3, lowpass_factor=0.7))
        ]
        self.sounds['shoot_shotgun'] = samples_to_sound(mix_tracks(shotgun_layers), self.audio_enabled)

        # 7. Railgun Fire
        rail_layers = [
            (0.00, generate_tone(0.30, freq_start=1800, freq_end=320, wave_type='saw', volume=0.5)),
            (0.00, generate_noise(0.28, volume=0.7, lowpass_factor=0.5)),
            (0.02, generate_tone(0.35, freq_start=90, freq_end=30, wave_type='sine', volume=0.85))
        ]
        self.sounds['shoot_railgun'] = samples_to_sound(mix_tracks(rail_layers), self.audio_enabled)

        # 8. Enemy Shoot
        enemy_shoot_layers = [
            (0.00, generate_noise(0.09, volume=0.45, lowpass_factor=0.3, decay_exp=2.8)),
            (0.00, generate_tone(0.08, freq_start=140, freq_end=50, wave_type='sine', volume=0.4))
        ]
        self.sounds['enemy_shoot'] = samples_to_sound(mix_tracks(enemy_shoot_layers), self.audio_enabled)

        # 9. Shuriken Throw
        shuriken_layers = [
            (0.00, generate_tone(0.09, freq_start=950, freq_end=420, wave_type='triangle', volume=0.35, tremolo_rate=30.0)),
            (0.00, generate_noise(0.06, volume=0.25, lowpass_factor=0.8))
        ]
        self.sounds['shuriken'] = samples_to_sound(mix_tracks(shuriken_layers), self.audio_enabled)

        # 10. Temporal Grenade & Barrel Explosion
        explosion_layers = [
            (0.00, generate_noise(0.55, volume=0.9, lowpass_factor=0.25, decay_exp=1.4)),
            (0.00, generate_tone(0.45, freq_start=110, freq_end=28, wave_type='sine', volume=0.85)),
            (0.05, generate_tone(0.25, freq_start=400, freq_end=80, wave_type='triangle', volume=0.4))
        ]
        self.sounds['explosion'] = samples_to_sound(mix_tracks(explosion_layers), self.audio_enabled)

        # 11. Dash Whoosh
        dash_layers = [
            (0.00, generate_noise(0.12, volume=0.4, lowpass_factor=0.6, decay_exp=2.0)),
            (0.00, generate_tone(0.10, freq_start=340, freq_end=120, wave_type='triangle', volume=0.3))
        ]
        self.sounds['dash'] = samples_to_sound(mix_tracks(dash_layers), self.audio_enabled)

        # 12. Bullet Ricochet
        ricochet_layers = [
            (0.00, generate_tone(0.14, freq_start=1800, freq_end=3400, wave_type='sine', volume=0.35)),
            (0.00, generate_noise(0.04, volume=0.3, lowpass_factor=0.85))
        ]
        self.sounds['ricochet'] = samples_to_sound(mix_tracks(ricochet_layers), self.audio_enabled)

        # 13. Enemy Death / Thud
        thud_layers = [
            (0.00, generate_tone(0.12, freq_start=120, freq_end=40, wave_type='sine', volume=0.65)),
            (0.00, generate_noise(0.10, volume=0.45, lowpass_factor=0.35))
        ]
        self.sounds['thud'] = samples_to_sound(mix_tracks(thud_layers), self.audio_enabled)

        # 14. Player Death
        death_layers = [
            (0.00, generate_noise(0.75, volume=0.75, lowpass_factor=0.18, decay_exp=1.2)),
            (0.00, generate_tone(0.60, freq_start=110, freq_end=22, wave_type='sine', volume=0.75))
        ]
        self.sounds['death'] = samples_to_sound(mix_tracks(death_layers), self.audio_enabled)

        # 15. Ammo & Chrono Pickups
        pickup_layers = [
            (0.00, generate_tone(0.06, freq_start=680, freq_end=680, wave_type='square', volume=0.25)),
            (0.06, generate_tone(0.10, freq_start=1020, freq_end=1020, wave_type='square', volume=0.28))
        ]
        self.sounds['pickup_ammo'] = samples_to_sound(mix_tracks(pickup_layers), self.audio_enabled)

        chrono_pickup_layers = [
            (0.00, generate_tone(0.07, freq_start=520, freq_end=780, wave_type='triangle', volume=0.3)),
            (0.07, generate_tone(0.12, freq_start=780, freq_end=1300, wave_type='sine', volume=0.35))
        ]
        self.sounds['pickup_chrono'] = samples_to_sound(mix_tracks(chrono_pickup_layers), self.audio_enabled)

        # 16. Heartbeat 1 & 2 (low-frequency slow-mo pulses)
        self.sounds['heart1'] = samples_to_sound(generate_tone(0.14, 58, 44, 'sine', 0.95), self.audio_enabled)
        self.sounds['heart2'] = samples_to_sound(generate_tone(0.11, 50, 38, 'sine', 0.75), self.audio_enabled)

        # 17. Level Clear Fanfare
        clear_layers = [
            (0.00, generate_tone(0.10, 440, 440, 'triangle', 0.35)),
            (0.10, generate_tone(0.10, 554, 554, 'triangle', 0.35)),
            (0.20, generate_tone(0.10, 659, 659, 'triangle', 0.35)),
            (0.30, generate_tone(0.26, 880, 880, 'sine', 0.45))
        ]
        self.sounds['level_clear'] = samples_to_sound(mix_tracks(clear_layers), self.audio_enabled)

        # 18. UI Hover & Click
        self.sounds['ui_hover'] = samples_to_sound(generate_tone(0.03, 800, 600, 'square', 0.15), self.audio_enabled)
        self.sounds['ui_click'] = samples_to_sound(generate_tone(0.05, 950, 750, 'square', 0.25), self.audio_enabled)

    def play(self, sfx_name: str, time_acc: float = 0.0, throttle: float = 0.0, volume_scale: float = 1.0):
        """Plays sound effect with throttling to prevent volume stacking."""
        if not self.audio_enabled:
            return

        sound = self.sounds.get(sfx_name)
        if not sound:
            return

        if throttle > 0.0 and (time_acc - self.last_played.get(sfx_name, -99.0)) < throttle:
            return

        self.last_played[sfx_name] = time_acc
        vol = max(0.0, min(1.0, self.master_volume * self.sfx_volume * volume_scale))
        sound.set_volume(vol)
        sound.play()

    def update_volume(self, master: float, sfx: float):
        """Updates SFX volume levels."""
        self.master_volume = master
        self.sfx_volume = sfx
