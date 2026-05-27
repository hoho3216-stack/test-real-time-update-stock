# eNet Stock Real-Time Quote Desktop App

A desktop application to fetch and display real-time stock prices from [eNet Hong Kong](https://www.etnet.com.hk/).

## Features

- 🔍 Search stocks by code
- 📊 Real-time price updates from eNet
- 💻 Cross-platform desktop UI (Windows, macOS, Linux)
- ⚡ Lightweight and responsive

## Setup

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository
```bash
git clone https://github.com/hoho3216-stack/test-real-time-update-stock.git
cd test-real-time-update-stock
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

## Usage

1. Enter a stock code (e.g., `0001` for HSBC)
2. Press Enter or click the "Search" button
3. The app will fetch data from eNet and display results

## Technical Details

- **Data Source**: https://www.etnet.com.hk/www/tc/stocks/realtime/quote.php
- **UI Framework**: PyQt5
- **Web Scraping**: BeautifulSoup4
- **HTTP Client**: requests

## Architecture

```
main.py              - Main application entry point
├── StockQuoteApp    - Main window and UI
└── StockFetcherThread - Background worker thread

stock_fetcher.py     - Data fetching logic
└── StockFetcher     - Handles eNet API requests
```

## TODO

- [ ] Parse and extract specific price fields from eNet
- [ ] Add price history/charting
- [ ] Implement data caching
- [ ] Add favorites/watchlist
- [ ] Create executable installers

## License

MIT

## Contributing

Feel free to submit issues and pull requests.
