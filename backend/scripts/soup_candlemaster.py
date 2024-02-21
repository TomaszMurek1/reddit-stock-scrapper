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
        "https://candlemaster.pl/competitions/15fdb4ac-8e03-4058-87cb-a9ed30ea7eeb/show"
    },
]

# User-specified dates
date1 = datetime.strptime('2024-02-01', '%Y-%m-%d')
date2 = datetime.strptime('2024-02-19', '%Y-%m-%d')
date3 = datetime.strptime('2024-02-20', '%Y-%m-%d')
dates = [date1, date2, date3]


def calculate_percentage_change(old_price, new_price):
    if old_price and new_price:
        return (new_price - old_price) / old_price * 100
    return None


def fetch_prices_for_dates(ticker, original_date, future_dates):
    try:
        # Find the earliest and latest date to minimize the data fetched
        earliest_date = min(original_date, *future_dates)
        latest_date = max(original_date, *future_dates)

        stock = yf.Ticker(ticker)
        hist = stock.history(start=earliest_date,
                             end=latest_date + timedelta(days=1))

        # Convert hist.index to a list of string-formatted dates for comparison
        formatted_hist_dates = hist.index.strftime('%Y-%m-%d').tolist()

        # Extract the closing prices for the original and future dates
        prices = {date: None for date in [original_date, *future_dates]}
        for date in prices.keys():
            formatted_date = date.strftime('%Y-%m-%d')
            if formatted_date in formatted_hist_dates:
                prices[date] = hist.loc[hist.index == formatted_date,
                                        'Close'].values[0]
        return prices
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def transform_row_data(row):
    """
    Transforms a single row of the DataFrame into a list of dictionaries
    representing the transformed data for Typ L and Typ S occurrences.
    """
    transformed_data = []
    date = row['Date']
    user = row['Uczestnik(nazwa z Twittera)']
    # Define a mapping for the occurrences of Typ L and Typ S
    type_positions = [('L', 3), ('S', 5), ('L', 7), ('S', 9)]

    for typ, pos in type_positions:
        if row.iloc[
                pos] != '-----':  # Check if the value at the position is not the placeholder
            transformed_data.append({
                'Date': date,
                'User': user,
                'Type': typ,
                'Ticker': row.iloc[pos]
            })

    return transformed_data


if __name__ == "__main__":
    all_data = []
    headers = []

    # Fetch and compile table data
    for index, item in enumerate(links_with_dates):
        soup = fetch_soup(item["url"])
        table_data, extracted_headers = extract_table_data(soup, item["date"])

        if index == 0:
            headers = extracted_headers

        all_data.extend(table_data)

    df = pd.DataFrame(all_data, columns=headers)

    # Transform the DataFrame data
    transformed_data = [
        item for _, row in df.iterrows() for item in transform_row_data(row)
    ]
    new_df = pd.DataFrame(transformed_data)

    # Add columns for price changes and calculate them
    for i, date in enumerate(dates, start=1):
        new_df[f'Change to Date {i}'] = None

    for index, row in new_df.iterrows():
        ticker = f"{row['Ticker']}.WA"
        original_date = datetime.strptime(row['Date'], '%Y-%m-%d')
        prices = fetch_prices_for_dates(ticker, original_date, dates)

        original_price = prices.get(original_date)

        for i, future_date in enumerate(dates, start=1):
            new_price = prices.get(future_date)
            percentage_change = calculate_percentage_change(
                original_price, new_price)
            new_df.at[index, f'Change to Date {i}'] = percentage_change

    print(new_df)
