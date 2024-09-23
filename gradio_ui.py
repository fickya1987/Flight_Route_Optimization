import gradio as gr
import pandas as pd
from flight_distance import *
from optimize import *
from weather import *

# Load airport data and aircraft data from CSV files
airport_df = pd.read_csv(r'airport.csv')  # Adjust the path to your CSV file
aircraft_df = pd.read_csv(r'aircraft.csv')  # Adjust the path to your CSV file

# Create a combined option list with both IATA codes and airport names
airport_options = [f"{row['IATA']} - {row['Airport_Name']}" for _, row in airport_df.iterrows()]

# Ensure the correct column is used for aircraft types
aircraft_type_column = 'Aircraft'
aircraft_options = aircraft_df[aircraft_type_column].tolist()

# Gradio function to determine if a route can be flown
def check_route(airport_selections, aircraft_type):
    # Extract IATA codes from the selected options
    airports = [selection.split(" - ")[0] for selection in airport_selections]
    
    # Step 1: Get Airport Coordinates
    lat_long_dict = get_airport_lat_long(airports)
    
    # Step 2: Calculate Distances between each node (airports)
    trip_distance = calculate_distances(airports)
    
    # Step 3: Get on-route weather
    raw_weather = fetch_weather_for_all_routes(airports, lat_long_dict)
    route_factors = extract_route_factors(raw_weather)
    
    # Step 4: Ensure the graph is bidirectional (undirected)
    for (a, b), dist in list(trip_distance.items()):
        trip_distance[(b, a)] = dist
    
    # Step 5: Find the optimal route based on weather, temperature, and distance
    optimal_route, optimal_distance = find_optimal_route(airports, trip_distance, route_factors)
    
    # Step 6: Fetch Aircraft Details
    aircraft_specs = get_aircraft_details(aircraft_type)
    
    # Check if aircraft details were retrieved successfully
    if isinstance(aircraft_specs, str):
        return {"Error": aircraft_specs}  # Return error message if aircraft not found
    
    # Prepare sector-wise details for flight time, fuel required, and refueling need
    sector_details = []
    refuel_required = False  # Flag to track if refueling is required
    
    for i in range(len(optimal_route) - 1):
        segment = (optimal_route[i], optimal_route[i + 1])
        segment_distance = trip_distance.get(segment) or trip_distance.get((segment[1], segment[0]))
        
        # Calculate fuel and time for this sector
        fuel, time = calculate_fuel_and_time_for_segment(segment_distance, aircraft_specs)
        sector_info = {
            "Sector": f"{optimal_route[i]} -> {optimal_route[i+1]}",
            "Fuel Required (kg)": round(fuel, 2),
            "Flight Time (hrs)": round(time, 2)
        }
        
        # Check if refueling is required for this sector
        if fuel > aircraft_specs['Max_Fuel_Capacity_kg']:
            sector_info["Refuel Required"] = "Yes"
            refuel_required = True
        else:
            sector_info["Refuel Required"] = "No"
        
        sector_details.append(sector_info)

    # Check the final leg (return to the starting point)
    last_segment = (optimal_route[-1], optimal_route[0])
    last_segment_distance = trip_distance.get(last_segment) or trip_distance.get((last_segment[1], last_segment[0]))
    fuel, time = calculate_fuel_and_time_for_segment(last_segment_distance, aircraft_specs)
    
    # Add final leg details
    final_leg_info = {
        "Sector": f"{optimal_route[-1]} -> {optimal_route[0]}",
        "Fuel Required (kg)": round(fuel, 2),
        "Flight Time (hrs)": round(time, 2)
    }
    
    if fuel > aircraft_specs['Max_Fuel_Capacity_kg']:
        final_leg_info["Refuel Required"] = "Yes"
        refuel_required = True
    else:
        final_leg_info["Refuel Required"] = "No"
    
    sector_details.append(final_leg_info)
    
    # Step 7: Prepare and return result
    if refuel_required:
        result = {
            "Optimal Route": " -> ".join(optimal_route) + f" -> {optimal_route[0]}",
            "Total Round Trip Distance": str(optimal_distance) + " km",
            "Can Fly Entire Route": "No, refueling required in one or more sectors.",
            "Sector Details": sector_details
        }
    else:
        result = {
            "Optimal Route": " -> ".join(optimal_route) + f" -> {optimal_route[0]}",
            "Total Round Trip Distance": str(optimal_distance) + " km",
            "Can Fly Entire Route": "Yes, no refueling required.",
            "Sector Details": sector_details
        }
    
    return result


# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("## Airport Route Feasibility Checker")
    airport_selector = gr.Dropdown(airport_options, multiselect=True, label="Select Airports (IATA - Name)")
    aircraft_selector = gr.Dropdown(aircraft_options, label="Select Aircraft Type")
    check_button = gr.Button("Check Route Feasibility")
    
    result_output = gr.JSON(label="Result")

    # Connect the button click to the check_route function
    check_button.click(fn=check_route, inputs=[airport_selector, aircraft_selector], outputs=result_output)

# Launch the Gradio app
demo.launch()
