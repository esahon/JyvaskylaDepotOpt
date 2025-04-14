class DepotSystem:
    """Handles bus depot logic and interacts with Julia."""
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.blocks = {(i, j): True for i in range(rows) for j in range(cols)}  # True = Active
        self.bus_assignments = {}  # Store bus type assignments {(i, j): bus_type}
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
        """Send depot state to Julia for processing and get bus type assignments."""
        from julia_interface import call_julia_function
        matrix = self.get_matrix()
        bus_types = call_julia_function(matrix)  # Use the updated Julia function
        return bus_types

    def send_to_julia_with_params(self, l, v, max_deviation, arrivals, departures):
        """Send matrix and additional parameters to Julia for processing."""
        from julia_interface import call_julia_function_with_params
        # Debugging: Print the data being sent to Julia
        print("DepotSystem -> Julia: l =", l)
        print("DepotSystem -> Julia: v =", v)
        print("DepotSystem -> Julia: max_deviation =", max_deviation)
        print("DepotSystem -> Julia: arrivals =", arrivals)
        print("DepotSystem -> Julia: departures =", departures)

        # Call the Julia function
        X, Y, Z = call_julia_function_with_params(l, v, max_deviation, arrivals, departures)
        return X, Y, Z

    def assign_buses(self, assignments):
        """Assign bus types to depot spots."""
        for (i, j), bus_type in assignments.items():
            self.bus_assignments[(i, j)] = bus_type

    def get_bus_type(self, x, y):
        """Get the bus type assigned to a specific spot."""
        return self.bus_assignments.get((x, y), None)

