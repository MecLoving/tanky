import random
from server.models.hex import Hex
from typing import Dict

class MapGenerator:
    @staticmethod
    def generate_balanced_map(radius: int = 5) -> Dict[Hex, str]:
        terrain = {}
        symmetric_positions = []
        
        # Generate symmetric positions for fair play
        for q in range(-radius, radius+1):
            for r in range(-radius, radius+1):
                if abs(-q-r) <= radius:
                    symmetric_positions.append((q, r))
        
        # Create mirrored terrain
        for q, r in symmetric_positions:
            terrain_type = random.choices(
                ["grass", "water", "mountain"],
                weights=[0.8, 0.1, 0.1]
            )[0]
            terrain[Hex(q, r)] = terrain_type
            terrain[Hex(-q, -r)] = terrain_type  # Mirror position
            
        return terrain

    @staticmethod
    def generate_random_map(radius: int = 5) -> Dict[Hex, str]:
        return {
            Hex(q, r): random.choices(
                ["grass", "water", "mountain"],
                weights=[0.8, 0.1, 0.1]
            )[0]
            for q in range(-radius, radius+1)
            for r in range(-radius, radius+1)
            if abs(-q-r) <= radius
        }