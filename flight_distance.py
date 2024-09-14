import pandas as pd
from math import *

def get_aircraft_details(aircraft_type):
    # Load the CSV file
    csv_file = r'aircraft.csv'  # Replace with the actual path if needed
    df = pd.read_csv(csv_file)

    # Check if the aircraft type exists in the DataFrame
    if aircraft_type not in df['Aircraft'].values:
        return f"Aircraft type '{aircraft_type}' not found in the dataset."

    # Fetch the relevant details for the given aircraft type
    aircraft_details = df[df['Aircraft'] == aircraft_type][[
        'Range_km',
        'Fuel_Consumption_kg/hr',
        'Cruising Speed (kts)',
        'Speed_kmh',
        'MaxFlightTime_hr',
        'Max_Fuel_Capacity_kg'
    ]]

    # Convert the result to a dictionary for easier reading
    details_dict = aircraft_details.to_dict(orient='records')[0]

    return details_dict

def get_airport_lat_long(identifiers):
    """
    Fetch latitude and longitude for a list of airport names or IATA codes.

    :param identifiers: List of airport names or IATA codes (minimum of 2)
    :return: Dictionary with airport identifiers as keys and (latitude, longitude) tuples as values
    """
    if len(identifiers) < 2:
        return "Please provide at least two airport identifiers."

    # Load the CSV file
    csv_file = r'airport.csv'  # Replace with the actual path if needed
    df = pd.read_csv(csv_file)

    # Efficiently filter rows where the 'Name' or 'IATA' matches any of the provided identifiers
    df_filtered = df[df['Airport_Name'].isin(identifiers) | df['IATA'].isin(identifiers)]

    # Extract relevant information and store in a dictionary
    lat_long_dict = {}
    for _, row in df_filtered.iterrows():
        identifier = row['IATA'] if row['IATA'] in identifiers else row['Name']
        lat_long_dict[identifier] = (row['Lat'], row['Long'])

    # Check if all identifiers were found
    not_found = [id for id in identifiers if id not in lat_long_dict]
    if not_found:
        return f"These identifiers were not found: {', '.join(not_found)}"

    return lat_long_dict

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on the Earth.
    """
    R = 6371.0  # Radius of Earth in kilometers
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    distance = round(R * c,2)
    return distance

def calculate_distances(airport_identifiers):
    """
    Calculate the distance between multiple airports.
    :param airport_identifiers: List of airport names or IATA codes
    :return: Dictionary with airport pairs as keys and their distances in kilometers as values
    """
    lat_long_dict = get_airport_lat_long(airport_identifiers)
    if isinstance(lat_long_dict, str):  # Check if there was an error fetching airport data
        return lat_long_dict

    # Calculate the distance for each combination of airports
    distances = {}
    identifiers = list(lat_long_dict.keys())
    for i in range(len(identifiers)):
        for j in range(i + 1, len(identifiers)):
            airport1 = identifiers[i]
            airport2 = identifiers[j]
            lat1, lon1 = lat_long_dict[airport1]
            lat2, lon2 = lat_long_dict[airport2]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            distances[(airport1, airport2)] = distance

    return distances

# Example usage:
# aircraft_type = input("Enter the aircraft type: ")
# aircraft_specs = get_aircraft_details(aircraft_type)
# print(aircraft_specs)

# fuel_burn_rate = aircraft_specs['Fuel_Consumption_kg/hr']
# cruising_speed = aircraft_specs['Max_Fuel_Capacity_kg']
# max_fuel_capacity = aircraft_specs['Speed_kmh']
# reserve_fuel_percentage = 0.05  # 5% reserve

# #Reserver Fuel calculation
# reserve_fuel = reserve_fuel_percentage*max_fuel_capacity

# #Flight Time
# flight_time = trip_distance/cruising_speed

# #Fuel needed for Trip
# fuel_required = flight_time*fuel_burn_rate

# total_fuel_with_reserve = fuel_required+reserve_fuel

# if total_fuel_with_reserve>max_fuel_capacity:
#     print("Cant Fly without refuel")
# else:
#     print(f"Total fuel required for the trip (including reserve): {round(total_fuel_with_reserve,2)} kg")
    
