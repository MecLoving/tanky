from hexgrid import Hex 

class Tank:
    def __init__(self, player, hex_pos, tank_type="regular"):
        if not hasattr(hex_pos, 'q') or not hasattr(hex_pos, 'r'):
            raise ValueError("hex_pos must be a Hex object with q and r attributes")
            
        self.player = player
        self.position = hex_pos  # Now properly stores Hex object
        self.type = tank_type
        self.strength = 1 if tank_type == "regular" else 2
        self.movement = 3
        self.has_star = False
        self.moves_remaining = self.movement
        self.destroyed = False
        
    def can_move_to(self, target_hex, hex_grid):
        """Check if movement is valid using the hex grid"""
        if self.destroyed:
            return False
        if self.moves_remaining <= 0:
            return False
        if not isinstance(target_hex, Hex):
            return False
            
        return target_hex in hex_grid.get_neighbors(self.position)
    
    def move_to(self, target_hex, hex_grid):
        """Execute the move if valid"""
        if self.can_move_to(target_hex, hex_grid):
            self.position = target_hex
            self.moves_remaining -= 1
            return True
        return False
    
    def attack(self, target):
        """Enhanced combat resolution with destruction handling"""
        if self.destroyed or target.destroyed:
            return "invalid_target"
            
        result = ""
        if self.strength > target.strength:
            target.destroyed = True
            result = "attacker_wins"
        elif self.strength < target.strength:
            self.destroyed = True
            result = "defender_wins"
        else:
            self.destroyed = True
            target.destroyed = True
            result = "both_destroyed"
        
        # Reset moves if tank survives
        if not self.destroyed:
            self.moves_remaining = 0  # End turn after attack
        return result
    
    def reset_moves(self):
        """Reset movement points at start of turn"""
        if not self.destroyed:
            self.moves_remaining = self.movement