import pandas as pd
from flight_distance import *
# from optimizer import *
from weather import *

airport_identifiers = ['SIN', 'LAX', 'JFK', 'CDG', 'LHR']  # Replace with actual identifiers

#Get Airport Coordinates
lat_long_dict = get_airport_lat_long(airport_identifiers)
print("Coordinates: \n",lat_long_dict)

#Get Distance between each node (airports)
trip_distance = calculate_distances(airport_identifiers)
print("Distance b/w Airports: \n",trip_distance)

#Get onroute weather
weather = fetch_weather_for_all_routes(airport_identifiers,lat_long_dict)
print("On Route weather: \n", weather)

# # Ensure the graph is bidirectional (undirected)
# for (a, b), dist in list(trip_distance.items()):
#     trip_distance[(b, a)] = dist

# # Find the optimal route with the new cost metric
# optimal_route, optimal_distance = find_optimal_route(airport_identifiers, trip_distance)

# print("Optimal Route:", " -> ".join(optimal_route) + f" -> {optimal_route[0]}")
# print("Total Adjusted Distance/Cost:", optimal_distance)
