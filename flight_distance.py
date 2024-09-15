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

def calculate_fuel_and_time(distance, cruising_speed, fuel_burn_rate, reserve_fuel_percentage, max_fuel_capacity):
    """
    Calculate the total fuel required for a given distance including reserve fuel and flight time.

    :param distance: Distance of the trip in kilometers
    :param cruising_speed: Cruising speed of the aircraft in km/h
    :param fuel_burn_rate: Fuel consumption rate in kg/hr
    :param reserve_fuel_percentage: Percentage of fuel to keep as reserve
    :param max_fuel_capacity: Maximum fuel capacity of the aircraft in kg
    :return: Total fuel required including reserve, and estimated flight time
    """
    # Phase speeds and times
    climb_speed = 280  # km/h
    climb_time = 15 / 60  # 15 minutes in hours
    descent_speed = 250  # km/h
    descent_time = 10 / 60  # 10 minutes in hours

    # Calculate distances for each phase
    climb_distance = climb_speed * climb_time
    descent_distance = descent_speed * descent_time
    cruise_distance = distance - (climb_distance + descent_distance)

    # Adjust if cruise distance is negative (short flights)
    if cruise_distance < 0:
        climb_time = climb_distance / climb_speed
        descent_time = descent_distance / descent_speed
        cruise_distance = 0

    cruise_time = cruise_distance / cruising_speed

    # Total flight time
    total_flight_time = climb_time + cruise_time + descent_time

    # Fuel calculations
    fuel_required = total_flight_time * fuel_burn_rate
    reserve_fuel = reserve_fuel_percentage * max_fuel_capacity
    total_fuel_with_reserve = fuel_required + reserve_fuel

    return total_fuel_with_reserve, total_flight_time


def check_route_feasibility(aircraft_type, trip_distances, aircraft_specs):
    """
    Check if the aircraft can fly each route without needing refuel and return expected flight times.

    :param aircraft_type: The type of the aircraft (e.g., "Airbus A320")
    :param trip_distances: Dictionary with airport pairs and distances
    :param aircraft_specs: Dictionary containing aircraft details
    :return: Dictionary with feasibility and flight time for each route
    """
    # Extract aircraft specifications
    fuel_burn_rate = aircraft_specs['Fuel_Consumption_kg/hr']  # kg per hour
    cruising_speed = aircraft_specs['Speed_kmh']  # km/h
    max_fuel_capacity = aircraft_specs['Max_Fuel_Capacity_kg']  # kg
    reserve_fuel_percentage = 0.05  # 5% reserve

    results = {}

    # Check feasibility for each route
    for (airport1, airport2), distance in trip_distances.items():
        # Calculate the total fuel required and flight time for the trip including reserve
        total_fuel_with_reserve, flight_time = calculate_fuel_and_time(
            distance, cruising_speed, fuel_burn_rate, reserve_fuel_percentage, max_fuel_capacity
        )

        if total_fuel_with_reserve > max_fuel_capacity:
            results[(airport1, airport2)] = {
                "Can Fly": False,
                "Reason": f"Cannot fly without refuel. Required: {round(total_fuel_with_reserve, 2)} kg, Capacity: {max_fuel_capacity} kg",
                "Expected Flight Time (hrs)": round(flight_time, 2)
            }
        else:
            results[(airport1, airport2)] = {
                "Can Fly": True,
                "Expected Flight Time (hrs)": round(flight_time, 2),
                "Total Fuel Required (kg)": round(total_fuel_with_reserve, 2)
            }
    return results

def can_fly_route(aircraft_type, airport_identifiers):
    """
    Determine if the aircraft can fly the route without needing refuel, considering fuel capacity and reserve.

    :param aircraft_type: The type of the aircraft (e.g., "Airbus A320")
    :param airport_identifiers: List of airport names or IATA codes
    :return: String message indicating if the aircraft can complete the trip or not
    """
    # Fetch aircraft details
    aircraft_specs = get_aircraft_details(aircraft_type)
    if isinstance(aircraft_specs, str):
        return aircraft_specs  # Return the error message if aircraft details are not found

    # Calculate distances between airports
    trip_distances = calculate_distances(airport_identifiers)
    if isinstance(trip_distances, str):
        return trip_distances  # Return the error message if distances could not be calculated

    # Check if the aircraft can fly each route without refuel
    return check_route_feasibility(aircraft_type, trip_distances, aircraft_specs)

# aircraft_type = input("Enter the aircraft type: ")
# aircraft_specs = get_aircraft_details(aircraft_type)
# print(aircraft_specs)

# airport_list = ['CCU', 'CDG', 'SIN']
# print(get_airport_lat_long(airport_list))

# trip_distance = calculate_distances(airport_list)
# print(trip_distance)

# # Check if the aircraft can fly the route without refuel
# result = can_fly_route(aircraft_type, airport_list)
# print(result)