class DepotSystem:
    """Handles bus depot logic and interacts with Julia."""
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.blocks = {(i, j): True for i in range(rows) for j in range(cols)}  # True = Active

    def toggle_block(self, x, y):
        """Toggle the state of a block."""
        self.blocks[(x, y)] = not self.blocks[(x, y)]

    def get_block_state(self, x, y):
        """Return the state of a block."""
        return self.blocks.get((x, y), False)

    def get_matrix(self):
        """Return the matrix in the format Julia expects (1 = On, 0 = Off)."""
        return [[1 if self.blocks[(i, j)] else 0 for j in range(self.cols)] for i in range(self.rows)]

    def send_to_julia(self):
        """Send depot state to Julia for processing."""
        #from julia_interface import tähän_julia_funktio
        #matrix = self.get_matrix()
        #julia_funktio(matrix)

