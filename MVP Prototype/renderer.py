class Renderer:
    def __init__(self, game):
        self.game = game
    
    def draw(self):
        """Draw the current game state"""
        print(f"Player {self.game.current_player}'s turn\n")
        
        # Draw hex grid
        for r in range(-self.game.grid.radius, self.game.grid.radius + 1):
            row = ""
            for q in range(-self.game.grid.radius, self.game.grid.radius + 1):
                if (q, r) in self.game.grid.grid:
                    hex = self.game.grid.grid[(q, r)]
                    tank = self._get_tank_at(hex)
                    if tank:
                        color = "\033[91m" if tank.player == 1 else "\033[94m"
                        symbol = "T" + ("*" if tank.has_star else "")
                        row += f"{color}{symbol}\033[0m "
                    else:
                        row += ". "
                else:
                    row += "  "
            print(row)
    
    def _get_tank_at(self, hex):
        """Find tank at given hex position"""
        for tank in self.game.tanks:
            if tank.position == hex:
                return tank
        return None