import openpyxl


def fill_lane_assignments_mapping(file_path, departures_mapping, arrivals_mapping):
    """
    Fill Excel with departure and arrival lane assignments.
    
    Args:
        file_path: Path to the Excel file
        departures_mapping: Dictionary mapping Lane objects to lists of bus IDs (from buses_mapped)
        arrivals_mapping: Dictionary mapping Lane objects to lists of bus IDs (from lanes)
    """
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    
    # Clear column T and set header
    for row in range(1, sheet.max_row + 1):
        sheet[f"T{row}"] = None
    sheet["T1"] = "Lähtöpaikka"
    
    # Create mappings from bus ID to lane name
    bus_to_departure_lane = {}
    bus_to_arrival_lane = {}
    
    # Build departure mapping
    for lane, bus_list in departures_mapping.items():
        for bus_id in bus_list:
            bus_to_departure_lane[bus_id] = lane.name

    # Build arrival mapping
    for lane, bus_list in arrivals_mapping.items():
        for bus_id in bus_list:
            bus_to_arrival_lane[bus_id] = lane.name

    # Track first and last occurrences of each bus ID
    bus_occurrences = {}
    for row in range(2, sheet.max_row + 1):
        bus_id = sheet[f"A{row}"].value
        if bus_id:
            if bus_id not in bus_occurrences:
                bus_occurrences[bus_id] = {"first": row, "last": row}
            else:
                bus_occurrences[bus_id]["last"] = row

    # Fill in departure and arrival lanes
    for bus_id, rows in bus_occurrences.items():
        # For departures
        if bus_id in bus_to_departure_lane:
            sheet[f"T{rows['first']}"] = bus_to_departure_lane[bus_id]
        else:
            sheet[f"T{rows['first']}"] = "Ulkona"
            
        # For arrivals
        if bus_id in bus_to_arrival_lane:
            sheet[f"T{rows['last']}"] = bus_to_arrival_lane[bus_id]
        else:
            sheet[f"T{rows['last']}"] = "Ulkona"

    workbook.save(file_path)
