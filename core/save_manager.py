# -*- coding: utf-8 -*-
"""
Save and Configuration Manager.
Handles persistent progression storage, high scores, ranks, settings, and stats.
"""
import os
import json
from core.constants import SAVE_PATH, RANK_ORDER

DEFAULT_SAVE_DATA = {
    "unlocked_level": 1,
    "ranks": {},            # { "0": "S+", "1": "A", ... }
    "best_times": {},       # { "0": 4.52, ... }
    "best_styles": {},      # { "0": 45, ... }
    "total_deaths": 0,
    "total_kills": 0,
    "total_deflects": 0,
    "endless_record_wave": 0,
    "endless_high_score": 0,
    "settings": {
        "master_volume": 0.8,
        "sfx_volume": 0.9,
        "music_volume": 0.6,
        "screen_shake": 1.0,
        "crt_filter": True,
        "blood_effects": True,
        "damage_numbers": True
    }
}

class SaveManager:
    """Manages player progression, level ranks, high scores, and persistent settings."""
    def __init__(self, filepath=SAVE_PATH):
        self.filepath = filepath
        self.data = self.load()

    def load(self) -> dict:
        """Loads data from disk or returns defaults if unreadable."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with default structure for any missing keys
                    merged = DEFAULT_SAVE_DATA.copy()
                    merged.update(loaded)
                    if "settings" in loaded:
                        merged["settings"] = DEFAULT_SAVE_DATA["settings"].copy()
                        merged["settings"].update(loaded["settings"])
                    return merged
            except Exception as e:
                print(f"[SaveManager] Error loading save file: {e}")
        return DEFAULT_SAVE_DATA.copy()

    def save(self):
        """Writes current data state to disk safely."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[SaveManager] Error saving data: {e}")

    def record_level_clear(self, level_idx: int, rank: str, time_taken: float, style_score: int, total_levels: int):
        """Updates progression if a higher rank or faster time was achieved."""
        key = str(level_idx)
        old_rank = self.data["ranks"].get(key, 'D')
        
        # Check if new rank is better
        old_idx = RANK_ORDER.index(old_rank) if old_rank in RANK_ORDER else 0
        new_idx = RANK_ORDER.index(rank) if rank in RANK_ORDER else 0
        if new_idx >= old_idx:
            self.data["ranks"][key] = rank

        # Update best time
        if key not in self.data["best_times"] or time_taken < self.data["best_times"][key]:
            self.data["best_times"][key] = round(time_taken, 2)

        # Update best style
        if key not in self.data["best_styles"] or style_score > self.data["best_styles"][key]:
            self.data["best_styles"][key] = style_score

        # Unlock next level
        self.data["unlocked_level"] = max(self.data["unlocked_level"], min(total_levels, level_idx + 2))
        self.save()

    def record_death(self):
        """Increments death counter."""
        self.data["total_deaths"] += 1
        self.save()

    def record_kills(self, count: int = 1):
        """Increments kill counter."""
        self.data["total_kills"] += count
        self.save()

    def record_deflect(self, count: int = 1):
        """Increments deflected bullet counter."""
        self.data["total_deflects"] += count
        self.save()

    def record_endless(self, wave: int, score: int):
        """Updates endless survival records."""
        if wave > self.data["endless_record_wave"]:
            self.data["endless_record_wave"] = wave
        if score > self.data["endless_high_score"]:
            self.data["endless_high_score"] = score
        self.save()

    def get_setting(self, key: str, default=None):
        """Retrieves a setting value."""
        return self.data.get("settings", {}).get(key, default)

    def set_setting(self, key: str, value):
        """Sets a setting value and saves to disk."""
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"][key] = value
        self.save()
