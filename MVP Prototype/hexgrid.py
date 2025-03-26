class Hex:
    def __init__(self, q, r):
        self.q = q  # axial q coordinate
        self.r = r  # axial r coordinate
    
    def __eq__(self, other):
        return self.q == other.q and self.r == other.r
    
    def __hash__(self):
        return hash((self.q, self.r))

class HexGrid:
    def __init__(self, radius=5):
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
        """Get all adjacent hexes"""
        directions = [(1, 0), (1, -1), (0, -1), 
                     (-1, 0), (-1, 1), (0, 1)]
        neighbors = []
        for dq, dr in directions:
            neighbor = (hex.q + dq, hex.r + dr)
            if neighbor in self.grid:
                neighbors.append(self.grid[neighbor])
        return neighbors
    
    def distance(self, a, b):
        """Calculate distance between two hexes"""
        return (abs(a.q - b.q) + abs(a.q + a.r - b.q - b.r) + abs(a.r - b.r)) // 2