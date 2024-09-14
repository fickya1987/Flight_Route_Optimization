import itertools

# Define the distances between the airports
distances = {
    ('SIN', 'LAX'): 14101.48,
    ('LAX', 'JFK'): 3974.20,
    ('JFK', 'CDG'): 5833.66,
}

# Define the factors for each route segment
route_factors = {('SIN', 'LAX'): {'weather': 'clear sky', 'temperature': 27.18}, ('LAX', 'JFK'): {'weather': 'clear sky', 'temperature': 25.37}, ('JFK', 
'CDG'): {'weather': 'clear sky', 'temperature': 21.18}}

# Ensure the graph is bidirectional (undirected)
for (a, b), dist in list(distances.items()):
    distances[(b, a)] = dist

for (a, b), factors in list(route_factors.items()):
    route_factors[(b, a)] = factors

# Function to assign a risk factor based on weather
def weather_risk(weather):
    risk_factors = {
        "clear sky": 0.1,
        "few clouds": 0.2,
        "scattered clouds": 0.3,
        "broken clouds": 0.4,
        "overcast clouds": 0.5,
        "light rain": 0.6,
        "rain": 0.7,
        "storm": 0.9
    }
    return risk_factors.get(weather, 0.5)  # Default risk factor if not listed

# Function to normalize temperature impact
def temperature_impact(temperature):
    # Assuming ideal temperature for fuel efficiency is around 20-25°C
    if temperature < 20 or temperature > 25:
        return abs(temperature - 22.5) / 30  # Normalize to a value between 0 and 1
    return 0.1  # Low impact in the ideal range

# Calculate the adjusted cost for each route segment
def calculate_adjusted_cost(segment, base_distance):
    if segment not in route_factors:
        segment = (segment[1], segment[0])  # Check the reversed segment
    weather = route_factors[segment]["weather"]
    temperature = route_factors[segment]["temperature"]
    
    weather_cost = weather_risk(weather) * 100  # Weight for weather impact
    temperature_cost = temperature_impact(temperature) * 50  # Weight for temperature impact
    
    total_cost = base_distance + weather_cost + temperature_cost
    return total_cost

# Update the distance function to include additional factors
def calculate_route_distance(route, distances):
    """Calculate the total cost for a given route, including additional factors."""
    total_distance = 0
    for i in range(len(route) - 1):
        segment = (route[i], route[i + 1])
        if segment not in distances:
            segment = (route[i + 1], route[i])
        base_distance = distances[segment]
        total_distance += calculate_adjusted_cost(segment, base_distance)
    # Add distance to return to the starting point
    last_segment = (route[-1], route[0])
    if last_segment not in distances:
        last_segment = (route[0], route[-1])
    base_distance = distances[last_segment]
    total_distance += calculate_adjusted_cost(last_segment, base_distance)
    
    return total_distance

def find_optimal_route(airports, distances):
    """Find the optimal route that covers all airports."""
    best_route = None
    min_distance = float('inf')

    # Generate all possible permutations of the route
    for route in itertools.permutations(airports):
        current_distance = calculate_route_distance(route, distances)
        if current_distance < min_distance:
            min_distance = current_distance
            best_route = route

    return best_route, min_distance

# List of all airports
airports = ['SIN', 'LAX', 'JFK', 'CDG']

# Find the optimal route with the new cost metric
optimal_route, optimal_distance = find_optimal_route(airports, distances)

print("Optimal Route:", " -> ".join(optimal_route) + f" -> {optimal_route[0]}")
print("Total Adjusted Distance/Cost:", optimal_distance)
