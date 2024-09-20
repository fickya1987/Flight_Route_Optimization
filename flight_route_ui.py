import gradio as gr
import pandas as pd
from optimizer import *
from weather import *
from flight_distance import *  # Assuming this function is defined in your aircraft capabilities module

# Load airport data and aircraft data from CSV files
airport_df = pd.read_csv(r'airport.csv')  # Adjust the path to your CSV file
aircraft_df = pd.read_csv(r'aircraft.csv')  # Adjust the path to your CSV file

# Create a combined option list with both IATA codes and airport names
airport_options = [f"{row['IATA']} - {row['Airport_Name']}" for _, row in airport_df.iterrows()]

# Ensure the correct column is used for aircraft types
aircraft_type_column = 'Aircraft'  # Adjust if your column name is different
if aircraft_type_column not in aircraft_df.columns:
    raise ValueError(f"Column '{aircraft_type_column}' not found in aircraft_types.csv. Available columns: {aircraft_df.columns}")

aircraft_options = aircraft_df[aircraft_type_column].tolist()

# Function to determine if a route can be flown
def check_route(airport_selections, aircraft_type):
    # Extract IATA codes from the selected options
    airports = [selection.split(" - ")[0] for selection in airport_selections]
    
    # Get coordinates for selected airports as a dictionary {IATA: (latitude, longitude)}
    lat_long_dict = get_airport_lat_long(airports)  # Ensure this function returns a dictionary in the expected format
    
    # Pass only the required details in the expected format for the weather function
    raw_weather = fetch_weather_for_all_routes(airports, lat_long_dict)  # This should receive the correct lat_long_dict
    
    # Extract route factors (e.g., conditions impacting the route)
    route_factors = extract_route_factors(raw_weather)

    # Calculate distances between selected airports
    trip_distance = calculate_distances(airports)

    # Ensure the graph is bidirectional
    for (a, b), dist in list(trip_distance.items()):
        trip_distance[(b, a)] = dist

    # Find the optimal route
    optimal_route, optimal_distance = find_optimal_route(airports, trip_distance, route_factors)

    # Check if the aircraft can fly the route without refueling
    result = can_fly_route(aircraft_type, airports)

    # Convert all dictionary keys to strings for JSON compatibility
    return {
        "Optimal Route": " -> ".join(optimal_route) + f" -> {optimal_route[0]}",
        "Total Round Trip Distance": str(optimal_distance),  # Convert to string if necessary
        "Can Fly Route": str(result)  # Convert to string if necessary
    }

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("## Airport Route Feasibility Checker")
    airport_selector = gr.Dropdown(airport_options, multiselect=True, label="Select Airports (IATA - Name)")
    aircraft_selector = gr.Dropdown(aircraft_options, label="Select Aircraft Type")
    check_button = gr.Button("Check Route Feasibility")
    
    result_output = gr.JSON(label="Result")

    check_button.click(fn=check_route, inputs=[airport_selector, aircraft_selector], outputs=result_output)

# Launch the Gradio app
demo.launch()
