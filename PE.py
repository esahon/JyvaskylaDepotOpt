import pandas as pd
from datetime import datetime
import copy
from julia import Main
from collections import Counter
from parking_busses import Lane, parking


# Load Julia script
Main.include("k_position_approach.jl")
Main.include("k_position_approach_PELA.jl") # Load the correct Julia script

class Bus:
    def __init__(self, bus_id, bus_fuel, bus_type, bus_color):
        self.bus_id = bus_id
        self.bus_fuel = bus_fuel
        self.bus_type = bus_type
        self.bus_color = bus_color

        self.arrival_time_MAKE = None # Saapumisaika alustetaan myöhemmin
        self.departure_time_TITO = None # Säilytetään `time`-muodossa

        self.arrival_time_TO = None # Saapumisaika alustetaan myöhemmin
        self.departure_time_PE = None # Säilytetään `time`-muodossa

        self.arrival_time_PE = None # Saapumisaika alustetaan myöhemmin
        self.departure_time_LA = None # Säilytetään `time`-muodossa

        self.arrival_time_LA = None # Saapumisaika alustetaan myöhemmin
        self.departure_time_SU = None # Säilytetään `time`-muodossa

        self.arrival_time_SU = None # Saapumisaika alustetaan myöhemmin
        self.departure_time_MA = None # Säilytetään `time`-muodossa


    def __repr__(self):
        return (
            f"Bus(\n"
            f"  ID={self.bus_id},\n"
            f"  Fuel={self.bus_fuel},\n"
            f"  Type={self.bus_type},\n"
            f"  Color={self.bus_color},\n\n"
            f"  Arrival_MAKE={self.arrival_time_MAKE},\n"
            f"  Departure_TITO={self.departure_time_TITO},\n\n"
            f"  Arrival_TO={self.arrival_time_TO},\n"
            f"  Departure_PE={self.departure_time_PE},\n\n"
            f"  Arrival_PE={self.arrival_time_PE},\n"
            f"  Departure_LA={self.departure_time_LA},\n\n"
            f"  Arrival_LA={self.arrival_time_LA},\n"
            f"  Departure_SU={self.departure_time_SU},\n\n"
            f"  Arrival_SU={self.arrival_time_SU}\n"
            f"  Departure_MA={self.departure_time_MA},\n"
            f")"
        )
        
# Bussityyppien määrittely (alkuliitteet ilman XXX)
BUS_TYPE_MAPPING = {
    "DMS": {"fuel": "Biodiesel", "type": "2-aks.", "color": "Super"},
    "DMV": {"fuel": "Biodiesel", "type": "2-aks.", "color": "Vihreä"},
    "SMS": {"fuel": "Sähkö", "type": "2-aks.", "color": "Super"},
    "SMV": {"fuel": "Sähkö", "type": "2-aks.", "color": "Vihreä"},
    "STS": {"fuel": "Sähkö", "type": "Teli", "color": "Super"},
    "STV": {"fuel": "Sähkö", "type": "Teli", "color": "Vihreä"},
    "SVV": {"fuel": "Sähkö", "type": "Volvo", "color": "Vihreä"}
    #"DTV": {"fuel": "Biodiesel", "type": "Teli", "color": "Vihreä"}
}

def all_arrivals_departures(file_paths):
    """Return all arrivals and departures from the bus list."""

    # Lataa Excel-tiedosto ja valitse vain Tunnus ja Lähtöaika
    df = pd.read_excel(file_paths[0], sheet_name=0, usecols=["Tunnus", "Lähtöaika", "Saapumisaika"])

    # Poista tyhjät arvot ja siisti Tunnus-sarake
    df = df.dropna(subset=["Tunnus", "Lähtöaika", "Saapumisaika"])  # Poista tyhjät rivit
    df["Tunnus"] = df["Tunnus"].str.strip()  # Poista ylimääräiset välilyönnit
 
    # Convert "Lähtöaika" and "Saapumisaika" to hours as decimals
    df["Lähtöaika"] = pd.to_datetime(df["Lähtöaika"], format="%H:%M:%S", errors="coerce").apply(
        lambda x: x.hour + x.minute / 60 if pd.notnull(x) else None
    )
    df["Saapumisaika"] = pd.to_datetime(df["Saapumisaika"], format="%H:%M:%S", errors="coerce").apply(
        lambda x: x.hour + x.minute / 60 if pd.notnull(x) else None
    )
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
        bus = Bus(bus_id, bus_fuel, bus_type, bus_color)
        bus.arrival_time_MAKE = arrival_time
        bus.departure_time_TITO = departure_time
        bus.departure_time_MA = departure_time
        busses.append(bus)

    for i in range(len(file_paths)-1):
        # Lataa Excel-tiedosto ja valitse vain Tunnus ja Lähtöaika
        df = pd.read_excel(file_paths[i], sheet_name=0, usecols=["Tunnus", "Saapumisaika"])
        df_2 = pd.read_excel(file_paths[i+1], sheet_name=0, usecols=["Tunnus", "Lähtöaika"])

        valid_types = list(BUS_TYPE_MAPPING.keys())

        def contains_valid_prefix(bus_id):
            return any(prefix in bus_id for prefix in valid_types)

        df = df[df["Tunnus"].apply(contains_valid_prefix)]
        df_2 = df_2[df_2["Tunnus"].apply(contains_valid_prefix)]

        # Merge the dataframes for "Tunnus", "Lähtöaika", and "Saapumisaika"
        #df_combined = pd.merge(
        #    df,
        #    df_2,
        #    on="Tunnus",
        #    how="inner"
        #)
        #df_combined = df_combined.dropna(subset=["Tunnus", "Lähtöaika", "Saapumisaika"])  # Poista tyhjät rivit
        #df_combined["Tunnus"] = df_combined["Tunnus"].str.strip()  # Poista ylimääräiset välilyönnit
        df["Tunnus"] = df["Tunnus"].str.strip()  # Poista ylimääräiset välilyönnit
        df_2["Tunnus"] = df_2["Tunnus"].str.strip()  # Poista ylimääräiset välilyönnit

    
        df["Saapumisaika"] = pd.to_datetime(df["Saapumisaika"], format="%H:%M:%S", errors="coerce").apply(
            lambda x: x.hour + x.minute / 60 if pd.notnull(x) else None
        )
        df_2["Lähtöaika"] = pd.to_datetime(df_2["Lähtöaika"], format="%H:%M:%S", errors="coerce").apply(
            lambda x: x.hour + x.minute / 60 if pd.notnull(x) else None
        )
        
        
        # Group by "Tunnus" and get the smallest "Lähtöaika" and largest "Saapumisaika"
        df = df.groupby("Tunnus").agg(
            largest_arrival=("Saapumisaika", "max")
        ).reset_index()

        df_2 = df_2.groupby("Tunnus").agg(
            smallest_departure=("Lähtöaika", "min")
        ).reset_index()

        # Update the bus objects with the new arrival and departure times
        for _, row in df.iterrows():
            bus_id = row["Tunnus"]
            arrival_time = row["largest_arrival"]

            bus_ids = [b.bus_id for b in busses]
            if bus_id not in bus_ids:
                # If the bus_id is not in the list, create a new bus object
                bus = Bus(bus_id, BUS_TYPE_MAPPING[bus_id[:3]]["fuel"], BUS_TYPE_MAPPING[bus_id[:3]]["type"], BUS_TYPE_MAPPING[bus_id[:3]]["color"])
                busses.append(bus)
            # Find the corresponding bus object
            bus = next((b for b in busses if b.bus_id == bus_id), None)
            if bus:
                # Update the appropriate departure and arrival times
                if i == 0:
                    bus.arrival_time_TO = arrival_time
                elif i == 1:
                    bus.arrival_time_PE = arrival_time
                elif i == 2:
                    bus.arrival_time_LA = arrival_time
                elif i == 3:
                    bus.arrival_time_SU = arrival_time


        for _, row in df_2.iterrows():
            bus_id = row["Tunnus"]
            departure_time = row["smallest_departure"]

            bus_ids = [b.bus_id for b in busses]
            if bus_id not in bus_ids:
                # If the bus_id is not in the list, create a new bus object
                bus = Bus(bus_id, BUS_TYPE_MAPPING[bus_id[:3]]["fuel"], BUS_TYPE_MAPPING[bus_id[:3]]["type"], BUS_TYPE_MAPPING[bus_id[:3]]["color"])
                busses.append(bus)

            # Find the corresponding bus object 
            bus = next((b for b in busses if b.bus_id == bus_id), None)
            if bus:
                # Update the appropriate departure and arrival times
                if i == 4:
                    bus.departure_time_TITO = departure_time
                elif i == 0:
                    bus.departure_time_PE = departure_time
                elif i == 1:
                    bus.departure_time_LA = departure_time
                elif i == 2:
                    bus.departure_time_SU = departure_time


    # Print the bus objects for debugging
    #for bus in busses:
    #    print(bus)
    for bus in busses:
        if bus.bus_id == "SVV703":
            print(bus)  

    print("Nro of buses:")
    print(len(busses))

    return busses

def adjust_none_arrivals(busses):
    """Adjust buses with None in arrival or departure times by adding 24 hours."""
    count = 0
    for bus in busses:
        if bus.arrival_time_MAKE is None:
            bus.arrival_time_MAKE = 24.0  
        if bus.departure_time_TITO is None:
            bus.departure_time_TITO = 24.0
        if bus.arrival_time_TO is None:
            bus.arrival_time_TO = 24.0
        if bus.departure_time_PE is None:
            bus.departure_time_PE = 24.0
        if bus.arrival_time_PE is None:
            bus.arrival_time_PE = 24.0
        if bus.departure_time_LA is None:
            bus.departure_time_LA = 24.0
        if bus.arrival_time_LA is None:
            bus.arrival_time_LA = 24.0
        if bus.departure_time_SU is None:
            bus.departure_time_SU = 24.0
        if bus.arrival_time_SU is None:
            bus.arrival_time_SU = 24.0
        if bus.departure_time_MA is None:
            bus.departure_time_MA = 24.0


if __name__ == "__main__":
    file_path1 = "data/KAJSYK24_MA-TO.xlsx"
    file_path2 = "data/KAJSYK24_PE.xlsx"
    file_path3 = "data/KAJSYK24_LA.xlsx"
    file_path4 = "data/KAJSYK24_SU.xlsx"
    file_path5 = "data/KAJSYK24_MA-TO.xlsx"
    file_paths = [file_path1, file_path2, file_path3, file_path4, file_path5]
    print(file_paths)
    busses = all_arrivals_departures(file_paths)
    #print(busses)

    # Convert "SVV" buses to "SMV" type
    for bus in busses:
        if bus.bus_id[:3] == "SVV":
            bus.bus_id = bus.bus_id.replace("SVV", "SMV", 1)
            bus.bus_fuel = BUS_TYPE_MAPPING["SMV"]["fuel"]
            bus.bus_type = BUS_TYPE_MAPPING["SMV"]["type"]
            bus.bus_color = BUS_TYPE_MAPPING["SMV"]["color"]

    # Adjust None arrival times
    #adjust_none_arrivals(busses)

    # PITÄÄ LISÄTÄ None aikoihin +24.00 per None arrival

    # Remove buses with None values in any of the arrival or departure times
    busses_arrivals_PE = []
    for bus in busses:
        if bus.arrival_time_PE is not None:
            busses_arrivals_PE.append(bus)

    busses_departures_LA = []
    for bus in busses:
        if bus.departure_time_LA is not None:
            busses_departures_LA.append(bus)

    # Find the SMV or STS buses that are parked behind the DMS or DMV buses (H, I, J columns). 
    arrival_ids_TO = []
    for bus in busses_arrivals_TO:
        arrival_ids_TO.append(bus.bus_id)

    departures_to_remove = [bus for bus in busses_departures_PE if bus.bus_id not in arrival_ids_TO][:2]
    for bus in departures_to_remove:
        busses_departures_PE.remove(bus)


    print("busses_arrivals_TO")
    print(busses_arrivals_TO)
    print("busses_departures_PE")
    print(busses_departures_PE)

        

    #arrivals_MAKE = copy.copy(sorted(busses, key=lambda x: x.arrival_time_MAKE))
    #departures_TITO = copy.copy(sorted(busses, key=lambda x: x.departure_time_TITO))

    arrivals_TO = copy.copy(sorted(busses_arrivals_TO, key=lambda x: x.arrival_time_TO))
    departures_PE = copy.copy(sorted(busses_departures_PE, key=lambda x: x.departure_time_PE))

    #arrivals_PE = copy.copy(sorted(busses, key=lambda x: x.arrival_time_PE))
    #departures_LA = copy.copy(sorted(busses, key=lambda x: x.departure_time_LA))

    #arrivals_LA = copy.copy(sorted(busses, key=lambda x: x.arrival_time_LA))
    #departures_SU = copy.copy(sorted(busses, key=lambda x: x.departure_time_SU))

    #arrivals_SU = copy.copy(sorted(busses, key=lambda x: x.arrival_time_SU))
    #arrivals_MA = copy.copy(sorted(busses, key=lambda x: x.departure_time_MA))


    arrivals_list_TO = []
    for_parking = []
    for bus in arrivals_TO:
        for_parking.append(bus.bus_id)
        arrivals_list_TO.append(bus.bus_id[:3])
    
    departures_list_PE = []
    for bus in departures_PE:
        departures_list_PE.append(bus.bus_id[:3])

    print(f"\nArrivals: {len(arrivals_list_TO)}")
    print(f"\nDepartures: {len(departures_list_PE)}")

    print(arrivals_list_TO[:4])
    print("Nro of buses in arrivals_list_MAKE:")
    print(len(arrivals_list_TO))
    print("Nro of busess in departures_list_TITO:")
    print(len(departures_list_PE))

    l = 12  # Number of lanes
    v = 6  # Total number of bus slots
    max_deviation = 5

    X, Y, Z , P = Main.optimize_model_k_approach(l, v, max_deviation, arrivals_list_TO, departures_list_PE)


    lanes_list = []
    for i, pat in enumerate(P):
        if X[i] > 0.99:
            for j in range(round(X[i])):
                print(f"Pattern {i+1}: {round(X[i])} instances of, {pat} pattern")
                obj = Lane(pat, i)
                lanes_list.append(obj)


    buses_mapped = parking(lanes_list, for_parking)
    #print(buses_mapped)