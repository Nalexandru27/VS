import openpyxl

class ExcelFile:
    def __init__(self, filename, columns):
        self.filename = filename
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.columns = columns
        self.sheet.append(columns)

    def add_stocks(self, stock_dict):
        row = []
        for column in self.columns:
            value = stock_dict.get(column, None)
            row.append(value)
        self.sheet.append(row)
    
    def save(self):
        try:
            self.workbook.save(self.filename)
            print(f"Excel file saved as {self.filename}")
        except Exception as e:
            print(f"Error saving Excel file: {e}")