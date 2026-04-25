# ─────────────────────────────────────────────────────
#  TITLE PAGE (Not page numbered — not counted in 10-page limit)
# ─────────────────────────────────────────────────────

**VICTORIA UNIVERSITY**

*(Insert University Logo Here)*

---

## Smart Agri Market: A Web-Based Agricultural Marketplace for Uganda

---

**By**

| Name | Reg. No | Student No. | Email Address | Phone Contact | Signature |
|------|---------|-------------|---------------|---------------|-----------|
|      |         |             |               |               |           |
|      |         |             |               |               |           |
|      |         |             |               |               |           |

**Department of Computing and Information Science**
**Faculty of Science and Technology**

---

A Proposal Submitted to the Department of Computing and Information Science in Fulfillment of the Requirements for the Award of a Degree of Bachelors of Information Technology of Victoria University

---

**Supervisor:** Dr. Joseph Ssemwogerere
**Department of Computing and Information Science**
**Faculty of Science and Technology**
**Email:** jssemwogerere@vu.ac.ug

**September, 2025**

---
---

*(Page numbering begins from here)*

---

# 1. Background / Introduction

Information and Communication Technology (ICT) has revolutionized virtually every sector of the global economy, including agriculture. According to the Food and Agriculture Organization (FAO, 2022), digital agricultural platforms have emerged as transformative tools that connect smallholder farmers to markets, price information, and critical agricultural services. In Sub-Saharan Africa, where over 60% of the population depends on agriculture for their livelihood (World Bank, 2023), ICT-driven solutions are increasingly recognized as catalysts for food security and economic empowerment.

In Uganda, agriculture contributes approximately 24% to the national GDP and employs over 70% of the working population (Uganda Bureau of Statistics [UBOS], 2023). Despite this significance, smallholder farmers face persistent challenges that limit their productivity and market access. The agricultural value chain in Uganda is characterized by information asymmetry, where farmers lack access to real-time market prices and are often exploited by middlemen who purchase produce at significantly below-market rates (Mugisha & Diiro, 2021). According to the International Fund for Agricultural Development (IFAD, 2022), Ugandan farmers lose an estimated 20-30% of their potential income due to price manipulation and lack of transparent market information.

Furthermore, access to quality agricultural inputs such as certified seeds, fertilizers, and pesticides remains fragmented, with suppliers concentrated in urban centers and few convenient channels for rural farmers to procure these essential products (Nakasone, 2023). The absence of a unified digital platform that integrates marketplace functionality, price intelligence, weather advisories, and agricultural input procurement has created a significant gap in Uganda's agricultural ecosystem.

## 1.1 Research Problem / Statement of the Problem

Ugandan smallholder farmers experience significant economic losses due to the absence of a transparent, centralized digital marketplace that provides real-time market price information, direct buyer-farmer connectivity, and integrated access to agricultural inputs and weather advisories. Currently, farmers rely on exploitative middlemen who manipulate prices, lack access to verified real-time commodity prices across different districts, and have no single platform that consolidates marketplace, weather, pest alerts, and input procurement services. This information asymmetry results in farmers selling their produce at 20-40% below fair market value, leading to reduced household incomes, food insecurity, and diminished agricultural investment across rural Uganda.

## 1.2 Objectives

### 1.2.1 General Objective

To design and develop a web-based agricultural marketplace platform (Smart Agri Market) that empowers Ugandan farmers with transparent market access, real-time price intelligence, and integrated agricultural support services.

### 1.2.2 Specific Objectives

1. To develop a multi-role digital marketplace that enables farmers to list and sell agricultural products directly to consumers, businesses, and transporters across all districts of Uganda.

2. To integrate real-time market price tracking using external APIs (World Food Programme) combined with crowdsourced farmer-reported prices that empower farmers with transparent pricing intelligence.

3. To implement an agricultural input store with a group-buying feature that enables smallholder farmers to access seeds, fertilizers, pesticides, and farming tools at discounted bulk rates.

4. To develop a weather advisory, pest alert, and planting season recommendation module that provides location-specific agricultural guidance to farmers based on their registered districts.

## 1.3 Significance / Importance / Contribution

This project makes significant contributions to both academic knowledge and practical agricultural development in Uganda:

**Academic Contribution:** The Smart Agri Market contributes to the growing body of knowledge on ICT for Development (ICT4D) by demonstrating how web-based platforms can address information asymmetry in agricultural value chains. The integration of crowdsourced price data with external API data (World Food Programme) presents a novel hybrid approach to price transparency that can serve as a model for future research in agricultural informatics.

**Technological Contribution:** The system introduces a unique combination of features not currently available on a single Ugandan agricultural platform: real-time price tracking from verified international sources (WFP, FAO), a crowdsourced price verification mechanism that prevents middleman exploitation, and a group-buying system for agricultural inputs that leverages collective purchasing power of smallholder farmers.

**Socio-Economic Value:** The platform directly addresses farmer poverty by enabling them to access fair market prices, eliminating exploitative middlemen, and reducing input costs through group purchasing. By providing weather alerts and pest advisories, the platform also helps farmers make informed decisions about planting, harvesting, and pest management, thereby improving crop yields and minimizing climate-related losses. The notification system ensures that no critical alert or market update is missed.

**Community Impact:** By organizing farmers across all Ugandan districts with district-level data aggregation and farmer listings, the platform fosters community building, knowledge sharing, and cooperative economic activity among rural agricultural communities.

## 1.4 Justification / Rationale

The urgency of this project stems from several converging factors. Uganda's rapidly growing population (projected to reach 50 million by 2030) demands increased agricultural productivity, yet smallholder farmers — who produce over 80% of the country's food — continue to operate with outdated tools, limited market access, and insufficient information (UBOS, 2023).

Mobile phone penetration in Uganda has reached approximately 70%, and internet access continues to expand rapidly, especially through affordable smartphones (Uganda Communications Commission, 2023). This digital infrastructure presents a timely opportunity to deploy a web-based agricultural platform that can reach even remote farming communities. Unlike existing solutions such as e-Soko and M-Farm, which focus solely on price information, the Smart Agri Market integrates marketplace transactions, input procurement, weather intelligence, pest management, and community features into a single, comprehensive platform.

The project is also justified by the Ugandan government's Digital Uganda Vision 2040, which explicitly prioritizes the digitization of agriculture as a key pillar for national economic transformation. The integration of World Food Programme (WFP) market data ensures that the platform provides internationally verified price information — a feature that no existing Ugandan agricultural app currently offers.

Additionally, the group-buying feature addresses the well-documented problem of input affordability. A study by the Alliance of Bioversity International and CIAT (2022) found that input costs can consume up to 50% of a smallholder farmer's income. By enabling collective purchasing at bulk discount rates, the platform can reduce these costs by 10-25%, directly improving farmer profitability.

## 1.5 Scope of the Project

This project covers the design, development, and testing of a web-based agricultural marketplace platform for Uganda. The investigation encompasses the current state of agricultural market information systems, price transparency challenges, and input access barriers faced by smallholder farmers across Ugandan districts. In terms of content, the system encompasses six core modules: (i) a multi-role user management system supporting farmers, consumers, businesses, input suppliers, and transporters across all 135+ districts of Uganda; (ii) a product marketplace with category-based browsing, search, and order management; (iii) a price intelligence engine integrating WFP API data with crowdsourced farmer-reported prices; (iv) an agricultural inputs e-commerce store with group-buying functionality; (v) a weather and pest alert advisory system with planting season recommendations; and (vi) a news and notification module for agricultural updates and government policy announcements. The platform will be developed using the Django web framework (Python), with SQLite for development-stage data storage, and will target both desktop and mobile web browsers. Geographically, the system covers all four regions of Uganda (Central, Eastern, Northern, and Western) with district-level granularity.

---

# 2. Literature Review

## 2.1 ICT in Agriculture: A Global Perspective

The application of Information and Communication Technology in agriculture has transformed the way farmers access markets, obtain price information, and manage agricultural operations globally. Verdouw et al. (2021) assert that digital agriculture platforms represent a paradigm shift from traditional farming, enabling data-driven decision-making that improves productivity, market access, and resource management. These platforms leverage web and mobile technologies to bridge the information gap between producers and consumers, providing real-time data on commodity prices, weather patterns, and best farming practices.

In developed countries, precision agriculture platforms have achieved significant adoption. The European Commission (2022) reports that over 80% of large-scale farms in the EU use at least one form of digital agricultural technology. However, Tsan et al. (2021) note that in developing countries, particularly in Sub-Saharan Africa, digital agricultural solutions face unique challenges including limited internet connectivity, low digital literacy among farmers, and insufficient integration of local market dynamics into platform design.

## 2.2 Agricultural Market Information Systems in East Africa

Several agricultural market information systems (MIS) have been developed for the East African context. Kenya's M-Farm, launched in 2010, was one of the pioneering SMS-based platforms that provided real-time market prices to farmers via mobile phones (Baumüller, 2018). Similarly, Uganda's e-Soko system provided price information through SMS alerts. However, Nakasone and Torero (2022) found that these early-generation platforms were limited by their text-only interfaces, one-directional information flow, and inability to facilitate actual marketplace transactions.

More recent platforms such as Twiga Foods (Kenya) and Farmshine (Uganda) have attempted to integrate marketplace functionality with price information (Reardon et al., 2021). Despite these advancements, these platforms tend to focus on a single aspect of the agricultural value chain — either market access or input supply — rather than offering a comprehensive, integrated solution. Muto and Yamano (2022) argue that the fragmentation of agricultural digital services forces farmers to use multiple platforms, resulting in increased complexity and reduced adoption rates.

A critical gap identified in existing literature is the absence of platforms that combine verified external price data (from organizations such as the World Food Programme and FAO) with localized crowdsourced price reports from farmers themselves. Minot and Dewina (2021) demonstrate that while official price data provides reliability, it often lacks the granularity needed for local market decisions. Conversely, crowdsourced price data offers local relevance but may lack verification. The Smart Agri Market addresses this gap by combining both data sources into a unified price intelligence module.

## 2.3 Group Buying and Cooperative Input Procurement

Access to quality agricultural inputs remains one of the most significant barriers to productivity improvement for smallholder farmers in Uganda. Liverpool-Tasie et al. (2022) report that approximately 80% of Ugandan smallholder farmers use no fertilizer at all due to high costs and limited availability. The fragmented nature of input supply chains, combined with the inability of individual smallholder farmers to negotiate bulk prices, perpetuates a cycle of low input usage and low yields.

Group-buying models have shown promise in addressing input affordability challenges. Chen et al. (2021) define group buying as a collective purchasing mechanism where multiple buyers consolidate their demand to access volume discounts from suppliers. In the agricultural context, this model has been successfully implemented by organizations such as One Acre Fund, which has demonstrated that collective input procurement can reduce costs by 15-30% while improving access to certified seeds and fertilizers (One Acre Fund, 2023).

However, existing group-buying implementations are typically facilitated by NGOs or cooperatives and require physical coordination. The digitization of group buying through web-based platforms — as proposed in this project — offers the potential to scale this model across geographic boundaries, enabling farmers from different districts to collectively procure inputs from verified suppliers through an automated pool-based system.

## 2.4 Weather-Based Agricultural Advisory Systems

Climate variability poses a significant threat to agricultural productivity in Uganda, where rain-fed agriculture accounts for over 95% of crop production (UBOS, 2023). Krell et al. (2021) emphasize that timely weather information and pest alerts can reduce crop losses by up to 25%, yet most Ugandan farmers lack access to localized, actionable weather advisories.

Several weather-based advisory systems have been developed for African agriculture. iCow (Kenya) integrates weather data with crop-specific recommendations, while WeFarm enables peer-to-peer agricultural knowledge sharing (Etwire et al., 2022). However, these platforms operate independently from marketplace systems, requiring farmers to switch between multiple applications. The integration of weather alerts, pest advisories, and planting season recommendations within a marketplace platform — as designed in the Smart Agri Market — reduces this fragmentation and provides a more holistic farming experience.

## 2.5 Review and Rating Systems in Agricultural E-Commerce

Trust is a critical factor in agricultural e-commerce, particularly in contexts where buyers and sellers may not have pre-existing relationships. Agyekum et al. (2022) identify trust deficit as the primary barrier to digital agricultural marketplace adoption in Sub-Saharan Africa. Review and rating systems have been widely adopted by e-commerce platforms such as Jumia and Amazon to build trust between transacting parties.

In the agricultural context, review systems serve an additional function: they incentivize quality. When farmers know that their products will be reviewed and rated, they are more likely to maintain higher quality standards (Reardon et al., 2021). The Smart Agri Market incorporates a comprehensive review system that includes quality ratings, delivery timeliness assessment, communication evaluation, and recommendation indicators, providing multi-dimensional trust metrics for both buyers and sellers.

---

# 3. Methodology

## 3.1 Research Design — Agile Development Methodology

This project adopts the **Agile Software Development methodology**, specifically following the **Iterative and Incremental** model. The Agile methodology is selected because of its flexibility, iterative feedback cycles, and ability to accommodate changing requirements — all of which are critical for developing a user-centered agricultural platform.

### Phase 1: Requirements Gathering and Analysis (Weeks 1-2)

**People Involved:** Project team members, supervisor, sample farmers, consumers, and input suppliers from selected districts.

**Activities:**
- Conduct stakeholder interviews with 15-20 farmers, 5-10 consumers, and 3-5 input suppliers across Central, Eastern, and Western Uganda.
- Distribute structured questionnaires (see Appendix iii) to gather requirements on marketplace features, price information needs, and input procurement challenges.
- Analyze existing agricultural platforms (e-Soko, M-Farm, Twiga Foods) to identify feature gaps.
- Document functional and non-functional requirements.

**Tools:** Google Forms (questionnaire distribution), Microsoft Word (documentation), draw.io (use case diagrams).

**Expected Outcome:** A comprehensive Software Requirements Specification (SRS) document detailing all functional modules, user roles, and system requirements.

### Phase 2: System Design (Weeks 3-4)

**People Involved:** Project team members, supervisor.

**Activities:**
- Design the system architecture (three-tier: Presentation, Business Logic, Database layers).
- Create Entity-Relationship Diagrams (ERD) for the database schema covering Users, Products, Orders, Prices, Inputs, Weather, and News entities.
- Design wireframes and UI mockups for key screens: Homepage, Product Listing, Farmer Dashboard, Price Tracker, Input Store, and Weather Advisory.
- Define the API integration strategy for the World Food Programme price data service.
- Design the multi-role authentication and authorization system (Farmer, Consumer, Business, Input Supplier, Transporter).

**Tools:** draw.io (ER diagrams, flowcharts), Figma (UI wireframes), Visual Studio Code (project scaffolding).

**Expected Outcome:** Complete system design documentation including ER diagrams, system architecture diagram, UI wireframes, and API integration plan.

### Phase 3: Implementation / Development (Weeks 5-10)

**People Involved:** Project team members.

**Activities:**
- Set up the Django project structure with modular app architecture (`accounts`, `marketplace`, `orders`, `inputs`, `weather`, `news`, `notifications`).
- Implement the custom User model with role-based access (Farmer, Consumer, Business, Input Supplier, Transporter).
- Develop the product marketplace module with CRUD operations, category management, search, and filtering.
- Build the price intelligence engine:
  - WFP API integration service for fetching real-time international commodity prices.
  - Currency conversion module (USD to UGX).
  - Crowdsourced price reporting and verification system.
  - Combined price display with source indicators.
- Develop the agricultural input store with group-buying pool functionality.
- Implement the weather advisory module (WeatherAlert, PlantingSeason, PestAlert models).
- Build the order management system with status tracking.
- Develop the review and rating system with farmer response capability.
- Implement the news module for agricultural updates and government policy announcements.
- Build the notification system for alerts, product updates, and news.
- Develop district-level data aggregation and visualization.

**Tools:** Python 3.10+, Django 4.2, SQLite (development database), HTML5/CSS3/JavaScript (frontend), Bootstrap 5 (responsive UI), Visual Studio Code (IDE), Git/GitHub (version control).

**Expected Outcome:** A fully functional web-based agricultural marketplace with all six core modules operational.

### Phase 4: Testing and Validation (Weeks 11-12)

**People Involved:** Project team members, supervisor, beta testers (5-10 users from each role type).

**Activities:**
- Conduct unit testing for all Django models, views, and service functions.
- Perform integration testing to verify module interactions (e.g., ordering a product triggers proper notifications, price data aggregation from both WFP and crowdsourced sources).
- Execute User Acceptance Testing (UAT) with sample farmers, consumers, and input suppliers.
- Test the WFP API integration for reliability and data accuracy.
- Validate the group-buying pool workflow (creation, joining, target reaching, completion).
- Test responsive design across desktop and mobile browsers.

**Tools:** Django TestCase (unit tests), Postman (API testing), Google Chrome DevTools (responsive testing).

**Expected Outcome:** A tested, validated system with documented test results and any identified issues resolved.

## 3.2 Data Collection Methods

**Primary Data:**
- **Structured Questionnaires:** Administered to 50 respondents (30 farmers, 10 consumers, 5 input suppliers, 5 business buyers) across 5 districts (Kampala, Wakiso, Jinja, Mbarara, Gulu) to assess marketplace needs, current pricing challenges, and technology adoption readiness. (See Appendix iii for the questionnaire.)
- **Interviews:** Semi-structured interviews with 10 key informants including agricultural extension officers, cooperative leaders, and market administrators.

**Secondary Data:**
- WFP Market Price API data for commodity price benchmarking.
- Uganda Bureau of Statistics (UBOS) agricultural reports.
- Research papers and journals on ICT in agriculture (APA 7th Edition referenced).

**Sample Size Justification:** A total of 50 primary respondents was selected through purposive sampling to ensure representation of all five user types (farmer, consumer, business, input supplier, transporter) across both urban and rural districts within the project's geographic scope.

## 3.3 Data Analysis

Quantitative data from questionnaires will be analyzed using descriptive statistics (frequencies, percentages, means) and presented through tables and charts. Qualitative data from interviews will be analyzed using thematic analysis to identify recurring patterns related to market access challenges, pricing transparency needs, and technology adoption barriers. All collected data will be stored both electronically (CSV files, Django database) and in hardcopy for future reference.

## 3.4 System Development

The system is developed using the following technology stack:

| Component | Technology |
|-----------|-----------|
| Backend Framework | Django 4.2 (Python 3.10+) |
| Database | SQLite (development), PostgreSQL (production-ready) |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| External APIs | WFP VAM API (market prices), ExchangeRate-API (currency conversion) |
| Version Control | Git / GitHub |
| Deployment | WSGI (Gunicorn) + Nginx (production) |

**Database Design:** The system uses a relational database with the following core entities:
- **User** (custom AbstractUser with role-based types, district assignment, WhatsApp integration)
- **FarmerProfile / InputSupplierProfile** (extended profile information)
- **Category, Product** (marketplace product listings)
- **MarketPrice, ExternalMarketPrice, CrowdsourcedPrice** (three-tier price intelligence)
- **Order, OrderItem** (order management with status tracking)
- **AgriculturalInput, InputCategory, GroupBuyPool, GroupBuyParticipant** (input store and group buying)
- **WeatherAlert, PlantingSeason, PestAlert** (agricultural advisories)
- **AgriNews, NewsCategory** (news and updates)
- **Review, ReviewResponse** (trust and reputation system)
- **Notification** (multi-type alert system)

**Programming:** Server-side logic is implemented through Django views with function-based views for flexibility. The price fetcher service integrates the WFP VAM API with automatic USD-to-UGX currency conversion. Frontend templates use Django's template engine with Bootstrap 5 for responsive, mobile-friendly interfaces.

**Testing:** Unit tests verify model integrity and view behavior. Integration tests validate module interactions. API endpoint testing verifies WFP data fetching reliability. User Acceptance Testing confirms usability with real stakeholders.

---

# 4. Limitations / Anticipated Problems

Several constraints may impact the implementation and adoption of this project:

1. **Internet Connectivity:** Many rural farming areas in Uganda have limited or unreliable internet access, which may restrict real-time access to the platform. Mitigation: The system is designed with lightweight, fast-loading pages and minimal data consumption.

2. **Digital Literacy:** Some target farmers may have limited experience with web-based platforms. Mitigation: The user interface is designed with simplicity and intuitive navigation in mind, and the WhatsApp number field facilitates alternative communication.

3. **API Reliability:** The WFP Market Price API and currency conversion APIs may experience downtime or rate limiting. Mitigation: The system implements fallback mechanisms (e.g., cached exchange rates, local crowdsourced prices) to ensure continued functionality.

4. **Data Accuracy:** Crowdsourced price reports depend on honest reporting by farmers. Mitigation: The platform includes a verification flag system that allows administrators to validate reported prices, and the combination with official WFP data provides a reliability cross-check.

---

# 5. References

1. Agyekum, C. K., Haifeng, H., & Agyeiwaa, A. (2022). Trust and digital agricultural marketplace adoption in Sub-Saharan Africa: A systematic review. *Journal of Agricultural Informatics*, 13(1), 34-48.

2. Alliance of Bioversity International and CIAT. (2022). *The cost of farming: Input affordability challenges for smallholder farmers in East Africa*. CGIAR Research Report.

3. Baumüller, H. (2018). The little we know: An exploratory literature review on the utility of mobile phone-enabled services for smallholder farmers. *Journal of International Development*, 30(1), 134-154.

4. Chen, L., Xu, Y., & Zhou, W. (2021). Group buying mechanisms in e-commerce: Models, strategies, and implications. *Electronic Commerce Research and Applications*, 47, 101049.

5. Etwire, P. M., Buah, S., &"; Kuwornu, J. K. (2022). Climate information services and agricultural decision-making in Africa. *Climate Risk Management*, 35, 100398.

6. Food and Agriculture Organization. (2022). *The State of Food and Agriculture 2022: Leveraging automation in agriculture for transforming agrifood systems*. FAO.

7. International Fund for Agricultural Development. (2022). *Rural Development Report 2022: Transforming food systems for rural prosperity*. IFAD.

8. Krell, N. T., Giroux, S. A., Guido, Z., Hannah, C., Lopus, S. E., Caylor, K. K., & Evans, T. P. (2021). Smallholder farmers' use of mobile phone services in central Kenya. *Climate and Development*, 13(3), 215-227.

9. Liverpool-Tasie, L. S., Omonona, B. T., & Sanou, A. (2022). Input market inefficiencies and their implications for agricultural productivity in Sub-Saharan Africa. *Food Policy*, 106, 102181.

10. Minot, N., & Dewina, R. (2021). Are market price data accurate? Evidence from a developing country. *Journal of Development Economics*, 148, 102561.

11. Mugisha, J., & Diiro, G. M. (2021). Market information asymmetry and smallholder farmer welfare in Uganda. *African Journal of Agricultural and Resource Economics*, 16(2), 112-128.

12. Muto, M., & Yamano, T. (2022). The impact of mobile phone coverage expansion on agricultural market participation: Panel data evidence from Uganda. *World Development*, 154, 105856.

13. Nakasone, E. (2023). Agricultural input market access and smallholder farmer adoption behavior in East Africa. *Agricultural Economics*, 54(1), 67-82.

14. Nakasone, E., & Torero, M. (2022). A text message away: ICTs as a tool to improve food security. *Agricultural Economics*, 47(S1), 49-59.

15. One Acre Fund. (2023). *Annual Report 2023: Serving smallholder farmers across Africa*. One Acre Fund Publications.

---

# 6. Appendices

## 6(i). Time Framework / Work Plan

| **Activity** | **Week 1-2** | **Week 3-4** | **Week 5-6** | **Week 7-8** | **Week 9-10** | **Week 11-12** | **Week 13** |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Requirements Gathering & Analysis | ██ | | | | | | |
| Literature Review | ██ | ██ | | | | | |
| System Design (Architecture, ER Diagrams, UI) | | ██ | | | | | |
| User Module Development (Accounts, Profiles) | | | ██ | | | | |
| Marketplace Module (Products, Categories, Orders) | | | ██ | ██ | | | |
| Price Intelligence Module (WFP API, Crowdsourced) | | | | ██ | | | |
| Input Store & Group Buying Module | | | | ██ | ██ | | |
| Weather, Pest Alert & News Modules | | | | | ██ | | |
| Review/Rating & Notification Systems | | | | | ██ | | |
| Testing (Unit, Integration, UAT) | | | | | | ██ | |
| Bug Fixes & Optimization | | | | | | ██ | |
| Documentation & Final Report | | | | | | ██ | ██ |
| Presentation Preparation | | | | | | | ██ |

## 6(ii). Budget

| **Item** | **Description** | **Quantity** | **Unit Cost (UGX)** | **Total (UGX)** |
|----------|----------------|:---:|---:|---:|
| **Equipment** | | | | |
| Laptop computer | Development workstation | 1 | 2,500,000 | 2,500,000 |
| External hard drive | Backup storage (1TB) | 1 | 150,000 | 150,000 |
| **Stationery** | | | | |
| Printing paper (reams) | Documentation and reports | 5 | 25,000 | 125,000 |
| Pens, folders, notebooks | General stationery | - | - | 50,000 |
| **Travel** | | | | |
| Transport for data collection | Visits to 5 districts | 10 trips | 50,000 | 500,000 |
| Local transport | Within-district travel | 20 trips | 10,000 | 200,000 |
| **Subsistence** | | | | |
| Meals during fieldwork | Data collection days | 15 days | 20,000 | 300,000 |
| Accommodation | Overnight stays during rural visits | 5 nights | 60,000 | 300,000 |
| **Research Assistance** | | | | |
| Research assistants | Data collection support | 2 persons × 5 days | 30,000 | 300,000 |
| **Services** | | | | |
| Internet bundles | Development and testing | 3 months | 100,000 | 300,000 |
| Domain and hosting | Web deployment (annual) | 1 year | 250,000 | 250,000 |
| Photocopying | Questionnaires and documents | 200 copies | 500 | 100,000 |
| Binding | Final report copies | 5 copies | 30,000 | 150,000 |
| Printing (color) | Final report and presentation | 5 copies | 40,000 | 200,000 |
| | | | **Grand Total** | **5,425,000** |

## 6(iii). Data Collection Instruments

### QUESTIONNAIRE

**Smart Agri Market: A Web-Based Agricultural Marketplace for Uganda**

**Dear Respondent,**

This questionnaire is designed to collect data for an academic project aimed at developing a web-based agricultural marketplace platform for Ugandan farmers. Your responses will be used strictly for academic purposes and will be treated with utmost confidentiality. Please answer all questions honestly.

---

**SECTION A: Demographic Information**

1. Gender:  [ ] Male  [ ] Female

2. Age Group:  [ ] 18-25  [ ] 26-35  [ ] 36-45  [ ] 46-55  [ ] Above 55

3. District of residence: ____________________

4. Role in agriculture:
   [ ] Farmer  [ ] Consumer/Buyer  [ ] Business (Hotel/Restaurant/School)  [ ] Input Supplier  [ ] Transporter

5. Level of education:
   [ ] No formal education  [ ] Primary  [ ] Secondary  [ ] Diploma  [ ] Degree  [ ] Postgraduate

6. Type of phone owned:
   [ ] Basic/Feature phone  [ ] Smartphone  [ ] Both  [ ] None

7. Do you have access to the internet?  [ ] Yes  [ ] No
   If yes, how often? [ ] Daily  [ ] Weekly  [ ] Occasionally

---

**SECTION B: Agricultural Market Access (For Farmers)**

8. What crops/products do you primarily grow or sell?
   ____________________

9. How do you currently find buyers for your produce?
   [ ] Local market  [ ] Middlemen/Brokers  [ ] Direct to consumers  [ ] Mobile phone (calls/SMS)  [ ] Social media (WhatsApp/Facebook)  [ ] Other: __________

10. How do you determine the selling price for your produce?
    [ ] Set my own price  [ ] Based on middleman's offer  [ ] Ask neighboring farmers  [ ] Check on the radio/TV  [ ] Use a mobile app/website  [ ] Other: __________

11. Have you ever felt cheated on the price of your produce?
    [ ] Never  [ ] Rarely  [ ] Sometimes  [ ] Often  [ ] Always

12. Would you be willing to use a web/mobile platform that shows you real-time market prices for your crops?
    [ ] Yes  [ ] No  [ ] Maybe

---

**SECTION C: Agricultural Inputs Access**

13. Where do you currently buy agricultural inputs (seeds, fertilizers, pesticides)?
    [ ] Local agro-dealer shop  [ ] District town market  [ ] Kampala  [ ] Through a cooperative  [ ] Online  [ ] Other: __________

14. What are the biggest challenges you face when buying agricultural inputs?
    [ ] High prices  [ ] Long distances to shops  [ ] Fake/counterfeit products  [ ] Limited variety  [ ] Lack of information about products  [ ] Other: __________

15. Would you be interested in a group-buying feature where you and other farmers could combine orders to get bulk discounts?
    [ ] Very interested  [ ] Interested  [ ] Neutral  [ ] Not interested

---

**SECTION D: Weather and Agricultural Information**

16. How do you currently get weather information for your farming activities?
    [ ] Radio/TV  [ ] Ask neighbors  [ ] Personal observation  [ ] Mobile phone/internet  [ ] Agricultural extension officer  [ ] Other: __________

17. Have you ever experienced crop loss due to unexpected weather changes?
    [ ] Yes  [ ] No
    If yes, what type? [ ] Drought  [ ] Heavy rain/floods  [ ] Hailstorms  [ ] Pest outbreak  [ ] Other: __________

18. Would weather alerts and planting season recommendations on a digital platform be useful to you?
    [ ] Very useful  [ ] Useful  [ ] Neutral  [ ] Not useful

---

**SECTION E: Technology Adoption Readiness**

19. Have you ever used a mobile app or website for any agricultural activity?
    [ ] Yes  [ ] No
    If yes, which one? ____________________

20. What features would you most like to see on a digital agricultural platform? (Select all that apply)
    [ ] Market price information  [ ] Selling my produce online  [ ] Buying farming inputs online  [ ] Weather alerts  [ ] Pest and disease alerts  [ ] Agricultural news  [ ] Group buying for discounts  [ ] Reviews and ratings for buyers/sellers  [ ] Other: __________

21. What would prevent you from using a web-based agricultural marketplace?
    [ ] No internet access  [ ] Don't know how to use technology  [ ] Don't trust online platforms  [ ] Too expensive (data costs)  [ ] Prefer traditional methods  [ ] Other: __________

---

**Thank you for your participation!**

---

### INTERVIEW GUIDE (For Key Informants)

**Smart Agri Market: A Web-Based Agricultural Marketplace for Uganda**

**Target:** Agricultural extension officers, cooperative leaders, market administrators.

1. In your experience, what are the biggest challenges farmers face in accessing fair market prices for their produce?

2. How do middlemen currently influence price setting in your area, and what impact does this have on farmer incomes?

3. What agricultural information services (digital or otherwise) are currently available to farmers in your district, and how effective are they?

4. In your opinion, what features would a digital agricultural marketplace need to be successfully adopted by farmers in your area?

5. How do farmers in your area currently access agricultural inputs (seeds, fertilizers, pesticides), and what challenges do they face?

6. Would a group-buying feature for agricultural inputs be beneficial for smallholder farmers? Why or why not?

7. How significant is the impact of weather variability on farming activities in your area, and what early warning systems currently exist?

8. What role do you think technology can play in improving the agricultural value chain in Uganda?

---

*End of Proposal*
