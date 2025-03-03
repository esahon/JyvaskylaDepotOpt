import pandas as pd
from datetime import datetime

class Bus:
    def __init__(self, bus_id, bus_type, departure_time):
        self.bus_id = bus_id
        self.bus_type = bus_type
        self.departure_time = departure_time  # Säilytetään `time`-muodossa

    def __repr__(self):
        return f"Bus(ID={self.bus_id}, Type={self.bus_type}, Departure={self.departure_time})"

# Bussityyppien määrittely (alkuliitteet ilman XXX)
BUS_TYPE_MAPPING = {
    "DMS": "Diesel",
    "DMV": "Diesel",
    "DTV": "Diesel",
    "SMS": "Electric",
    "SMV": "Electric",
    "STS": "Electric",
    "STV": "Electric",
    "SVV": "Electric",
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
    buses = []
    for _, row in df.iterrows():
        bus_id = row["Tunnus"]
        departure_time = row["Lähtöaika"]

        # Selvitä bussityyppi tarkistamalla alkuliite
        bus_type = next((key for key in BUS_TYPE_MAPPING.keys() if bus_id.startswith(key)), None)
        fuel_type = BUS_TYPE_MAPPING.get(bus_type)

        # Luo bussi-olio
        bus = Bus(bus_id, fuel_type, departure_time)
        buses.append(bus)

    return buses


# TESTI
if __name__ == "__main__":
    file_path = "data/KAJSYK24_MA-TO.xlsx"
    print(file_path)
    buses = process_buses_from_excel(file_path)
    print(buses[:10])
