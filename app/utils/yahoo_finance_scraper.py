import requests
from bs4 import BeautifulSoup
import pandas as pd
from lxml import etree


def get_stock_details(stock_code):
    url = f"https://finance.yahoo.co.jp/quote/{stock_code}.T"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.content, "html.parser")

        # Scraping the required data using CSS selectors
        def safe_float_conversion(value):
            try:
                return float(value.replace(",", "").replace("%", ""))
            except ValueError:
                return float("nan")

        current_price = safe_float_conversion(
            soup.select_one(
                "#root > main > div > section > div.PriceBoardMain__1nb3 > div.PriceBoardMain__priceInformation__3YfB > div.PriceBoardMain__headerPrice__gbs7 > span > span > span"
            ).text.strip()
        )
        market_cap = safe_float_conversion(
            soup.select_one(
                "#referenc > div > ul > li:nth-child(1) > dl > dd > span.StyledNumber__1fof.StyledNumber--vertical__2aoh.DataListItem__number__1DMR > span > span.StyledNumber__value__3rXW.DataListItem__value__11kV"
            ).text.strip()
        )
        per = safe_float_conversion(
            soup.select_one(
                "#referenc > div > ul > li:nth-child(5) > dl > dd > a > span.StyledNumber__1fof.StyledNumber--vertical__2aoh.DataListItem__number__1DMR > span > span.StyledNumber__value__3rXW.DataListItem__value__11kV"
            ).text.strip()
        )
        pbr = safe_float_conversion(
            soup.select_one(
                "#referenc > div > ul > li:nth-child(6) > dl > dd > a > span.StyledNumber__1fof.StyledNumber--vertical__2aoh.DataListItem__number__1DMR > span > span.StyledNumber__value__3rXW.DataListItem__value__11kV"
            ).text.strip()
        )
        dividend_yield = safe_float_conversion(
            soup.select_one(
                "#referenc > div > ul > li:nth-child(3) > dl > dd > span.StyledNumber__1fof.StyledNumber--vertical__2aoh.DataListItem__number__1DMR > span > span.StyledNumber__value__3rXW.DataListItem__value__11kV"
            ).text.strip()
        )

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    except AttributeError as e:
        print(f"Failed to extract data: {e}")
        return None

    details = {
        "current_price": current_price,
        "market_cap": market_cap,
        "PER": per,
        "PBR": pbr,
        "dividend_yield": dividend_yield,
    }

    return details


def fetch_yahoo_data(ipo_df, force_scrape=False):
    stock_codes = ipo_df["stock_code"].dropna().unique()

    # Initialize columns for stock details
    if force_scrape:
        ipo_df["current_price"] = None
        ipo_df["market_cap"] = None
        ipo_df["PER"] = None
        ipo_df["PBR"] = None
        ipo_df["dividend_yield"] = None

    # Fetch details for each stock and update the DataFrame
    for index, code in enumerate(stock_codes):
        last_update = (
            ipo_df.at[index, "last_update"] if "last_update" in ipo_df.columns else None
        )
        if (
            not force_scrape
            and last_update
            and (pd.to_datetime("today") - pd.to_datetime(last_update)).days < 30
        ):
            print(f"Skipping {code} as it was updated within the last month.")
            continue

        details = get_stock_details(code)
        if details:
            ipo_df.at[index, "current_price"] = details["current_price"]
            ipo_df.at[index, "market_cap"] = details["market_cap"]
            ipo_df.at[index, "PER"] = details["PER"]
            ipo_df.at[index, "PBR"] = details["PBR"]
            ipo_df.at[index, "dividend_yield"] = details["dividend_yield"]
            ipo_df.at[index, "last_update"] = pd.to_datetime("today").strftime(
                "%Y-%m-%d"
            )

    return ipo_df
