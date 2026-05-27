import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict

class StockFetcher:
    """Fetch stock price data from eNet Hong Kong"""
    
    BASE_URL = "https://www.etnet.com.hk/www/tc/stocks/realtime/quote.php"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    @staticmethod
    def fetch_stock_data(code: str) -> Optional[Dict]:
        """
        Fetch stock data for given code
        
        Args:
            code: Stock code (e.g., "0001" for HSBC)
            
        Returns:
            Dictionary with stock data or None if fetch fails
        """
        try:
            params = {'code': code.strip()}
            response = requests.get(
                StockFetcher.BASE_URL,
                params=params,
                headers=StockFetcher.HEADERS,
                timeout=10
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Parse the page to extract stock information
            # You may need to adjust selectors based on actual page structure
            stock_data = {
                'code': code,
                'status': 'success',
                'url': response.url
            }
            
            return stock_data
            
        except requests.RequestException as e:
            print(f"Error fetching data for {code}: {e}")
            return {
                'code': code,
                'status': 'error',
                'error': str(e)
            }
