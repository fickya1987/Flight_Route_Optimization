import requests
import itertools
from geopy.distance import geodesic
from functools import lru_cache

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
@lru_cache(maxsize=128)
def fetch_weather(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    return response.json()

# Fetch weather data for a specific segment (using caching to avoid redundant requests)
def get_segment_weather(start_coords, end_coords):
    points = get_intermediate_points(start_coords, end_coords)
    points.insert(0, start_coords)
    points.append(end_coords)

    weather_descriptions = []
    temperatures = []

    for point in points:
        weather = fetch_weather(point[0], point[1])
        weather_descriptions.append(weather['weather'][0]['description'])
        temperatures.append(weather['main']['temp'])

    avg_temperature = sum(temperatures) / len(temperatures)
    most_common_weather = max(set(weather_descriptions), key=weather_descriptions.count)

    return {
        "weather": most_common_weather,
        "temperature": round(avg_temperature, 2)
    }

# Fetch and cache weather data for each segment in the routes
def fetch_segment_weather_data(airport_identifiers, airports):
    segment_weather_cache = {}

    for route in itertools.permutations(airport_identifiers, len(airport_identifiers)):
        for i in range(len(route) - 1):
            start_airport = route[i]
            end_airport = route[i + 1]
            segment_key = tuple(sorted([start_airport, end_airport]))

            if segment_key not in segment_weather_cache:
                start_coords = (airports[start_airport][0], airports[start_airport][1])
                end_coords = (airports[end_airport][0], airports[end_airport][1])
                segment_weather_cache[segment_key] = get_segment_weather(start_coords, end_coords)

    return segment_weather_cache

# Aggregate weather data for all routes using the cached segment data
def fetch_weather_for_all_routes(airport_identifiers, airports):
    route_factors = {}
    segment_weather_cache = fetch_segment_weather_data(airport_identifiers, airports)

    for route in itertools.permutations(airport_identifiers, len(airport_identifiers)):
        route_key = " -> ".join(route)
        route_factors[route_key] = []

        for i in range(len(route) - 1):
            start_airport = route[i]
            end_airport = route[i + 1]
            segment_key = tuple(sorted([start_airport, end_airport]))
            segment_weather = segment_weather_cache[segment_key]

            route_factors[route_key].append({
                "segment": f"{start_airport} -> {end_airport}",
                "weather": segment_weather["weather"],
                "temperature": segment_weather["temperature"]
            })

    return route_factors

