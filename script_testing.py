import pandas as pd

file_path = "data/KAJSYK24_MA-TO.xlsx"
df = pd.read_excel(file_path, header=2)  # Read without assuming the first row as headers

print(df.head())  # Print first few rows to inspect the actual data

