#!/usr/bin/env python3
"""
Hong Kong Stock Price Viewer - Modern Desktop Application
A modern customtkinter-based GUI application for fetching and displaying real-time
Hong Kong stock information using yfinance with dark/light theme support.

Features:
- Modern customtkinter UI with dark/light theme
- Auto-refresh stock prices every 3 seconds
- Theme toggle (dark/light mode)
- Real-time data from yfinance
- Responsive and beautiful design

Usage:
    python app.py
"""

import customtkinter as ctk
import threading
from datetime import datetime
import yfinance as yf
from typing import Optional, Dict, Any


# Configure customtkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"


class StockPriceApp(ctk.CTk):
    """Main application class for stock price viewer using customtkinter."""
    
    def __init__(self) -> None:
        """Initialize the modern application."""
        super().__init__()
        
        # Window configuration
        self.title("HK Stock Price Viewer")
        self.geometry("1000x750")
        self.minsize(800, 600)
        
        # Store the currently displayed stock data
        self.current_stock_code: str = ""
        self.current_data: Optional[Dict[str, Any]] = None
        
        # Auto-refresh settings
        self.auto_refresh_enabled = False
        self.refresh_interval = 3000  # 3 seconds in milliseconds
        self.refresh_timer_id: Optional[str] = None
        
        # Set grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Build the UI
        self.build_ui()
        
        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def build_ui(self) -> None:
        """Build the main UI components with customtkinter."""
        # Main container with proper spacing
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_container.grid_rowconfigure(3, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # ===== HEADER =====
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📈 HK Stock Price Viewer",
            font=("Helvetica", 24, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Theme toggle button
        self.theme_button = ctk.CTkButton(
            header_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            width=120,
            height=35,
            corner_radius=8
        )
        self.theme_button.grid(row=0, column=1, sticky="e")
        
        # ===== INPUT SECTION =====
        input_frame = ctk.CTkFrame(main_container)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Stock code label and input
        ctk.CTkLabel(
            input_frame,
            text="Stock Code (HK):",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(10, 10), pady=10)
        
        self.stock_code_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="e.g., 0700, 9988, 0005",
            height=40,
            border_width=2,
            corner_radius=8,
            font=("Helvetica", 12)
        )
        self.stock_code_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.stock_code_entry.bind('<Return>', lambda e: self.search_stock())
        
        # Button frame
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="e", padx=(10, 0), pady=10)
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=0)
        
        # Get Price button
        self.search_button = ctk.CTkButton(
            button_frame,
            text="🔍 Get Price",
            command=self.search_stock,
            height=40,
            width=100,
            corner_radius=8,
            font=("Helvetica", 11, "bold")
        )
        self.search_button.grid(row=0, column=0, padx=5)
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_stock,
            state="disabled",
            height=40,
            width=100,
            corner_radius=8,
            font=("Helvetica", 11, "bold")
        )
        self.refresh_button.grid(row=0, column=1, padx=5)
        
        # Auto-refresh toggle
        self.auto_refresh_button = ctk.CTkButton(
            button_frame,
            text="⏱️ Auto Refresh",
            command=self.toggle_auto_refresh,
            state="disabled",
            height=40,
            width=120,
            corner_radius=8,
            font=("Helvetica", 11, "bold"),
            fg_color=["#1f6aa5", "#0d47a1"]
        )
        self.auto_refresh_button.grid(row=0, column=2, padx=5)
        
        # Loading indicator
        self.loading_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=("Helvetica", 10)
        )
        self.loading_label.grid(row=0, column=3, padx=(10, 0))
        
        # ===== RESULTS SECTION =====
        results_frame = ctk.CTkFrame(main_container)
        results_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 15))
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Results label
        ctk.CTkLabel(
            results_frame,
            text="Stock Information",
            font=("Helvetica", 14, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Scrollable frame for results
        self.scrollable_frame = ctk.CTkScrollableFrame(
            results_frame,
            corner_radius=10
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Initial message
        self.info_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Enter a stock code (e.g., 0005, 0700, 9988) and click 'Get Price'",
            font=("Helvetica", 13),
            text_color=["gray50", "gray70"]
        )
        self.info_label.pack(pady=40)
        
        # ===== STATUS BAR =====
        status_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        status_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=("Helvetica", 10),
            text_color=["gray50", "gray70"]
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.time_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Helvetica", 10),
            text_color=["gray50", "gray70"]
        )
        self.time_label.grid(row=0, column=1, sticky="e")
    
    def toggle_theme(self) -> None:
        """Toggle between dark and light theme."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
        # Update button text
        button_text = "☀️ Light Mode" if new_mode == "dark" else "🌙 Dark Mode"
        self.theme_button.configure(text=button_text)
    
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
        """Search for stock data in a separate thread."""
        code = self.stock_code_entry.get().strip()
        if not code:
            self.show_error("Please enter a stock code")
            return
        
        # Disable buttons and show loading indicator
        self.search_button.configure(state="disabled")
        self.refresh_button.configure(state="disabled")
        self.auto_refresh_button.configure(state="disabled")
        self.stock_code_entry.configure(state="disabled")
        self.loading_label.configure(text="Loading... ⏳")
        self.status_label.configure(text="Fetching data...")
        
        # Stop any existing auto-refresh
        if self.refresh_timer_id:
            self.after_cancel(self.refresh_timer_id)
            self.refresh_timer_id = None
        self.auto_refresh_enabled = False
        
        # Run the fetch in a separate thread
        thread = threading.Thread(target=self._fetch_stock_data, args=(code,), daemon=True)
        thread.start()
    
    def refresh_stock(self) -> None:
        """Refresh the currently displayed stock data."""
        if self.current_stock_code:
            self.stock_code_entry.delete(0, "end")
            self.stock_code_entry.insert(0, self.current_stock_code.replace('.HK', ''))
            
            # Disable buttons and show loading indicator
            self.search_button.configure(state="disabled")
            self.refresh_button.configure(state="disabled")
            self.auto_refresh_button.configure(state="disabled")
            self.stock_code_entry.configure(state="disabled")
            self.loading_label.configure(text="Refreshing... ⏳")
            self.status_label.configure(text="Fetching data...")
            
            # Run the fetch in a separate thread
            thread = threading.Thread(
                target=self._fetch_stock_data,
                args=(self.current_stock_code.replace('.HK', ''),),
                daemon=True
            )
            thread.start()
    
    def toggle_auto_refresh(self) -> None:
        """Toggle auto-refresh on/off."""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        
        if self.auto_refresh_enabled:
            self.auto_refresh_button.configure(
                fg_color=["#28a745", "#20c997"],
                text="⏱️ Auto: ON"
            )
            self.status_label.configure(text="Auto-refresh enabled (every 3 seconds)")
            self._schedule_auto_refresh()
        else:
            self.auto_refresh_button.configure(
                fg_color=["#1f6aa5", "#0d47a1"],
                text="⏱️ Auto: OFF"
            )
            self.status_label.configure(text="Auto-refresh disabled")
            if self.refresh_timer_id:
                self.after_cancel(self.refresh_timer_id)
                self.refresh_timer_id = None
    
    def _schedule_auto_refresh(self) -> None:
        """Schedule the next auto-refresh after 3 seconds."""
        if self.auto_refresh_enabled and self.current_stock_code:
            self.refresh_timer_id = self.after(self.refresh_interval, self._auto_refresh)
    
    def _auto_refresh(self) -> None:
        """Perform auto-refresh of stock data."""
        if self.auto_refresh_enabled and self.current_stock_code:
            self.loading_label.configure(text="Auto-refreshing... ⏳")
            
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
                self.after(0, self.show_error, "Invalid stock code")
                return
            
            # Fetch stock data using yfinance
            stock = yf.Ticker(formatted_code)
            info = stock.info
            
            # Check if we got valid data
            if not info or 'shortName' not in info:
                self.after(0, self.show_error, f"Stock code '{code}' not found or invalid")
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
            self.after(0, self._display_stock_data, formatted_code, stock_data)
            
        except Exception as e:
            error_msg = str(e)
            self.after(0, self.show_error, f"Error: {error_msg}")
        finally:
            # Re-enable buttons in main thread
            self.after(0, self._enable_buttons)
            # Schedule next auto-refresh if enabled
            if self.auto_refresh_enabled:
                self.after(0, self._schedule_auto_refresh)
    
    def _display_stock_data(self, code: str, data: Dict[str, Any]) -> None:
        """Display fetched stock data in the UI."""
        # Clear previous widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Stock name
        name_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=f"{data['shortName']} ({code})",
            font=("Helvetica", 18, "bold")
        )
        name_label.pack(pady=(0, 20))
        
        # Get current price
        current_price = data.get('currentPrice') or data.get('regularMarketPrice', 'N/A')
        
        # Create main info frame
        main_info_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        main_info_frame.pack(fill="x", pady=(0, 20))
        
        # Price display
        price_frame = ctk.CTkFrame(main_info_frame, fg_color="transparent")
        price_frame.pack(side="left", padx=(0, 40))
        
        ctk.CTkLabel(
            price_frame,
            text="Price:",
            font=("Helvetica", 11, "bold"),
            text_color=["gray50", "gray70"]
        ).pack(anchor="w")
        
        if isinstance(current_price, (int, float)):
            price_label = ctk.CTkLabel(
                price_frame,
                text=f"HK${current_price:.2f}",
                font=("Helvetica", 26, "bold"),
                text_color="#3498db"
            )
        else:
            price_label = ctk.CTkLabel(price_frame, text=str(current_price), font=("Helvetica", 26, "bold"))
        price_label.pack(anchor="w")
        
        # Change percentage
        change_pct = data.get('regularMarketChangePercent', 'N/A')
        change = data.get('regularMarketChange', 'N/A')
        
        change_frame = ctk.CTkFrame(main_info_frame, fg_color="transparent")
        change_frame.pack(side="left", padx=(0, 40))
        
        ctk.CTkLabel(
            change_frame,
            text="Change:",
            font=("Helvetica", 11, "bold"),
            text_color=["gray50", "gray70"]
        ).pack(anchor="w")
        
        if isinstance(change_pct, (int, float)):
            change_color = "#27ae60" if change_pct >= 0 else "#e74c3c"
            sign = '+' if change_pct >= 0 else ''
            change_text = f"{sign}{change_pct:.2f}%"
            change_value = f"{sign}{change:.2f}" if isinstance(change, (int, float)) else str(change)
            
            change_label = ctk.CTkLabel(
                change_frame,
                text=f"{change_text} ({change_value})",
                font=("Helvetica", 18, "bold"),
                text_color=change_color
            )
        else:
            change_label = ctk.CTkLabel(change_frame, text=str(change_pct), font=("Helvetica", 18, "bold"))
        
        change_label.pack(anchor="w")
        
        # Separator
        separator = ctk.CTkFrame(self.scrollable_frame, height=2, fg_color=["gray70", "gray30"])
        separator.pack(fill="x", pady=20)
        
        # Details section label
        details_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Details",
            font=("Helvetica", 13, "bold")
        )
        details_label.pack(anchor="w", pady=(0, 10))
        
        # Details frame
        details_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        details_container.pack(fill="x", pady=(0, 10))
        
        # Details in a grid format
        details = [
            ("Previous Close", data.get('regularMarketPreviousClose', 'N/A')),
            ("Day High", data.get('regularMarketDayHigh', 'N/A')),
            ("Day Low", data.get('regularMarketDayLow', 'N/A')),
            ("Volume", data.get('regularMarketVolume', 'N/A')),
        ]
        
        for idx, (label, value) in enumerate(details):
            # Create row frame
            row_frame = ctk.CTkFrame(details_container, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            # Label
            ctk.CTkLabel(
                row_frame,
                text=f"{label}:",
                font=("Helvetica", 11, "bold"),
                text_color=["gray50", "gray70"],
                width=120
            ).pack(side="left", anchor="w")
            
            # Value formatting
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
            
            ctk.CTkLabel(
                row_frame,
                text=formatted_value,
                font=("Helvetica", 11),
                text_color=["gray30", "gray80"]
            ).pack(side="left")
        
        # Update status and timestamp
        auto_status = " (Auto-refresh: ON)" if self.auto_refresh_enabled else ""
        self.status_label.configure(text=f"✓ Stock data updated - {code}{auto_status}")
        self._update_timestamp()
        self.loading_label.configure(text="")
    
    def _enable_buttons(self) -> None:
        """Re-enable UI buttons after data fetch completes."""
        self.search_button.configure(state="normal")
        self.stock_code_entry.configure(state="normal")
        if self.current_stock_code:
            self.refresh_button.configure(state="normal")
            self.auto_refresh_button.configure(state="normal")
    
    def show_error(self, error_msg: str) -> None:
        """Display error message in the results area."""
        # Clear previous widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Error frame
        error_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        error_frame.pack(pady=40)
        
        # Error icon and message
        ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=("Helvetica", 40)
        ).pack(pady=(0, 10))
        
        error_label = ctk.CTkLabel(
            error_frame,
            text=error_msg,
            font=("Helvetica", 13),
            text_color="#e74c3c"
        )
        error_label.pack()
        
        self.status_label.configure(text=f"✗ Error: {error_msg}")
        self.loading_label.configure(text="")
    
    def _update_timestamp(self) -> None:
        """Update the timestamp label with current time."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=f"Last updated: {current_time}")
    
    def on_close(self) -> None:
        """Handle window close event - clean up auto-refresh timer."""
        if self.refresh_timer_id:
            self.after_cancel(self.refresh_timer_id)
        self.destroy()


def main() -> None:
    """Main entry point for the application."""
    app = StockPriceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
