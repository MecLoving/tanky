import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import random
from .game_state import GameState
from .models.player import Player

class MatchmakingSystem:
    def __init__(self):
        self.queues: Dict[str, List[Player]] = {
            "casual": [],
            "ranked": [],
            "custom": {}
        }
        self.active_matches: Dict[str, GameState] = {}
    
    async def find_match(self, player: Player, queue_type: str = "casual"):
        if queue_type == "custom":
            return await self._handle_custom_game(player)
        
        self.queues[queue_type].append(player)
        match = await self._try_match_players(queue_type)
        if match:
            game = GameState(match_id=f"match_{len(self.active_matches)+1}")
            game.initialize_players([p.id for p in match])
            self.active_matches[game.match_id] = game
            return game
    
    async def _try_match_players(self, queue_type: str) -> Optional[List[Player]]:
        queue = self.queues[queue_type]
        if len(queue) >= 2:
            matched = random.sample(queue, 2)
            for p in matched:
                queue.remove(p)
            return matched
        return None
    
    async def _handle_custom_game(self, player: Player):
        # Custom game logic here
        pass