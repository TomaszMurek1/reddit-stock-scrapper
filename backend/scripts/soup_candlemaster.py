from datetime import datetime, timedelta
import requests
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf

import warnings

# Ignore specific FutureWarnings from yfinance
warnings.filterwarnings(
    "ignore",
    message="The 'unit' keyword in TimedeltaIndex construction is deprecated")


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
        "2024-01-31",
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


# User-specified dates
date1 = datetime.strptime('2024-02-01', '%Y-%m-%d')
date2 = datetime.strptime('2024-02-19', '%Y-%m-%d')
date3 = datetime.strptime('2024-02-20', '%Y-%m-%d')
dates = [date1, date2, date3]


def get_closing_price(ticker, date):
    stock_data = yf.download(ticker,
                             start=date,
                             end=date + pd.Timedelta(days=1))
    if not stock_data.empty:
        return stock_data['Close'][0]
    return None


def calculate_percentage_change(old_price, new_price):
    if old_price and new_price:
        return (new_price - old_price) / old_price * 100
    return None


# Adjusted function to fetch prices for multiple dates
def fetch_prices_for_dates(ticker, original_date, future_dates):
    # Find the earliest and latest date to minimize the data fetched
    earliest_date = min(original_date, *future_dates)
    latest_date = max(original_date, *future_dates)

    stock = yf.Ticker(ticker)
    hist = stock.history(start=earliest_date,
                         end=latest_date + timedelta(days=1))

    # Extract the closing prices for the original and future dates
    prices = {date: None for date in [original_date, *future_dates]}
    for date in prices.keys():
        if date.strftime('%Y-%m-%d') in hist.index.strftime('%Y-%m-%d'):
            prices[date] = hist.loc[date.strftime('%Y-%m-%d'), 'Close']
    return prices


if __name__ == "__main__":
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
    # Adding columns for price changes
    for i, date in enumerate(dates, start=1):
        new_df[f'Change to Date {i}'] = None

    for index, row in new_df.iterrows():
        ticker = row['Ticker'] + '.WA'
        original_date = datetime.strptime(row['Date'], '%Y-%m-%d')
        # Fetch all required prices at once
        prices = fetch_prices_for_dates(ticker, original_date, dates)
        original_price = prices[original_date]

        for i, date in enumerate(dates, start=1):
            new_price = prices[date]
            percentage_change = calculate_percentage_change(
                original_price, new_price)
            new_df.at[index, f'Change to Date {i}'] = percentage_change

    print(new_df)
