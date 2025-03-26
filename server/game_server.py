import asyncio
import websockets
import json
from server.game_state import GameState
from .matchmaking import MatchmakingSystem
from shared.protocols import GameMessage

class GameServer:
    def __init__(self):
        self.matchmaking = MatchmakingSystem()
        self.active_games = {}
        self.connections = {}

    async def handle_connection(self, websocket, path):
        try:
            async for message in websocket:
                msg = GameMessage.from_json(message)
                if msg.type == "JOIN_QUEUE":
                    await self.matchmaking.find_match(msg.data['player'])
                elif msg.type == "MOVE_TANK":
                    game = self.active_games.get(msg.data['match_id'])
                    if game:
                        success = game.move_tank(
                            msg.data['player_id'],
                            msg.data['tank_id'],
                            msg.data['destination']
                        )
                        await websocket.send(GameMessage(
                            type="MOVE_RESULT",
                            data={"success": success}
                        ).to_json())
        finally:
            if websocket in self.connections:
                del self.connections[websocket]

    async def run(self, host='0.0.0.0', port=8765):
        async with websockets.serve(self.handle_connection, host, port):
            await asyncio.Future()  # Run forever