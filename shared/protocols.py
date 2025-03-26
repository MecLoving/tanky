from enum import Enum
from dataclasses import dataclass
import json
from typing import Dict, Any
from server.models.hex import Hex

class MessageType(Enum):
    # Matchmaking
    JOIN_QUEUE = "join_queue"
    MATCH_FOUND = "match_found"
    # Gameplay
    GAME_STATE = "game_state"
    MOVE_TANK = "move_tank"
    COMBAT_RESULT = "combat_result"
    GAME_OVER = "game_over"

@dataclass
class GameMessage:
    type: MessageType
    data: Dict[str, Any]
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self._serialize(self.data)
        })
    
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            data=cls._deserialize(data["data"])
        )
    
    def _serialize(self, data):
        if isinstance(data, dict):
            return {k: self._serialize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize(item) for item in data]
        elif isinstance(data, Hex):
            return {"__hex__": True, "q": data.q, "r": data.r}
        return data
    
    @classmethod
    def _deserialize(cls, data):
        if isinstance(data, dict):
            if "__hex__" in data:
                return Hex(data["q"], data["r"])
            return {k: cls._deserialize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls._deserialize(item) for item in data]
        return data