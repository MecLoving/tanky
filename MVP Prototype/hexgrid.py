class Hex:
    def __init__(self, q, r):
        self.q = q  # axial q coordinate
        self.r = r  # axial r coordinate
        self.s = -q - r  # cubic s coordinate
    
    def __eq__(self, other):
        return self.q == other.q and self.r == other.r
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def distance(self, other):
        """Calculate distance between two hexes using cubic coordinates"""
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs(self.s - other.s)) // 2

class HexGrid:
    def __init__(self, radius=3):
        self.radius = radius
        self.grid = self._generate_hex_grid()
    
    def _generate_hex_grid(self):
        """Generate a hexagonal grid within given radius"""
        grid = {}
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                s = -q - r
                if abs(q) <= self.radius and abs(r) <= self.radius and abs(s) <= self.radius:
                    grid[(q, r)] = Hex(q, r)
        return grid
    
    def get_neighbors(self, hex):
        """Get adjacent hexes from the grid"""
        if not isinstance(hex, Hex):
            raise ValueError("Expected Hex object")
            
        directions = [
            (+1, 0), (+1, -1), (0, -1),
            (-1, 0), (-1, +1), (0, +1)
        ]
        neighbors = []
        for dq, dr in directions:
            neighbor_pos = (hex.q + dq, hex.r + dr)
            if neighbor_pos in self.grid:
                neighbors.append(self.grid[neighbor_pos])
        return neighbors
    def is_valid_position(self, q, r):
        """Check if coordinates are within bounds"""
        return (q, r) in self.grid