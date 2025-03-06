import pandas as pd
from datetime import datetime

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
    "DTV": {"fuel": "Biodiesel", "type": "Teli", "color": "Vihreä"},
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
    print(df)
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
    print(busses[:5])

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