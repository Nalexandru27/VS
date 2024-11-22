import openpyxl

class ExcelFile:
    def __init__(self, filename, columns):
        self.filename = filename
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.sheet.append(columns)

    def add_stocks(self, stock):
        for key, value in stock.items():
            self.sheet.append(value)
    
    def save(self):
        self.workbook.save(self.filename)
        print(f"Excel file saved as {self.filename}")