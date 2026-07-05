# 5. Apps: Inputs & Weather

## 5.1 App: `inputs`

The `inputs` app allows `input_supplier` users to list agricultural supplies (seeds, fertilizers, equipment) and handles basic B2B or B2C ordering.

### Models
- **`InputCategory`**: `name`, `description`, `image`. (e.g., Seeds, Fertilizers).
- **`AgriculturalInput`**: 
  - `supplier`: FK to `User`.
  - `category`: FK to `InputCategory`.
  - `name`, `description`, `price`, `stock_quantity`.
  - `is_certified`: `BooleanField`. Crucial for trust (verifying authentic seeds).
- **`InputOrder`** & **`InputOrderItem`**: Mirrors the `marketplace` order system but specifically for inputs. Status flows: pending → processing → shipped → delivered.

### Views & URLs
- **`input_list`** (`/inputs/`): Displays all inputs.
- **`input_detail`** (`/inputs/<pk>/`): Details and order button.
- **`supplier_dashboard`** (`/inputs/dashboard/`): Management for suppliers.
- **`add_input`, `edit_input`**: CRUD operations.
- **`place_order`**: Creates `InputOrder`.

### Technical Debt / Gaps
- **Duplication**: The order logic in `inputs` is almost entirely duplicated from `orders`. A unified `Order` model with a `ContentType` framework or generic relations could significantly reduce this tech debt.

---

## 5.2 App: `weather`

The `weather` app is an essential utility for farmers, offering real-time weather data, forecasts, and AI-like advisory algorithms based on OpenWeather API.

### Models
- **`WeatherAlert`**:
  - `district`, `alert_type` (Heavy Rain, Drought, High Temp), `severity`.
  - `message`: Text of the alert.
  - `is_active`, `expires_at`.
- **`CropCalendar`**: Stores hardcoded planting/harvest windows. (Currently mostly bypassed in favor of the `FarmingAdvisor` service dictionary).

### Services: `farming_advisor.py`
This is a critical service file that dictates the "smart" aspects of the platform.
- **`FarmingAdvisor` Class**:
  - **Inputs**: District name, OpenWeather API key (from environment).
  - **Logic**:
    - **`get_current_weather`**: Hits `http://api.openweathermap.org/data/2.5/weather`. Translates HTTP responses into a structured dictionary (temp, humidity, rain volume).
    - **`get_planting_recommendations`**: Analyzes the current month against a hardcoded `CROP_SEASONS` dictionary (maize, beans, cassava, etc.). If it's planting season, and temperatures are optimal, and rain is forecasted within 3 days, it recommends planting.
    - **`get_spraying_advice`**: Checks current wind speed (< 15 km/h) and imminent rain. If rain is expected within hours, it advises *against* spraying chemicals to prevent runoff.
  - **Error Handling**: Wraps API calls in `try...except`. On failure, it gracefully returns `None` or empty lists to prevent 500 Server Errors on the dashboard.
  - **Gaps**: Harvest predictions are listed as a feature but rely purely on static `growth_days` math from the current date, not real historical planting dates from the farmer.

### Views & URLs
- **`weather_dashboard`** (`/weather/`): Shows current conditions, a 5-day forecast, and advisory cards.
- **`api_weather_data`** (`/weather/api/data/`): A JSON endpoint utilized by frontend widgets.
