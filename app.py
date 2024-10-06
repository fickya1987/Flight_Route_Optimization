import gradio as gr
import pandas as pd
from map_generator import *
from flight_distance import *
from optimize import *
from weather import *

airport_df = pd.read_csv(r'airport.csv') 
aircraft_df = pd.read_csv(r'aircraft.csv')  

airport_options = [f"{row['IATA']} - {row['Airport_Name']} - {row['Country']}" for _, row in airport_df.iterrows()]
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

    sector_details_html = """
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>Sector</th>
            <th>Fuel Required (Tonnes)</th>
            <th>Flight Time (hrs)</th>
            <th>Refuel Required</th>
            <th>CO2 Emission (Tonnes)</th>
        </tr>
    """
    for sector in feasibility_result["Sector Details"]:
        sector_details_html += f"""
        <tr>
            <td>{sector['Sector']}</td>
            <td>{round(sector['Fuel Required (kg)']/1000,2)}</td>
            <td>{sector['Flight Time (hrs)']}</td>
            <td>{sector['Refuel Required']}</td>
            <td>{round(sector['Fuel Required (kg)']*3.16/1000,2)}</td>
        </tr>
        """
    sector_details_html += "</table>"

    if feasibility_result["Can Fly Entire Route"]:
        result = f"""
        <h3>Optimal Route</h3>
        <p>{" -> ".join(optimal_route) + f" -> {optimal_route[0]}"}</p>
        <h3>Total Round Trip Distance</h3>
        <p>{optimal_distance} km</p>
        <h3>Round Trip Fuel Required (Tonnes)</h3>
        <p>{round(feasibility_result["Total Fuel Required (kg)"]/1000,2)}</p>
        <h3>Round Trip Flight Time (hrs)</h3>
        <p>{feasibility_result["Total Flight Time (hrs)"]}</p>
        <h3>Total CO2 Emission (Tonnes)</h3>
        <p>{round(feasibility_result["Total Fuel Required (kg)"]*3.16/1000,2)}</p>
        <h3>Can Fly Entire Route</h3>
        <p>Yes</p>
        <h3>Sector Details</h3>
        {sector_details_html}
        """
    else:
        result = f"""
        <h3>Optimal Route</h3>
        <p>{" -> ".join(optimal_route) + f" -> {optimal_route[0]}"}</p>
        <h3>Total Round Trip Distance</h3>
        <p>{optimal_distance} km</p>
        <h3>Can Fly Entire Route</h3>
        <p>No, refueling required in one or more sectors.</p>
        <h3>Sector Details</h3>
        {sector_details_html}
        """
    
    return result, map_html

# Gradio Interface
with gr.Blocks(theme=gr.themes.Default()) as demo:
    gr.Markdown("## Flight Route Planner - [[GitHub]](https://github.com/souvik0306/Flight_Route_Optimization)")
    # Step-wise instructions
    gr.Markdown("""
    1. **Select Airports:** Choose multiple airports from the dropdown list to form your route.
    2. **Select Aircraft Type:** Pick the type of aircraft you plan to use for the route.
    3. **Check Route Feasibility:** Click the 'Check Route Feasibility' button to see the results, including the optimal route, fuel requirements, and refueling sectors.
    """)

    # Place components in two columns for results and map
    with gr.Row():
        with gr.Column():
            airport_selector = gr.Dropdown(airport_options, multiselect=True, label="Select Airports (IATA - Name)", value=["JFK - John F Kennedy Intl - United States", "SIN - Changi Intl - Singapore", "LHR - Heathrow - United Kingdom"])
            aircraft_selector = gr.Dropdown(aircraft_options, label="Select Aircraft Type", value="Airbus A350-900")
            check_button = gr.Button("Check Route Feasibility")
            gr.Markdown("## Route Map")
            map_output = gr.HTML(label="Interactive Route Map with Refueling Sectors")
        
        with gr.Column():
            result_output = gr.HTML(label="Feasibility Result (Route, Fuel, Refueling Info)")

    # Connect the button click to the check_route function
    check_button.click(
        fn=check_route, 
        inputs=[airport_selector, aircraft_selector], 
        outputs=[result_output, map_output]
    )
    
    gr.Markdown("**Note:** The actual flight time and performance may vary since the dataset used is very rudimentary. In the real world, the same aircraft can have different internal configurations, leading to variations in flight time and fuel consumption.")

# Launch the Gradio app
demo.launch()