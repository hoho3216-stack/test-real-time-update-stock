# Hong Kong Stock Price Viewer

A simple Python desktop application for viewing real-time stock prices for Hong Kong stocks using a clean Tkinter interface.

## Features

✅ Clean and modern Tkinter GUI
✅ Search Hong Kong stocks by code (0005, 0700, 9988, etc.)
✅ Auto-format input with .HK suffix
✅ Display real-time stock information:
  - Stock name / company name
  - Current price
  - Price change and change percentage
  - Volume
  - Previous close
  - Day high / low

✅ Loading indicator while fetching data
✅ Error handling for invalid codes and network issues
✅ Refresh button to update current stock
✅ Status bar showing last updated time
✅ Resizable window with reasonable default size
✅ Threading to prevent UI freezing

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- yfinance

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hoho3216-stack/test-real-time-update-stock.git
cd test-real-time-update-stock
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python app.py
```

1. Enter a Hong Kong stock code (e.g., `0005` for HSTECH, `0700` for Tencent, `9988` for Alibaba)
2. Press Enter or click the "Get Price" button
3. View the stock information displayed
4. Click "Refresh" to update the current stock
5. Search for another stock by entering a new code

## Supported Stock Codes (Examples)

- 0001 - HSBC Holdings
- 0005 - HSTECH (Hang Seng Tech Index ETF)
- 0700 - Tencent
- 9988 - Alibaba (HK listed)
- 2800 - Tracker Fund of Hong Kong

## License

MIT

## Author

Created for tracking Hong Kong stock prices easily.
