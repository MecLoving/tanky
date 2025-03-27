from hexgrid import Hex 

class Renderer:
    def __init__(self, game):
        self.game = game
        self.hex_numbers = self._generate_hex_numbers()
        self.player_colors = {
            1: '\033[91m',  # Red
            2: '\033[94m'   # Blue
        }

    def draw(self, highlight_positions=None, selected_tank_index=None):
        """Render the hex grid with tanks and game state"""
        print(f"\n{self._get_turn_header()}")
        
        # Print the hex grid map
        for r in range(-self.game.grid.radius, self.game.grid.radius + 1):
            line = " " * abs(r) * 3  # Proper hexagonal indentation
            
            for q in range(-self.game.grid.radius, self.game.grid.radius + 1):
                if (q, r) in self.game.grid.grid:
                    hex = self.game.grid.grid[(q, r)]
                    pos_num = self.hex_numbers[(hex.q, hex.r)]
                    tank = self._get_tank_at(hex)
                    
                    if tank:
                        # Render tank with position number
                        line += self._render_tank(tank, pos_num, selected_tank_index)
                    else:
                        # Render empty hex with position number
                        if highlight_positions and hex in highlight_positions:
                            line += f"\033[7m{pos_num:3d}\033[0m "  # Highlighted
                        else:
                            line += f"{pos_num:3d} "  # Normal
                else:
                    line += "    "  # Empty space for non-grid positions
            print(line)

    def _render_tank(self, tank, pos_num, selected_tank_index):
        """Render a tank with its position number and status"""
        is_selected = (selected_tank_index is not None and 
                      self.game.tanks[selected_tank_index] == tank)
        
        color = self.player_colors[tank.player]
        moves = "∞" if tank.has_star or self.game.players[tank.player].unlimited_moves else tank.moves_remaining
        symbol = f"T{tank.tank_id}{'*' if tank.has_star else ''}"
        
        if is_selected:
            return f"{color}\033[7m{pos_num}:{symbol}({moves})\033[0m "
        return f"{color}{pos_num}:{symbol}({moves})\033[0m "

    def _get_turn_header(self):
        """Generate turn information header"""
        player = self.game.current_player
        mp = player.movement_points
        return (f"{player.color}{player.name}'s Turn {self.game.turn_count} "
                f"(MP: {mp}/5)\033[0m")

    def _generate_hex_numbers(self):
        """Generate permanent numbering for hex positions"""
        numbers = {}
        counter = 1
        # Sort by rows (r) then columns (q)
        for r in range(-self.game.grid.radius, self.game.grid.radius + 1):
            for q in range(-self.game.grid.radius, self.game.grid.radius + 1):
                if (q, r) in self.game.grid.grid:
                    numbers[(q, r)] = counter
                    counter += 1
        return numbers

    def get_hex_by_number(self, number):
        """Get hex from permanent number"""
        for coords, num in self.hex_numbers.items():
            if num == number:
                return self.game.grid.grid[coords]
        return None

    def get_position_number(self, hex):
        """Get permanent number for a hex position"""
        if isinstance(hex, Hex):
            return self.hex_numbers.get((hex.q, hex.r), None)
        return self.hex_numbers.get(hex, None)

    def _get_tank_at(self, hex):
        """Find tank at given hex position"""
        if isinstance(hex, Hex):
            hex_pos = (hex.q, hex.r)
        else:
            hex_pos = hex
            
        for tank in self.game.tanks:
            if not tank.destroyed and (tank.position.q, tank.position.r) == hex_pos:
                return tank
        return None

    def show_available_tanks(self, available_tanks):
        """Display available tanks with their position numbers"""
        print("\nAvailable Tanks:")
        for tank in available_tanks:
            pos_num = self.get_position_number(tank.position)
            moves = "∞" if tank.has_star else tank.moves_remaining
            print(f"T{tank.tank_id}: Pos {pos_num} ({moves} moves left)")

    def show_available_moves(self, tank, valid_moves):
        """Display available moves for a tank"""
        pos_num = self.get_position_number(tank.position)
        print(f"\nT{tank.tank_id} at position {pos_num}")
        print("Available moves to positions: " + 
              ", ".join(str(self.get_position_number(move)) for move in valid_moves))

    def show_firing_results(self, targets, hits):
        """Display results of firing phase"""
        print("\n--- FIRING RESULTS ---")
        hit_set = set((h.q, h.r) if isinstance(h, Hex) else h for h in hits)
        for target in targets:
            coord = (target.q, target.r) if isinstance(target, Hex) else target
            pos_num = self.get_position_number(coord)
            status = "HIT!" if coord in hit_set else "Miss"
            print(f"Shot at position {pos_num} ({coord}): {status}")

    def draw_hex_coordinates(self):
        """Display hex grid with axial coordinates for reference"""
        print("\nHex Coordinates (q,r):")
        for r in range(-self.game.grid.radius, self.game.grid.radius + 1):
            line = " " * abs(r) * 3
            for q in range(-self.game.grid.radius, self.game.grid.radius + 1):
                if (q, r) in self.game.grid.grid:
                    line += f"[{q},{r}]".ljust(6)
                else:
                    line += "      "
            print(line)