from hexgrid import HexGrid, Hex
from units import Tank
from renderer import Renderer

class Game:
    def __init__(self, grid_radius=3, tanks_per_player=3):
        self.grid = HexGrid(radius=grid_radius)
        self.players = {
            1: {'movement_points': 5, 'start_row': grid_radius, 'color': '\033[91m', 'unlimited_moves': False},
            2: {'movement_points': 5, 'start_row': -grid_radius, 'color': '\033[94m', 'unlimited_moves': False}
        }
        self.current_player = 1
        self.tanks = self._setup_tanks(tanks_per_player)
        self.game_over = False
        self.winner = None

    def _setup_tanks(self, count):
        tanks = []
        valid_positions = [
            pos for pos in self.grid.grid 
            if abs(pos[1]) == self.grid.radius  # Only edge rows
        ]
        
        # Player 1 tanks (bottom row)
        p1_positions = [pos for pos in valid_positions if pos[1] > 0]
        for i, pos in enumerate(p1_positions[:count]):
            tanks.append(Tank(1, self.grid.grid[pos], i+1))
        
        # Player 2 tanks (top row)
        p2_positions = [pos for pos in valid_positions if pos[1] < 0]
        for i, pos in enumerate(p2_positions[:count]):
            tanks.append(Tank(2, self.grid.grid[pos], i+1))
            
        return tanks

    def _check_movement_limits(self, player_num):
        """Check and update movement restrictions immediately"""
        original_tanks = [t for t in self.tanks if t.player == player_num]
        destroyed_count = len([t for t in original_tanks if t.destroyed])
        
        # If half or more original tanks destroyed, lift restrictions
        if destroyed_count >= len(original_tanks)/2:
            self.players[player_num]['unlimited_moves'] = True
            # Immediately update all alive tanks' movement
            for tank in [t for t in original_tanks if not t.destroyed]:
                tank.moves_remaining = float('inf')
                print(f"Player {player_num}'s Tank {tank.tank_id} movement unlocked!")  # Debug

    def move_tank(self, tank_index, target_hex):
        try:
            tank = self.tanks[tank_index]
            player_data = self.players[self.current_player]
            
            # Validate move conditions (both player MP and tank moves)
            if (tank.player != self.current_player or 
                tank.destroyed or 
                not tank.can_move or  # Uses the new can_move property
                player_data['movement_points'] < 1):
                return False
                
            if not self.grid.is_valid_position(target_hex.q, target_hex.r):
                return False
                
            # Check if target is adjacent
            if target_hex not in self.grid.get_neighbors(tank.position):
                return False

    # Deduct MP immediately for any valid move attempt
            player_data['movement_points'] -= 1


            # Handle combat if enemy tank present
            target_tank = self._get_tank_at(target_hex)
            if target_tank and target_tank.player != self.current_player:
                result = tank.attack(target_tank)
                    # Check movement restrictions for both players after combat
                self._check_movement_limits(self.current_player)
                self._check_movement_limits(target_tank.player)

                if not result["tie"] and result["winner"] == self.current_player:
                    # Successful attack - move to target hex
                    tank.position = target_hex
                    if not tank.has_star and not self.players[self.current_player]['unlimited_moves']:
                        tank.moves_remaining -= 1
                elif result["tie"]:
                    # Tie - no movement occurs, but MP was already consumed
                    pass  

                self._check_game_over()
            else:
                # Normal movement
                tank.position = target_hex
                if not tank.has_star and not self.players[self.current_player]['unlimited_moves']:
                    tank.moves_remaining -= 1
            
            # Check for upgrade
            goal_row = -self.players[tank.player]['start_row']
            if tank.position.r == goal_row:
                tank.has_star = True
                tank.moves_remaining = float('inf')
             # End turn if no MP left
            if player_data['movement_points'] <= 0:
                self._end_turn()
                
            return True
        except (IndexError, AttributeError):
            return False



    def attack(self, attacking_tank, defending_tank):
        """Handle combat and check for movement limit removal"""
        result = super().attack(attacking_tank, defending_tank)
        self._check_movement_limits(defending_tank.player)
        if defending_tank.destroyed:
            self._check_movement_limits(attacking_tank.player)  # Also check attacker in case of tie
        return result

    def _execute_move(self, tank, target_hex, player_data):
        """Handle movement with immediate restriction checks"""
        # First check if movement limits were lifted during combat
        if self.players[tank.player]['unlimited_moves']:
            tank.moves_remaining = float('inf')
        
        # Then proceed with movement
        tank.position = target_hex
        player_data['movement_points'] -= 1
        
        # Only consume moves if limits still apply
        if not (tank.has_star or player_data['unlimited_moves']):
            tank.moves_remaining -= 1
        
        # Check for upgrade
        if tank.position.r == -self.players[tank.player]['start_row']:
            tank.has_star = True
            tank.moves_remaining = float('inf')
        
        if player_data['movement_points'] <= 0:
            self._end_turn()

    def _end_turn(self):
        """Reset movement points while preserving unlimited moves status"""
        self.players[self.current_player]['movement_points'] = 5
        
        # Only reset move counts if limits still apply
        if not self.players[self.current_player]['unlimited_moves']:
            for tank in self.tanks:
                if tank.player == self.current_player and not tank.has_star:
                    tank.moves_remaining = 3
        
        self.current_player = 3 - self.current_player
        print(f"Player {self.current_player} turn - Unlimited moves: {self.players[self.current_player]['unlimited_moves']}")  # Debug    
 
    def _get_tank_at(self, hex):
            for tank in self.tanks:
                if not tank.destroyed and tank.position == hex:
                    return tank
            return None

    def _check_game_over(self):
        """Check if any player has no tanks left"""
        p1_tanks = any(not t.destroyed for t in self.tanks if t.player == 1)
        p2_tanks = any(not t.destroyed for t in self.tanks if t.player == 2)
        
        if not p1_tanks:
            self.game_over = True
            self.winner = 2
        elif not p2_tanks:
            self.game_over = True
            self.winner = 1

    def get_valid_moves(self, tank):
            if tank.destroyed or tank.moved_this_turn:
                return []
            return self.grid.get_neighbors(tank.position)
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