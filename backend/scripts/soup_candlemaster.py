import requests
import pandas as pd
from bs4 import BeautifulSoup


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
    print(df)
