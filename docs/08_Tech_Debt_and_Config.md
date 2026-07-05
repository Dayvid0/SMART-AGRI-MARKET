# 8. Technical Debt & Config (Known Gaps)

During the panel defense, it is highly likely that reviewers will ask about the limitations of the current prototype. Here is an exhaustive, code-level breakdown of the system's technical debt and missing features.

## 8.1 Critical Feature Gaps

### Missing Payment Gateway Integration
- **Location**: `orders/views.py` (Functions: `place_order`, `update_order_status`).
- **Gap**: The platform currently operates strictly on a "trust" or Cash-On-Delivery basis. When an order is placed, the `payment_status` is simply initialized as `pending`. There is no redirection to a payment gateway (like Flutterwave or MTN Mobile Money API), and no webhooks to securely confirm payment before shipping.

### Faked / Hardcoded Harvest Predictions
- **Location**: `weather/services/farming_advisor.py` (Lines 23–58).
- **Gap**: The Agricultural Advisory feature boasts harvest predictions, but the code reveals a static `CROP_SEASONS` dictionary. It calculates harvest dates based purely on a hardcoded `growth_days` integer (e.g., Maize = 90 days) added to the current date, rather than allowing farmers to log their actual planting dates in the database and tracking from there.

### Simplistic Transporter Matching
- **Location**: `orders/views.py` (Function: `delivery_detail`).
- **Gap**: The location-based matching for logistics does not use geospatial data (like PostGIS or GPS coordinates). It relies entirely on string matching. It checks if the `pickup_district` string exists within a comma-separated list in `TransporterProfile.coverage_districts`. A minor typo in registration breaks the matching entirely.

## 8.2 Hardcoded Data & Vulnerabilities

### Hardcoded Exchange Rates
- **Location**: `marketplace/services/price_fetcher.py` (Line 22).
- **Gap**: The system defines `_FALLBACK_USD_TO_UGX = 3700`. If the `open.er-api.com` exchange API goes down, the platform will silently fall back to an exchange rate that could be months or years out of date, heavily skewing the WFP price intelligence data.

### Missing Validation
- **Location**: `accounts/forms.py` (and `views.py` `register` function).
- **Gap**: There is very little backend validation on phone numbers or WhatsApp numbers. A user could enter alphabetic characters or international formats that break SMS gateway integrations later on.

## 8.3 Architecture & Config Debt (`config` App)

### No Automated Testing
- **Location**: `tests.py` files across all apps (e.g., `weather/tests.py`, `marketplace/tests.py`).
- **Gap**: All `tests.py` files are virtually empty (~60 bytes). There are zero unit tests or integration tests written for critical flows like order placement or price aggregation.

### SQLite in Production
- **Location**: `config/settings.py` (Lines 73-78).
- **Gap**: The system is currently running on SQLite (`django.db.backends.sqlite3`). While acceptable for a prototype, a multi-tenant marketplace with simultaneous transactions and order locking requires a concurrent relational database like PostgreSQL.

### Email Backend configuration
- **Location**: `config/settings.py` (Lines 125-128).
- **Gap**: The `EMAIL_BACKEND` defaults to the console (`django.core.mail.backends.console.EmailBackend`). Any password reset emails or notifications are currently just printed to the terminal running the server, rather than actually being delivered to users via SMTP.
