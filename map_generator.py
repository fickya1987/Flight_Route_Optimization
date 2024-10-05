import folium

# Function to create the map
def create_route_map(airports, lat_long_dict, optimal_route, refuel_sectors):
    """
    Create a map displaying the optimal route with red straight lines, 
    and dotted lines for sectors requiring refuel. Adds a legend for line meanings.
    """
    # Create the map centered at the first airport
    start_lat, start_long = lat_long_dict[optimal_route[0]]
    route_map = folium.Map(location=[start_lat, start_long], zoom_start=4)

    # Collect bounds for autoscaling the map
    bounds = []

    # Add markers for each airport
    for i, airport in enumerate(optimal_route):
        lat, lon = lat_long_dict[airport]
        bounds.append([lat, lon])
        folium.Marker(
            [lat, lon], 
            popup=f"{airport} - {airports[airport]}",
            icon=folium.DivIcon(html=f'''
                <div style="
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14pt;
                    color: black;
                ">{i + 1}</div>
            ''')
        ).add_to(route_map)


    # Draw lines between the airports
    for i in range(len(optimal_route) - 1):
        airport1 = optimal_route[i]
        airport2 = optimal_route[i + 1]
        lat1, lon1 = lat_long_dict[airport1]
        lat2, lon2 = lat_long_dict[airport2]

        # Check if refuel is required for this sector
        if (airport1, airport2) in refuel_sectors or (airport2, airport1) in refuel_sectors:
            folium.PolyLine(
                locations=[(lat1, lon1), (lat2, lon2)], color="red", weight=2.5, opacity=1, dash_array="10,10"
            ).add_to(route_map)
        else:
            folium.PolyLine(
                locations=[(lat1, lon1), (lat2, lon2)], color="red", weight=2.5, opacity=1
            ).add_to(route_map)

    # Special case for two points: check the return leg explicitly
    lat_last, lon_last = lat_long_dict[optimal_route[-1]]
    lat_start, lon_start = lat_long_dict[optimal_route[0]]
    if (optimal_route[-1], optimal_route[0]) in refuel_sectors or (optimal_route[0], optimal_route[-1]) in refuel_sectors:
        folium.PolyLine(
            locations=[(lat_last, lon_last), (lat_start, lon_start)], color="red", weight=2.5, opacity=1, dash_array="10,10"
        ).add_to(route_map)
    else:
        folium.PolyLine(
            locations=[(lat_last, lon_last), (lat_start, lon_start)], color="red", weight=2.5, opacity=1
        ).add_to(route_map)

    # Autoscale the map to fit all points
    route_map.fit_bounds(bounds)

    # Add custom legend as a child of the map
    # Add custom legend as a child of the map
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; 
        left: 50px; 
        width: 250px; 
        height: 90px; 
        background-color: white; 
        border: 2px solid grey; 
        z-index: 9999; 
        font-size: 14px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    ">
        <strong>Legend</strong><br>
        <i class="fa fa-minus" style="color:red"></i> Solid line: No refuel required<br>
        <i class="fa fa-ellipsis-h" style="color:red"></i> Dotted line: Refuel required
    </div>
    <style>
        @media (max-width: 600px) {
            div[style*="position: fixed"] {
                bottom: 10px !important;
                left: 10px !important;
                width: 200px !important;
                font-size: 12px !important;
            }
        }
    </style>
    '''
    route_map.get_root().html.add_child(folium.Element(legend_html))

    # Convert the map to HTML string
    return route_map._repr_html_()
