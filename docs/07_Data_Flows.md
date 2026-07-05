# 7. Data Flow Narratives

To truly understand how Smart Agri Market operates, it helps to trace full user journeys end-to-end through the code.

## Flow 1: Farmer Lists a Product
1. **Trigger**: Farmer logs in and clicks "Add Product" on their dashboard.
2. **View**: `marketplace.views.add_product` is called.
3. **Template**: Renders `marketplace/product_form.html`.
4. **Action**: Farmer fills out name, price, quantity, category, and uploads an image, then submits (POST).
5. **View Logic**: `add_product` validates the data. It forcibly assigns `request.user` to the `product.farmer` field so a farmer cannot create a listing under someone else's name.
6. **Database**: A new `Product` row is inserted into the SQLite database.
7. **Return**: Redirects back to `marketplace:farmer_dashboard`, where the new product now appears in the active listings query.

## Flow 2: Consumer Places an Order & Transporter Claims Delivery
1. **Trigger**: Consumer views a product (`marketplace.views.product_detail`) and clicks "Order".
2. **View**: `orders.views.place_order` intercepts the POST request.
3. **Database (Order)**: Creates an `Order` (status: 'pending') and an `OrderItem` (locking in the `price_at_time`).
4. **Trigger**: The Farmer logs in, sees the order, and clicks "Request Delivery".
5. **View**: `orders.views.request_delivery` handles the POST.
6. **Database (Delivery)**: Creates a `DeliveryRequest` with `pickup_district` and `delivery_district` and status 'open'.
7. **Matching**: When a Transporter logs in and views `orders.views.delivery_detail`, the view loops through `TransporterProfile` objects. If the transporter's `coverage_districts` array contains the pickup or delivery district, they see an "Accept Delivery" button.
8. **View**: Transporter clicks "Accept". `orders.views.accept_delivery` is called.
9. **Database Update**: The `DeliveryRequest.transporter` field is set to `request.user` (the transporter), and status changes to 'accepted'.

## Flow 3: Price Intelligence Page Loads
1. **Trigger**: User navigates to `/market-prices/`.
2. **View**: `marketplace.views.market_prices` is invoked.
3. **Query (Local)**: Fetches `CrowdsourcedPrice.objects.all()` and `ExternalMarketPrice.objects.filter(is_active=True)`.
4. **Service**: Calls `combine_price_sources(external, crowdsourced)` in `marketplace/services/price_fetcher.py`.
5. **Logic**: 
   - Loops over external prices, extracting the latest WFP price per commodity.
   - Loops over crowdsourced prices, grouping them by `product_name`.
   - Computes the average, min, and max for crowdsourced reports.
   - Merges them into a unified dictionary structure.
6. **Template**: Passes the combined dictionary to `marketplace/market_prices.html`, which renders the comparison tables and trend arrows.

## Flow 4: Weather Advisory Generation
1. **Trigger**: Farmer navigates to `/weather/`.
2. **View**: `weather.views.weather_dashboard` is invoked.
3. **Service**: Instantiates `FarmingAdvisor()`.
4. **API Call**: Calls `OpenWeatherMap` via `requests.get()` using the farmer's district coordinates.
5. **Algorithm**: 
   - Receives JSON payload with temp, humidity, and 5-day forecast.
   - Passes data into `get_planting_recommendations()`.
   - Checks the current date against hardcoded `CROP_SEASONS`. If it's planting season (e.g., March for Maize), and rain is forecasted, it appends a "Plant Now" advisory.
   - Passes data into `get_spraying_advice()`. If rain is imminent, appends a "Do NOT spray" advisory.
6. **Template**: Renders `weather/dashboard.html` with the dynamically generated advisories.
