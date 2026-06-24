"""
Price Fetcher Service — AgriMarket Uganda

Fetches Uganda food prices from HDX (Humanitarian Data Exchange / OCHA),
which publishes the WFP VAM food price dataset in a stable, free, keyless CSV.

CSV columns: date, admin1, admin2, market, category, commodity, unit,
             priceflag, pricetype, currency, price, usdprice
"""

import csv
import io
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)

_FALLBACK_USD_TO_UGX = 3700

# HDX package endpoint — stable, no API key required
HDX_PACKAGE_URL = (
    "https://data.humdata.org/api/3/action/package_show"
    "?id=wfp-food-prices-for-uganda"
)

# Mapping of HDX/WFP commodity names → normalised display names
COMMODITY_DISPLAY = {
    'maize (white)': 'Maize',
    'maize': 'Maize',
    'beans (dry)': 'Beans',
    'beans': 'Beans',
    'rice (milled)': 'Rice',
    'rice': 'Rice',
    'cassava (fresh)': 'Cassava',
    'cassava': 'Cassava',
    'sweet potatoes': 'Sweet Potato',
    'potatoes (irish)': 'Irish Potato',
    'groundnuts (shelled)': 'Groundnuts',
    'groundnuts': 'Groundnuts',
    'sorghum': 'Sorghum',
    'millet (finger)': 'Millet',
    'millet': 'Millet',
    'tomatoes': 'Tomatoes',
    'onions': 'Onions',
    'cabbage': 'Cabbage',
    'bananas (matoke)': 'Matooke',
    'bananas': 'Bananas',
    'coffee (arabica)': 'Coffee',
    'sugar': 'Sugar',
    'salt': 'Salt',
    'oil (vegetable)': 'Cooking Oil',
    'wheat flour': 'Wheat Flour',
    'milk (fresh)': 'Fresh Milk',
    'eggs': 'Eggs',
    'beef': 'Beef',
    'fish (fresh)': 'Fresh Fish',
    'pork': 'Pork',
    'chicken': 'Chicken',
}


def get_usd_to_ugx_rate() -> float:
    """
    Fetch current USD→UGX exchange rate from open.er-api.com (no key required).
    Returns fallback constant if the request fails.
    """
    try:
        resp = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=5,
        )
        resp.raise_for_status()
        rate = resp.json().get("rates", {}).get("UGX")
        if rate:
            logger.info("Live USD→UGX rate: %s", rate)
            return float(rate)
        logger.warning("UGX rate missing from API response, using fallback.")
    except Exception as exc:
        logger.warning("Exchange rate fetch failed (%s). Using fallback %s.", exc, _FALLBACK_USD_TO_UGX)
    return _FALLBACK_USD_TO_UGX


def _get_hdx_csv_url() -> Optional[str]:
    """
    Query HDX CKAN API to get the download URL for the Uganda food prices CSV.
    Returns the URL string or None if it cannot be determined.
    """
    try:
        resp = requests.get(HDX_PACKAGE_URL, timeout=10)
        resp.raise_for_status()
        resources = resp.json().get("result", {}).get("resources", [])
        for r in resources:
            if r.get("format", "").upper() == "CSV":
                url = r.get("download_url") or r.get("url")
                if url:
                    logger.info("HDX CSV URL: %s", url)
                    return url
    except Exception as exc:
        logger.error("Could not retrieve HDX CSV URL: %s", exc)
    return None


def fetch_hdx_prices(days_back: int = 60) -> List[Dict]:
    """
    Download and parse the WFP Uganda food prices CSV from HDX.

    Returns a list of normalised price dicts:
        product_name, price (Decimal, UGX), unit, market_location,
        district, date_recorded, source, currency
    """
    csv_url = _get_hdx_csv_url()
    if not csv_url:
        logger.error("No HDX CSV URL found — skipping price fetch.")
        return []

    try:
        resp = requests.get(csv_url, timeout=30)
        resp.raise_for_status()
    except Exception as exc:
        logger.error("Failed to download HDX price CSV: %s", exc)
        return []

    cutoff = datetime.now().date() - timedelta(days=days_back)

    # Fetch exchange rate ONCE (outside any per-row loop)
    usd_to_ugx: Optional[float] = None

    results: List[Dict] = []
    try:
        reader = csv.DictReader(io.StringIO(resp.text))
        for row in reader:
            try:
                raw_date = row.get("date", "").strip()
                date_recorded = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                continue

            if date_recorded < cutoff:
                continue

            commodity = row.get("commodity", "").strip().lower()
            if not commodity:
                continue

            # Normalise commodity name
            display_name = COMMODITY_DISPLAY.get(commodity, commodity.title())

            # Price — prefer local currency column
            currency = row.get("currency", "UGX").strip().upper()
            raw_price = row.get("price", "").strip()
            if not raw_price:
                # Fall back to USD price and convert
                raw_price = row.get("usdprice", "").strip()
                currency = "USD"

            if not raw_price:
                continue

            try:
                price_float = float(raw_price)
            except ValueError:
                continue

            if currency == "USD":
                # Lazy-fetch rate only if we actually need it
                if usd_to_ugx is None:
                    usd_to_ugx = get_usd_to_ugx_rate()
                price_float = price_float * usd_to_ugx
                currency = "UGX"

            price = Decimal(str(price_float)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

            unit = row.get("unit", "kg").strip().lower()
            market = row.get("market", "").strip() or "Uganda"
            district = row.get("admin2", "").strip() or row.get("admin1", "").strip() or "Uganda"

            # Only include retail prices (ignore wholesale for farmer-facing display)
            price_type = row.get("pricetype", "").strip().lower()
            if price_type == "wholesale":
                continue

            results.append({
                "product_name": display_name,
                "price": price,
                "unit": unit,
                "market_location": market,
                "district": district,
                "date_recorded": date_recorded,
                "source": "HDX/WFP",
                "currency": "UGX",
            })

    except Exception as exc:
        logger.error("Error parsing HDX CSV: %s", exc)

    logger.info("HDX price fetch: %d records parsed (last %d days).", len(results), days_back)
    return results


def combine_price_sources(external_prices: List[Dict], crowdsourced_prices) -> List[Dict]:
    """
    Merge external (WFP/HDX) prices with crowdsourced farmer prices into a
    unified list, one entry per product. Aggregates multiple crowdsourced
    reports (avg/min/max/count) rather than discarding duplicates.

    Args:
        external_prices: list of dicts from fetch_hdx_prices() or DB query
        crowdsourced_prices: QuerySet of CrowdsourcedPrice

    Returns:
        List of dicts keyed by product name with both sources where available.
    """
    combined: Dict[str, Dict] = {}

    # --- External prices: keep the most recent entry per product ---
    for price in external_prices:
        key = price["product_name"].lower()
        existing = combined.get(key)
        if existing is None or price["date_recorded"] > existing.get("ext_date", price["date_recorded"]):
            combined[key] = {
                "product_name": price["product_name"],
                "ext_price": price["price"],
                "ext_date": price["date_recorded"],
                "ext_market": price.get("market_location", ""),
                "unit": price["unit"],
                "has_external": True,
                "has_crowdsourced": False,
                # Aligning template keys
                "has_wfp": True,
                "wfp_price": price["price"],
            }

    # --- Crowdsourced prices: aggregate all reports per product ---
    # Accumulate raw price values first, then compute stats
    cs_buckets: Dict[str, List[float]] = {}
    cs_meta: Dict[str, Dict] = {}

    for cs in crowdsourced_prices:
        key = cs.product_name.lower()
        if key not in cs_buckets:
            cs_buckets[key] = []
            cs_meta[key] = {
                "product_name": cs.product_name,
                "unit": cs.unit,
                "location": cs.location,
            }
        cs_buckets[key].append(float(cs.price))

    for key, prices_list in cs_buckets.items():
        avg = Decimal(str(sum(prices_list) / len(prices_list))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        lo = Decimal(str(min(prices_list)))
        hi = Decimal(str(max(prices_list)))
        meta = cs_meta[key]

        if key in combined:
            combined[key]["cs_avg"] = avg
            combined[key]["cs_min"] = lo
            combined[key]["cs_max"] = hi
            combined[key]["cs_count"] = len(prices_list)
            combined[key]["cs_location"] = meta["location"]
            combined[key]["has_crowdsourced"] = True
            # Aligning template keys
            combined[key]["crowdsourced_price"] = avg
        else:
            combined[key] = {
                "product_name": meta["product_name"],
                "cs_avg": avg,
                "cs_min": lo,
                "cs_max": hi,
                "cs_count": len(prices_list),
                "cs_location": meta["location"],
                "unit": meta["unit"],
                "has_external": False,
                "has_crowdsourced": True,
                # Aligning template keys
                "has_wfp": False,
                "crowdsourced_price": avg,
            }

    return sorted(combined.values(), key=lambda x: x["product_name"])
