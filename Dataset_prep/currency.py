import pandas as pd

# Load the CSV files
csv1_file = r'currencyrates.csv'  # Replace with the path to your CSV1 file
csv2_file = r'countrycurrency.csv'  # Replace with the path to your CSV2 file

# Read the CSVs into DataFrames
df1 = pd.read_csv(csv1_file)  # This CSV contains just currency codes
df2 = pd.read_csv(csv2_file)  # This CSV contains currency codes and country names

# Merge df1 with df2 on the currency code
# Assuming the column name for currency codes in both CSVs is 'CurrencyCode'
# If the column names are different, replace 'CurrencyCode' with the correct column names
df_merged = pd.merge(df1, df2[['Currency_code', 'currency_country_name']], on='Currency_code', how='left')

# Save the updated DataFrame back to csv1
df_merged.to_csv(csv1_file, index=False)

print("Country names have been successfully added to csv1.")
