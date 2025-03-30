import pandas as pd
import os
from datetime import datetime
from filter_ipo_data import clean_and_filter_ipo_data
from jpx_scraper import scrape_jpx_ipo_list
from yahoo_finance_scraper import fetch_yahoo_data
from irbank_scraper import fetch_irbank_data


def main():
    # Step 1: Read pre-filter CSV if it exists
    print("Step 1: フィルター前CSVを読み込み中...")
    is_new_list = False
    try:
        ipo_df = pd.read_csv("ipo_list.csv")
        print("Existing IPO list loaded.")
    except FileNotFoundError:
        print("No existing IPO list found. Creating a new one.")
        ipo_df = pd.DataFrame()
        is_new_list = True

    # Step 2: Scrape IPO data from JPX
    print("Step 2: JPXデータ取得中...")
    jpx_df = scrape_jpx_ipo_list()

    # Merge with existing data
    if not ipo_df.empty and not jpx_df.empty:
        ipo_df = pd.concat([ipo_df, jpx_df]).drop_duplicates(
            subset=["stock_code"], keep="last"
        )
    elif not jpx_df.empty:
        ipo_df = jpx_df

    # Step 3: Fetch additional stock data from Yahoo Finance
    print("Step 3: Yahoo Finenceデータ取得中...")
    # Force scrape for new IPO list
    ipo_df = fetch_yahoo_data(ipo_df, force_scrape=is_new_list)

    # Step 4: Add Yahoo data to IPO data and then add the growth flag from IRBank
    print("Step 4: irBankデータ取得中...")
    # Force scrape for new IPO list
    ipo_df = fetch_irbank_data(ipo_df, force_scrape=is_new_list)

    # Save the pre-filter DataFrame to a CSV file
    ipo_df.to_csv("ipo_list.csv", index=False)
    print("Pre-filter data has been saved to ipo_list.csv")

    # Step 5: Filter the combined data
    print("Step 5: フィルター処理中...")
    filtered_df = clean_and_filter_ipo_data(ipo_df)

    # Step 6: Output the filtered DataFrame to a CSV file with date in the filename
    print("Step 6: 評価結果をcsvで出力中...")
    today_str = datetime.now().strftime("%Y%m%d")
    filtered_filename = f"filtered_ipo_list_{today_str}.csv"
    filtered_df.to_csv(filtered_filename, index=False)
    print(f"Filtered data has been saved to {filtered_filename}")


if __name__ == "__main__":
    main()
