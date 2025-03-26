class Tank:
    def __init__(self, player, hex_pos, tank_type="regular"):
        self.player = player
        self.position = hex_pos
        self.type = tank_type
        self.strength = 1 if tank_type == "regular" else 2
        self.movement = 3
        self.has_star = False
        self.moves_remaining = self.movement  # Track moves per turn
        
    def can_move_to(self, target_hex):
        """Check if movement is valid"""
        if self.moves_remaining <= 0:
            return False
            
        # Calculate distance
        distance = self.position.distance(target_hex)
        return distance == 1  # Only allow adjacent moves
    
    def move_to(self, target_hex):
        """Execute the move"""
        self.position = target_hex
        self.moves_remaining -= 1