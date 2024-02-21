from datetime import datetime, timedelta
import requests
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf


def fetch_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def extract_table_data(soup, date):
    # Extract headers from the <thead> section, skipping the first header
    table_head = soup.find('thead')
    headers = [header.text.strip() for header in table_head.find_all('th')][1:]

    # Add 'Date' header at the beginning
    headers.insert(0, 'Date')

    table_body = soup.find('tbody')
    rows = table_body.find_all('tr')

    data = []
    for row in rows:
        cells = row.find_all('td')  # Use 'td' for data cells
        row_data = [cell.text.strip() for cell in cells]
        # Prepend the date to the row data
        row_data.insert(0, date)
        data.append(row_data)

    return data, headers


links_with_dates = [
    {
        "date":
        "2022-10-10",
        "url":
        "https://candlemaster.pl/competitions/7aa8d158-7301-4bdf-9862-953530c031fc/show"
    },
    # Add more links with dates as needed
]


def fetch_price(ticker, date):
    stock = yf.Ticker(ticker + '.WA')
    hist = stock.history(start=date, end=date + timedelta(days=1))
    if not hist.empty:
        return hist['Close'][0]
    return None


if __name__ == "__main__":
    constant_date = '2023-01-01'
    all_data = []
    headers = []

    for index, item in enumerate(links_with_dates):
        soup = fetch_soup(item["url"])
        table_data, extracted_headers = extract_table_data(soup, item["date"])

        # Use headers from the first table as the column names for the DataFrame
        if index == 0:
            headers = extracted_headers

        all_data.extend(table_data)

    df = pd.DataFrame(all_data, columns=headers)
    transformed_data = []
    for _, row in df.iterrows():
        date = row['Date']
        user = row['Uczestnik(nazwa z Twittera)']

        # Since direct column name access is ambiguous due to duplicates,
        # we access the columns by position. Here's how you might map them:
        # Typ L (1st occurrence) -> row[3], Typ S (1st occurrence) -> row[5]
        # Typ L (2nd occurrence) -> row[7], Typ S (2nd occurrence) -> row[9]
        # These indices might need adjustment based on the actual DataFrame structure.

        # Process Typ L and Typ S (first occurrence)
        if row.iloc[3] != '-----':  # Adjust index for Typ L
            transformed_data.append({
                'Date': date,
                'User': user,
                'Type': 'L',
                'Ticker': row.iloc[3]
            })
        if row.iloc[5] != '-----':  # Adjust index for Typ S
            transformed_data.append({
                'Date': date,
                'User': user,
                'Type': 'S',
                'Ticker': row.iloc[5]
            })

        # Process Typ L and Typ S (second occurrence)
        if row.iloc[7] != '-----':  # Adjust index for the second Typ L
            transformed_data.append({
                'Date': date,
                'User': user,
                'Type': 'L',
                'Ticker': row.iloc[7]
            })
        if row.iloc[9] != '-----':  # Adjust index for the second Typ S
            transformed_data.append({
                'Date': date,
                'User': user,
                'Type': 'S',
                'Ticker': row.iloc[9]
            })

    new_df = pd.DataFrame(transformed_data)

    print(new_df)
