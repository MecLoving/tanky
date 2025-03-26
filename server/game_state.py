import random
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from server.models.hex import Hex
from .models.tank import Tank, TankType
from .models.player import Player

class GameMap:
    def __init__(self, radius=5):
        self.radius = radius
        self.terrain = self._generate_terrain()
        self.blocked_terrain = {"water", "mountain"}
    
    def _generate_terrain(self) -> Dict[Hex, str]:
        terrain_types = ["grass"] * 8 + ["water"] * 1 + ["mountain"] * 1
        return {
            hex: random.choice(terrain_types)
            for hex in self._generate_hex_grid()
        }
    
    def _generate_hex_grid(self) -> List[Hex]:
        return [
            Hex(q, r)
            for q in range(-self.radius, self.radius + 1)
            for r in range(-self.radius, self.radius + 1)
            if abs(-q - r) <= self.radius
        ]
    
    def is_passable(self, hex: Hex) -> bool:
        return hex in self.terrain and self.terrain[hex] not in self.blocked_terrain

class GameState:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.map = GameMap()
        self.players: Dict[str, Player] = {}
        self.current_turn: str = ""
        self.turn_phase: str = "movement"
        self.game_over = False
    
    def initialize_players(self, player_ids: List[str]):
        for i, player_id in enumerate(player_ids):
            home_row = self.map.radius if i == 0 else -self.map.radius
            self.players[player_id] = Player(
                player_id=player_id,
                tanks=self._create_tanks(player_id, home_row),
                home_row=home_row
            )
        self.current_turn = player_ids[0]
    
    def _create_tanks(self, player_id: str, home_row: int) -> List[Tank]:
        home_hexes = [h for h in self.map.terrain 
                     if h.r == home_row and self.map.is_passable(h)]
        return [
            Tank(
                tank_id=i+1,
                player_id=player_id,
                position=random.choice(home_hexes),
                tank_type=TankType.ENHANCED if i % 3 == 0 else TankType.REGULAR
            )
            for i in range(6)  # 6 tanks per player
        ]
    
    def move_tank(self, player_id: str, tank_id: int, destination: Hex) -> bool:
        player = self.players.get(player_id)
        if not player or player_id != self.current_turn:
            return False
        
        tank = next((t for t in player.tanks if t.id == tank_id and not t.destroyed), None)
        if not tank or not self._is_valid_move(tank, destination):
            return False
        
        tank.move_to(destination)
        self._check_tank_arrival(tank)
        self._check_combat(tank)
        return True
    
    def _is_valid_move(self, tank: Tank, destination: Hex) -> bool:
        if not self.map.is_passable(destination):
            return False
        
        if tank.movement_restricted and len(tank.movement_history) >= 3:
            return False
        
        return destination in tank.get_valid_moves(self.map)
    
    def _check_tank_arrival(self, tank: Tank):
        target_row = -tank.player.home_row
        if not tank.has_reached_end and tank.position.r == target_row:
            tank.has_reached_end = True
    
    def _check_combat(self, moving_tank: Tank):
        for player in self.players.values():
            if player.player_id == moving_tank.player_id:
                continue
                
            for enemy_tank in player.tanks:
                if not enemy_tank.destroyed and enemy_tank.position == moving_tank.position:
                    self._resolve_combat(moving_tank, enemy_tank)
    
    def _resolve_combat(self, tank1: Tank, tank2: Tank):
        if tank1.type == tank2.type:
            tank1.destroy()
            tank2.destroy()
        elif tank1.type.value > tank2.type.value:
            tank2.destroy()
        else:
            tank1.destroy()
        
        self._check_game_over()
    
    def _check_game_over(self):
        alive_players = [
            p for p in self.players.values()
            if any(not t.destroyed for t in p.tanks)
        ]
        if len(alive_players) < 2:
            self.game_over = True
    
    def get_visible_state(self, player_id: str) -> Dict:
        player = self.players[player_id]
        return {
            "map": {str(h): t for h, t in self.map.terrain.items()},
            "your_tanks": [t.serialize() for t in player.tanks],
            "enemy_tanks": [
                t.serialize(include_type=False) 
                for p in self.players.values()
                if p.player_id != player_id
                for t in p.tanks
                if t.is_visible_to(player_id)
            ],
            "current_turn": self.current_turn,
            "game_over": self.game_over
        }