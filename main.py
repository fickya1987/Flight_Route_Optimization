import pandas as pd
from flight_distance import *
from optimize import *
from weather import *

airport_identifiers = ['IDSUB', 'RUNVS', 'IDJKT']  # Replace with actual identifiers

# Step 1: Get Airport Coordinates
lat_long_dict = get_airport_lat_long(airport_identifiers)

# Step 2: Get Distance between each node (airports)
trip_distance = calculate_distances(airport_identifiers)

# Step 3: Get on-route weather
# Assuming 'fetch_weather_for_all_routes' is available in weather module
raw_weather = fetch_weather_for_all_routes(airport_identifiers, lat_long_dict)
route_factors = extract_route_factors(raw_weather)

# Step 4: Ensure the graph is bidirectional (undirected)
for (a, b), dist in list(trip_distance.items()):
    trip_distance[(b, a)] = dist

# Step 5: Find the optimal route based on weather, temperature, and distance
optimal_route, optimal_distance = find_optimal_route(airport_identifiers, trip_distance, route_factors)

# Display the optimal route and total adjusted distance
print("Optimal Route:", " -> ".join(optimal_route) + f" -> {optimal_route[0]}")
print("Total Round Trip Distance:", optimal_distance, "km")

# Step 6: Fetch Aircraft Details (e.g., Boeing 787-9)
aircraft_type = "MERATUS BINTAN"
aircraft_specs = get_aircraft_details(aircraft_type)

# Check if aircraft details were retrieved successfully
if isinstance(aircraft_specs, str):
    print(aircraft_specs)  # Print error if aircraft not found
else:
    # Step 7: Check if the aircraft can fly the route
    route_feasibility = check_route_feasibility(optimal_route, trip_distance, aircraft_specs)

    if route_feasibility["Can Sail Entire Route"]:
        print(f"Total fuel required for the entire route: {route_feasibility['Total Fuel Required (kg)']} kg")
        print(f"Total sail time for the entire route: {route_feasibility['Total Sail Time (hrs)']} hours")
    else:
        print("The vessel cannot sail the entire route without refueling for at least one sector.")
