import requests
import pandas as pd

class ExportPriceHistory:
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

    

