# -*- coding: utf-8 -*-
"""
Dynamic Music and Ambience Engine for MOMENTUM: Chrono Blade.
Synthesizes procedural cyberpunk tracks with adaptive time dilation and volume modulation.
"""
import math
import random
import pygame
from core.constants import AUDIO_SAMPLE_RATE
from audio.synthesizer import generate_tone, mix_tracks, samples_to_sound, DummySound

class MusicEngine:
    """Manages adaptive soundtrack generation, playback, and time-dilation volume modulation."""
    def __init__(self, audio_enabled: bool = True):
        self.audio_enabled = audio_enabled
        self.master_volume = 0.8
        self.music_volume = 0.6
        self.tracks = {}
        self.current_track = None
        self.current_channel = None
        self.music_enabled = True

        if self.audio_enabled:
            self._build_all_tracks()

    def _build_all_tracks(self):
        """Generates procedural music tracks."""
        # 1. Track: "CHRONO DRIFT" (Default Ambient Action Theme)
        duration = 8.0
        n_samples = int(duration * AUDIO_SAMPLE_RATE)
        master_buffer = [0.0] * n_samples

        # Sub-bass pulse
        for i in range(n_samples):
            t = i / AUDIO_SAMPLE_RATE
            bass_sub = math.sin(2.0 * math.pi * 55.0 * t) * (0.55 + 0.45 * math.sin(2.0 * math.pi * 0.5 * t))
            env = min(1.0, i / (AUDIO_SAMPLE_RATE * 0.3), (n_samples - i) / (AUDIO_SAMPLE_RATE * 0.3))
            master_buffer[i] += bass_sub * 0.16 * env

        # Atmospheric filtered noise pad
        last_noise = 0.0
        for i in range(n_samples):
            raw = random.uniform(-1.0, 1.0)
            last_noise += 0.03 * (raw - last_noise)
            env = min(1.0, i / (AUDIO_SAMPLE_RATE * 0.5), (n_samples - i) / (AUDIO_SAMPLE_RATE * 0.5))
            master_buffer[i] += last_noise * 0.04 * env

        # Arpeggio Melody Stabs (A minor / Cyber noir chords)
        arpeggios = [
            (1.0, 440.0),   # A4
            (2.0, 523.25),  # C5
            (3.0, 659.25),  # E5
            (4.5, 392.0),   # G4
            (5.5, 440.0),   # A4
            (6.8, 329.63)   # E4
        ]
        for start_t, freq in arpeggios:
            tone_samples = generate_tone(0.45, freq, freq * 0.98, 'triangle', volume=0.07, attack=0.01)
            offset_idx = int(start_t * AUDIO_SAMPLE_RATE)
            for j, val in enumerate(tone_samples):
                if offset_idx + j < n_samples:
                    master_buffer[offset_idx + j] += val

        self.tracks['main_theme'] = samples_to_sound(master_buffer, self.audio_enabled)

        # 2. Track: "BOSS WARDEN OVERDRIVE" (High Intensity Fast Synth)
        boss_dur = 6.0
        n_boss = int(boss_dur * AUDIO_SAMPLE_RATE)
        boss_buf = [0.0] * n_boss

        for i in range(n_boss):
            t = i / AUDIO_SAMPLE_RATE
            # Driving saw-bass
            p = (t * 110.0) % 1.0
            saw = (p * 2.0 - 1.0) * (0.6 + 0.4 * math.sin(2.0 * math.pi * 2.0 * t))
            env = min(1.0, i / (AUDIO_SAMPLE_RATE * 0.2), (n_boss - i) / (AUDIO_SAMPLE_RATE * 0.2))
            boss_buf[i] += saw * 0.12 * env

        boss_stabs = [
            (0.5, 220.0), (1.2, 246.94), (2.0, 261.63), (2.8, 293.66),
            (3.5, 329.63), (4.2, 293.66), (5.0, 261.63)
        ]
        for start_t, freq in boss_stabs:
            tone_samples = generate_tone(0.28, freq, freq, 'saw', volume=0.08, attack=0.005)
            offset_idx = int(start_t * AUDIO_SAMPLE_RATE)
            for j, val in enumerate(tone_samples):
                if offset_idx + j < n_boss:
                    boss_buf[offset_idx + j] += val

        self.tracks['boss_theme'] = samples_to_sound(boss_buf, self.audio_enabled)

    def play_track(self, track_name: str = 'main_theme'):
        """Starts looping the chosen music track."""
        if not self.audio_enabled or not self.music_enabled:
            return

        track = self.tracks.get(track_name)
        if not track:
            return

        if self.current_track == track_name and self.current_channel and self.current_channel.get_busy():
            return

        self.stop()
        self.current_track = track_name
        self.current_channel = track.play(loops=-1)
        self.update_dilation(1.0)

    def update_dilation(self, time_scale: float):
        """
        Dynamically adjusts music volume based on time scale (quieter during freeze, rich during action).
        """
        if not self.audio_enabled or not self.music_enabled or not self.current_track:
            return

        track = self.tracks.get(self.current_track)
        if track:
            # Scale volume smoothly with time dilation (min 30% volume so bass still thumps)
            dilation_factor = 0.35 + 0.65 * min(1.0, max(0.0, (time_scale - 0.02) / 0.98))
            effective_vol = self.master_volume * self.music_volume * dilation_factor
            track.set_volume(max(0.0, min(1.0, effective_vol)))

    def toggle_music(self) -> bool:
        """Toggles music on or off."""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.play_track(self.current_track or 'main_theme')
        else:
            self.stop()
        return self.music_enabled

    def stop(self):
        """Stops active music."""
        if not self.audio_enabled:
            return
        for track in self.tracks.values():
            track.stop()

    def update_volume(self, master: float, music: float):
        """Updates music volume levels."""
        self.master_volume = master
        self.music_volume = music
        self.update_dilation(1.0)
