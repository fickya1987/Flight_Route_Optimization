import requests
import itertools
from geopy.distance import geodesic

# Replace with your OpenWeather API key
API_KEY = '9811dd1481209c64fba6cb2c90f27140'

# Interpolation function to get intermediate points between airports
def get_intermediate_points(start, end, num_points=4):
    points = []
    lat_step = (end[0] - start[0]) / (num_points + 1)
    lon_step = (end[1] - start[1]) / (num_points + 1)
    
    for i in range(1, num_points + 1):
        point = (start[0] + lat_step * i, start[1] + lon_step * i)
        points.append(point)
    
    return points

# Fetch weather data for a given coordinate
def fetch_weather(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    return response.json()

# Fetch weather along all possible routes
def fetch_weather_for_all_routes(airport_identifiers, airports):
    route_factors = {}

    # Generate all possible routes (permutations) 
    for route in itertools.permutations(airport_identifiers, len(airport_identifiers)):
        route_key = " -> ".join(route)  # Key for route factors
        route_factors[route_key] = []

        for i in range(len(route) - 1):
            start_airport = route[i]
            end_airport = route[i + 1]
            start_coords = (airports[start_airport][0], airports[start_airport][1])
            end_coords = (airports[end_airport][0], airports[end_airport][1])
            
            # Get 4 intermediate points along the route
            points = get_intermediate_points(start_coords, end_coords)
            
            # Include start and end airport coordinates
            points.insert(0, start_coords)
            points.append(end_coords)
            
            # Fetch weather for each point
            weather_descriptions = []
            temperatures = []
            
            for point in points:
                weather = fetch_weather(point[0], point[1])
                weather_descriptions.append(weather['weather'][0]['description'])
                temperatures.append(weather['main']['temp'])
            
            # Aggregate weather for the route segment
            avg_temperature = sum(temperatures) / len(temperatures)
            most_common_weather = max(set(weather_descriptions), key=weather_descriptions.count)
            
            # Store the result in the route_factors dictionary for each route segment
            segment_key = f"{start_airport} -> {end_airport}"
            route_factors[route_key].append({
                "segment": segment_key,
                "weather": most_common_weather,
                "temperature": round(avg_temperature, 2)
            })

    return route_factors

# Example airport coordinates
airports = {
    'SIN': (1.3644, 103.9915),  # Singapore Changi Airport
    'LAX': (33.9416, -118.4085),  # Los Angeles International Airport
    'JFK': (40.6413, -73.7781),  # John F. Kennedy International Airport
    'CDG': (49.0097, 2.5479),  # Charles de Gaulle Airport
    'LHR': (51.4700, -0.4543)   # London Heathrow Airport
}

airport_identifiers = ['SIN', 'LAX', 'JFK', 'CDG', 'LHR']  # Replace with actual identifiers

# Fetch the weather along all possible routes
route_weather = fetch_weather_for_all_routes(airport_identifiers, airports)

# Display the weather data for each route
for route, factors in route_weather.items():
    print(f"Route: {route}")
    for factor in factors:
        print(f"  Segment: {factor['segment']}, Weather: {factor['weather']}, Temperature: {factor['temperature']} °C")
    print()
