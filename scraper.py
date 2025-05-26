import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_market_cap_data():
    url = "https://companiesmarketcap.com/assets-by-market-cap/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if not table:
        print("No table found on the page.")
        return pd.DataFrame()

    rows = table.find_all("tr")[1:]  # Skip header row
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            asset = cols[1].get_text(strip=True)
            market_cap_str = cols[2].get_text(strip=True).replace("$", "").replace(",", "").replace("B", "")
            try:
                market_cap = float(market_cap_str)
                data.append((asset, market_cap))
            except ValueError:
                continue

    df = pd.DataFrame(data, columns=["Asset", "Market Cap (B USD)"])
    df["Weight (%)"] = 100 * df["Market Cap (B USD)"] / df["Market Cap (B USD)"].sum()
    return df


if __name__ == "__main__":
    df = fetch_market_cap_data()
    print(df)
