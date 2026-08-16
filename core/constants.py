# -*- coding: utf-8 -*-
"""
Core Constants and Configuration for MOMENTUM: Chrono Blade.
Defines screen dimensions, physics parameters, color schemes, audio settings, and combat tuning.
"""
import os
import pygame

# ==========================================
# Display & Engine Configuration
# ==========================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TARGET_FPS = 60
WINDOW_TITLE = "MOMENTUM: Chrono Blade — Time Moves When You Move"

# Save file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = os.path.join(BASE_DIR, "momentum_save.json")
CUSTOM_LEVELS_DIR = os.path.join(BASE_DIR, "custom_levels")

# ==========================================
# Color Palette (Cyber Noir & Crimson Red)
# ==========================================
COLOR_BG = (10, 10, 14)
COLOR_GRID = (18, 18, 24)
COLOR_WALL = (26, 26, 36)
COLOR_WALL_EDGE = (75, 75, 95)
COLOR_WALL_GLOW = (40, 40, 55)

COLOR_WHITE = (245, 245, 250)
COLOR_GRAY = (140, 142, 155)
COLOR_DIM = (70, 72, 85)
COLOR_DARK = (20, 20, 26)

COLOR_RED = (255, 45, 60)
COLOR_HOT = (255, 120, 80)
COLOR_PINK = (255, 65, 135)
COLOR_DARKRED = (110, 15, 25)
COLOR_BLOOD = (145, 16, 28)

COLOR_CYAN = (40, 220, 240)
COLOR_GOLD = (255, 205, 50)
COLOR_GREEN = (60, 230, 120)
COLOR_PURPLE = (160, 60, 240)

# Rank Colors
RANK_COLORS = {
    'S+': COLOR_GOLD,
    'S': COLOR_RED,
    'A': COLOR_HOT,
    'B': COLOR_CYAN,
    'C': COLOR_WHITE,
    'D': COLOR_GRAY
}
RANK_ORDER = ['D', 'C', 'B', 'A', 'S', 'S+']

# ==========================================
# Audio Configuration
# ==========================================
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 32
AUDIO_BUFFER_SIZE = 512

# ==========================================
# Time Dilation Tuning
# ==========================================
TIME_SCALE_STILL = 0.025     # Minimum time rate when player is completely still
TIME_SCALE_MOVE = 1.0        # Time rate during normal movement
TIME_SCALE_FOCUS = 0.15      # Temporal focus slow-motion
TIME_SCALE_KILLCAM = 0.10    # Cinematic slow-mo on final kill
TIME_SCALE_ACCEL = 14.0      # How rapidly time catches up to player movement

# ==========================================
# Combat & Player Tuning
# ==========================================
PLAYER_BASE_SPEED = 300.0
PLAYER_RADIUS = 12
PLAYER_DASH_SPEED = 850.0
PLAYER_DASH_DURATION = 0.18
PLAYER_DASH_COOLDOWN = 0.75
PLAYER_MAX_FOCUS = 100.0
PLAYER_FOCUS_DRAIN = 30.0    # Drain per second in focus mode
PLAYER_FOCUS_RECHARGE = 15.0 # Recharge per second when moving/killing

# Katana Settings
KATANA_SLASH_DURATION = 0.12
KATANA_COOLDOWN = 0.28
KATANA_RANGE = 82
KATANA_ARC_ANGLE = 1.25      # radians (+/- from aim direction)
KATANA_DEFLECT_SPEED = 780.0
KATANA_HEAVY_CHARGE_TIME = 0.55
KATANA_HEAVY_DASH_SPEED = 920.0

# Weapons Configuration
WEAPON_PISTOL = 'pistol'
WEAPON_SHOTGUN = 'shotgun'
WEAPON_RAILGUN = 'railgun'
WEAPON_SHURIKEN = 'shuriken'

WEAPON_CONFIGS = {
    WEAPON_PISTOL: {
        'name': 'KINETIC 9MM',
        'damage': 1,
        'fire_rate': 0.18,
        'bullet_speed': 820.0,
        'spread': 0.02,
        'ammo_per_shot': 1,
        'color': COLOR_WHITE,
        'bounces': 2,
        'kickback': 35.0,
        'shake': 2.0
    },
    WEAPON_SHOTGUN: {
        'name': 'BREACHER-8',
        'damage': 1,
        'fire_rate': 0.65,
        'bullet_speed': 720.0,
        'pellets': 6,
        'spread': 0.32,
        'ammo_per_shot': 2,
        'color': COLOR_HOT,
        'bounces': 1,
        'kickback': 90.0,
        'shake': 5.5
    },
    WEAPON_RAILGUN: {
        'name': 'CHRONO RAIL',
        'damage': 3,
        'fire_rate': 0.85,
        'bullet_speed': 1600.0,
        'spread': 0.0,
        'ammo_per_shot': 3,
        'color': COLOR_CYAN,
        'bounces': 0,
        'piercing': True,
        'kickback': 120.0,
        'shake': 7.0
    },
    WEAPON_SHURIKEN: {
        'name': 'CHRONO BLADE-THROW',
        'damage': 1,
        'fire_rate': 0.25,
        'bullet_speed': 900.0,
        'spread': 0.04,
        'ammo_per_shot': 0,
        'cooldown': 0.6,
        'color': COLOR_CYAN,
        'bounces': 0,
        'kickback': 15.0,
        'shake': 1.5
    }
}

# ==========================================
# Enemy Tuning Table
# ==========================================
ENEMY_TYPES = {
    'grunt': {
        'name': 'Trooper',
        'hp': 1,
        'radius': 13,
        'color': COLOR_RED,
        'charge_time': 0.70,
        'cooldown': 1.4,
        'bullet_speed': 340.0,
        'sight_range': 680,
        'move_speed': 110.0,
        'score_value': 100
    },
    'shotgun': {
        'name': 'Enforcer',
        'hp': 2,
        'radius': 15,
        'color': COLOR_HOT,
        'charge_time': 0.90,
        'cooldown': 2.2,
        'bullet_speed': 310.0,
        'sight_range': 500,
        'move_speed': 90.0,
        'pellets': 4,
        'spread': 0.28,
        'score_value': 200
    },
    'sniper': {
        'name': 'Marksman',
        'hp': 1,
        'radius': 12,
        'color': COLOR_PINK,
        'charge_time': 1.40,
        'cooldown': 2.8,
        'bullet_speed': 1050.0,
        'sight_range': 1400,
        'move_speed': 70.0,
        'score_value': 250
    },
    'rusher': {
        'name': 'Cyber Ninja',
        'hp': 1,
        'radius': 13,
        'color': (255, 30, 45),
        'charge_time': 0.30,
        'cooldown': 0.8,
        'bullet_speed': 0.0,
        'sight_range': 650,
        'move_speed': 180.0,
        'dash_speed': 520.0,
        'score_value': 220
    },
    'shield': {
        'name': 'Riot Warden',
        'hp': 3,
        'radius': 16,
        'color': (230, 160, 40),
        'charge_time': 1.10,
        'cooldown': 2.0,
        'bullet_speed': 380.0,
        'sight_range': 600,
        'move_speed': 85.0,
        'score_value': 300
    },
    'drone': {
        'name': 'Seeker Drone',
        'hp': 1,
        'radius': 11,
        'color': COLOR_CYAN,
        'charge_time': 0.50,
        'cooldown': 1.6,
        'bullet_speed': 420.0,
        'sight_range': 800,
        'move_speed': 140.0,
        'burst_count': 3,
        'score_value': 180
    },
    'boss': {
        'name': 'CHRONO WARDEN',
        'hp': 25,
        'radius': 24,
        'color': (255, 20, 70),
        'charge_time': 0.60,
        'cooldown': 1.2,
        'bullet_speed': 460.0,
        'sight_range': 1600,
        'move_speed': 120.0,
        'score_value': 2000
    }
}
