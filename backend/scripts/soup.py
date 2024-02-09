import requests
import pandas as pd
from bs4 import BeautifulSoup

# Define a list of stock symbols you are interested in
# For demonstration, we'll use a small list, but for a real scenario, you might want a comprehensive list or a way to generate it
urlRZiS = "https://www.biznesradar.pl/raporty-finansowe-rachunek-zyskow-i-strat/ASBISC"
urlBilans = "https://www.biznesradar.pl/raporty-finansowe-bilans/ASBISC"
urlPrzeplywy = "https://www.biznesradar.pl/raporty-finansowe-przeplywy-pieniezne/ASBISC"
response = requests.get(urlPrzeplywy)
soup = BeautifulSoup(response.text, "html.parser")
# Placeholder for stocks meeting the criteria
table = soup.find(
    "table", attrs={"class": "report-table"}
)  # Use the actual class or ID of the table
rows = table.find_all("tr")


def find_deepest_text(element):
    if not element.find_all():
        return element.text.strip()
    for child in element.children:
        return find_deepest_text(child)


all_row_data = []

for index, row in enumerate(rows):
    if index < 1:  # Skip the first 2 rows
        continue
    cells = row.find_all("td")[
        :-1
    ]  # Exclude the last column by slicing all but the last cell
    row_data = []
    for index, cell in enumerate(cells):
        if index == 0:  # For the first cell in each row, extract the deepest text
            cell_data = find_deepest_text(cell)
        else:  # For remaining cells, find a span with the specified class and get its text
            span_with_class = cell.find("span", class_="value")
            if span_with_class:
                cell_data = span_with_class.text.replace(
                    " ", ""
                ).strip()  # Remove all spaces and then strip
            else:
                cell_data = None  # Or "" for an empty string
        row_data.append(cell_data)
    all_row_data.append(row_data)


# Create a DataFrame from the accumulated data
df = pd.DataFrame(all_row_data)

# Specify your desired CSV file path
csv_file_path = "soup.csv"

# Export the DataFrame to a CSV file
df.to_csv(csv_file_path, index=False, header=False)
