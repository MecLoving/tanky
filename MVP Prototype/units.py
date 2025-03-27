from hexgrid import Hex 

class Tank:
    def __init__(self, player, position, tank_id):
        self.player = player
        self.position = position
        self.tank_id = tank_id
        self.destroyed = False
        self.has_star = False
        self.moved_this_turn = False
        self.moves_remaining = 3  # Each tank gets 3 moves max per turn
    
    @property
    def can_move(self):
        """Check if tank can move (has moves remaining or is upgraded)"""
        return (self.moves_remaining > 0 or
                self.has_star or
                self.player.unlimited_moves) 
    
    @property
    def strength(self):
        return self.tank_id
    
    @property
    def effective_strength(self):
        return self.strength * 2 if self.has_star else self.strength
    
    def attack(self, target):
        """Resolve combat between tanks and return winner info"""
        if self.effective_strength > target.effective_strength:
            target.destroyed = True
            return {"winner": self.player, "tie": False}
        elif self.effective_strength < target.effective_strength:
            self.destroyed = True
            return {"winner": target.player, "tie": False}
        else:
            # Tie - both tanks destroyed
            self.destroyed = True
            target.destroyed = True
            return {"winner": None, "tie": True}
        
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
       
    def reset_moves(self):
        """Reset movement points at start of turn"""
        if not self.destroyed:
            self.moves_remaining = self.movement