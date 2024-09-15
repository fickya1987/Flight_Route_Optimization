import itertools

def extract_route_factors(raw_weather):
    """
    Extracts route factors from raw weather data by breaking down routes into individual segments.

    Parameters:
    - raw_weather (dict): The raw weather data with routes and corresponding weather details.

    Returns:
    - dict: A dictionary with segments as keys (in tuple format) and a list of weather and temperature data.
    """
    route_factors = {}
    for route, segments in raw_weather.items():
        for segment in segments:
            segment_key = tuple(segment['segment'].split(' -> '))
            if segment_key not in route_factors:
                route_factors[segment_key] = []
            route_factors[segment_key].append({
                'weather': segment['weather'],
                'temperature': segment['temperature']
            })
    return route_factors

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
def calculate_adjusted_cost(segment, base_distance, route_factors):
    # Handle both directions of the segment
    if segment in route_factors:
        factors = route_factors[segment]
    elif (segment[1], segment[0]) in route_factors:
        factors = route_factors[(segment[1], segment[0])]
    else:
        raise ValueError(f"Segment {segment} not found in route factors.")

    # Aggregate weather and temperature data if there are multiple entries for the segment
    weather_descriptions = [factor["weather"] for factor in factors]
    temperatures = [factor["temperature"] for factor in factors]

    most_common_weather = max(set(weather_descriptions), key=weather_descriptions.count)
    avg_temperature = sum(temperatures) / len(temperatures)
    
    weather_cost = weather_risk(most_common_weather) * 100  # Weight for weather impact
    temperature_cost = temperature_impact(avg_temperature) * 50  # Weight for temperature impact
    
    total_cost = base_distance + weather_cost + temperature_cost
    return total_cost

# Update the distance function to include additional factors
def calculate_route_distance(route, distances, route_factors):
    """Calculate the total cost for a given route, including additional factors."""
    total_distance = 0
    for i in range(len(route) - 1):
        segment = (route[i], route[i + 1])
        if segment not in distances:
            segment = (route[i + 1], route[i])
        base_distance = distances[segment]
        total_distance += calculate_adjusted_cost(segment, base_distance, route_factors)
    
    # Add distance to return to the starting point
    last_segment = (route[-1], route[0])
    if last_segment not in distances:
        last_segment = (route[0], route[-1])
    base_distance = distances[last_segment]
    total_distance += calculate_adjusted_cost(last_segment, base_distance, route_factors)
    
    return total_distance

def find_optimal_route(airports, distances, route_factors):
    """Find the optimal route that covers all airports."""
    best_route = None
    min_distance = float('inf')

    # Generate all possible permutations of the route
    for route in itertools.permutations(airports):
        try:
            current_distance = calculate_route_distance(route, distances, route_factors)
            if current_distance < min_distance:
                min_distance = current_distance
                best_route = route
        except ValueError as e:
            print(e)  # Log the error to debug missing segments

    return best_route, min_distance
