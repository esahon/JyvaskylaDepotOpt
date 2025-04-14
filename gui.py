from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QSizePolicy
from bus_processor import process_buses_from_excel

class DepotBlock(QPushButton):
    """A clickable block representing a bus depot space."""
    def __init__(self, x, y, depot_system):
        super().__init__()
        self.x = x
        self.y = y
        self.depot_system = depot_system
        self.update_style()
        self.clicked.connect(self.toggle_state)

    def toggle_state(self):
        """Toggle block state and update the matrix."""
        self.depot_system.toggle_block(self.x, self.y)
        self.update_style()

    def update_style(self):
        """Update appearance based on block state and bus type."""
        state = self.depot_system.get_block_state(self.x, self.y)
        bus_type = self.depot_system.get_bus_type(self.x, self.y)
        self.setText(bus_type if bus_type else ("On" if state else "Off"))
        self.setStyleSheet("background-color: red;" if not state else "background-color: green;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class DepotGUI(QWidget):
    """Main GUI representing the bus depot."""
    def __init__(self, depot_system):
        super().__init__()
        self.setWindowTitle("Bus Depot")
        self.layout = QGridLayout()
        self.depot_system = depot_system
        self.blocks = {}

        # Main window layout
        main_layout = QVBoxLayout()

        # Create the "Optimize" button
        optimize_button = QPushButton("Optimize")
        optimize_button.clicked.connect(self.optimize)
        optimize_button.setFixedSize(100, 40)

        # Create the "Print Matrix" button
        print_button = QPushButton("Print Matrix")
        print_button.clicked.connect(self.print_matrix)
        print_button.setFixedSize(100, 40)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push the buttons to the right
        button_layout.addWidget(optimize_button)
        button_layout.addWidget(print_button)

        # Add the button layout to the main layout at the top
        main_layout.addLayout(button_layout)

        # Adjust window size and margins for the grid layout
        self.setGeometry(100, 100, 800, 600)  # Keep the same window size
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Adding the depot blocks to the grid layout
        for i in range(depot_system.rows):
            for j in range(depot_system.cols):
                block = DepotBlock(i, j, depot_system)
                self.blocks[(i, j)] = block
                self.layout.addWidget(block, i, j)

        main_layout.addLayout(self.layout)  # Add grid layout below the button

        self.setLayout(main_layout)

    def optimize(self):
        """Call the Julia function to optimize the depot state and update GUI."""
        # Process buses from the Excel file
        file_path = "data/KAJSYK24_MA-TO.xlsx"  # Update with the correct file path
        busses = process_buses_from_excel(file_path)

        # Extract arrivals and departures as bus types
        arrivals = [bus.bus_id[:3] for bus in busses]
        departures = arrivals  # Assuming departures are the same as arrivals for now

        l = self.depot_system.rows  # Number of lanes
        v = self.depot_system.cols  # Total number of bus slots
        max_deviation = 5

        # Debugging: Print the data being sent to Julia
        print("GUI -> Julia: l =", l)
        print("GUI -> Julia: v =", v)
        print("GUI -> Julia: max_deviation =", max_deviation)
        print("GUI -> Julia: arrivals =", arrivals)
        print("GUI -> Julia: departures =", departures)

        # Call the Julia function with the bus type list
        X, Y, Z = self.depot_system.send_to_julia_with_params(l, v, max_deviation, arrivals, departures)

        # Map the results to the GUI
        assignments = self.map_bus_types_to_spots(Z)
        self.depot_system.assign_buses(assignments)
        self.update_blocks()

        # Ensure the GUI size remains unchanged
        self.setFixedSize(self.size())

    def map_bus_types_to_spots(self, bus_types):
        """Map bus types to available spots in the depot."""
        assignments = {}
        index = 0
        for i in range(self.depot_system.rows):
            for j in range(self.depot_system.cols):
                if self.depot_system.get_block_state(i, j) and index < len(bus_types):
                    assignments[(i, j)] = bus_types[index]
                    index += 1
        return assignments

    def update_blocks(self):
        """Refresh the GUI blocks to reflect the updated assignments."""
        for block in self.blocks.values():
            block.update_style()

    def print_matrix(self):
        """Print the depot matrix to the terminal."""
        matrix = self.depot_system.get_matrix()
        for row in matrix:
            print(row)

    def closeEvent(self, event):
        """Send the final depot state to Julia when the window is closed."""
        self.depot_system.send_to_julia()


