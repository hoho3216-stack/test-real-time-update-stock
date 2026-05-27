import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from stock_fetcher import StockFetcher

class StockFetcherThread(QThread):
    """Worker thread for fetching stock data"""
    result_ready = pyqtSignal(dict)
    
    def __init__(self, code: str):
        super().__init__()
        self.code = code
    
    def run(self):
        data = StockFetcher.fetch_stock_data(self.code)
        self.result_ready.emit(data)

class StockQuoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.fetcher_thread = None
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("eNet Stock Quote Viewer")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Search layout
        search_layout = QHBoxLayout()
        
        # Stock code input
        self.stock_code_input = QLineEdit()
        self.stock_code_input.setPlaceholderText("Enter stock code (e.g., 0001)")
        self.stock_code_input.returnPressed.connect(self.search_stock)
        search_layout.addWidget(QLabel("Stock Code:"))
        search_layout.addWidget(self.stock_code_input)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_stock)
        search_layout.addWidget(self.search_button)
        
        main_layout.addLayout(search_layout)
        
        # Status label
        self.status_label = QLabel("Ready to search")
        main_layout.addWidget(self.status_label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Property", "Value"])
        main_layout.addWidget(self.results_table)
        
        central_widget.setLayout(main_layout)
    
    def search_stock(self):
        """Search for stock data"""
        code = self.stock_code_input.text().strip()
        
        if not code:
            self.status_label.setText("Please enter a stock code")
            return
        
        self.status_label.setText(f"Searching for stock {code}...")
        self.search_button.setEnabled(False)
        
        # Create and start fetcher thread
        self.fetcher_thread = StockFetcherThread(code)
        self.fetcher_thread.result_ready.connect(self.display_results)
        self.fetcher_thread.start()
    
    def display_results(self, data: dict):
        """Display results in the table"""
        self.search_button.setEnabled(True)
        
        if data.get('status') == 'success':
            self.status_label.setText(f"Stock {data['code']} loaded successfully")
            self.results_table.setRowCount(0)
            
            # Add data rows
            for key, value in data.items():
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(str(key)))
                self.results_table.setItem(row, 1, QTableWidgetItem(str(value)))
        else:
            error_msg = data.get('error', 'Unknown error')
            self.status_label.setText(f"Error: {error_msg}")

def main():
    app = QApplication(sys.argv)
    window = StockQuoteApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
