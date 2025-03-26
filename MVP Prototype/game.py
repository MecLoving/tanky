from hexgrid import HexGrid
from units import Tank
from renderer import Renderer

class Game:
    def __init__(self):
        self.grid = HexGrid(radius=5)
        self.players = [1, 2]
        self.current_player = 1
        self.tanks = self._setup_tanks()
        self.game_over = False
        self.winner = None  # Initialize winner
    
    def _setup_tanks(self):
        """Place tanks on opposite sides"""
        tanks = []
        # Player 1 tanks on south edge
        for q in range(-2, 3):
            pos = self.grid.grid[(q, 3)]
            tanks.append(Tank(1, pos))
        
        # Player 2 tanks on north edge
        for q in range(-2, 3):
            pos = self.grid.grid[(q, -3)]
            tanks.append(Tank(2, pos))
        
        return tanks
    
    def move_tank(self, tank_index, target_hex):
        """Attempt to move a tank"""
        tank = self.tanks[tank_index]
        if tank.player != self.current_player:
            return False
        
        if tank.can_move_to(target_hex):
            tank.position = target_hex
            self._check_victory_condition(tank)
            self._end_turn()
            return True
        return False
    
    def _check_victory_condition(self, tank):
        """Check if tank reached opposite side"""
        target_row = -3 if tank.player == 1 else 3
        if tank.position.r == target_row:
            tank.has_star = True
            self._check_game_over()
    
    def _check_game_over(self):
        """Check if one player has no tanks left"""
        p1_tanks = sum(1 for t in self.tanks if t.player == 1)
        p2_tanks = sum(1 for t in self.tanks if t.player == 2)
        
        if p1_tanks == 0:
            self.game_over = True
            self.winner = 2
        elif p2_tanks == 0:
            self.game_over = True
            self.winner = 1
    
    def _end_turn(self):
        """Switch to next player"""
        self.current_player = 2 if self.current_player == 1 else 1

