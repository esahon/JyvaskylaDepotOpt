from PySide6.QtWidgets import QApplication
import sys
from gui import DepotGUI
from system import DepotSystem

def main():
    app = QApplication(sys.argv)
    
    # Initialize system logic
    depot_system = DepotSystem(rows=6, cols=17)
    
    # Create GUI and pass the system logic to it
    window = DepotGUI(depot_system)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
