import pandas as pd
from datetime import datetime
import copy

from julia import Main
from collections import Counter

# Load Julia script
Main.include("k_position_approach.jl")

class Bus:
    def __init__(self, bus_id, bus_fuel, bus_type, bus_color, departure_time, arrival_time):
        self.bus_id = bus_id
        self.bus_fuel = bus_fuel
        self.bus_type = bus_type
        self.bus_color = bus_color
        self.departure_time = departure_time  # Säilytetään `time`-muodossa
        self.arrival_time = arrival_time # Saapumisaika alustetaan myöhemmin

    def __repr__(self):
        return f"Bus(ID={self.bus_id}, Fuel={self.bus_fuel}, Type={self.bus_type}, Color={self.bus_color}, Departure={self.departure_time}, Arrival={self.arrival_time})"

# Bussityyppien määrittely (alkuliitteet ilman XXX)
BUS_TYPE_MAPPING = {
    "DMS": {"fuel": "Biodiesel", "type": "2-aks.", "color": "Super"},
    "DMV": {"fuel": "Biodiesel", "type": "2-aks.", "color": "Vihreä"},
    "SMS": {"fuel": "Sähkö", "type": "2-aks.", "color": "Super"},
    "SMV": {"fuel": "Sähkö", "type": "2-aks.", "color": "Vihreä"},
    "STS": {"fuel": "Sähkö", "type": "Teli", "color": "Super"},
    "STV": {"fuel": "Sähkö", "type": "Teli", "color": "Vihreä"},
}

def process_buses_from_excel(file_path):
    # Lataa Excel-tiedosto ja valitse vain Tunnus ja Lähtöaika
    df = pd.read_excel(file_path, sheet_name=0, usecols=["Tunnus", "Lähtöaika", "Saapumisaika"])

    # Poista tyhjät arvot ja siisti Tunnus-sarake
    df = df.dropna(subset=["Tunnus", "Lähtöaika", "Saapumisaika"])  # Poista tyhjät rivit
    df["Tunnus"] = df["Tunnus"].str.strip()  # Poista ylimääräiset välilyönnit
 
    df["Lähtöaika"] = pd.to_datetime(df["Lähtöaika"], format="%H:%M:%S", errors="coerce").dt.time
    df["Saapumisaika"] = pd.to_datetime(df["Saapumisaika"], format="%H:%M:%S", errors="coerce").dt.time
    df = df.dropna(subset=["Lähtöaika", "Saapumisaika"])

    valid_types = list(BUS_TYPE_MAPPING.keys())

    def contains_valid_prefix(bus_id):
        return any(prefix in bus_id for prefix in valid_types)

    df = df[df["Tunnus"].apply(contains_valid_prefix)]
    
    #Ryhmittele Tunnuksen mukaan ja ota pienin Lähtöaika ja suurin Saapumisaika
    grouped = df.groupby("Tunnus").agg(
        smallest_departure=("Lähtöaika", "min"),
        largest_arrival=("Saapumisaika", "max")
    ).reset_index()
    # Luo bussit DataFramesta
    busses = []
    for _, row in grouped.iterrows():
        bus_id = row["Tunnus"]
        departure_time = row["smallest_departure"]
        arrival_time = row["largest_arrival"]

        # Selvitä bussityyppi tarkistamalla alkuliite
        bus_type_key = next((key for key in BUS_TYPE_MAPPING.keys() if bus_id.startswith(key)), None)
        bus_type_mapping = BUS_TYPE_MAPPING.get(bus_type_key)

        bus_fuel = bus_type_mapping["fuel"]
        bus_type = bus_type_mapping["type"]
        bus_color = bus_type_mapping["color"]

        # Luo bussi-olio
        bus = Bus(bus_id, bus_fuel, bus_type, bus_color, departure_time, arrival_time)
        busses.append(bus)

    return busses


# TESTI
if __name__ == "__main__":
    file_path = "data/KAJSYK24_PE.xlsx"
    print(file_path)
    busses = process_buses_from_excel(file_path)
    #bus_type_list = bus_type_list[:-4]
    

    # Filter out "teli" type buses
    teli_buses = [bus for bus in busses if "Teli" in bus.bus_type]

    # Sort "teli" buses by departure time in descending order
    teli_buses_sorted = sorted(teli_buses, key=lambda x: (datetime.combine(datetime.min, x.arrival_time) - datetime.combine(datetime.min, x.departure_time)).total_seconds(), reverse=True)

    # Keep only the five "teli" buses with the latest departure times
    teli_buses_to_keep = [
        bus for bus in teli_buses_sorted 
        if bus.departure_time <= datetime.strptime("08:00", "%H:%M").time()
    ]
    teli_buses_to_keep = teli_buses_to_keep[:5]

    print(teli_buses_to_keep)

    # Create the bus_type_list with only the required buses
    bus_type_list = busses

    # Print the "teli" buses remaining in the list after filtering
    #teli_buses_remaining = [
    #    bus for bus in busses 
    #    if "Teli" in bus.bus_type and bus in teli_buses_to_keep
    #]
    #print("\nTeli buses remaining after filtering:")
    #for bus in teli_buses_remaining:
    #    print(bus)
    

    if len(bus_type_list) > 72 + 17:
        diff = len(bus_type_list) - 72 - 17
        dmv_count = 0
        for i in range(len(bus_type_list) - 1, -1, -1):
            if bus_type_list[i].bus_id[:3] == "DMV":
                del bus_type_list[i]
                dmv_count += 1
            if dmv_count == diff:
                break
    print("Size of bus_type_list:")
    print(len(bus_type_list))

    bus_type_list_increasing_arrival = copy.copy(sorted(bus_type_list, key=lambda x: x.arrival_time))
    bus_type_list_increasing_departure = copy.copy(sorted(bus_type_list, key=lambda x: x.departure_time))

    # Print the final bus_type_list
    print(f"\nBuses in bus_type_list sorted by departures: {len(bus_type_list_increasing_arrival)}")
    print("\nFinal bus_type_list:")
    print(bus_type_list_increasing_arrival)

    type_counts = Counter([bus.bus_type[:3] for bus in bus_type_list_increasing_arrival])
    print(f"\nNumber of different types in bus_type_list: {len(type_counts)}")
    print("Counts of each type:")
    for bus_type, count in type_counts.items():
        print(f"{bus_type[:3]}: {count}")


    l = 12  # Number of lanes
    v = 6  # Total number of bus slots
    max_deviation = 1
    arrivals = []
    
    while bus_type_list_increasing_arrival:
        bus = bus_type_list_increasing_arrival.pop(0)
        arrivals.append(bus.bus_id[:3])
    
    departures = []
    while bus_type_list_increasing_departure:
        bus = bus_type_list_increasing_departure.pop(0)
        departures.append(bus.bus_id[:3])

    print(f"\nArrivals: {arrivals}")
    print(f"\nDepartures: {departures}")

    # Call the function with parameters
    # X on vektori, jonka arvot kertovat patternien määrän kullekin patternin indexille.
    #  Esim: [1, 0, 3, 0] -> 1 kpl pattern 1, 0 kpl pattern 2, 3 kpl pattern 3, 0 kpl pattern 4
    X, Y, Z = Main.optimize_model_k_approach(l, v, max_deviation, arrivals, departures)

    bus_id_to_find = "SMV501"
    for bus in busses:
        if bus.bus_id == bus_id_to_find:
            bus_found = bus
            break

    if bus_found:
        print(f"\nBus with ID {bus_id_to_find}:")
        print(bus_found)
    else:
        print(f"\nNo bus found with ID {bus_id_to_find}")