import requests
import pandas as pd

class SaveDocsData:
    def __init__(self, url):
        self.url = url

    def save_data(self, csv_file_path):
        # Correct CSV export URL
        csv_url = self.url

        response = requests.get(csv_url)

        with open(csv_file_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        print("File saved as 'spreadsheet_data.csv'")

    def process_data(self, csv_file_path, new_csv_file_path):
        # Load the data, skipping the first four lines
        data_path = csv_file_path  # Replace with the actual file path
        df = pd.read_csv(data_path, skiprows=4)

        # Clean column names
        df.columns = df.columns.str.strip()

        # Verify column names
        print("Column names:", df.columns)

        # Select relevant columns
        columns_of_interest = ["Symbol", "Company", "Sector", "No Years", "DGR 1Y", "DGR 3Y", "DGR 5Y", "DGR 10Y"]

        # Filter the dataframe: 'No Years' >= 10
        if "No Years" in df.columns:
            filtered_df = df[df["No Years"] >= 10][columns_of_interest]

            # Convert "No Years" to numeric if necessary
            filtered_df["No Years"] = pd.to_numeric(filtered_df["No Years"], errors="coerce")

            # Filter rows where the symbol does not contain a period
            filtered_df = filtered_df[~filtered_df["Symbol"].str.contains(r"\.", na=False)]

            # Sort by "No Years" in descending order
            sorted_df = filtered_df.sort_values(by="No Years", ascending=False)

            # Export to a new CSV
            sorted_df.to_csv(new_csv_file_path, index=False)
            print("Filtered and sorted data saved to 'filtered_sorted_companies.csv'")
        else:
            print("'No Years' column not found. Verify the column names.")