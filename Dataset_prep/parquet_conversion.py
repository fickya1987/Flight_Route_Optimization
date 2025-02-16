import pandas as pd

# Use 'pyarrow' or 'fastparquet' for faster Parquet operations
parquet_engine = 'pyarrow'  # or 'fastparquet'

# Specify data types for columns if known
dtype = {
    'column1': 'int64',
    'column2': 'float64',
    'column3': 'object',
    # Add other columns as needed
}

# Load CSV data with specified data types
df = pd.read_csv('seaport_01.csv', dtype=dtype)

# Save as Parquet using the specified engine
df.to_parquet('airport.parquet', engine=parquet_engine)
