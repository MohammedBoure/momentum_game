# -*- coding: utf-8 -*-
"""
Interactive Map and Level Editor for MOMENTUM: Chrono Blade.
Allows creating, editing, testing, and saving custom levels with intuitive mouse and keyboard controls.
"""
import os
import json
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_WALL, COLOR_WALL_EDGE,
    COLOR_WHITE, COLOR_RED, COLOR_CYAN, COLOR_GOLD, COLOR_HOT, COLOR_PINK,
    COLOR_GRAY, COLOR_DIM, CUSTOM_LEVELS_DIR
)

class LevelEditor:
    """In-game map editor supporting grid snapping, entity placement, drag-box walls, and instant testing."""
    def __init__(self, screen, save_manager, sound_lib, ui_renderer):
        self.screen = screen
        self.save_manager = save_manager
        self.sound_lib = sound_lib
        self.ui = ui_renderer
        
        self.grid_size = 32
        self.current_tool = 'wall'
        self.tools = ['wall', 'player', 'grunt', 'shotgun', 'sniper', 'rusher', 'shield', 'drone', 'crate', 'barrel', 'turret']
        
        # Level payload
        self.level_name = "Custom Arena 1"
        self.player_spawn = [200, 360]
        self.walls = []
        self.crates = []
        self.barrels = []
        self.turrets = []
        self.enemies = []
        
        # Dragging state for walls
        self.drag_start = None
        self.notification = "WELCOME TO LEVEL EDITOR: 1-9 TOOL, LMB PLACE, RMB DELETE, S SAVE, T TEST"
        self.notif_timer = 5.0

    def handle_event(self, ev: pygame.event.Event) -> str:
        """Handles editor inputs. Returns 'test', 'exit', or None."""
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                return 'exit'
            elif ev.key == pygame.K_t:
                return 'test'
            elif ev.key == pygame.K_s:
                self.save_level()
            elif ev.key == pygame.K_1: self.current_tool = 'wall'
            elif ev.key == pygame.K_2: self.current_tool = 'player'
            elif ev.key == pygame.K_3: self.current_tool = 'grunt'
            elif ev.key == pygame.K_4: self.current_tool = 'shotgun'
            elif ev.key == pygame.K_5: self.current_tool = 'sniper'
            elif ev.key == pygame.K_6: self.current_tool = 'rusher'
            elif ev.key == pygame.K_7: self.current_tool = 'shield'
            elif ev.key == pygame.K_8: self.current_tool = 'drone'
            elif ev.key == pygame.K_9: self.current_tool = 'barrel'
            elif ev.key == pygame.K_0: self.current_tool = 'crate'

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            gx = (mx // self.grid_size) * self.grid_size
            gy = (my // self.grid_size) * self.grid_size

            if ev.button == 1:  # Left Click Place
                if self.current_tool == 'wall':
                    self.drag_start = (gx, gy)
                elif self.current_tool == 'player':
                    self.player_spawn = [gx + self.grid_size // 2, gy + self.grid_size // 2]
                elif self.current_tool == 'barrel':
                    self.barrels.append([gx + self.grid_size // 2, gy + self.grid_size // 2])
                elif self.current_tool == 'crate':
                    self.crates.append([gx, gy, self.grid_size, self.grid_size, 'ammo'])
                elif self.current_tool == 'turret':
                    self.turrets.append([gx + self.grid_size // 2, gy + self.grid_size // 2, 0.0])
                else:  # Enemy types
                    self.enemies.append((self.current_tool, gx + self.grid_size // 2, gy + self.grid_size // 2))

            elif ev.button == 3:  # Right Click Delete
                # Delete closest object near mouse
                self.enemies = [e for e in self.enemies if math.hypot(e[1] - mx, e[2] - my) > 20]
                self.barrels = [b for b in self.barrels if math.hypot(b[0] - mx, b[1] - my) > 20]
                self.walls = [w for w in self.walls if not pygame.Rect(*w).collidepoint(mx, my)]
                self.crates = [c for c in self.crates if not pygame.Rect(c[0], c[1], c[2], c[3]).collidepoint(mx, my)]

        elif ev.type == pygame.MOUSEBUTTONUP:
            if ev.button == 1 and self.drag_start and self.current_tool == 'wall':
                mx, my = pygame.mouse.get_pos()
                gx = (mx // self.grid_size) * self.grid_size
                gy = (my // self.grid_size) * self.grid_size
                x1, y1 = self.drag_start
                rx = min(x1, gx)
                ry = min(y1, gy)
                rw = max(self.grid_size, abs(gx - x1) + self.grid_size)
                rh = max(self.grid_size, abs(gy - y1) + self.grid_size)
                self.walls.append([rx, ry, rw, rh])
                self.drag_start = None

        return None

    def export_data(self) -> dict:
        """Returns map data dictionary matching campaign level schema."""
        return {
            "name": self.level_name,
            "description": "Custom user-generated arena.",
            "par_time": 15,
            "player_spawn": tuple(self.player_spawn),
            "walls": [tuple(w) for w in self.walls],
            "crates": [tuple(c) for c in self.crates],
            "barrels": [tuple(b) for b in self.barrels],
            "turrets": [tuple(t) for t in self.turrets],
            "ammo_pickups": [],
            "chrono_pickups": [],
            "enemies": list(self.enemies)
        }

    def save_level(self):
        """Saves custom map to disk."""
        try:
            os.makedirs(CUSTOM_LEVELS_DIR, exist_ok=True)
            path = os.path.join(CUSTOM_LEVELS_DIR, "custom_map.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.export_data(), f, indent=2)
            self.notification = f"LEVEL SAVED TO: custom_map.json"
            self.notif_timer = 4.0
        except Exception as e:
            self.notification = f"SAVE ERROR: {e}"
            self.notif_timer = 4.0

    def update(self, dt: float):
        if self.notif_timer > 0:
            self.notif_timer -= dt

    def draw(self):
        """Renders editor canvas, grid lines, placed entities, and toolbar."""
        s = self.screen
        s.fill(COLOR_BG)

        # 1. Grid Lines
        for x in range(0, SCREEN_WIDTH, self.grid_size):
            pygame.draw.line(s, (18, 18, 26), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, self.grid_size):
            pygame.draw.line(s, (18, 18, 26), (0, y), (SCREEN_WIDTH, y), 1)

        # 2. Walls
        for w in self.walls:
            r = pygame.Rect(*w)
            pygame.draw.rect(s, COLOR_WALL, r)
            pygame.draw.rect(s, COLOR_WALL_EDGE, r, 2)

        # 3. Active Drag Wall Preview
        if self.drag_start:
            mx, my = pygame.mouse.get_pos()
            gx = (mx // self.grid_size) * self.grid_size
            gy = (my // self.grid_size) * self.grid_size
            x1, y1 = self.drag_start
            rx = min(x1, gx)
            ry = min(y1, gy)
            rw = max(self.grid_size, abs(gx - x1) + self.grid_size)
            rh = max(self.grid_size, abs(gy - y1) + self.grid_size)
            pygame.draw.rect(s, (60, 60, 80), (rx, ry, rw, rh), 2)

        # 4. Crates & Barrels
        for c in self.crates:
            pygame.draw.rect(s, (45, 45, 60), (c[0], c[1], c[2], c[3]))
            pygame.draw.rect(s, (90, 90, 110), (c[0], c[1], c[2], c[3]), 2)
        for b in self.barrels:
            pygame.draw.circle(s, COLOR_RED, (b[0], b[1]), 14, 2)

        # 5. Player Spawn
        pygame.draw.circle(s, COLOR_WHITE, (self.player_spawn[0], self.player_spawn[1]), 12)
        self.ui.render_text(s, "PLAYER", 11, (self.player_spawn[0], self.player_spawn[1] - 18), COLOR_WHITE)

        # 6. Enemies
        for kind, ex, ey in self.enemies:
            col = COLOR_HOT if kind == 'shotgun' else (COLOR_PINK if kind == 'sniper' else (COLOR_CYAN if kind == 'drone' else COLOR_RED))
            pygame.draw.circle(s, col, (int(ex), int(ey)), 12, 2)
            self.ui.render_text(s, kind[:4].upper(), 10, (int(ex), int(ey) - 16), col)

        # 7. Toolbar & Help Overlay (Top Header)
        pygame.draw.rect(s, (14, 14, 20), (0, 0, SCREEN_WIDTH, 48))
        pygame.draw.line(s, COLOR_WALL_EDGE, (0, 48), (SCREEN_WIDTH, 48), 2)
        self.ui.render_text(s, f"TOOL: [{self.current_tool.upper()}]   (1-9 TO SELECT)", 15, (20, 24), COLOR_CYAN, anchor='midleft')
        self.ui.render_text(s, "S: SAVE MAP   •   T: TEST PLAY   •   ESC: MENU", 15, (SCREEN_WIDTH - 20, 24), COLOR_GRAY, anchor='midright')

        if self.notif_timer > 0:
            self.ui.render_text(s, self.notification, 14, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 24), COLOR_GOLD)
