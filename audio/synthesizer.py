# -*- coding: utf-8 -*-
"""
Procedural Audio Synthesizer.
Generates crisp procedural sound waves, frequency chirps, envelopes, and filtered noise buffers
directly into Pygame Sound objects without external audio dependencies.
"""
import math
import array
import random
import pygame
from core.constants import AUDIO_SAMPLE_RATE

class DummySound:
    """Fallback silent sound object when audio hardware is unavailable."""
    def play(self, *args, **kwargs): pass
    def stop(self): pass
    def set_volume(self, *args, **kwargs): pass
    def get_volume(self): return 0.0

def generate_tone(duration: float, freq_start: float, freq_end: float = None,
                  wave_type: str = 'sine', volume: float = 0.5,
                  tremolo_rate: float = 0.0, attack: float = 0.005, decay_exp: float = 2.0) -> list:
    """
    Generates a single-frequency or sweeping tone buffer.
    Waves: 'sine', 'square', 'triangle', 'saw'.
    """
    sample_count = int(duration * AUDIO_SAMPLE_RATE)
    if sample_count <= 0:
        return []
    if freq_end is None:
        freq_end = freq_start

    output = [0.0] * sample_count
    phase = 0.0
    attack_samples = int(attack * AUDIO_SAMPLE_RATE)

    for i in range(sample_count):
        progress = i / sample_count
        cur_freq = freq_start + (freq_end - freq_start) * progress
        phase += 2.0 * math.pi * cur_freq / AUDIO_SAMPLE_RATE

        # Waveform generation
        if wave_type == 'sine':
            sample = math.sin(phase)
        elif wave_type == 'square':
            sample = 1.0 if (phase % (2.0 * math.pi)) < math.pi else -1.0
        elif wave_type == 'triangle':
            p = (phase % (2.0 * math.pi)) / math.pi
            sample = (p * 2.0 - 1.0) if p < 1.0 else (3.0 - p * 2.0)
        elif wave_type == 'saw':
            p = (phase % (2.0 * math.pi)) / (2.0 * math.pi)
            sample = p * 2.0 - 1.0
        else:
            sample = math.sin(phase)

        # Envelope
        envelope = (1.0 - progress) ** decay_exp
        if attack_samples > 0 and i < attack_samples:
            envelope *= (i / attack_samples)

        # Tremolo (amplitude modulation)
        trem = 1.0
        if tremolo_rate > 0.0:
            trem = 0.65 + 0.35 * math.sin(2.0 * math.pi * tremolo_rate * i / AUDIO_SAMPLE_RATE)

        output[i] = sample * volume * envelope * trem

    return output

def generate_noise(duration: float, volume: float = 0.5, lowpass_factor: float = 0.5,
                   decay_exp: float = 2.0, metallic: bool = False) -> list:
    """
    Generates filtered noise for explosions, gunshots, impacts, and whooshes.
    """
    sample_count = int(duration * AUDIO_SAMPLE_RATE)
    if sample_count <= 0:
        return []

    output = [0.0] * sample_count
    last_sample = 0.0

    for i in range(sample_count):
        progress = i / sample_count
        raw_noise = random.uniform(-1.0, 1.0)

        if metallic:
            raw_noise = math.sin(raw_noise * 12.0)

        # Simple single-pole low-pass filter
        last_sample += lowpass_factor * (raw_noise - last_sample)
        envelope = (1.0 - progress) ** decay_exp

        output[i] = last_sample * volume * envelope * 2.0

    return output

def mix_tracks(layers: list) -> list:
    """
    Combines multiple audio track layers at specific offsets: [(offset_sec, sample_list), ...]
    """
    if not layers:
        return []

    total_len = max(int(offset * AUDIO_SAMPLE_RATE) + len(samples) for offset, samples in layers)
    master_buf = [0.0] * total_len

    for offset, samples in layers:
        start_idx = int(offset * AUDIO_SAMPLE_RATE)
        for i, val in enumerate(samples):
            if start_idx + i < total_len:
                master_buf[start_idx + i] += val

    return master_buf

def samples_to_sound(samples: list, audio_enabled: bool = True) -> pygame.mixer.Sound:
    """
    Converts floating point sample list (-1.0 to 1.0) into a playable 16-bit Pygame Sound.
    """
    if not audio_enabled or not samples:
        return DummySound()

    try:
        raw_bytes = array.array('h')
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            raw_bytes.append(int(clamped * 32000))
        return pygame.mixer.Sound(buffer=raw_bytes.tobytes())
    except Exception as e:
        print(f"[Synthesizer] Failed creating sound buffer: {e}")
        return DummySound()
