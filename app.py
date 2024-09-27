import gradio as gr
import pandas as pd
from map_generator import *
from flight_distance import *
from optimize import *
from weather import *
# Load airport data and aircraft data from Parquet and CSV files
airport_df = pd.read_parquet(r'airport.parquet')  # Adjust the path to your Parquet file
aircraft_df = pd.read_csv(r'aircraft.csv')  # Adjust the path to your CSV file

airport_options = [f"{row['IATA']} - {row['Airport_Name']}" for _, row in airport_df.iterrows()]
airports_dict = {row['IATA']: row['Airport_Name'] for _, row in airport_df.iterrows()}  # For map display

# Ensure the correct column is used for aircraft types
aircraft_type_column = 'Aircraft'
aircraft_options = aircraft_df[aircraft_type_column].tolist()

def check_route(airport_selections, aircraft_type):
    airports = [selection.split(" - ")[0] for selection in airport_selections]
    lat_long_dict = get_airport_lat_long(airports)
    trip_distance = calculate_distances(airports)
    raw_weather = fetch_weather_for_all_routes(airports, lat_long_dict)
    route_factors = extract_route_factors(raw_weather)
    
    for (a, b), dist in list(trip_distance.items()):
        trip_distance[(b, a)] = dist
    
    optimal_route, optimal_distance = find_optimal_route(airports, trip_distance, route_factors)
    aircraft_specs = get_aircraft_details(aircraft_type)
    
    if isinstance(aircraft_specs, str):
        return {"Error": aircraft_specs}, ""
    
    feasibility_result = check_route_feasibility(optimal_route, trip_distance, aircraft_specs)
    map_html = create_route_map(airports_dict, lat_long_dict, optimal_route, feasibility_result["Refuel Sectors"])
    
    if feasibility_result["Can Fly Entire Route"]:
        result = {
            "Optimal Route": " -> ".join(optimal_route) + f" -> {optimal_route[0]}",
            "Total Round Trip Distance": f"{optimal_distance} km",
            "Total Fuel Required": feasibility_result["Total Fuel Required (kg)"],
            "Total Flight Time": feasibility_result["Total Flight Time (hrs)"],
            "Can Fly Entire Route": "Yes",
            "Sector Details": feasibility_result["Sector Details"]
        }
    else:
        result = {
            "Optimal Route": " -> ".join(optimal_route) + f" -> {optimal_route[0]}",
            "Total Round Trip Distance": f"{optimal_distance} km",
            "Can Fly Entire Route": "No, refueling required in one or more sectors.",
            "Sector Details": feasibility_result["Sector Details"]
        }
    
    return result, map_html

# Gradio Interface
with gr.Blocks(theme=gr.themes.Default()) as demo:
    gr.Markdown("## Airport Route Feasibility Checker")

    # Place components in two columns for results and map
    with gr.Row():
        with gr.Column():
            airport_selector = gr.Dropdown(airport_options, multiselect=True, label="Select Airports (IATA - Name)")
            aircraft_selector = gr.Dropdown(aircraft_options, label="Select Aircraft Type")
            check_button = gr.Button("Check Route Feasibility")
            result_output = gr.JSON(label="Feasibility Result (Route, Fuel, Refueling Info)")
        
        with gr.Column():
            gr.Markdown("## Route Map")
            map_output = gr.HTML(label="Interactive Route Map with Refueling Sectors")

    # Connect the button click to the check_route function
    check_button.click(
        fn=check_route, 
        inputs=[airport_selector, aircraft_selector], 
        outputs=[result_output, map_output]
    )

# Launch the Gradio app
demo.launch()