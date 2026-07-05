# 2. App: Accounts

The `accounts` app handles user authentication, profile management, role-based authorization (Farmer, Consumer, Business, Transporter), and verification requests.

## 2.1 Models

### Model: `User` (extends `AbstractUser`)
- **`user_type`**: `CharField` (choices: farmer, consumer, business, input_supplier, transporter). Defines the core role and permissions of the user.
- **`phone`, `whatsapp_number`**: `CharField`. Essential for direct communication (WhatsApp is widely used in Uganda for business).
- **`location`, `address`, `district`**: Store the physical base of operations. Crucial for location-based matching (e.g., finding nearby transporters or predicting weather).
- **`profile_picture`**: `ImageField`. User avatar.
- **`is_verified`**: `BooleanField`. Indicates if an admin has approved their `VerificationRequest` (critical for trust in the marketplace).
- **`specialization`**: `CharField` (e.g., Crop Farming, Livestock). Helps in tailoring agricultural advice and product filtering.
- **`first_login`**: `BooleanField`. Used to trigger onboarding flows.

### Model: `FarmerProfile`
- **Relationship**: `OneToOneField` to `User`.
- **`farm_name`**, **`farm_size`** (Decimal): Captures business scale.
- **`specialization`**: Specific farming focus.
- **`rating_average`**, **`total_sales`**: Denormalized metrics updated continuously to prevent expensive aggregations on the landing page.

### Model: `TransporterProfile`
- **Relationship**: `OneToOneField` to `User`.
- **`vehicle_type`**: `CharField` (e.g., motorcycle, pickup, lorry).
- **`vehicle_registration`**: `CharField`. Needed for accountability.
- **`capacity_kg`**: `DecimalField`. Used to filter transporters capable of handling specific order weights.
- **`coverage_districts`**: `TextField` (comma-separated). Simplistic way to match transporters to farmer/buyer districts.

### Model: `VerificationRequest`
- **Relationship**: `OneToOneField` to `User`.
- **`national_id_image`**, **`farm_or_business_photo`**: Required for KYC (Know Your Customer).
- **`status`**: `CharField` (pending, approved, rejected).
- **`reviewed_by`**: `ForeignKey` to `User` (Admin). Auditing field to track who approved the verification.

## 2.2 Views

### `register`
- **URL**: `/accounts/register/` | **Method**: GET, POST
- **Logic**: Validates `RegisterForm`. Creates a `User` instance. Based on `user_type`, it dynamically creates either a `FarmerProfile` or a `TransporterProfile` with default values so the database integrity holds.
- **Return**: Redirects to `accounts:login` on success, or re-renders `accounts/register.html` with errors.

### `user_login`
- **URL**: `/accounts/login/` | **Method**: GET, POST
- **Logic**: Uses Django's `authenticate()` and `login()`.
- **Return**: Redirects to `marketplace:home`.

### `logout_view`
- **URL**: `/accounts/logout/` | **Method**: POST only (`@require_POST`)
- **Logic**: Calls `logout()`. Enforces `@never_cache` and explicitly sets cache-control headers on the response to prevent back-button hijacking.
- **Return**: Redirects to `accounts:login`.

### `dashboard`
- **URL**: `/accounts/dashboard/` | **Method**: GET
- **Permissions**: `@login_required`
- **Logic**: Gathers `farmer_profile`, `transporter_profile`, and `verification_request`.
- **Return**: Renders `accounts/dashboard.html`.

## 2.3 URLs
- `path('register/', views.register, name='register')`
- `path('login/', views.user_login, name='login')`
- `path('logout/', views.logout_view, name='logout')`
- `path('dashboard/', views.dashboard, name='dashboard')`
- `path('edit-profile/', views.edit_profile, name='edit_profile')`
- `path('verification/submit/', views.submit_verification, name='submit_verification')`
- Password reset flows (`password-reset/`, `password-reset/done/`, etc.) map directly to Django's built-in `auth_views`.

## 2.4 Forms & Middleware
- **`RegisterForm`**: Handles custom validation for the extended user fields.
- **`LoginRequiredMiddleware`**: Added globally in `config/settings.py` to enforce that all views (unless explicitly whitelisted like `/` or `/accounts/login/`) redirect to login.
- **`LogoutProtectionMiddleware`**: Injects headers (`Cache-Control: no-cache, no-store, must-revalidate, private`) for authenticated users to ensure sensitive pages aren't stored in the browser's back/forward cache.
