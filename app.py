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

# Color palette
COLORS = {
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "green": "#10B981",
    "green_dark": "#059669",
    "red": "#EF4444",
    "red_dark": "#DC2626",
    "card_dark": "#1E293B",
    "card_light": "#F8FAFC",
    "surface_dark": "#0F172A",
    "surface_light": "#FFFFFF",
    "muted_dark": "#94A3B8",
    "muted_light": "#64748B",
    "border_dark": "#334155",
    "border_light": "#E2E8F0",
}


class StockPriceApp(ctk.CTk):
    """Main application class for stock price viewer using customtkinter."""

    def __init__(self) -> None:
        """Initialize the modern application."""
        super().__init__()

        # Window configuration
        self.title("HK Stock Price Viewer")
        self.geometry("1050x780")
        self.minsize(850, 650)

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
        """Build the main UI components with a modern card-based layout."""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # ===== HEADER BAR =====
        header_frame = ctk.CTkFrame(
            main_container,
            corner_radius=16,
            fg_color=[COLORS["card_light"], COLORS["card_dark"]],
            border_width=1,
            border_color=[COLORS["border_light"], COLORS["border_dark"]],
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header_frame.grid_columnconfigure(1, weight=1)

        # App icon + title
        title_label = ctk.CTkLabel(
            header_frame,
            text="  HK Stock Price Viewer",
            font=("Segoe UI", 22, "bold"),
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=16)

        # Right-side header controls
        header_controls = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_controls.grid(row=0, column=1, sticky="e", padx=20, pady=16)

        self.theme_switch_var = ctk.StringVar(value="dark")
        self.theme_switch = ctk.CTkSwitch(
            header_controls,
            text="Dark Mode",
            command=self.toggle_theme,
            variable=self.theme_switch_var,
            onvalue="dark",
            offvalue="light",
            font=("Segoe UI", 12),
            switch_width=44,
            switch_height=22,
        )
        self.theme_switch.pack(side="right")

        # ===== SEARCH CARD =====
        search_card = ctk.CTkFrame(
            main_container,
            corner_radius=16,
            fg_color=[COLORS["card_light"], COLORS["card_dark"]],
            border_width=1,
            border_color=[COLORS["border_light"], COLORS["border_dark"]],
        )
        search_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        search_card.grid_columnconfigure(0, weight=1)

        # Search row
        search_row = ctk.CTkFrame(search_card, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=(20, 12))
        search_row.grid_columnconfigure(0, weight=1)

        self.stock_code_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Enter stock code  (e.g. 0700, 9988, 0005)",
            height=46,
            border_width=2,
            corner_radius=12,
            font=("Segoe UI", 13),
        )
        self.stock_code_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.stock_code_entry.bind("<Return>", lambda e: self.search_stock())

        self.search_button = ctk.CTkButton(
            search_row,
            text="Get Price",
            command=self.search_stock,
            height=46,
            width=130,
            corner_radius=12,
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
        )
        self.search_button.grid(row=0, column=1)

        # Action buttons row
        action_row = ctk.CTkFrame(search_card, fg_color="transparent")
        action_row.pack(fill="x", padx=20, pady=(0, 20))

        self.refresh_button = ctk.CTkButton(
            action_row,
            text="Refresh",
            command=self.refresh_stock,
            state="disabled",
            height=36,
            width=110,
            corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=["#E2E8F0", "#334155"],
            hover_color=["#CBD5E1", "#475569"],
            text_color=["#334155", "#E2E8F0"],
        )
        self.refresh_button.pack(side="left", padx=(0, 8))

        self.auto_refresh_button = ctk.CTkButton(
            action_row,
            text="Auto Refresh",
            command=self.toggle_auto_refresh,
            state="disabled",
            height=36,
            width=130,
            corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=["#E2E8F0", "#334155"],
            hover_color=["#CBD5E1", "#475569"],
            text_color=["#334155", "#E2E8F0"],
        )
        self.auto_refresh_button.pack(side="left", padx=(0, 12))

        self.loading_label = ctk.CTkLabel(
            action_row,
            text="",
            font=("Segoe UI", 11),
            text_color=[COLORS["muted_light"], COLORS["muted_dark"]],
        )
        self.loading_label.pack(side="left")

        # ===== RESULTS CARD =====
        results_card = ctk.CTkFrame(
            main_container,
            corner_radius=16,
            fg_color=[COLORS["card_light"], COLORS["card_dark"]],
            border_width=1,
            border_color=[COLORS["border_light"], COLORS["border_dark"]],
        )
        results_card.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        results_card.grid_rowconfigure(1, weight=1)
        results_card.grid_columnconfigure(0, weight=1)

        # Results header
        results_header = ctk.CTkFrame(results_card, fg_color="transparent")
        results_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 0))

        ctk.CTkLabel(
            results_header,
            text="Stock Information",
            font=("Segoe UI", 15, "bold"),
        ).pack(side="left")

        # Scrollable results area
        self.scrollable_frame = ctk.CTkScrollableFrame(
            results_card,
            corner_radius=12,
            fg_color="transparent",
        )
        self.scrollable_frame.grid(
            row=1, column=0, sticky="nsew", padx=16, pady=(8, 16)
        )
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Placeholder message
        self.info_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Enter a stock code above and click 'Get Price' to begin",
            font=("Segoe UI", 13),
            text_color=[COLORS["muted_light"], COLORS["muted_dark"]],
        )
        self.info_label.pack(pady=60)

        # ===== STATUS BAR =====
        status_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        status_frame.grid(row=3, column=0, sticky="ew", pady=(4, 0))
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=("Segoe UI", 10),
            text_color=[COLORS["muted_light"], COLORS["muted_dark"]],
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        self.time_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Segoe UI", 10),
            text_color=[COLORS["muted_light"], COLORS["muted_dark"]],
        )
        self.time_label.grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def toggle_theme(self) -> None:
        """Toggle between dark and light theme."""
        new_mode = self.theme_switch_var.get()
        ctk.set_appearance_mode(new_mode)

    # ------------------------------------------------------------------
    # Stock code formatting
    # ------------------------------------------------------------------

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
        if not code.endswith(".HK"):
            code += ".HK"
        return code

    # ------------------------------------------------------------------
    # Search & refresh
    # ------------------------------------------------------------------

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
        self.loading_label.configure(text="Loading...")
        self.status_label.configure(text="Fetching data...")

        # Stop any existing auto-refresh
        if self.refresh_timer_id:
            self.after_cancel(self.refresh_timer_id)
            self.refresh_timer_id = None
        self.auto_refresh_enabled = False

        # Run the fetch in a separate thread
        thread = threading.Thread(
            target=self._fetch_stock_data, args=(code,), daemon=True
        )
        thread.start()

    def refresh_stock(self) -> None:
        """Refresh the currently displayed stock data."""
        if self.current_stock_code:
            self.stock_code_entry.delete(0, "end")
            self.stock_code_entry.insert(
                0, self.current_stock_code.replace(".HK", "")
            )

            # Disable buttons and show loading indicator
            self.search_button.configure(state="disabled")
            self.refresh_button.configure(state="disabled")
            self.auto_refresh_button.configure(state="disabled")
            self.stock_code_entry.configure(state="disabled")
            self.loading_label.configure(text="Refreshing...")
            self.status_label.configure(text="Fetching data...")

            # Run the fetch in a separate thread
            thread = threading.Thread(
                target=self._fetch_stock_data,
                args=(self.current_stock_code.replace(".HK", ""),),
                daemon=True,
            )
            thread.start()

    # ------------------------------------------------------------------
    # Auto-refresh
    # ------------------------------------------------------------------

    def toggle_auto_refresh(self) -> None:
        """Toggle auto-refresh on/off."""
        self.auto_refresh_enabled = not self.auto_refresh_enabled

        if self.auto_refresh_enabled:
            self.auto_refresh_button.configure(
                fg_color=[COLORS["green"], COLORS["green_dark"]],
                hover_color=[COLORS["green_dark"], COLORS["green"]],
                text="Auto: ON",
                text_color="#FFFFFF",
            )
            self.status_label.configure(
                text="Auto-refresh enabled (every 3 seconds)"
            )
            self._schedule_auto_refresh()
        else:
            self.auto_refresh_button.configure(
                fg_color=["#E2E8F0", "#334155"],
                hover_color=["#CBD5E1", "#475569"],
                text="Auto Refresh",
                text_color=["#334155", "#E2E8F0"],
            )
            self.status_label.configure(text="Auto-refresh disabled")
            if self.refresh_timer_id:
                self.after_cancel(self.refresh_timer_id)
                self.refresh_timer_id = None

    def _schedule_auto_refresh(self) -> None:
        """Schedule the next auto-refresh after 3 seconds."""
        if self.auto_refresh_enabled and self.current_stock_code:
            self.refresh_timer_id = self.after(
                self.refresh_interval, self._auto_refresh
            )

    def _auto_refresh(self) -> None:
        """Perform auto-refresh of stock data."""
        if self.auto_refresh_enabled and self.current_stock_code:
            self.loading_label.configure(text="Auto-refreshing...")

            thread = threading.Thread(
                target=self._fetch_stock_data,
                args=(self.current_stock_code.replace(".HK", ""),),
                daemon=True,
            )
            thread.start()

    # ------------------------------------------------------------------
    # Data fetching (background thread)
    # ------------------------------------------------------------------

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
            if not info or "shortName" not in info:
                self.after(
                    0,
                    self.show_error,
                    f"Stock code '{code}' not found or invalid",
                )
                return

            # Extract relevant information
            stock_data = {
                "shortName": info.get("shortName", "N/A"),
                "currentPrice": info.get("currentPrice", "N/A"),
                "regularMarketPrice": info.get("regularMarketPrice", "N/A"),
                "regularMarketPreviousClose": info.get(
                    "regularMarketPreviousClose", "N/A"
                ),
                "regularMarketChange": info.get("regularMarketChange", "N/A"),
                "regularMarketChangePercent": info.get(
                    "regularMarketChangePercent", "N/A"
                ),
                "regularMarketVolume": info.get("regularMarketVolume", "N/A"),
                "regularMarketDayHigh": info.get(
                    "regularMarketDayHigh", "N/A"
                ),
                "regularMarketDayLow": info.get("regularMarketDayLow", "N/A"),
            }

            self.current_stock_code = formatted_code
            self.current_data = stock_data

            # Update UI in main thread
            self.after(
                0, self._display_stock_data, formatted_code, stock_data
            )

        except Exception as e:
            error_msg = str(e)
            self.after(0, self.show_error, f"Error: {error_msg}")
        finally:
            # Re-enable buttons in main thread
            self.after(0, self._enable_buttons)
            # Schedule next auto-refresh if enabled
            if self.auto_refresh_enabled:
                self.after(0, self._schedule_auto_refresh)

    # ------------------------------------------------------------------
    # Display results
    # ------------------------------------------------------------------

    def _display_stock_data(self, code: str, data: Dict[str, Any]) -> None:
        """Display fetched stock data in a modern card-based layout."""
        # Clear previous widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # ---------- Stock name ----------
        name_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=data["shortName"],
            font=("Segoe UI", 20, "bold"),
            anchor="w",
        )
        name_label.pack(fill="x", pady=(4, 0))

        code_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=code,
            font=("Segoe UI", 12),
            text_color=[COLORS["muted_light"], COLORS["muted_dark"]],
            anchor="w",
        )
        code_label.pack(fill="x", pady=(0, 16))

        # ---------- Price + Change hero row ----------
        hero_frame = ctk.CTkFrame(
            self.scrollable_frame,
            corner_radius=14,
            fg_color=[COLORS["surface_light"], COLORS["surface_dark"]],
            border_width=1,
            border_color=[COLORS["border_light"], COLORS["border_dark"]],
        )
        hero_frame.pack(fill="x", pady=(0, 20))

        hero_inner = ctk.CTkFrame(hero_frame, fg_color="transparent")
        hero_inner.pack(fill="x", padx=24, pady=24)

        # Current price
        current_price = data.get("currentPrice") or data.get(
            "regularMarketPrice", "N/A"
        )

        price_col = ctk.CTkFrame(hero_inner, fg_color="transparent")
        price_col.pack(side="left", padx=(0, 48))

        ctk.CTkLabel(
            price_col,
            text="CURRENT PRICE",
            font=("Segoe UI", 10, "bold"),
            text_color=[COLORS["muted_light"], COLORS["muted_dark"]],
            anchor="w",
        ).pack(anchor="w")

        if isinstance(current_price, (int, float)):
            price_text = f"HK$ {current_price:,.2f}"
        else:
            price_text = str(current_price)

        ctk.CTkLabel(
            price_col,
            text=price_text,
            font=("Segoe UI", 32, "bold"),
            text_color=COLORS["accent"],
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        # Change
        change_pct = data.get("regularMarketChangePercent", "N/A")
        change = data.get("regularMarketChange", "N/A")

        change_col = ctk.CTkFrame(hero_inner, fg_color="transparent")
        change_col.pack(side="left")

        ctk.CTkLabel(
            change_col,
            text="CHANGE",
            font=("Segoe UI", 10, "bold"),
            text_color=[COLORS["muted_light"], COLORS["muted_dark"]],
            anchor="w",
        ).pack(anchor="w")

        if isinstance(change_pct, (int, float)):
            is_positive = change_pct >= 0
            change_color = COLORS["green"] if is_positive else COLORS["red"]
            arrow = "\u25B2" if is_positive else "\u25BC"
            sign = "+" if is_positive else ""
            pct_text = f"{sign}{change_pct:.2f}%"
            abs_text = (
                f"{sign}{change:.2f}"
                if isinstance(change, (int, float))
                else str(change)
            )

            change_row = ctk.CTkFrame(change_col, fg_color="transparent")
            change_row.pack(anchor="w", pady=(4, 0))

            ctk.CTkLabel(
                change_row,
                text=f"{arrow} {pct_text}",
                font=("Segoe UI", 22, "bold"),
                text_color=change_color,
            ).pack(side="left")

            ctk.CTkLabel(
                change_row,
                text=f"  ({abs_text})",
                font=("Segoe UI", 14),
                text_color=change_color,
            ).pack(side="left", pady=(4, 0))
        else:
            ctk.CTkLabel(
                change_col,
                text=str(change_pct),
                font=("Segoe UI", 22, "bold"),
            ).pack(anchor="w", pady=(4, 0))

        # ---------- Detail metric cards ----------
        details = [
            ("Previous Close", data.get("regularMarketPreviousClose", "N/A")),
            ("Day High", data.get("regularMarketDayHigh", "N/A")),
            ("Day Low", data.get("regularMarketDayLow", "N/A")),
            ("Volume", data.get("regularMarketVolume", "N/A")),
        ]

        cards_frame = ctk.CTkFrame(
            self.scrollable_frame, fg_color="transparent"
        )
        cards_frame.pack(fill="x")
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="metric")

        for idx, (label, value) in enumerate(details):
            card = ctk.CTkFrame(
                cards_frame,
                corner_radius=12,
                fg_color=[COLORS["surface_light"], COLORS["surface_dark"]],
                border_width=1,
                border_color=[COLORS["border_light"], COLORS["border_dark"]],
            )
            card.grid(row=0, column=idx, padx=4, pady=4, sticky="nsew")

            card_inner = ctk.CTkFrame(card, fg_color="transparent")
            card_inner.pack(padx=16, pady=16, fill="both", expand=True)

            ctk.CTkLabel(
                card_inner,
                text=label.upper(),
                font=("Segoe UI", 9, "bold"),
                text_color=[COLORS["muted_light"], COLORS["muted_dark"]],
                anchor="w",
            ).pack(anchor="w")

            # Format value
            if label == "Volume" and isinstance(value, (int, float)):
                if value >= 1_000_000:
                    formatted_value = f"{value / 1_000_000:,.2f}M"
                elif value >= 1_000:
                    formatted_value = f"{value / 1_000:,.2f}K"
                else:
                    formatted_value = str(int(value))
            elif isinstance(value, (int, float)) and label != "Volume":
                formatted_value = f"HK$ {value:,.2f}"
            else:
                formatted_value = str(value)

            ctk.CTkLabel(
                card_inner,
                text=formatted_value,
                font=("Segoe UI", 16, "bold"),
                anchor="w",
            ).pack(anchor="w", pady=(6, 0))

        # Update status and timestamp
        auto_status = (
            " (Auto-refresh: ON)" if self.auto_refresh_enabled else ""
        )
        self.status_label.configure(
            text=f"Stock data updated \u2014 {code}{auto_status}"
        )
        self._update_timestamp()
        self.loading_label.configure(text="")

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

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

        # Error container
        error_frame = ctk.CTkFrame(
            self.scrollable_frame, fg_color="transparent"
        )
        error_frame.pack(pady=50)

        ctk.CTkLabel(
            error_frame,
            text="\u26A0",
            font=("Segoe UI", 44),
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            error_frame,
            text=error_msg,
            font=("Segoe UI", 13),
            text_color=COLORS["red"],
        ).pack()

        self.status_label.configure(text=f"Error: {error_msg}")
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
