# 6. Apps: News & Notifications

## 6.1 App: `news`

The `news` app acts as a basic CMS (Content Management System) for agricultural updates, best practices, and platform announcements.

### Models
- **`NewsCategory`**: `name`, `slug`.
- **`AgriNews`**:
  - `title`, `slug`, `author` (FK to User).
  - `content`: `TextField` (stores HTML or Markdown).
  - `image`: `ImageField`.
  - `category`: FK to `NewsCategory`.
  - `status`: `CharField` (draft, published).
  - `published_at`: `DateTimeField`.

### Views & URLs
- **`news_list`** (`/news/`): Shows published articles, ordered by newest first.
- **`news_detail`** (`/news/<slug>/`): Renders the full article.

---

## 6.2 App: `notifications`

A lightweight notification engine to alert users to order status changes, price alerts, or incoming messages.

### Models
- **`Notification`**:
  - `recipient`: FK to `User`.
  - `title`, `message`: String data.
  - `notification_type`: `CharField` (order, price_alert, system, message).
  - `is_read`: `BooleanField`. Toggled when the user views it.
  - `link`: `CharField` (optional). Deep link to the relevant object (e.g., `/orders/detail/5/`).

### Views & URLs
- **`notification_list`** (`/notifications/`): Renders a list of all notifications for `request.user`.
- **`mark_as_read`** (`/notifications/read/<id>/`): Updates `is_read = True` and redirects to the `link`.
- **`mark_all_read`** (`/notifications/read-all/`): Bulk updates all notifications for the user.

### Signals (The "Smart" part)
- The app relies heavily on Django Signals to automate notifications without tightly coupling the apps.
- For example, a `post_save` signal on the `Order` model in the `orders` app triggers the creation of a `Notification` object directed at the farmer when a new order is created, and directed at the buyer when the `status` changes to 'shipped'.
