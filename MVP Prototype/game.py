from hexgrid import HexGrid, Hex
from units import Tank
from renderer import Renderer

class Game:
    def __init__(self):
        self.grid = HexGrid(radius=3)
        self.players = [1, 2]
        self.current_player = 1
        self.tanks = self._setup_tanks()
        self.game_over = False
        self.winner = None

    def get_valid_moves(self, tank):
        """Get list of valid move positions for a tank"""
        if tank.destroyed or tank.moves_remaining <= 0:
            return []
        return self.grid.get_neighbors(tank.position)  # Call on grid instance
    
    def _setup_tanks(self):
        tanks = []
        # Player 1 tanks (bottom)
        for q in range(-1, 2):
            if (q, 2) in self.grid.grid:  # Check if position exists
                pos = self.grid.grid[(q, 2)]  # Get Hex object from grid
                tanks.append(Tank(1, pos))  # Pass Hex object to Tank
            
        # Player 2 tanks (top)
        for q in range(-1, 2):
            if (q, -2) in self.grid.grid:  # Check if position exists
                pos = self.grid.grid[(q, -2)]  # Get Hex object from grid
                tanks.append(Tank(2, pos))  # Pass Hex object to Tank
        
        return tanks
    
    def move_tank(self, tank_index, target_hex):
        """Attempt to move a tank"""
        try:
            tank = self.tanks[tank_index]
            if tank.player != self.current_player:
                print("Not your tank!")
                return False
            
            if not tank.can_move_to(target_hex, self.grid):  # Pass grid here
                print("Invalid move!")
                return False
                
            if tank.move_to(target_hex, self.grid):  # Pass grid here
                self._check_victory_condition(tank)
                if all(t.moves_remaining <= 0 or t.player != self.current_player 
                    for t in self.tanks):
                    self._end_turn()
                return True
            return False
        except IndexError:
            print("Invalid tank selection!")
            return False
    
    def _check_victory_condition(self, tank):
        """Check if tank reached opposite side"""
        target_row = -2 if tank.player == 1 else 2  # Adjusted for radius=3
        if tank.position.r == target_row:
            tank.has_star = True
            self._check_game_over()
    
    def _check_game_over(self):
        """Check if one player has no tanks left"""
        p1_tanks = sum(1 for t in self.tanks if t.player == 1 and not t.has_star)
        p2_tanks = sum(1 for t in self.tanks if t.player == 2 and not t.has_star)
        
        if p1_tanks == 0:
            self.game_over = True
            self.winner = 2
        elif p2_tanks == 0:
            self.game_over = True
            self.winner = 1
    
    def _end_turn(self):
        """Switch to next player and reset moves"""
        self.current_player = 2 if self.current_player == 1 else 1
        for tank in self.tanks:
            if tank.player == self.current_player:
                tank.moves_remaining = tank.movement

def main():
    game = Game()
    renderer = Renderer(game)
    
    while not game.game_over:
        renderer.draw()
        print(f"\nPlayer {game.current_player}'s turn")
        print("Available tanks:")
        
        # Show available tanks with their permanent numbers
        available_tanks = []
        for i, tank in enumerate(game.tanks):
            if tank.player == game.current_player and not tank.destroyed:
                pos_number = renderer.get_position_number(tank.position)
                if pos_number is not None:
                    available_tanks.append(i)
                    print(f"{i}: Tank at position {pos_number} ({tank.moves_remaining} moves left)")
        
        if not available_tanks:
            print("No available tanks to move!")
            game._end_turn()
            continue
        
        try:
            tank_idx = int(input("\nSelect tank: "))
            if tank_idx not in available_tanks:
                print("Invalid tank selection!")
                continue
            
            # Show available moves for selected tank
            tank = game.tanks[tank_idx]
            renderer.draw(selected_tank_index=tank_idx)
            print(f"\nSelected Tank at position {renderer.get_position_number(tank.position)}")
            print("Available moves to adjacent positions:")
            
            # Get valid moves from Game class
            neighbors = game.get_valid_moves(tank)  # Updated call
            neighbor_numbers = []
            for neighbor in neighbors:
                num = renderer.get_position_number(neighbor)
                if num is not None:
                    neighbor_numbers.append(str(num))
            
            print(", ".join(neighbor_numbers))
            target_num = int(input("Move to position number: "))
            target_hex = renderer.get_hex_by_number(target_num)
            
            if not target_hex or target_hex not in neighbors:  # Check against valid moves
                print("Invalid move position!")
                continue
                
            if not game.move_tank(tank_idx, target_hex):
                print("Move failed!")
                continue
                
        except ValueError:
            print("Please enter numbers only!")
            continue
    
    renderer.draw()
    print(f"\nGame over! Player {game.winner} wins!")

if __name__ == "__main__":
    main()