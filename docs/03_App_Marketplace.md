# 3. App: Marketplace

The `marketplace` app is the core of the platform. It handles product listings by farmers, categorization, price tracking (crowdsourced + WFP HDX), farmer portfolios, and the review/reputation system.

## 3.1 Models

### Model: `Category`
- **`name`**: `CharField` (Unique). E.g., Vegetables, Cereals.
- **`description`**: `TextField`.
- **`image`**: `ImageField`. Visual representation on the frontend.

### Model: `Product`
- **Relationship**: `ForeignKey` to `accounts.User` (limit to 'farmer', 'business'), `ForeignKey` to `Category`.
- **`name`, `description`**: Core product details.
- **`price`**: `DecimalField`. Price per unit in UGX.
- **`quantity`, `unit`**: e.g., 50 kg, 10 bunches.
- **`status`**: `CharField` (available, out_of_stock, discontinued).
- **`is_group_buy_eligible`**: `BooleanField`. Indicates if consumers can pool resources to buy this wholesale.
- **`minimum_group_buy`**: `IntegerField`. Threshold for triggering a group buy.

### Model: `MarketPrice` (Legacy/Internal) & `ExternalMarketPrice` (WFP/HDX)
- **`ExternalMarketPrice`**: Caches daily prices retrieved from HDX.
  - `commodity_name`, `market_location`, `price_ugx`, `date_recorded`.
- **`CrowdsourcedPrice`**: Allows farmers to self-report local prices.
  - `product_name`, `price`, `location`, `date_reported`, `reported_by` (FK to User).

### Model: `Review` & `ReviewResponse`
- **`Review`**: Links `reviewer` (Consumer) and `farmer` (Farmer).
  - `rating` (1-5), `comment`.
- **`ReviewResponse`**: Allows farmers to reply to reviews. `OneToOne` with `Review`.

## 3.2 Views

### Browsing & Homepage
- **`home`**: (URL: `/`) Renders `landing.html` for unauthenticated visitors, and the dashboard (`marketplace/home.html`) for logged-in users, featuring stats, recent orders, and HDX price previews.
- **`product_list`**: (URL: `/products/`) Displays available products with filtering by category, search term, and district.
- **`product_detail`**: (URL: `/products/<pk>/`) Shows product info, farmer rating, and 'Add to Cart' / 'Order' actions.
- **`district_list` / `farmer_list`**: (URLs: `/districts/`, `/farmers/`) Directory views.

### Price Intelligence
- **`market_prices`**: (URL: `/market-prices/`) Core aggregation view. Calls `combine_price_sources(external, crowdsourced)` to merge WFP HDX data with local user-submitted prices. Displays trend indicators (up/down).
- **`price_tracker`**: (URL: `/price-tracker/`) Renders a line chart for historical prices using JSON payloads.
- **`report_price`**: (URL: `/report-price/`) Allows farmers to submit a `CrowdsourcedPrice`. Requires `@login_required` and `user_type == 'farmer'`.

### Farmer Dashboard & Product Management
- **`farmer_dashboard`**: (URL: `/dashboard/`) Farmer-specific view showing total sales, active listings, and pending orders.
- **`add_product`, `edit_product`, `delete_product`**: Standard CRUD operations for the `Product` model. Enforces that the logged-in user is the owner of the product.

### Reviews
- **`create_review`**: (URL: `/reviews/create/<order_id>/`) Validates that the user actually purchased from the farmer before allowing a review.
- **`farmer_reviews`**: Lists all reviews for a farmer.
- **`add_response`**: Allows the farmer to reply.

## 3.3 Services & Utilities

### `price_fetcher.py` (Line-by-line explanation)
- **Inputs**: Number of days back to look for prices (default 60).
- **Outputs**: A normalized list of dictionary objects merging external and crowdsourced prices.
- **Logic**:
  1. Calls `_get_hdx_csv_url()` to hit the CKAN API and find the latest WFP CSV.
  2. Downloads the CSV into memory (`io.StringIO`).
  3. Iterates over rows. If currency is USD, it fetches the real-time exchange rate from `open.er-api.com` (caching it for the loop).
  4. Filters out wholesale prices (keeping retail).
  5. The `combine_price_sources()` function then loops through local `CrowdsourcedPrice` objects, groups them by product, calculates `avg/min/max`, and merges this dictionary with the HDX dictionary.
- **Error Handling**: Uses broad `except Exception` blocks to catch network or parsing errors, logging them and returning empty lists or using fallback rates (e.g., `_FALLBACK_USD_TO_UGX = 3700`) so the UI never crashes.

## 3.4 URLs
- Browsing: `/`, `/products/`, `/products/<pk>/`
- Prices: `/market-prices/`, `/price-tracker/`, `/report-price/`
- Management: `/dashboard/`, `/products/add/`, `/products/<pk>/edit/`, `/products/<pk>/delete/`
- Reviews: `/reviews/create/<order_id>/`, `/reviews/farmer/<farmer_id>/`, `/reviews/response/<review_id>/`
