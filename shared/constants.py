from enum import Enum

class GamePhase(Enum):
    LOBBY = 0
    MATCHMAKING = 1
    DEPLOYMENT = 2
    MOVEMENT = 3
    COMBAT = 4
    GAME_OVER = 5

class TerrainType(Enum):
    GRASS = 0
    WATER = 1
    MOUNTAIN = 2

# Movement costs
MOVEMENT_COST = {
    TerrainType.GRASS: 1,
    TerrainType.WATER: 0,    # Impassable
    TerrainType.MOUNTAIN: 0  # Impassable
}

# Server configuration
MAX_PLAYERS = 2
TANKS_PER_PLAYER = 6
MAP_RADIUS = 5