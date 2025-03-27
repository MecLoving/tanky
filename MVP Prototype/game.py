from hexgrid import HexGrid, Hex
from units import Tank
from renderer import Renderer

class Game:
    def __init__(self, grid_radius=3, tanks_per_player=3):
        self.grid = HexGrid(radius=grid_radius)
        self.tanks = []
        self.turn_count = 0
        self.game_over = False
        self.winner = None
        self.firing_targets = []
        
        # Player setup
        self.players = {
            1: Player(id=1, name="Red", color='\033[91m', start_row=grid_radius, game=self),
            2: Player(id=2, name="Blue", color='\033[94m', start_row=-grid_radius, game=self)
        }
        self.current_player = self.players[1]
        self._setup_tanks(tanks_per_player)
        self.renderer = Renderer(self)  # Single renderer instance

    def _setup_tanks(self, count):
        """Initialize tanks at starting positions"""
        for player in self.players.values():
            edge_positions = [pos for pos in self.grid.grid 
                            if pos[1] == player.start_row]
            for i, pos in enumerate(edge_positions[:count]):
                tank = Tank(
                    player=player.id,
                    position=self.grid.grid[pos],
                    tank_id=i+1
                )
                self.tanks.append(tank)
                player.original_tanks.append(tank)

    def start_turn(self):
        """Begin a new turn with proper phase sequencing"""
        self.turn_count += 1
        self.current_player.reset_movement_points()
        self.renderer.draw()
        
        # Skip firing phase for first complete rotation (both players)
        if self.turn_count > 2:
            self._handle_firing_phase()
        
        self._handle_movement_phase()
        
        if self.turn_count > 2:
            self._resolve_firing()
        
        self._end_turn()

    def _handle_firing_phase(self):
        """Opponent's pre-movement firing using position numbers"""
        opponent = self.current_player.opponent
        num_shots = len(opponent.alive_tanks)
        
        print(f"\n{opponent.color}{opponent.name}'s FIRING PHASE\033[0m ({num_shots} shots)")
        self.renderer.draw()  # Show current positions
        
        self.firing_targets = []
        for shot_num in range(1, num_shots + 1):
            while True:
                try:
                    target_num = int(input(f"Shot {shot_num}/{num_shots} (position number): "))
                    target_hex = self.renderer.get_hex_by_number(target_num)
                    if target_hex:
                        self.firing_targets.append(target_hex)
                        break
                    print("Invalid position number!")
                except ValueError:
                    print("Please enter a number!")

    def _handle_movement_phase(self):
        """Player's movement phase with position numbers"""
        print(f"\n{self.current_player.color}{self.current_player.name}'s MOVEMENT PHASE\033[0m")
        
        while self.current_player.movement_points > 0 and not self.game_over:
            available_tanks = [t for t in self.current_player.alive_tanks 
                             if not t.destroyed and t.moves_remaining > 0]
            
            if not available_tanks:
                print("No movable tanks remaining!")
                break
                
            # Tank selection without requiring 'T' prefix
            selected_tank = self._select_tank(available_tanks)
            if not selected_tank:
                continue
                
            # Show available moves before movement input
            valid_moves = self.grid.get_neighbors(selected_tank.position)
            self.renderer.show_available_moves(selected_tank, valid_moves)
            
            # Movement using position numbers
            self._process_tank_movement(selected_tank, valid_moves)

    def _select_tank(self, available_tanks):
        """Tank selection accepting both 'T1' and '1' formats"""
        self.renderer.show_available_tanks(available_tanks)
        
        while True:
            selection = input("\nSelect tank (1/2/3) or 'end': ").strip().lower()
            if selection == 'end':
                return None
                
            # Handle both '1' and 't1' formats
            if selection.startswith('t'):
                selection = selection[1:]
                
            try:
                tank_num = int(selection)
                selected = next((t for t in available_tanks if t.tank_id == tank_num), None)
                if selected:
                    return selected
                print("Invalid tank number!")
            except ValueError:
                print("Please enter a number or 'end'")

    def _process_tank_movement(self, tank, valid_moves):
        """Movement using position numbers with validation"""
        move_numbers = [self.renderer.get_position_number(move) for move in valid_moves]
        self.renderer.draw(highlight_positions=valid_moves)
        
        while True:
            try:
                target_num = int(input("Move to position number (or 0 to cancel): "))
                if target_num == 0:
                    return False
                    
                target_hex = self.renderer.get_hex_by_number(target_num)
                if target_hex and target_hex in valid_moves:
                    self._execute_move(tank, target_hex)
                    return True
                print("Invalid position number!")
            except ValueError:
                print("Please enter a number!")

    def _execute_move(self, tank, target_hex):
        """Execute validated tank movement"""
        enemy_tank = self._get_tank_at(target_hex)
        
        # Combat resolution
        if enemy_tank and enemy_tank.player != tank.player:
            result = tank.attack(enemy_tank)
            if result["winner"] == tank.player:
                tank.position = target_hex
                if not tank.has_star:
                    tank.moves_remaining -= 1
        else:
            # Normal movement
            tank.position = target_hex
            if not tank.has_star:
                tank.moves_remaining -= 1
            
            # Check for upgrade
            if target_hex.r == -self.players[tank.player].start_row:
                tank.has_star = True
                tank.moves_remaining = float('inf')
        
        self.current_player.use_movement_point()
        self._check_movement_limits()
        self._check_game_over()

    def _resolve_firing(self):
        """Resolve firing phase hits"""
        hits = []
        print("\n--- FIRING RESULTS ---")
        
        for target in self.firing_targets:
            tank = self._get_tank_at(target)
            pos_num = self.renderer.get_position_number(target)
            if tank:
                tank.destroyed = True  # Fixed: Set destroyed flag directly
                hits.append(target)
                print(f"Hit at position {pos_num}! T{tank.tank_id} destroyed!")
                # Check if this kill lifted movement restrictions
                self._check_movement_limits()
            else:
                print(f"Miss at position {pos_num}")
        
        self.firing_targets = []
        self._check_game_over()

    def _check_movement_limits(self):
        """Update movement restrictions based on tank losses"""
        for player in self.players.values():
            alive_tanks = len([t for t in player.original_tanks if not t.destroyed])
            if alive_tanks <= len(player.original_tanks) / 2:
                player.lift_movement_restrictions()

    def _check_game_over(self):
        """Check win conditions"""
        for player in self.players.values():
            if not any(not t.destroyed for t in self.tanks if t.player == player.id):
                self.game_over = True
                self.winner = player.opponent
                return

    def _end_turn(self):
        """Clean up and switch players"""
        for tank in self.tanks:
            if tank.player == self.current_player.id and not tank.has_star:
                tank.moves_remaining = 3
        self.current_player = self.current_player.opponent

    def _get_tank_at(self, hex_pos):
        """Find tank at position"""
        if isinstance(hex_pos, Hex):
            hex_pos = (hex_pos.q, hex_pos.r)
        return next((t for t in self.tanks 
                    if not t.destroyed and (t.position.q, t.position.r) == hex_pos), None)


class Player:
    """Player state management"""
    def __init__(self, id, name, color, start_row, game):
        self.id = id
        self.name = name
        self.color = color
        self.start_row = start_row
        self.game = game
        self.movement_points = 5
        self.unlimited_moves = False
        self.original_tanks = []
        
    @property
    def opponent(self):
        return self.game.players[2] if self.id == 1 else self.game.players[1]
        
    @property
    def alive_tanks(self):
        return [t for t in self.game.tanks 
               if t.player == self.id and not t.destroyed]
                
    def reset_movement_points(self):
        self.movement_points = 5
        
    def use_movement_point(self):
        self.movement_points -= 1
        
    def lift_movement_restrictions(self):
        self.unlimited_moves = True
        for tank in self.alive_tanks:
            tank.moves_remaining = float('inf')


def main():
    """Main game loop"""
    game = Game()
    
    while not game.game_over:
        game.start_turn()
    
    print(f"\nGame Over! {game.winner.name} wins!")


if __name__ == "__main__":
    main()