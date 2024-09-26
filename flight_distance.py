import pandas as pd
from math import radians, sin, cos, sqrt, asin

### Modular Flight Calculation Functions ###

def get_aircraft_details(aircraft_type):
    """
    Fetch aircraft details based on the given aircraft type.
    """
    csv_file = 'aircraft.csv'
    df = pd.read_csv(csv_file)
    if aircraft_type not in df['Aircraft'].values:
        return f"Aircraft type '{aircraft_type}' not found in the dataset."
    
    aircraft_details = df[df['Aircraft'] == aircraft_type][[
        'Range_km', 'Fuel_Consumption_kg/hr', 'Cruising Speed (kts)', 
        'Speed_kmh', 'MaxFlightTime_hr', 'Max_Fuel_Capacity_kg']]
    
    return aircraft_details.to_dict(orient='records')[0]


def get_airport_lat_long(identifiers):
    """
    Get latitude and longitude for a list of airport identifiers (IATA codes).
    """
    csv_file = 'airport.csv'
    parquet_file = 'airport.parquet'
    
    # Try reading the parquet file first
    try:
        df = pd.read_parquet(parquet_file)
    except FileNotFoundError:
        # If parquet file is not found, fall back to reading the CSV file
        df = pd.read_csv(csv_file)
    
    df_filtered = df[df['Airport_Name'].isin(identifiers) | df['IATA'].isin(identifiers)]
    lat_long_dict = {row['IATA']: (row['Lat'], row['Long']) for _, row in df_filtered.iterrows()}
    return lat_long_dict


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on Earth (in kilometers).
    """
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return round(R * 2 * asin(sqrt(a)), 2)


def calculate_distances(airport_identifiers):
    """
    Calculate the distance between each pair of airports.
    """
    lat_long_dict = get_airport_lat_long(airport_identifiers)
    distances = {}
    for i in range(len(airport_identifiers)):
        for j in range(i + 1, len(airport_identifiers)):
            airport1, airport2 = airport_identifiers[i], airport_identifiers[j]
            lat1, lon1 = lat_long_dict[airport1]
            lat2, lon2 = lat_long_dict[airport2]
            distances[(airport1, airport2)] = haversine_distance(lat1, lon1, lat2, lon2)
    return distances


def calculate_fuel_and_time_for_segment(segment_distance, aircraft_specs):
    """
    Calculate the fuel and time required for a single flight segment.
    """
    cruising_speed = aircraft_specs['Speed_kmh']
    fuel_burn_rate = aircraft_specs['Fuel_Consumption_kg/hr']
    max_fuel_capacity = aircraft_specs['Max_Fuel_Capacity_kg']
    reserve_fuel_percentage = 0.05  # 5% reserve fuel

    climb_speed, descent_speed = 300, 350
    climb_time, descent_time = 15 / 60, 10 / 60  # in hours
    climb_distance = climb_speed * climb_time
    descent_distance = descent_speed * descent_time

    # Calculate cruise distance
    cruise_distance = segment_distance - (climb_distance + descent_distance)
    cruise_distance = max(0, cruise_distance)  # Ensure cruise distance is not negative

    # Calculate flight time for each phase
    cruise_time = cruise_distance / cruising_speed
    total_flight_time = climb_time + cruise_time + descent_time

    # Calculate fuel required
    fuel_required = total_flight_time * fuel_burn_rate
    reserve_fuel = reserve_fuel_percentage * max_fuel_capacity
    total_fuel_with_reserve = fuel_required + reserve_fuel

    return total_fuel_with_reserve, total_flight_time
