import itertools
from flight_distance import *

def extract_route_factors(raw_weather):
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
        "clear sky": 0.1, "few clouds": 0.2, "scattered clouds": 0.3,
        "broken clouds": 0.4, "overcast clouds": 0.5, "light rain": 0.6,
        "rain": 0.7, "storm": 0.9
    }
    return risk_factors.get(weather, 0.5)

def temperature_impact(temperature):
    if temperature < 20 or temperature > 25:
        return abs(temperature - 22.5) / 30
    return 0.1

def calculate_adjusted_cost(segment, base_distance, route_factors):
    if segment in route_factors:
        factors = route_factors[segment]
    elif (segment[1], segment[0]) in route_factors:
        factors = route_factors[(segment[1], segment[0])]
    else:
        raise ValueError(f"Segment {segment} not found in route factors.")
    
    weather_descriptions = [factor["weather"] for factor in factors]
    temperatures = [factor["temperature"] for factor in factors]
    most_common_weather = max(set(weather_descriptions), key=weather_descriptions.count)
    avg_temperature = sum(temperatures) / len(temperatures)
    weather_cost = weather_risk(most_common_weather) * 100
    temperature_cost = temperature_impact(avg_temperature) * 50
    return base_distance + weather_cost + temperature_cost

def find_optimal_route(airports, distances, route_factors):
    best_route, min_distance = None, float('inf')
    for route in itertools.permutations(airports):
        total_distance = 0
        for i in range(len(route) - 1):
            segment = (route[i], route[i + 1])
            base_distance = distances.get(segment) or distances.get((segment[1], segment[0]))
            total_distance += calculate_adjusted_cost(segment, base_distance, route_factors)
        last_segment = (route[-1], route[0])
        base_distance = distances.get(last_segment) or distances.get((last_segment[1], last_segment[0]))
        total_distance += calculate_adjusted_cost(last_segment, base_distance, route_factors)
        if total_distance < min_distance:
            min_distance, best_route = round(total_distance, 2), route
    return best_route, min_distance

def check_segment_feasibility(segment, trip_distance, aircraft_specs):
    segment_distance = trip_distance.get(segment) or trip_distance.get((segment[1], segment[0]))
    fuel_required, flight_time = calculate_fuel_and_time_for_segment(segment_distance, aircraft_specs)
    can_fly = fuel_required <= aircraft_specs['Max_Fuel_Capacity_kg']
    return can_fly, fuel_required, flight_time

def check_route_feasibility(optimal_route, trip_distance, aircraft_specs):
    total_fuel, total_time = 0, 0
    refuel_sectors, sector_details = [], []
    can_fly_entire_route = True

    for i in range(len(optimal_route) - 1):
        segment = (optimal_route[i], optimal_route[i + 1])
        can_fly, fuel, time = check_segment_feasibility(segment, trip_distance, aircraft_specs)
        sector_info = {
            "Sector": f"{optimal_route[i]} -> {optimal_route[i+1]}",
            "Fuel Required (kg)": round(fuel, 2),
            "Flight Time (hrs)": round(time, 2),
            "Refuel Required": "Yes" if not can_fly else "No"
        }
        sector_details.append(sector_info)
        if not can_fly:
            print(f"Cannot fly the sector {optimal_route[i]} -> {optimal_route[i+1]} without refueling.")
            print(f"Fuel required: {round(fuel, 2)} kg, capacity: {aircraft_specs['Max_Fuel_Capacity_kg']} kg")
            refuel_sectors.append((optimal_route[i], optimal_route[i+1]))
            can_fly_entire_route = False
        else:
            print(f"Fuel required for {optimal_route[i]} -> {optimal_route[i+1]}: {round(fuel, 2)} kg")
            print(f"Flight time for this sector: {round(time, 2)} hours")
        total_fuel += fuel
        total_time += time

    last_segment = (optimal_route[-1], optimal_route[0])
    can_fly, fuel, time = check_segment_feasibility(last_segment, trip_distance, aircraft_specs)
    final_leg_info = {
        "Sector": f"{optimal_route[-1]} -> {optimal_route[0]}",
        "Fuel Required (kg)": round(fuel, 2),
        "Flight Time (hrs)": round(time, 2),
        "Refuel Required": "Yes" if not can_fly else "No"
    }
    sector_details.append(final_leg_info)
    if not can_fly:
        print(f"Cannot fly the sector {optimal_route[-1]} -> {optimal_route[0]} without refueling.")
        print(f"Fuel required: {round(fuel, 2)} kg, capacity: {aircraft_specs['Max_Fuel_Capacity_kg']} kg")
        refuel_sectors.append((optimal_route[-1], optimal_route[0]))
        can_fly_entire_route = False
    else:
        print(f"Fuel required for {optimal_route[-1]} -> {optimal_route[0]}: {round(fuel, 2)} kg")
        print(f"Flight time for this sector: {round(time, 2)} hours")
    total_fuel += fuel
    total_time += time

    if can_fly_entire_route:
        return {
            "Total Fuel Required (kg)": round(total_fuel, 2),
            "Total Flight Time (hrs)": round(total_time, 2),
            "Can Fly Entire Route": True,
            "Sector Details": sector_details,
            "Refuel Sectors": refuel_sectors
        }
    else:
        return {
            "Can Fly Entire Route": False,
            "Sector Details": sector_details,
            "Refuel Sectors": refuel_sectors
        }
