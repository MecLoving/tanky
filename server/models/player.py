from dataclasses import dataclass, field
from typing import List
from .tank import Tank
from shared.constants import TANKS_PER_PLAYER

@dataclass
class Player:
    player_id: str
    tanks: List[Tank] = field(default_factory=list)
    home_row: int = 0
    rating: int = 1000
    wins: int = 0
    losses: int = 0

    @property
    def destroyed_tanks(self) -> int:
        return sum(1 for tank in self.tanks if tank.destroyed)

    @property
    def remaining_tanks(self) -> int:
        return TANKS_PER_PLAYER - self.destroyed_tanks

    def is_defeated(self) -> bool:
        return all(tank.destroyed for tank in self.tanks)

    def serialize(self) -> dict:
        return {
            'player_id': self.player_id,
            'rating': self.rating,
            'record': f'{self.wins}/{self.losses}',
            'tanks': [tank.serialize() for tank in self.tanks]
        }