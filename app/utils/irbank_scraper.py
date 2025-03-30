import requests
from bs4 import BeautifulSoup
import pandas as pd
import math


def convert_to_number(value):
    """Convert a string with Japanese numerical units to a float."""
    import re

    value = re.sub(
        r"[^\d.]", "", value.strip()
    )  # Remove non-numeric characters except for the decimal point
    if value == "" or value == "-":
        return float("nan")
    elif "兆" in value:
        return float(value.replace("兆", "").replace(",", "")) * 1_000_000_000_000
    elif "億" in value:
        return float(value.replace("億", "").replace(",", "")) * 100_000_000
    elif "百万" in value:
        return float(value.replace("百万", "").replace(",", "")) * 1_000_000
    else:
        return float(value.replace(",", ""))


def scrape_irbank_performance(stock_code, company_name):
    url = f"https://irbank.net/{stock_code}/results"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Example parsing logic (to be customized based on actual HTML structure)
    performance_data = []
    for row in soup.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) >= 8:
            performance_data.append(
                {
                    "year": columns[0].text.strip(),
                    "revenue": (convert_to_number(columns[1].text)),
                    "operating_profit": (convert_to_number(columns[2].text)),
                    "ordinary_profit": (convert_to_number(columns[3].text)),
                    "net_profit": (convert_to_number(columns[4].text)),
                    # "eps": columns[6].text.strip(),
                    # "roe": columns[7].text.strip(),
                    # "operating_profit_margin": (
                    #     (convert_to_number(columns[2].text))
                    #     / (convert_to_number(columns[1].text))
                    #     if convert_to_number(columns[1].text) not in [0, None]
                    #     and not math.isnan(convert_to_number(columns[1].text))
                    #     else None
                    # ),
                    # "stock_code": stock_code,
                    # "company_name": company_name,
                }
            )

    return performance_data


def fetch_irbank_data(ipo_df, force_scrape=False):
    # Fetch performance data for each stock
    growth_flags = []
    for index, row in ipo_df.iterrows():
        code = row["stock_code"]
        company_name = row["company_name"]

        # Skip if data was updated within the last month and force_scrape is False
        last_update = row.get("last_update") if "last_update" in row.index else None
        if (
            not force_scrape
            and last_update
            and (pd.to_datetime("today") - pd.to_datetime(last_update)).days < 30
        ):
            print(
                f"Skipping {code} ({company_name}) as it was updated within the last month."
            )
            # Use existing growth flag if available
            if "growth_flag" in row.index:
                growth_flags.append(
                    {"stock_code": code, "growth_flag": row["growth_flag"]}
                )
            else:
                growth_flags.append({"stock_code": code, "growth_flag": False})
            continue

        data = scrape_irbank_performance(code, company_name)

        # Determine if the company has experienced growth in revenue and operating profit
        if len(data) >= 3:
            recent_data = data[-3:]  # Get the last three years of data
            revenue_growth = all(
                recent_data[i]["revenue"] < recent_data[i + 1]["revenue"]
                for i in range(len(recent_data) - 1)
            )
            operating_profit_growth = all(
                recent_data[i]["operating_profit"]
                < recent_data[i + 1]["operating_profit"]
                for i in range(len(recent_data) - 1)
            )
            growth_flag = revenue_growth and operating_profit_growth
        else:
            growth_flag = False  # Not enough data to determine growth

        growth_flags.append({"stock_code": code, "growth_flag": growth_flag})

    # Create a dictionary mapping stock_code to growth_flag
    growth_flags_dict = {
        item["stock_code"]: item["growth_flag"] for item in growth_flags
    }

    # Add growth_flag column if it doesn't exist
    if "growth_flag" not in ipo_df.columns:
        ipo_df["growth_flag"] = False

    # Update growth_flag values directly in ipo_df
    for index, row in ipo_df.iterrows():
        stock_code = row["stock_code"]
        if stock_code in growth_flags_dict:
            ipo_df.at[index, "growth_flag"] = growth_flags_dict[stock_code]

    # Ensure no NaN values in growth_flag column
    ipo_df["growth_flag"] = ipo_df["growth_flag"].fillna(False)

    return ipo_df
