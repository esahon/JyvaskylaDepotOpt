import pandas as pd
from datetime import datetime

from julia import Main
from collections import Counter

# Load Julia script
Main.include("k_position_approach.jl")

class Bus:
    def __init__(self, bus_id, bus_fuel, bus_type, bus_color, departure_time):
        self.bus_id = bus_id
        self.bus_fuel = bus_fuel
        self.bus_type = bus_type
        self.bus_color = bus_color
        self.departure_time = departure_time  # Säilytetään `time`-muodossa

    def __repr__(self):
        return f"Bus(ID={self.bus_id}, Fuel={self.bus_fuel}, Type={self.bus_type}, Color={self.bus_color}, Departure={self.departure_time})"

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
    df = pd.read_excel(file_path, usecols=["Tunnus", "Lähtöaika"])

    # Poista tyhjät arvot ja siisti Tunnus-sarake
    df = df.dropna(subset=["Tunnus", "Lähtöaika"])  # Poista tyhjät rivit
    df["Tunnus"] = df["Tunnus"].str.strip()  # Poista ylimääräiset välilyönnit
 
    df["Lähtöaika"] = pd.to_datetime(df["Lähtöaika"], format="%H:%M:%S", errors="coerce").dt.time
    df = df.dropna(subset=["Lähtöaika"])

    valid_types = list(BUS_TYPE_MAPPING.keys())

    def contains_valid_prefix(bus_id):
        return any(prefix in bus_id for prefix in valid_types)

    df = df[df["Tunnus"].apply(contains_valid_prefix)]

    # Pidä vain jokaisen Tunnuksen ensimmäinen Lähtöaika
    df = df.sort_values(by="Lähtöaika")  # Järjestä lähtöajat aikajärjestykseen
    df = df.drop_duplicates(subset=["Tunnus"], keep="first")  # Pidä ensimmäinen rivi jokaiselle Tunnukselle
    # Luo bussit DataFramesta
    busses = []
    for _, row in df.iterrows():
        bus_id = row["Tunnus"]
        departure_time = row["Lähtöaika"]

        # Selvitä bussityyppi tarkistamalla alkuliite
        bus_type_key = next((key for key in BUS_TYPE_MAPPING.keys() if bus_id.startswith(key)), None)
        bus_type_mapping = BUS_TYPE_MAPPING.get(bus_type_key)

        bus_fuel = bus_type_mapping["fuel"]
        bus_type = bus_type_mapping["type"]
        bus_color = bus_type_mapping["color"]

        # Luo bussi-olio
        bus = Bus(bus_id, bus_fuel, bus_type, bus_color, departure_time)
        busses.append(bus)

    return busses


# TESTI
if __name__ == "__main__":
    file_path = "data/KAJSYK24_MA-TO.xlsx"
    print(file_path)
    busses = process_buses_from_excel(file_path)
    #bus_type_list = bus_type_list[:-4]
    

    # Filter out "teli" type buses
    teli_buses = [bus for bus in busses if "Teli" in bus.bus_type]

    # Sort "teli" buses by departure time in descending order
    teli_buses_sorted = sorted(teli_buses, key=lambda x: x.departure_time, reverse=True)

    # Keep only the five "teli" buses with the latest departure times
    teli_buses_to_keep = teli_buses_sorted[:5]

    # Create the bus_type_list with only the required buses
    bus_type_list = [
        bus.bus_id[:3] for bus in busses 
        if "Teli" not in bus.bus_type or bus in teli_buses_to_keep
    ]

    # Print the "teli" buses remaining in the list after filtering
    teli_buses_remaining = [
        bus for bus in busses 
        if "Teli" in bus.bus_type and bus in teli_buses_to_keep
    ]
    print("\nTeli buses remaining after filtering:")
    for bus in teli_buses_remaining:
        print(bus)
    
    # Remove the last "DMV" type bus from bus_type_list
    for i in range(len(bus_type_list) - 1, -1, -1):
        if bus_type_list[i] == "DMV":
            del bus_type_list[i]
            break

    # Print the final bus_type_list
    print(f"\nBuses in bus_type_list: {len(bus_type_list)}")
    print("\nFinal bus_type_list:")
    print(bus_type_list)

    type_counts = Counter(bus_type_list)
    print(f"\nNumber of different types in bus_type_list: {len(type_counts)}")
    print("Counts of each type:")
    for bus_type, count in type_counts.items():
        print(f"{bus_type}: {count}")


    l = 12  # Number of lanes
    v = 6  # Total number of bus slots
    max_deviation = 5
    arrivals = bus_type_list
    departures = bus_type_list

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