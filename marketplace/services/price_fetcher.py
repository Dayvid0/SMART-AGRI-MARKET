"""
WFP (World Food Programme) Market Price Fetcher Service

This service fetches agricultural commodity prices from the WFP API
and combines them with local crowdsourced prices for Uganda markets.
"""

import requests
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WFPPriceFetcher:
    """
    Fetches market prices from WFP VAM (Vulnerability Analysis and Mapping) API
    """
    
    BASE_URL = "https://api.vam.wfp.org/dataviz/api"
    
    # Uganda country code in WFP system
    UGANDA_CODE = "UGA"
    
    # Mapping of common crop names to WFP commodity names
    COMMODITY_MAPPING = {
        'maize': 'Maize',
        'beans': 'Beans',
        'rice': 'Rice',
        'cassava': 'Cassava',
        'sweet potato': 'Sweet potato',
        'irish potato': 'Potato',
        'groundnuts': 'Groundnuts (Shelled)',
        'sorghum': 'Sorghum',
        'millet': 'Millet',
        'tomatoes': 'Tomatoes',
        'onions': 'Onions',
        'cabbage': 'Cabbage',
        'cooking banana': 'Cooking banana (green)',
        'bananas': 'Bananas',
        'coffee': 'Coffee',
        'tea': 'Tea',
        'sugar': 'Sugar',
        'salt': 'Salt',
        'cooking oil': 'Oil (vegetable)',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AgriMarket-Uganda/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_latest_prices(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch latest market prices from WFP API for Uganda
        
        Args:
            days_back: Number of days to look back for price data
            
        Returns:
            List of price dictionaries with standardized format
        """
        try:
            # WFP API endpoint for market prices
            endpoint = f"{self.BASE_URL}/MarketPrices/PriceMonthly"
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = {
                'CountryCode': self.UGANDA_CODE,
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d')
            }
            
            logger.info(f"Fetching WFP prices for Uganda from {start_date} to {end_date}")
            
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse and normalize the data
            normalized_prices = self._normalize_wfp_data(data)
            
            logger.info(f"Successfully fetched {len(normalized_prices)} price records from WFP")
            
            return normalized_prices
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching WFP prices: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in WFP price fetch: {e}")
            return []
    
    def _normalize_wfp_data(self, raw_data: Dict) -> List[Dict]:
        """
        Normalize WFP API response to our standard format
        
        Returns:
            List of dicts with keys: product_name, price, unit, market_location, 
            date_recorded, source, currency
        """
        normalized = []
        
        # WFP API returns data in different formats, handle accordingly
        if not raw_data or 'items' not in raw_data:
            return normalized
        
        for item in raw_data.get('items', []):
            try:
                # Extract relevant fields
                product_name = item.get('commodityName', '').strip()
                price = item.get('price')
                unit = item.get('unit', 'kg').lower()
                market = item.get('marketName', 'Uganda Market')
                date_str = item.get('date', '')
                
                # Skip if essential data is missing
                if not product_name or price is None:
                    continue
                
                # Parse date
                try:
                    date_recorded = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    date_recorded = datetime.now().date()
                
                # Convert price to UGX if needed (WFP might return USD)
                currency = item.get('currency', 'UGX')
                if currency == 'USD':
                    # Approximate conversion rate (should be updated regularly)
                    price = float(price) * 3700  # 1 USD ≈ 3700 UGX
                
                normalized.append({
                    'product_name': product_name,
                    'price': Decimal(str(price)),
                    'unit': unit,
                    'market_location': market,
                    'date_recorded': date_recorded,
                    'source': 'WFP API',
                    'currency': 'UGX'
                })
                
            except Exception as e:
                logger.warning(f"Error normalizing WFP item: {e}")
                continue
        
        return normalized
    
    def get_commodity_price(self, commodity_name: str) -> Optional[Dict]:
        """
        Get the latest price for a specific commodity
        
        Args:
            commodity_name: Name of the commodity (e.g., 'maize', 'beans')
            
        Returns:
            Price dictionary or None if not found
        """
        # Map to WFP commodity name
        wfp_name = self.COMMODITY_MAPPING.get(commodity_name.lower())
        
        if not wfp_name:
            logger.warning(f"No WFP mapping for commodity: {commodity_name}")
            return None
        
        # Fetch recent prices
        prices = self.fetch_latest_prices(days_back=7)
        
        # Find matching commodity
        for price in prices:
            if price['product_name'].lower() == wfp_name.lower():
                return price
        
        return None


def combine_price_sources(wfp_prices: List[Dict], crowdsourced_prices: List) -> List[Dict]:
    """
    Combine WFP API prices with crowdsourced farmer prices
    
    Prioritizes:
    1. Most recent data
    2. WFP data for reliability
    3. Crowdsourced data for local context
    
    Args:
        wfp_prices: List of WFP price dicts
        crowdsourced_prices: QuerySet of CrowdsourcedPrice objects
        
    Returns:
        Combined list of price data with source indicators
    """
    combined = {}
    
    # Add WFP prices
    for price in wfp_prices:
        key = price['product_name'].lower()
        combined[key] = {
            'product_name': price['product_name'],
            'wfp_price': price['price'],
            'wfp_date': price['date_recorded'],
            'market': price['market_location'],
            'unit': price['unit'],
            'has_wfp': True,
            'has_crowdsourced': False
        }
    
    # Add crowdsourced prices
    for cs_price in crowdsourced_prices:
        key = cs_price.product_name.lower()
        
        if key in combined:
            # Add to existing entry
            combined[key]['crowdsourced_price'] = cs_price.price
            combined[key]['crowdsourced_date'] = cs_price.date_reported
            combined[key]['has_crowdsourced'] = True
        else:
            # Create new entry
            combined[key] = {
                'product_name': cs_price.product_name,
                'crowdsourced_price': cs_price.price,
                'crowdsourced_date': cs_price.date_reported,
                'market': cs_price.location,
                'unit': cs_price.unit,
                'has_wfp': False,
                'has_crowdsourced': True
            }
    
    return list(combined.values())
