# 1. Architecture, Integrations & Database Schema
## 1.1 High-Level Architecture
Smart Agri Market employs a standard **Three-Tier Architecture** built on the Django framework (MVT - Model, View, Template):
- **Presentation Tier (Templates & Static)**: HTML, CSS (Inter font, FontAwesome), and JavaScript. Views are rendered dynamically using Django's template engine.
- **Application Tier (Django Views & Services)**: Business logic lies in `views.py` and dedicated service files (e.g., `price_fetcher.py`, `openweather.py`). Controllers route HTTP requests to appropriate handlers.
- **Data Tier (SQLite / ORM)**: Data is persistently stored using SQLite (via Django's ORM) with relational links between accounts, marketplace items, and orders.

## 1.2 External Integrations
### WFP/HDX Price Intelligence
- **Source**: Humanitarian Data Exchange (HDX) WFP Food Prices dataset for Uganda.
- **Auth/Access**: Open/Keyless CSV endpoint.
- **Execution**: Handled by `marketplace/services/price_fetcher.py`. Fetches the CKAN package to locate the CSV, downloads it, and parses prices. Applies a fallback USD to UGX exchange rate if needed via `open.er-api.com`.
- **Fallback**: If HDX is down, the system relies on `CrowdsourcedPrice` local database entries.

### OpenWeather API (Agricultural Advisory)
- **Source**: OpenWeatherMap API.
- **Auth/Access**: Authenticated via `WEATHER_API_KEY` environment variable.
- **Execution**: Handled by `weather/services/farming_advisor.py`. Fetches current and forecast data based on district coordinates.
- **Fallback**: If the API fails, the system logs the error and gracefully returns an empty context to the template, preventing site crashes.

## 1.3 Database Schema (ERD)
Below is the exhaustive, automatically extracted database schema across all registered applications.

### App: `accounts`
#### Table: `accounts_user` (Model: `User`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `logentry` | ManyToOneRel | Null | → `django_admin_log` |
| `farmer_profile` | OneToOneRel | Null | → `accounts_farmerprofile` |
| `supplier_profile` | OneToOneRel | Null | → `accounts_inputsupplierprofile` |
| `transporter_profile` | OneToOneRel | Null | → `accounts_transporterprofile` |
| `verification_request` | OneToOneRel | Null | → `accounts_verificationrequest` |
| `verifications_reviewed` | ManyToOneRel | Null | → `accounts_verificationrequest` |
| `products` | ManyToOneRel | Null | → `marketplace_product` |
| `reported_prices` | ManyToOneRel | Null | → `marketplace_crowdsourcedprice` |
| `reviews_given` | ManyToOneRel | Null | → `marketplace_review` |
| `reviews_received` | ManyToOneRel | Null | → `marketplace_review` |
| `orders_placed` | ManyToOneRel | Null | → `orders_order` |
| `orders_received` | ManyToOneRel | Null | → `orders_order` |
| `assigned_deliveries` | ManyToOneRel | Null | → `orders_deliveryrequest` |
| `inputs` | ManyToOneRel | Null | → `inputs_agriculturalinput` |
| `organized_pools` | ManyToOneRel | Null | → `inputs_groupbuypool` |
| `groupbuyparticipant` | ManyToOneRel | Null | → `inputs_groupbuyparticipant` |
| `submitted_news` | ManyToOneRel | Null | → `news_agrinews` |
| `published_news` | ManyToOneRel | Null | → `news_agrinews` |
| `notifications` | ManyToOneRel | Null | → `notifications_notification` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `password` | CharField | - |  |
| `last_login` | DateTimeField | Null, Blank |  |
| `is_superuser` | BooleanField | - |  (Designates that this user has all permissions without explicitly assigning them.) |
| `username` | CharField | Unique |  (Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.) |
| `first_name` | CharField | Blank |  |
| `last_name` | CharField | Blank |  |
| `email` | EmailField | Blank |  |
| `is_staff` | BooleanField | - |  (Designates whether the user can log into this admin site.) |
| `is_active` | BooleanField | - |  (Designates whether this user should be treated as active. Unselect this instead of deleting accounts.) |
| `date_joined` | DateTimeField | - |  |
| `user_type` | CharField | - |  |
| `phone` | CharField | Blank |  |
| `whatsapp_number` | CharField | Blank |  |
| `location` | CharField | - |  |
| `address` | TextField | Blank |  |
| `profile_picture` | ImageField | Null, Blank |  |
| `is_verified` | BooleanField | - |  |
| `created_at` | DateTimeField | Blank |  |
| `district` | CharField | Blank |  |
| `specialization` | CharField | Blank |  |
| `first_login` | BooleanField | - |  |
| `groups` | ManyToManyField | Blank | → `auth_group` (The groups this user belongs to. A user will get all permissions granted to each of their groups.) |
| `user_permissions` | ManyToManyField | Blank | → `auth_permission` (Specific permissions for this user.) |

#### Table: `accounts_farmerprofile` (Model: `FarmerProfile`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `user` | OneToOneField | Unique | → `accounts_user` |
| `farm_name` | CharField | - |  |
| `farm_size` | DecimalField | - |  (Farm size in acres) |
| `specialization` | CharField | - |  |
| `rating_average` | DecimalField | - |  |
| `total_sales` | IntegerField | - |  |

#### Table: `accounts_inputsupplierprofile` (Model: `InputSupplierProfile`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `user` | OneToOneField | Unique | → `accounts_user` |
| `company_name` | CharField | - |  |
| `business_license` | CharField | Blank |  |
| `specialization` | CharField | - |  |
| `rating_average` | DecimalField | - |  |

#### Table: `accounts_transporterprofile` (Model: `TransporterProfile`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `user` | OneToOneField | Unique | → `accounts_user` |
| `vehicle_type` | CharField | - |  |
| `vehicle_registration` | CharField | Blank |  (Number plate e.g. UAA 123B) |
| `capacity_kg` | DecimalField | - |  (Maximum load capacity in kg) |
| `coverage_districts` | TextField | - |  (Comma-separated districts covered e.g. Kampala,Wakiso,Mukono) |
| `rating_average` | DecimalField | - |  |
| `total_deliveries` | IntegerField | - |  |

#### Table: `accounts_verificationrequest` (Model: `VerificationRequest`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `user` | OneToOneField | Unique | → `accounts_user` |
| `national_id_image` | ImageField | Null, Blank |  (National ID or passport scan) |
| `farm_or_business_photo` | ImageField | Null, Blank |  (Photo of farm, business premises, or vehicle) |
| `business_reg_number` | CharField | Blank |  (Business registration number (if applicable)) |
| `notes` | TextField | Blank |  (Additional context from the applicant) |
| `status` | CharField | - |  |
| `rejection_reason` | TextField | Blank |  (Reason for rejection (shown to user)) |
| `reviewed_by` | ForeignKey | Null, Blank | → `accounts_user` |
| `submitted_at` | DateTimeField | Blank |  |
| `reviewed_at` | DateTimeField | Null, Blank |  |

### App: `marketplace`
#### Table: `marketplace_category` (Model: `Category`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `products` | ManyToOneRel | Null | → `marketplace_product` |
| `market_prices` | ManyToOneRel | Null | → `marketplace_marketprice` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `name` | CharField | Unique |  (Category name (e.g., Vegetables, Fruits)) |
| `description` | TextField | Blank |  (Description of this category) |
| `image` | ImageField | Null, Blank |  (Category icon/image) |
| `created_at` | DateTimeField | Blank |  |

#### Table: `marketplace_product` (Model: `Product`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `orderitem` | ManyToOneRel | Null | → `orders_orderitem` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `farmer` | ForeignKey | - | → `accounts_user` (Farmer or business user who listed this product) |
| `category` | ForeignKey | Null | → `marketplace_category` |
| `name` | CharField | - |  (Product name (e.g., Fresh Matooke)) |
| `description` | TextField | - |  (Detailed description of the product) |
| `price` | DecimalField | - |  (Price per unit in UGX) |
| `quantity` | IntegerField | - |  (Available quantity) |
| `unit` | CharField | - |  |
| `location` | CharField | - |  (Where product is located (district/city)) |
| `image` | ImageField | Null, Blank |  (Main product image) |
| `image2` | ImageField | Null, Blank |  (Additional image) |
| `image3` | ImageField | Null, Blank |  (Additional image) |
| `is_urgent` | BooleanField | - |  (Mark as urgent sale (reduces post-harvest losses)) |
| `urgent_discount` | IntegerField | - |  (Discount percentage for urgent sales (0-50%)) |
| `harvest_date` | DateField | Null, Blank |  (When was this harvested) |
| `status` | CharField | - |  |
| `created_at` | DateTimeField | Blank |  |
| `updated_at` | DateTimeField | Blank |  |

#### Table: `marketplace_marketprice` (Model: `MarketPrice`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `product_name` | CharField | - |  (Product name (e.g., Maize, Coffee, Matooke)) |
| `category` | ForeignKey | - | → `marketplace_category` |
| `market_location` | CharField | - |  (Market location (e.g., Owino Market, Nakasero)) |
| `min_price` | DecimalField | - |  (Minimum price in UGX) |
| `max_price` | DecimalField | - |  (Maximum price in UGX) |
| `average_price` | DecimalField | - |  (Average market price in UGX) |
| `unit` | CharField | - |  (Unit of measurement) |
| `date_recorded` | DateField | Blank |  (Date when price was recorded) |
| `source` | CharField | - |  (Source of price information) |

#### Table: `marketplace_externalmarketprice` (Model: `ExternalMarketPrice`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `product_name` | CharField | - |  (Product/commodity name) |
| `price` | DecimalField | - |  (Price in UGX) |
| `unit` | CharField | - |  (Unit of measurement) |
| `market_location` | CharField | - |  (Market or region) |
| `source` | CharField | - |  (Data source) |
| `date_recorded` | DateField | - |  (Date when price was recorded) |
| `fetched_at` | DateTimeField | Blank |  (When we fetched this data) |
| `is_active` | BooleanField | - |  (Whether this price is still current) |
| `currency` | CharField | - |  |
| `raw_data` | JSONField | Null, Blank |  (Original API response for reference) |

#### Table: `marketplace_crowdsourcedprice` (Model: `CrowdsourcedPrice`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `reporter` | ForeignKey | - | → `accounts_user` |
| `product_name` | CharField | - |  |
| `price` | DecimalField | - |  |
| `unit` | CharField | - |  |
| `buyer_type` | CharField | - |  |
| `location` | CharField | - |  |
| `market_name` | CharField | Blank |  |
| `date_reported` | DateField | Blank |  |
| `is_verified` | BooleanField | - |  |
| `notes` | TextField | Blank |  (Additional context) |

#### Table: `marketplace_review` (Model: `Review`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `response` | OneToOneRel | Null | → `marketplace_reviewresponse` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `reviewer` | ForeignKey | - | → `accounts_user` (User who wrote the review) |
| `farmer` | ForeignKey | - | → `accounts_user` (Farmer being reviewed) |
| `order` | OneToOneField | Unique | → `orders_order` (Order this review is for) |
| `rating` | IntegerField | - |  (Rating from 1 to 5 stars) |
| `comment` | TextField | - |  (Review comment) |
| `product_quality` | IntegerField | - |  (Quality of products (1-5)) |
| `communication` | IntegerField | - |  (Communication quality (1-5)) |
| `delivery_speed` | IntegerField | - |  (Delivery speed (1-5)) |
| `would_recommend` | BooleanField | - |  (Would you recommend this farmer?) |
| `created_at` | DateTimeField | Blank |  |
| `updated_at` | DateTimeField | Blank |  |

#### Table: `marketplace_reviewresponse` (Model: `ReviewResponse`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `review` | OneToOneField | Unique | → `marketplace_review` |
| `response_text` | TextField | - |  (Farmer's response to the review) |
| `created_at` | DateTimeField | Blank |  |

### App: `orders`
#### Table: `orders_order` (Model: `Order`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `marketplace_review` | OneToOneRel | Null | → `marketplace_review` |
| `items` | ManyToOneRel | Null | → `orders_orderitem` |
| `delivery_request` | OneToOneRel | Null | → `orders_deliveryrequest` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `buyer` | ForeignKey | - | → `accounts_user` (User who placed the order) |
| `farmer` | ForeignKey | - | → `accounts_user` (Farmer who will fulfill the order) |
| `order_number` | CharField | Unique |  (Unique order identifier) |
| `status` | CharField | - |  |
| `total_amount` | DecimalField | - |  (Total order amount in UGX) |
| `delivery_address` | TextField | - |  (Where to deliver the order) |
| `delivery_phone` | CharField | - |  (Contact phone for delivery) |
| `notes` | TextField | Blank |  (Additional notes or instructions) |
| `created_at` | DateTimeField | Blank |  |
| `updated_at` | DateTimeField | Blank |  |

#### Table: `orders_orderitem` (Model: `OrderItem`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `order` | ForeignKey | - | → `orders_order` (Parent order) |
| `product` | ForeignKey | - | → `marketplace_product` (Product being ordered) |
| `quantity` | IntegerField | - |  (Quantity ordered) |
| `unit_price` | DecimalField | - |  (Price per unit at time of order) |
| `subtotal` | DecimalField | - |  (Quantity × Unit Price) |
| `created_at` | DateTimeField | Blank |  |

#### Table: `orders_deliveryrequest` (Model: `DeliveryRequest`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `order` | OneToOneField | Unique | → `orders_order` (Order this delivery is for) |
| `transporter` | ForeignKey | Null, Blank | → `accounts_user` (Assigned transporter (blank = open request)) |
| `pickup_district` | CharField | - |  (District where goods will be picked up) |
| `delivery_district` | CharField | - |  (District where goods will be delivered) |
| `pickup_address` | TextField | Blank |  (Specific pickup location / landmark) |
| `offered_price` | DecimalField | - |  (Transport fee offered in UGX) |
| `status` | CharField | - |  |
| `notes` | TextField | Blank |  (Special delivery instructions) |
| `created_at` | DateTimeField | Blank |  |
| `assigned_at` | DateTimeField | Null, Blank |  |
| `delivered_at` | DateTimeField | Null, Blank |  |

### App: `inputs`
#### Table: `inputs_inputcategory` (Model: `InputCategory`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `agriculturalinput` | ManyToOneRel | Null | → `inputs_agriculturalinput` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `name` | CharField | - |  |
| `category_type` | CharField | - |  |
| `description` | TextField | Blank |  |
| `image` | ImageField | Null, Blank |  |

#### Table: `inputs_agriculturalinput` (Model: `AgriculturalInput`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `groupbuypool` | ManyToOneRel | Null | → `inputs_groupbuypool` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `supplier` | ForeignKey | - | → `accounts_user` |
| `category` | ForeignKey | - | → `inputs_inputcategory` |
| `name` | CharField | - |  |
| `description` | TextField | - |  |
| `brand` | CharField | Blank |  |
| `price` | DecimalField | - |  |
| `quantity_available` | IntegerField | - |  |
| `unit` | CharField | - |  (e.g., kg, liters, pieces) |
| `manufacturer` | CharField | Blank |  |
| `usage_instructions` | TextField | Blank |  |
| `safety_warnings` | TextField | Blank |  |
| `image` | ImageField | - |  |
| `image2` | ImageField | Null, Blank |  |
| `min_group_order` | IntegerField | - |  (Minimum quantity for group purchase discount) |
| `group_discount_percentage` | IntegerField | - |  (Discount % for group orders) |
| `status` | CharField | - |  |
| `created_at` | DateTimeField | Blank |  |
| `updated_at` | DateTimeField | Blank |  |

#### Table: `inputs_groupbuypool` (Model: `GroupBuyPool`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `participants` | ManyToOneRel | Null | → `inputs_groupbuyparticipant` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `input_item` | ForeignKey | - | → `inputs_agriculturalinput` |
| `organizer` | ForeignKey | - | → `accounts_user` |
| `target_quantity` | IntegerField | - |  (Target quantity to unlock discount) |
| `current_quantity` | IntegerField | - |  |
| `status` | CharField | - |  |
| `deadline` | DateTimeField | - |  (Deadline to reach target) |
| `created_at` | DateTimeField | Blank |  |

#### Table: `inputs_groupbuyparticipant` (Model: `GroupBuyParticipant`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `pool` | ForeignKey | - | → `inputs_groupbuypool` |
| `farmer` | ForeignKey | - | → `accounts_user` |
| `quantity` | IntegerField | - |  |
| `joined_at` | DateTimeField | Blank |  |

### App: `news`
#### Table: `news_newscategory` (Model: `NewsCategory`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `agrinews` | ManyToOneRel | Null | → `news_agrinews` |
| `id` | BigAutoField | Blank, PK, Unique |  |
| `name` | CharField | - |  |
| `icon` | CharField | - |  |

#### Table: `news_agrinews` (Model: `AgriNews`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `title` | CharField | - |  |
| `news_type` | CharField | - |  |
| `category` | ForeignKey | Null, Blank | → `news_newscategory` |
| `content` | TextField | - |  |
| `summary` | TextField | - |  (Brief summary for preview) |
| `source` | CharField | - |  (e.g., Ministry of Agriculture) |
| `source_url` | URLField | Blank |  |
| `image` | ImageField | Null, Blank |  |
| `is_featured` | BooleanField | - |  |
| `is_urgent` | BooleanField | - |  (Mark as urgent alert) |
| `status` | CharField | - |  |
| `source_type` | CharField | - |  |
| `submitted_by` | ForeignKey | Null, Blank | → `accounts_user` |
| `published_by` | ForeignKey | Null, Blank | → `accounts_user` |
| `published_at` | DateTimeField | Blank |  |
| `views` | IntegerField | - |  |

### App: `weather`
#### Table: `weather_weatheralert` (Model: `WeatherAlert`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `alert_type` | CharField | - |  |
| `severity` | CharField | - |  |
| `title` | CharField | - |  |
| `description` | TextField | - |  |
| `affected_regions` | CharField | - |  (Comma-separated regions) |
| `start_date` | DateTimeField | - |  |
| `end_date` | DateTimeField | - |  |
| `recommendations` | TextField | - |  (What farmers should do) |
| `created_at` | DateTimeField | Blank |  |
| `is_active` | BooleanField | - |  |

#### Table: `weather_plantingseason` (Model: `PlantingSeason`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `crop_name` | CharField | - |  |
| `region` | CharField | - |  |
| `best_planting_start` | DateField | - |  |
| `best_planting_end` | DateField | - |  |
| `expected_harvest_start` | DateField | - |  |
| `expected_harvest_end` | DateField | - |  |
| `rainfall_required` | CharField | - |  (e.g., 800-1200mm) |
| `temperature_range` | CharField | - |  (e.g., 20-30°C) |
| `planting_tips` | TextField | - |  |

#### Table: `weather_pestalert` (Model: `PestAlert`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `pest_name` | CharField | - |  |
| `affected_crops` | CharField | - |  (Comma-separated crops) |
| `affected_regions` | CharField | - |  |
| `description` | TextField | - |  |
| `symptoms` | TextField | - |  (How to identify the pest/disease) |
| `severity` | CharField | - |  |
| `control_measures` | TextField | - |  (How to control/prevent) |
| `recommended_products` | TextField | Blank |  (Recommended pesticides) |
| `image` | ImageField | Null, Blank |  |
| `reported_date` | DateTimeField | Blank |  |
| `is_active` | BooleanField | - |  |

### App: `notifications`
#### Table: `notifications_notification` (Model: `Notification`)
| Field Name | Type | Properties | Description / Related To |
|------------|------|------------|--------------------------|
| `id` | BigAutoField | Blank, PK, Unique |  |
| `user` | ForeignKey | - | → `accounts_user` |
| `notification_type` | CharField | - |  |
| `title` | CharField | - |  |
| `message` | TextField | - |  |
| `link` | URLField | Null, Blank |  |
| `read` | BooleanField | - |  |
| `created_at` | DateTimeField | Blank |  |

