from enum import Enum
from dataclasses import dataclass, field
from typing import List
from server.models.hex import Hex

class TankType(Enum):
    REGULAR = 1
    ENHANCED = 2

@dataclass
class Tank:
    id: int
    player_id: str
    position: Hex
    type: TankType = TankType.REGULAR
    has_reached_end: bool = False
    destroyed: bool = False
    movement_history: List[Hex] = field(default_factory=list)

    @property
    def movement_restricted(self) -> bool:
        """Check if tank has movement restrictions"""
        return self.type == TankType.REGULAR

    def move_to(self, new_position: Hex):
        """Update tank position and record movement"""
        self.movement_history.append(self.position)
        self.position = new_position

    def get_valid_moves(self, game_map) -> List[Hex]:
        """Calculate allowed moves based on game rules"""
        if not self.movement_restricted or self.has_reached_end:
            directions = range(6)  # All directions
        else:
            # Restricted directions based on player side
            directions = [0, 1, 5] if self.player_id == "player1" else [2, 3, 4]

        valid_moves = []
        for direction in directions:
            neighbor = self.position.neighbor(direction)
            if game_map.is_passable(neighbor):
                valid_moves.append(neighbor)

        # Prevent backtracking to previous position
        if len(self.movement_history) >= 2:
            valid_moves = [m for m in valid_moves if m != self.movement_history[-2]]

        return valid_moves

    def serialize(self, include_type: bool = True) -> dict:
        """Convert tank data to serializable dict"""
        return {
            "id": self.id,
            "position": {"q": self.position.q, "r": self.position.r},
            "type": self.type.value if include_type else None,
            "hasReachedEnd": self.has_reached_end,
            "destroyed": self.destroyed,
            "movementPoints": self.calculate_remaining_moves()
        }

    def calculate_remaining_moves(self) -> int:
        """Calculate remaining movement points"""
        if not self.movement_restricted:
            return float('inf')  # Unlimited moves for enhanced tanks
        return max(0, 3 - len(self.movement_history))