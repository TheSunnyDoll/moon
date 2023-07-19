import numpy as np
import pandas as pd

def pivothigh(data, left_len, right_len):
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data, columns=["high"])
    # Create an array to store the pivot high values
    pivot_highs = []

    for i in range(left_len, len(df) - right_len):

        if df["high"][i] > max(max(df["high"][i-left_len:i]),max(df["high"][i+1:i+right_len+1])):
            pivot_highs.append(float(df["high"][i]))

    return pivot_highs

def pivotlow(data, left_len, right_len):
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data, columns=["low"])

    pivot_lows = []

    for i in range(left_len, len(df) - right_len):
        if df["low"][i] < min(min(df["low"][i-left_len:i]),min(df["low"][i+1:i+right_len+1])):
            pivot_lows.append(float(df["low"][i]))

    return pivot_lows

# Example usage:
data = {
    "high": [10, 15, 12, 18, 16,99,20, 14, 22, 25, 21],
    "low": [5, 8, 6, 9, 5,7, 12, 10, 15, 18, 14]
}

# Get pivot high and pivot low values
pivot_highs = pivothigh(data["high"], left_len=2, right_len=2)
pivot_lows = pivotlow(data["low"], left_len=2, right_len=2)

print("Pivot Highs:", pivot_highs)
print("Pivot Lows:", pivot_lows)
