import requests
import pandas as pd

class ExportPrice:
    def __init__(self, url_google_sheet):
        self.url_google_sheet = url_google_sheet
        
    def save_data(self, csv_file_path):
        response = requests.get(self.url_google_sheet)
        csv_text = response.content.decode("utf-8")
        if response.status_code == 200:
            with open(csv_file_path, "w", encoding="utf-8") as f:
                f.write(csv_text)  
            print(f"File saved as {csv_file_path}")
        else:
            print("Failed to download file")

    def process_data(self, csv_file_path, new_csv_file_path):
        df = pd.read_csv(csv_file_path, skip_blank_lines=True, decimal=",", thousands=".")
        df.columns = df.columns.str.strip()
        df.to_csv(new_csv_file_path, index=False)
        
    

    

