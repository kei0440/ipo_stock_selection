import requests
from bs4 import BeautifulSoup
import pandas as pd


def scrape_jpx_ipo_list():
    urls = [
        "https://www.jpx.co.jp/listing/stocks/new/index.html",
        "https://www.jpx.co.jp/listing/stocks/new/00-archives-01.html",
        "https://www.jpx.co.jp/listing/stocks/new/00-archives-02.html",
        "https://www.jpx.co.jp/listing/stocks/new/00-archives-03.html",
        "https://www.jpx.co.jp/listing/stocks/new/00-archives-04.html",
    ]
    ipo_data = []
    existing_companies = set()  # Track existing companies

    # Load existing IPO list to check for duplicates
    try:
        existing_ipo_df = pd.read_csv("ipo_list.csv")
        existing_companies = set(existing_ipo_df["company_name"])
    except FileNotFoundError:
        pass  # If the file doesn't exist, proceed without it

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        rows = soup.find_all("tr")
        for i in range(0, len(rows), 2):
            first_row = rows[i].find_all("td")
            second_row = rows[i + 1].find_all("td") if i + 1 < len(rows) else []

            if first_row and second_row:
                company_name = first_row[1].text.strip()
                if "代表者インタビュー" in company_name:
                    company_name = company_name.replace(
                        "代表者インタビュー", ""
                    ).strip()

                if company_name not in existing_companies:
                    ipo_data.append(
                        {
                            "listing_date": first_row[0].text.strip().split(" ")[0],
                            "market_segment": second_row[0].text.strip(),
                            "stock_code": first_row[2].text.strip(),
                            "company_name": company_name,
                        }
                    )

    # Convert to DataFrame
    ipo_df = pd.DataFrame(ipo_data)
    return ipo_df
