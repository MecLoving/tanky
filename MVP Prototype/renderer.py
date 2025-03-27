class Renderer:
    def __init__(self, game):
        self.game = game
        self.hex_numbers = self._generate_hex_numbers()  # Permanent numbering
        self.selected_tank = None
    
    
    def _generate_hex_numbers(self):
        """Generate permanent numbering for all hex positions"""
        numbers = {}
        number = 0
        for r in range(-self.game.grid.radius, self.game.grid.radius + 1):
            for q in range(-self.game.grid.radius, self.game.grid.radius + 1):
                if (q, r) in self.game.grid.grid:
                    numbers[(q, r)] = number
                    number += 1
        return numbers
    
    def _get_tank_display(self, tank):
        """Show movement status based on current rules"""
        color = self.game.players[tank.player]['color']
        moves_display = "∞" if (tank.has_star or 
                            self.game.players[tank.player]['unlimited_moves']) \
                        else tank.moves_remaining
        symbol = f"T{tank.strength}{'*' if tank.has_star else ''}({moves_display})"
        return f"{color}{symbol}\033[0m"
    
    def draw(self, selected_tank_index=None):
        print(f"Player {self.game.current_player}'s turn")
        print(f"Movement Points: {self.game.players[self.game.current_player]['movement_points']}\n")
        
        for r in range(-self.game.grid.radius, self.game.grid.radius + 1):
            indent = abs(r) * "  "
            print(indent, end="")
            
            for q in range(-self.game.grid.radius, self.game.grid.radius + 1):
                if (q, r) in self.game.grid.grid:
                    hex = self.game.grid.grid[(q, r)]
                    tank = self._get_tank_at(hex)
                    pos_number = self.hex_numbers[(q, r)]
                    
                    if tank:
                        # Highlight selected tank
                        is_selected = (self.selected_tank is not None and 
                                      self.game.tanks[self.selected_tank] == tank)
                        
                        color = "\033[91m" if tank.player == 1 else "\033[94m"
                        highlight = "\033[7m" if is_selected else ""
                        symbol = f"{highlight}{color}T{'*' if tank.has_star else ''}\033[0m"
                        print(f"{pos_number:2d}:{symbol}", end=" ")
                    else:
                        print(f"{pos_number:4d}", end=" ")
                else:
                    print("     ", end="")
            print("\n")
    
    def get_hex_by_number(self, number):
        """Get hex from permanent number"""
        for coords, num in self.hex_numbers.items():
            if num == number:
                return self.game.grid.grid[coords]
        return None
    
    def get_position_number(self, hex):
        """Get permanent number for a hex position"""
        return self.hex_numbers.get((hex.q, hex.r))
    
    def _get_tank_at(self, hex):
        for tank in self.game.tanks:
            if not tank.destroyed and tank.position == hex:
                return tank
        return None