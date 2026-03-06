import pandas as pd

try:
    df = pd.read_excel('dataset.xlsx')
    print("Columns found:", df.columns.tolist())
    print("First row:", df.iloc[0].to_dict())
except Exception as e:
    print(f"Error reading excel: {e}")
