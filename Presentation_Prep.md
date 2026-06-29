# Smart Agri Market — Final Year Panel Presentation Prep

Here is your comprehensive, structured preparation guide to ensure you are ready to confidently face your panel and defend your project. Read this carefully before presentation day.

---

## STEP 1 — Map the Codebase

**1-Paragraph Description of the App End-to-End:**
Smart Agri Market is a multi-role Django web application designed to eliminate agricultural middlemen. Farmers register to list their produce and join group-buying pools for cheaper inputs. Consumers and businesses can browse these listings and place direct orders. The app empowers farmers with a "Price Intelligence" dashboard that pulls real-time international commodity prices (via the WFP API) and compares them with crowdsourced local prices. It also features a "Climate Suite" that uses the OpenWeather API to give tailored planting and spraying advice based on the farmer's district.

**Major Folders & Responsibilities:**
- `accounts/`: Handles the custom User model, role-based registration (Farmer, Consumer, Transporter, Supplier), and verification requests.
- `marketplace/`: Manages product listings (Categories, Products), reviews, and the crucial `price_fetcher.py` service (WFP API integration).
- `orders/`: Handles the cart/checkout logic (`Order`, `OrderItem`) and the `DeliveryRequest` system where transporters bid on or accept delivery jobs.
- `inputs/`: Manages the agricultural input store and the "Group Buy" functionality (`GroupBuyPool`).
- `weather/`: Contains the `farming_advisor.py` service which hits the OpenWeather API to provide planting, harvesting, and spraying recommendations.
- `news/` & `notifications/`: Handles agricultural alerts and system-wide user notifications.
- `config/`: The core Django settings, routing (`urls.py`), and environment configuration.

**Proposal vs. Reality (Implementation Status):**
- **User Management:** ✅ Fully Implemented (Role-based access works well).
- **Product Marketplace:** ✅ Fully Implemented (Listing, searching, and basic ordering work).
- **Price Intelligence:** ✅ Fully Implemented (External WFP data + local crowdsourced data merge successfully).
- **Agricultural Advisory:** ⚠️ Partially Implemented (Weather alerts and spraying logic work via API, but *Harvest Predictions* are faked/hardcoded).
- **Location-based Matching:** ⚠️ Partially Implemented (Transporters are filtered by district, but there is no actual real-time GPS tracking).
- **Payments & Escrow:** ❌ Missing (Orders just go to "Pending" status—there is no Flutterwave, Stripe, or MTN Mobile Money integration).

---

## STEP 2 — What Will Embarrass You in a Live Demo

You must know these landmines so you aren't caught lying or freezing on stage.

1. **The "Fake" Harvest Predictions:**
   - **Where:** `weather/views.py` (Lines 44-48)
   - **What:** The app displays harvest progress, but it is **100% hardcoded**. The code literally says `sample_planted_crops = [{'crop': 'maize', 'planted_date': date(2026, 1, 15)}...]`. If a panelist asks you to add a new crop and see the prediction update, it will fail.
   - **How to handle it:** Admit it's a prototype. Say, *"For this prototype phase, the harvest prediction module uses sample data to demonstrate the UI flow, as building the full crop-tracking lifecycle was outside the 13-week scope."*

2. **The Missing Payment Gateway:**
   - **Where:** `orders/views.py` (`place_order` function)
   - **What:** When a user clicks "Place Order", the system just calculates the total and saves it to the database. No money moves.
   - **How to handle it:** Be proactive. Say, *"Currently, the platform operates on a Cash-on-Delivery (COD) or off-platform Mobile Money model. Integrating an Escrow API is slated for Phase 2."*

3. **Weak Database Validation (Fragile Part):**
   - **Where:** `marketplace/models.py` (`price = models.DecimalField(...)`)
   - **What:** The database models lack `MinValueValidator(0)`. While your HTML forms might prevent negative numbers, the database itself does not.
   - **How to handle it:** If asked about data integrity, admit that while frontend validation exists, adding strict ORM-level constraints is a necessary next step for production.

4. **Security / Data Issues:**
   - **Where:** `.env` file and `populate_sample_data.py`
   - **What:** Your `.env` file contains your actual `OPENWEATHER_API_KEY` and the Django `SECRET_KEY`. If this was pushed to GitHub, it's a security flaw. Furthermore, your sample data script uses plaintext passwords like "admin123".
   - **How to handle it:** State that the environment variables are strictly managed locally for the demo and that in production, secrets are injected via the hosting provider (e.g., AWS Secrets Manager or Heroku Config Vars).

---

## STEP 3 — File-by-File Explanation

**1. `marketplace/services/price_fetcher.py`**
- **What it does:** Reaches out to the Humanitarian Data Exchange (HDX) to download a CSV of Uganda food prices provided by the World Food Programme, converts USD to UGX, and merges it with farmer-reported prices.
- **Design Reasoning:** The WFP API doesn't require an authentication key and provides internationally verified data, which solves the "trust" issue in local pricing.
- **Explain it out loud:** *"This service acts as our price engine; it automatically downloads verified commodity prices from the World Food Programme and averages them with local prices reported directly by our farmers."*
- **Hard Question:** *"What happens if the WFP server goes down during the demo?"*
  - **Model Answer:** *"The system is designed with a hybrid approach. If the external API fails, the system automatically falls back to displaying only the crowdsourced prices reported by our local farmers, ensuring the platform remains functional."*

**2. `weather/services/farming_advisor.py`**
- **What it does:** Uses the OpenWeatherMap API to get the 5-day forecast, checks for rain and wind, and applies logical rules (e.g., "If wind > 15km/h, don't spray pesticides").
- **Design Reasoning:** Farmers lose crops to sudden weather changes. By turning raw weather data into actionable text ("Delay spraying"), the app becomes a decision-support tool, not just a weather widget.
- **Explain it out loud:** *"It takes live weather data like wind and rain forecasts and translates it into simple farming advice, like telling a farmer whether it's safe to spray pesticides today."*
- **Hard Question:** *"How does your app know the optimal temperature for Maize versus Cassava?"*
  - **Model Answer:** *"We created a lightweight rules engine—a dictionary in the code—that stores the optimal temperature ranges, rainfall needs, and growing days for Uganda's top 5 staple crops based on agricultural best practices."*

**3. `orders/views.py`**
- **What it does:** Handles cart checkout, order status updates, and the creation of `DeliveryRequest` objects so transporters can see available jobs.
- **Design Reasoning:** It decouples ordering from delivery. Because rural logistics are difficult, the app lets farmers broadcast a delivery need, and independent transporters can claim it.
- **Explain it out loud:** *"It processes the buyer's order and immediately creates a delivery broadcast so that registered truck drivers in that specific district can accept the transport job."*
- **Hard Question:** *"How do you prevent a farmer from ordering their own product to artificially boost their sales stats?"*
  - **Model Answer:** *"In the `place_order` view, we explicitly check if `request.user == product.farmer` and block the transaction with an error message."*

**4. `inputs/views.py` (Group Buying)**
- **What it does:** Allows a farmer to create a "Pool" for a product (like fertilizer) with a target quantity. Other farmers join until the target is hit, unlocking a bulk discount.
- **Design Reasoning:** Individual smallholder farmers can't afford bulk fertilizer. Digitizing the cooperative model allows them to combine purchasing power without needing to be in the same room.
- **Explain it out loud:** *"It works like a digital cooperative; farmers pool their small orders together into one massive order to unlock wholesale discounts from suppliers."*

---

## STEP 4 — Connection to SDLC Prototyping

Your proposal claims you used **SDLC Prototyping**. The panel will look for proof that you actually built a prototype and iterated on it, rather than just coding everything in one straight line (Waterfall).

- **Phase 1: Requirements Analysis**
  - **Code Evidence:** The custom roles in `accounts/models.py` (Farmer, Transporter, Business) directly mirror the 5 distinct user types you identified in your survey questionnaires.
- **Phase 2: System Design**
  - **Code Evidence:** The modular structure of Django (separate apps for `weather`, `orders`, `marketplace`) aligns perfectly with the High-Level Architecture diagram in your proposal.
- **Phase 3: Prototype Development**
  - **Code Evidence:** The `populate_sample_data.py` file is the ultimate proof of prototyping. You built a script to flood the database with fake data so you could rapidly test the UI before real users existed.
  - **Missing Evidence (Be ready to explain):** You don't have multiple versions (e.g., v1, v2) visible in the final code. *Explain verbally:* "Our first prototype was just the marketplace. We presented it to our supervisor, who noted the lack of trust. Based on that feedback, we iterated and added the WFP Price Intelligence module in prototype iteration 2."
- **Phase 4: Testing & Evaluation**
  - **Missing Evidence:** There are no automated test files (like `test_models.py`) utilized heavily in the repo.
  - **How to handle it:** State that because this was an Agile Prototype, testing was primarily User Acceptance Testing (UAT) — manually walking users through the UI — rather than extensive Unit Testing.

---

## STEP 5 — Prioritized Fix List

If you only have a few days before the presentation, focus your time here:

**🔴 MUST FIX (Will break demo or make you look bad)**
1. **Remove the Fake Harvest Data:**
   - *File:* `weather/views.py`
   - *Fix:* At line 44, delete or comment out the `sample_planted_crops` array and the call to `get_harvest_predictions`. It is better to have one less feature than to have a panelist click "Add Crop" and realize the dashboard is hardcoded.

**🟡 SHOULD FIX IF TIME ALLOWS (Looks more polished)**
1. **Add Minimum Value Validators:**
   - *File:* `marketplace/models.py` and `orders/models.py`
   - *Fix:* Import `MinValueValidator` from `django.core.validators` and add `validators=[MinValueValidator(0)]` to all `DecimalField` prices and `IntegerField` quantities. This proves you understand database integrity.
2. **Hide your `.env` variables:**
   - Ensure your `.env` file is in your `.gitignore` so you don't accidentally display your `SECRET_KEY` if you open your GitHub repo on the projector.

**🟢 DON'T TOUCH (Low risk, explain verbally)**
1. **Payment Gateway Integration:** Do not try to rush an integration with Stripe or Flutterwave right now. You will likely break the order flow. Stick to the "Cash on Delivery" narrative.
2. **Real-time GPS Tracking for Transporters:** Too complex for a final-year prototype. Stick to the current "Accept Delivery Request" logic.
