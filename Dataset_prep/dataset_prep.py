import pandas as pd

# Read the CSV file
csv_file = 'aircraft.csv'  # Replace with your actual file name
df = pd.read_csv(csv_file)

# Function to convert nautical miles to kilometers
def nautical_miles_to_km(nautical_miles):
    return nautical_miles * 1.852

# Assuming the column with nautical miles is named 'NauticalMiles'
# Replace 'NauticalMiles' with the actual column name if it's different
# df['Kilometers'] = df['NauticalMiles'].apply(nautical_miles_to_km)

# Function to convert speed from knots to km/h
def knots_to_kmh(knots):
    return knots * 1.852

# Function to calculate maximum flight time (hours)
def calculate_max_flight_time(range_km, speed_kmh):
    if speed_kmh == 0:  # Avoid division by zero
        return None
    return range_km / speed_kmh

def max_fuel_capacity(fuel_rate, max_flight_time):
    if max_flight_time == 0:  # Avoid division by zero
        return None
    return fuel_rate*max_flight_time

# Convert cruising speed from knots to km/h and add as a new column
# df['Speed_kmh'] = df['Cruising Speed (kts)'].apply(knots_to_kmh)

# Calculate maximum flight time and add as a new column
# Assuming 'Kilometers' represents the range
# df['MaxFlightTime_hr'] = df.apply(lambda row: calculate_max_flight_time(row['Range_km'], row['Speed_kmh']), axis=1)

df['Max_Fuel_Capacity'] = df.apply(lambda row: max_fuel_capacity(row['Fuel_Consumption_kg/hr'],row['MaxFlightTime_hr']),axis=1)
# Save the updated DataFrame back to the same CSV file
df.to_csv(csv_file, index=False)

print("Conversion complete. Speed (km/h) and Max Flight Time (hr) columns added to the CSV.")