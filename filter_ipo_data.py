import pandas as pd


def clean_and_filter_ipo_data(df):

    # Filtering based on specified conditions
    filtered_df = df[
        (df["growth_flag"] == True) & (df["PER"] <= 15) & (df["dividend_yield"] >= 3)
    ]

    return filtered_df
