from PySide6.QtWidgets import QApplication
import sys
from gui import DepotGUI
from system import DepotSystem
from bus_processor import process_buses_from_excel

def main():
    app = QApplication(sys.argv)
    
    # Process buses from the Excel file
    file_path = "data/KAJSYK24_MA-TO.xlsx"  # Update with the correct file path
    busses = process_buses_from_excel(file_path)
    bus_type_list = [bus.bus_id[:3] for bus in busses]  # Extract bus types

    # Initialize system logic
    rows, cols = 6, 12  # Updated depot dimensions
    depot_system = DepotSystem(rows=rows, cols=cols)

    # Pass bus types to the system (optional, if needed for initialization)
    # Example: depot_system.initialize_bus_types(bus_type_list)

    # Create GUI and pass the system logic to it
    window = DepotGUI(depot_system)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
