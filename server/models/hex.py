from dataclasses import dataclass
from shared.constants import TerrainType

@dataclass(frozen=True)
class Hex:
    """Core hex coordinate logic"""
    q: int
    r: int
    
    def __add__(self, other): ...
    def distance_to(self, other): ...
    # ... (all your existing Hex methods)

class GameHex(Hex):
    """Server-specific game extensions"""
    def is_passable(self, terrain: TerrainType) -> bool:
        return terrain != TerrainType.WATER
    
    def movement_cost(self, terrain: TerrainType) -> int:
        return {
            TerrainType.GRASS: 1,
            TerrainType.MOUNTAIN: 2
        }.get(terrain, 0)