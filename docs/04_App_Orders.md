# 4. App: Orders

The `orders` app orchestrates the purchasing workflow from product selection to delivery matching. It handles basic transactional states but currently lacks integrated payment processing (a noted technical debt).

## 4.1 Models

### Model: `Order`
- **Relationships**: `ForeignKey` to `accounts.User` (`buyer`), `ForeignKey` to `accounts.User` (`farmer`).
- **`order_number`**: `CharField` (Unique). Auto-generated human-readable ID (e.g., `ORD-20250208-A1B2`).
- **`total_amount`**: `DecimalField`. Calculated total cost in UGX.
- **`status`**: `CharField` (choices: pending, confirmed, processing, shipped, delivered, cancelled). Essential state machine for the order lifecycle.
- **`shipping_address`**: `TextField`. Where the goods need to go.
- **`payment_status`**: `CharField` (pending, paid, failed, refunded). Currently primarily stays 'pending' or is manually updated, due to lack of payment gateway.
- **`payment_method`**: `CharField` (mobile_money, cash_on_delivery, bank_transfer).

### Model: `OrderItem`
- **Relationships**: `ForeignKey` to `Order`, `ForeignKey` to `marketplace.Product`.
- **`quantity`**: `IntegerField`. How much of the product was ordered.
- **`price_at_time`**: `DecimalField`. Crucial for historical accuracy; records the product's price at the moment of purchase so future price changes don't alter past orders.

### Model: `DeliveryRequest`
- **Relationships**: `OneToOneField` to `Order`, `ForeignKey` to `accounts.User` (`transporter`, nullable).
- **`status`**: `CharField` (open, accepted, picked_up, in_transit, delivered, cancelled).
- **`pickup_district`, `delivery_district`**: `CharField`. Used by the system to match open delivery requests with transporters covering those districts.
- **`pickup_address`**: `TextField`.
- **`offered_price`**: `DecimalField`. The transport fee the farmer/buyer is willing to pay.
- **`notes`**: `TextField`. Special handling instructions.

## 4.2 Views

### `place_order`
- **URL**: `/orders/place/<product_id>/` | **Method**: GET, POST
- **Permissions**: `@login_required`
- **Logic**: 
  - Retrieves `Product`. Validates requested quantity against `product.quantity`.
  - Calculates `total_price = quantity * product.price`.
  - Creates `Order` and `OrderItem` atomically.
  - Updates `product.quantity`.
- **Return**: Redirects to `orders:order_detail`.

### `order_detail`
- **URL**: `/orders/detail/<order_id>/` | **Method**: GET
- **Permissions**: `@login_required`
- **Logic**: Fetches `Order`. Checks permissions (user must be buyer or farmer). Calculates subtotal and fetches associated `DeliveryRequest` if it exists.

### `my_orders`
- **URL**: `/orders/my-orders/` | **Method**: GET
- **Permissions**: `@login_required`
- **Logic**: Splits orders into `purchases` (where user is buyer) and `sales` (where user is farmer) for display on a unified dashboard.

### `update_order_status` & `cancel_order`
- **URL**: `/orders/update-status/<order_id>/` | `/orders/cancel/<order_id>/`
- **Permissions**: `@login_required`
- **Logic**: State management. `cancel_order` includes logic to restore product inventory (`product.quantity += item.quantity`).

### Delivery Views
- **`request_delivery`**: (URL: `/orders/delivery/request/<order_id>/`). Creates a `DeliveryRequest` for an order.
- **`delivery_detail`**: (URL: `/orders/delivery/<delivery_id>/`). Shows details. For open requests, it scans `TransporterProfile` objects to find transporters whose `coverage_districts` list intersects with the pickup or delivery district.
- **`accept_delivery`**: (URL: `/orders/delivery/accept/<delivery_id>/`). Assigns the `request.user` (must be a transporter) to the `DeliveryRequest` and changes status to 'accepted'.

## 4.3 URLs
- `path('place/<product_id>/', views.place_order)`
- `path('detail/<order_id>/', views.order_detail)`
- `path('my-orders/', views.my_orders)`
- `path('update-status/<order_id>/', views.update_order_status)`
- `path('cancel/<order_id>/', views.cancel_order)`
- `path('delivery/request/<order_id>/', views.request_delivery)`
- `path('delivery/<delivery_id>/', views.delivery_detail)`
- `path('delivery/accept/<delivery_id>/', views.accept_delivery)`

## 4.4 Missing Implementations / Gaps
- **Payments**: The `payment_status` is essentially a placeholder. The checkout flow completes immediately upon hitting "Place Order" without an actual gateway intercept (like Stripe, MTN Momo, or Flutterwave).
- **Location Tracking**: Transporter matching is purely text-based (matching district strings) rather than using geospatial coordinates or live GPS.
