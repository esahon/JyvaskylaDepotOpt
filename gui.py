from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QSizePolicy

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
        """Update appearance based on block state."""
        state = self.depot_system.get_block_state(self.x, self.y)
        self.setText("On" if state else "Off")
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

        # Increase window size and add margins for the grid layout
        self.setGeometry(100, 100, 800, 600)
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
        """Call the Julia function to optimize the depot state."""
        self.depot_system.send_to_julia()

    def print_matrix(self):
        """Print the depot matrix to the terminal."""
        matrix = self.depot_system.get_matrix()
        for row in matrix:
            print(row)

    def closeEvent(self, event):
        """Send the final depot state to Julia when the window is closed."""
        self.depot_system.send_to_julia()


