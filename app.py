#!/usr/bin/env python3
"""
Hong Kong Stock Price Viewer - Desktop Application
A simple Tkinter-based GUI application for fetching and displaying real-time
Hong Kong stock information using yfinance.

Features:
- Auto-refresh stock prices every 3 seconds
- Clean, modern Tkinter interface
- Real-time data from yfinance

Usage:
    python app.py
"""

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
import yfinance as yf
from typing import Optional, Dict, Any


class StockPriceApp:
    """Main application class for stock price viewer."""
    
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the application.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("Hong Kong Stock Price Viewer")
        self.root.geometry("900x700")
        self.root.minsize(700, 600)
        
        # Store the currently displayed stock data
        self.current_stock_code: str = ""
        self.current_data: Optional[Dict[str, Any]] = None
        self.is_loading = False
        
        # Auto-refresh settings
        self.auto_refresh_enabled = False
        self.refresh_interval = 3000  # 3 seconds in milliseconds
        self.refresh_timer_id: Optional[str] = None
        
        # Configure style
        self.setup_styles()
        
        # Build the UI
        self.build_ui()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_styles(self) -> None:
        """Configure custom styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define custom colors
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 9))
        style.configure('Error.TLabel', font=('Arial', 10), foreground='red')
        style.configure('Success.TLabel', font=('Arial', 10), foreground='green')
        style.configure('TButton', font=('Arial', 10))
    
    def build_ui(self) -> None:
        """Build the main UI components."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # ===== INPUT SECTION =====
        input_frame = ttk.LabelFrame(main_frame, text="Stock Search", padding="10")
        input_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Stock code label and input
        ttk.Label(input_frame, text="Stock Code (HK):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.stock_code_entry = ttk.Entry(input_frame, font=('Arial', 11), width=20)
        self.stock_code_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        self.stock_code_entry.bind('<Return>', lambda e: self.search_stock())
        
        # Search button
        self.search_button = ttk.Button(input_frame, text="Get Price", command=self.search_stock)
        self.search_button.grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        # Refresh button
        self.refresh_button = ttk.Button(input_frame, text="Refresh", command=self.refresh_stock, state=tk.DISABLED)
        self.refresh_button.grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        
        # Auto-refresh toggle button
        self.auto_refresh_button = ttk.Button(
            input_frame,
            text="Auto Refresh: OFF",
            command=self.toggle_auto_refresh,
            state=tk.DISABLED
        )
        self.auto_refresh_button.grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        
        # Loading indicator
        self.loading_label = ttk.Label(input_frame, text="", style='Status.TLabel')
        self.loading_label.grid(row=0, column=5, sticky=tk.E, padx=(10, 0))
        
        # ===== RESULTS SECTION =====
        results_frame = ttk.LabelFrame(main_frame, text="Stock Information", padding="10")
        results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create a frame for the results with scrollbar
        canvas_frame = ttk.Frame(results_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        # Canvas and scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, padding="10")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Initial message
        self.info_label = ttk.Label(
            self.scrollable_frame,
            text="Enter a stock code (e.g., 0005, 0700, 9988) and click 'Get Price'",
            justify=tk.CENTER,
            foreground='gray'
        )
        self.info_label.pack(pady=20)
        
        # ===== STATUS BAR =====
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            style='Status.TLabel',
            relief=tk.SUNKEN
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.time_label = ttk.Label(
            status_frame,
            text="",
            style='Status.TLabel',
            relief=tk.SUNKEN
        )
        self.time_label.pack(side=tk.RIGHT, fill=tk.X, padx=(5, 0))
    
    def format_stock_code(self, code: str) -> str:
        """
        Format stock code by adding .HK suffix if not present.
        
        Args:
            code: Raw stock code input
            
        Returns:
            Formatted stock code
        """
        code = code.strip().upper()
        if not code:
            return ""
        if not code.endswith('.HK'):
            code += '.HK'
        return code
    
    def search_stock(self) -> None:
        """
        Search for stock data in a separate thread to avoid blocking the UI.
        This method is called when the user clicks the "Get Price" button or presses Enter.
        """
        code = self.stock_code_entry.get().strip()
        if not code:
            self.show_error("Please enter a stock code")
            return
        
        # Disable buttons and show loading indicator
        self.search_button.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.auto_refresh_button.config(state=tk.DISABLED)
        self.stock_code_entry.config(state=tk.DISABLED)
        self.loading_label.config(text="Loading... ⏳")
        self.status_label.config(text="Fetching data...")
        
        # Stop any existing auto-refresh
        if self.refresh_timer_id:
            self.root.after_cancel(self.refresh_timer_id)
            self.refresh_timer_id = None
        self.auto_refresh_enabled = False
        self.auto_refresh_button.config(text="Auto Refresh: OFF", state=tk.DISABLED)
        
        # Run the fetch in a separate thread
        thread = threading.Thread(target=self._fetch_stock_data, args=(code,), daemon=True)
        thread.start()
    
    def refresh_stock(self) -> None:
        """Refresh the currently displayed stock data."""
        if self.current_stock_code:
            self.stock_code_entry.delete(0, tk.END)
            self.stock_code_entry.insert(0, self.current_stock_code.replace('.HK', ''))
            
            # Disable buttons and show loading indicator
            self.search_button.config(state=tk.DISABLED)
            self.refresh_button.config(state=tk.DISABLED)
            self.auto_refresh_button.config(state=tk.DISABLED)
            self.stock_code_entry.config(state=tk.DISABLED)
            self.loading_label.config(text="Refreshing... ⏳")
            self.status_label.config(text="Fetching data...")
            
            # Run the fetch in a separate thread
            thread = threading.Thread(target=self._fetch_stock_data, args=(self.current_stock_code.replace('.HK', ''),), daemon=True)
            thread.start()
    
    def toggle_auto_refresh(self) -> None:
        """Toggle auto-refresh on/off."""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        
        if self.auto_refresh_enabled:
            self.auto_refresh_button.config(text="Auto Refresh: ON")
            self.status_label.config(text="Auto-refresh enabled (every 3 seconds)")
            # Start auto-refresh
            self._schedule_auto_refresh()
        else:
            self.auto_refresh_button.config(text="Auto Refresh: OFF")
            self.status_label.config(text="Auto-refresh disabled")
            # Cancel any pending auto-refresh
            if self.refresh_timer_id:
                self.root.after_cancel(self.refresh_timer_id)
                self.refresh_timer_id = None
    
    def _schedule_auto_refresh(self) -> None:
        """Schedule the next auto-refresh after 3 seconds."""
        if self.auto_refresh_enabled and self.current_stock_code:
            # Schedule the next refresh
            self.refresh_timer_id = self.root.after(self.refresh_interval, self._auto_refresh)
    
    def _auto_refresh(self) -> None:
        """Perform auto-refresh of stock data."""
        if self.auto_refresh_enabled and self.current_stock_code:
            self.loading_label.config(text="Auto-refreshing... ⏳")
            
            # Run the fetch in a separate thread
            thread = threading.Thread(
                target=self._fetch_stock_data,
                args=(self.current_stock_code.replace('.HK', ''),),
                daemon=True
            )
            thread.start()
    
    def _fetch_stock_data(self, code: str) -> None:
        """
        Fetch stock data from yfinance (runs in separate thread).
        
        Args:
            code: Stock code entered by user
        """
        try:
            formatted_code = self.format_stock_code(code)
            
            if not formatted_code:
                self.root.after(0, self.show_error, "Invalid stock code")
                return
            
            # Fetch stock data using yfinance
            stock = yf.Ticker(formatted_code)
            info = stock.info
            
            # Check if we got valid data
            if not info or 'shortName' not in info:
                self.root.after(0, self.show_error, f"Stock code '{code}' not found or invalid")
                return
            
            # Extract relevant information
            stock_data = {
                'shortName': info.get('shortName', 'N/A'),
                'currentPrice': info.get('currentPrice', 'N/A'),
                'regularMarketPrice': info.get('regularMarketPrice', 'N/A'),
                'regularMarketPreviousClose': info.get('regularMarketPreviousClose', 'N/A'),
                'regularMarketChange': info.get('regularMarketChange', 'N/A'),
                'regularMarketChangePercent': info.get('regularMarketChangePercent', 'N/A'),
                'regularMarketVolume': info.get('regularMarketVolume', 'N/A'),
                'regularMarketDayHigh': info.get('regularMarketDayHigh', 'N/A'),
                'regularMarketDayLow': info.get('regularMarketDayLow', 'N/A'),
            }
            
            self.current_stock_code = formatted_code
            self.current_data = stock_data
            
            # Update UI in main thread
            self.root.after(0, self._display_stock_data, formatted_code, stock_data)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self.show_error, f"Error: {error_msg}")
        finally:
            # Re-enable buttons in main thread
            self.root.after(0, self._enable_buttons)
            # Schedule next auto-refresh if enabled
            if self.auto_refresh_enabled:
                self.root.after(0, self._schedule_auto_refresh)
    
    def _display_stock_data(self, code: str, data: Dict[str, Any]) -> None:
        """
        Display fetched stock data in the UI.
        
        Args:
            code: Stock code
            data: Dictionary containing stock information
        """
        # Clear previous widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Stock name
        name_label = ttk.Label(
            self.scrollable_frame,
            text=f"{data['shortName']} ({code})",
            style='Title.TLabel'
        )
        name_label.pack(pady=(0, 15))
        
        # Get current price
        current_price = data.get('currentPrice') or data.get('regularMarketPrice', 'N/A')
        
        # Create main info frame
        main_info_frame = ttk.Frame(self.scrollable_frame)
        main_info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Price display
        price_frame = ttk.Frame(main_info_frame)
        price_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        ttk.Label(price_frame, text="Price:", style='Header.TLabel').pack(anchor=tk.W)
        
        if isinstance(current_price, (int, float)):
            price_label = ttk.Label(
                price_frame,
                text=f"HK${current_price:.2f}",
                font=('Arial', 20, 'bold'),
                foreground='darkblue'
            )
        else:
            price_label = ttk.Label(price_frame, text=str(current_price), font=('Arial', 20, 'bold'))
        price_label.pack(anchor=tk.W)
        
        # Change percentage
        change_pct = data.get('regularMarketChangePercent', 'N/A')
        change = data.get('regularMarketChange', 'N/A')
        
        change_frame = ttk.Frame(main_info_frame)
        change_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        ttk.Label(change_frame, text="Change:", style='Header.TLabel').pack(anchor=tk.W)
        
        if isinstance(change_pct, (int, float)):
            change_color = 'green' if change_pct >= 0 else 'red'
            sign = '+' if change_pct >= 0 else ''
            change_text = f"{sign}{change_pct:.2f}%"
            change_value = f"{sign}{change:.2f}" if isinstance(change, (int, float)) else str(change)
            
            change_label = ttk.Label(
                change_frame,
                text=f"{change_text} ({change_value})",
                font=('Arial', 14, 'bold'),
                foreground=change_color
            )
        else:
            change_label = ttk.Label(change_frame, text=str(change_pct), font=('Arial', 14, 'bold'))
        
        change_label.pack(anchor=tk.W)
        
        # Separator
        ttk.Separator(self.scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Details section
        details_label = ttk.Label(self.scrollable_frame, text="Details", style='Header.TLabel')
        details_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Details in a grid format
        details = [
            ("Previous Close", data.get('regularMarketPreviousClose', 'N/A')),
            ("Day High", data.get('regularMarketDayHigh', 'N/A')),
            ("Day Low", data.get('regularMarketDayLow', 'N/A')),
            ("Volume", data.get('regularMarketVolume', 'N/A')),
        ]
        
        for label, value in details:
            detail_frame = ttk.Frame(self.scrollable_frame)
            detail_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(detail_frame, text=f"{label}:", width=20, font=('Arial', 10)).pack(side=tk.LEFT)
            
            if label == "Volume" and isinstance(value, (int, float)):
                if value >= 1_000_000:
                    formatted_value = f"{value / 1_000_000:.2f}M"
                elif value >= 1_000:
                    formatted_value = f"{value / 1_000:.2f}K"
                else:
                    formatted_value = str(int(value))
            elif isinstance(value, (int, float)) and label != "Volume":
                formatted_value = f"HK${value:.2f}"
            else:
                formatted_value = str(value)
            
            ttk.Label(detail_frame, text=formatted_value, font=('Arial', 10), foreground='darkslategray').pack(side=tk.LEFT)
        
        # Update status and timestamp
        if self.auto_refresh_enabled:
            self.status_label.config(text=f"✓ Stock data updated - {code} (Auto-refresh: ON)")
        else:
            self.status_label.config(text=f"✓ Stock data updated - {code}")
        self._update_timestamp()
        self.loading_label.config(text="")
    
    def _enable_buttons(self) -> None:
        """Re-enable UI buttons after data fetch completes."""
        self.search_button.config(state=tk.NORMAL)
        self.stock_code_entry.config(state=tk.NORMAL)
        if self.current_stock_code:
            self.refresh_button.config(state=tk.NORMAL)
            self.auto_refresh_button.config(state=tk.NORMAL)
    
    def show_error(self, error_msg: str) -> None:
        """
        Display error message in the results area.
        
        Args:
            error_msg: Error message to display
        """
        # Clear previous widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        error_label = ttk.Label(
            self.scrollable_frame,
            text=error_msg,
            style='Error.TLabel',
            font=('Arial', 12),
            justify=tk.CENTER
        )
        error_label.pack(pady=20)
        
        self.status_label.config(text=f"✗ Error: {error_msg}")
        self.loading_label.config(text="")
    
    def _update_timestamp(self) -> None:
        """Update the timestamp label with current time."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Last updated: {current_time}")
    
    def on_close(self) -> None:
        """Handle window close event - clean up auto-refresh timer."""
        if self.refresh_timer_id:
            self.root.after_cancel(self.refresh_timer_id)
        self.root.destroy()


def main() -> None:
    """Main entry point for the application."""
    root = tk.Tk()
    app = StockPriceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
