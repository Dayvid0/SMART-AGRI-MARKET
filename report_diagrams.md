 # CHAPTER FOUR: SYSTEM ANALYSIS AND DESIGN DIAGRAMS

This document contains the system design models and diagrams for the Smart Agri-Market Platform. The diagrams are generated using **Mermaid.js** syntax, which can be rendered directly in most modern Markdown viewers, GitHub, or by pasting the code blocks into [Mermaid Live Editor](https://mermaid.live).

---

## 4.6 High Level Architecture of the Developed System

The system follows a three-tier architecture utilizing the Django MVT (Model-View-Template) pattern.

```mermaid
architecture-beta
    group client(cloud)[Client Tier]
    group server(cloud)[Application Tier - Django]
    group data(database)[Data Tier]

    service browser(internet)[Web Browser / PWA] in client
    
    service views(server)[Views / Controllers] in server
    service templates(server)[Templates / UI] in server
    service models(server)[Models / ORM] in server
    
    service db(database)[Database] in data
    
    browser:R --> L:templates
    templates:R --> L:views
    views:R --> L:models
    models:R --> L:db
```

*(Alternatively, standard flowchart representation of the architecture)*

```mermaid
graph TD
    subgraph Client Tier
        B[Web Browser / Mobile PWA]
    end
    
    subgraph Application Tier [Django Server]
        URL[URL Dispatcher]
        V[Views / Business Logic]
        T[Templates / HTML]
        M[Models / ORM]
    end
    
    subgraph Data Tier
        DB[(Relational Database)]
    end
    
    B -- HTTP Request --> URL
    URL --> V
    V -- Data Request --> M
    M -- SQL Query --> DB
    DB -- Results --> M
    M -- Data Objects --> V
    V -- Context --> T
    T -- Rendered HTML --> V
    V -- HTTP Response --> B
```

---

## 4.7 The Flow Chart of the Developed System

This flowchart illustrates the general user journey and decision logic within the platform.

```mermaid
flowchart TD
    Start([Start]) --> Login{Is User Logged In?}
    Login -- No --> Register[Register / Login]
    Register --> Dashboard
    Login -- Yes --> Dashboard[User Dashboard]
    
    Dashboard --> Role{User Role?}
    
    Role -- Buyer --> Browse[Browse Marketplace / Input Store]
    Role -- Farmer --> Manage[Manage Farm Products]
    Role -- Transporter --> Deliver[View Delivery Requests]
    
    Browse --> Action{Action?}
    Action -- Buy Product --> Checkout[Checkout Flow]
    Action -- Negotiate --> Chat[Chat / Negotiate with Farmer]
    Chat --> Deal{Deal Accepted?}
    Deal -- Yes --> Checkout
    Deal -- No --> Chat
    
    Checkout --> Order[Place Order]
    Order --> DeliveryReq[Auto-Request Transport]
    DeliveryReq --> Deliver
    
    Deliver --> Accept[Accept Delivery]
    Accept --> Transit[In Transit]
    Transit --> Dropoff[Mark as Delivered]
    
    Dropoff --> Confirm[Buyer Confirms Receipt]
    Confirm --> Complete([End Process])
```

---

## 4.8 The Context Diagram (Level 0 DFD)

The Context Diagram shows the system as a single process interacting with external entities (actors).

```mermaid
flowchart LR
    Buyer((Buyer))
    Farmer((Farmer))
    Supplier((Input Supplier))
    Transporter((Transporter))
    
    System((("Smart Agri-Market\nSystem")))
    
    Buyer -- "Searches products, Places Orders,\n Makes Payments, Confirms Delivery" --> System
    System -- "Order Confirmations, Receipts,\n Deal Offers" --> Buyer
    
    Farmer -- "Manages Products, Negotiates Deals,\n Updates Status" --> System
    System -- "Order Notifications, Chat Messages" --> Farmer
    
    Supplier -- "Lists Agricultural Inputs,\n Creates Group Buys" --> System
    System -- "Input Orders, Group Buy Updates" --> Supplier
    
    Transporter -- "Accepts Delivery Requests,\n Updates Delivery Status" --> System
    System -- "Available Delivery Jobs" --> Transporter
```

---

## 4.8.1 The Level One DFD

This diagram breaks the main system down into major sub-processes.

```mermaid
flowchart TD
    %% External Entities
    B((Buyer))
    F((Farmer))
    T((Transporter))
    
    %% Processes
    P1((1.0 User\nManagement))
    P2((2.0 Product\nManagement))
    P3((3.0 Order\nProcessing))
    P4((4.0 Delivery\nManagement))
    P5((5.0 Negotiation\nChat))
    
    %% Data Stores
    D1[(D1: Users)]
    D2[(D2: Products)]
    D3[(D3: Orders)]
    D4[(D4: Chat/Deals)]
    
    %% Data Flows
    B & F & T -->|Credentials| P1
    P1 -->|Store User| D1
    
    F -->|Product Details| P2
    P2 -->|Store Product| D2
    
    B -->|Search Query| P2
    P2 -->|Product List| B
    
    B & F -->|Messages / Offers| P5
    P5 -->|Store Chat| D4
    P5 -->|Deal Details| P3
    
    B -->|Checkout Data| P3
    P3 -->|Store Order| D3
    P3 -->|Order Notification| F
    
    P3 -->|Auto-Generate Request| P4
    P4 -->|Available Jobs| T
    T -->|Status Update| P4
    P4 -->|Delivery Status| B
```

---

## 4.9 The Use Case Diagram

*Note: In Mermaid, Use Case diagrams are drawn using flowcharts or state diagrams styled to look like Use Cases.*

```mermaid
flowchart LR
    %% Actors
    Buyer((Buyer))
    Farmer((Farmer))
    Transporter((Transporter))
    Supplier((Input Supplier))
    
    %% System Boundary
    subgraph Smart Agri-Market System
        UC1([Register/Login])
        UC2([Manage Products])
        UC3([Browse & Search])
        UC4([Negotiate Price])
        UC5([Place Order])
        UC6([Manage Group Buys])
        UC7([Accept Delivery Request])
        UC8([Confirm Delivery Receipt])
    end
    
    %% Relationships
    Buyer --> UC1
    Farmer --> UC1
    Transporter --> UC1
    Supplier --> UC1
    
    Farmer --> UC2
    Supplier --> UC2
    
    Buyer --> UC3
    Farmer --> UC3
    
    Buyer --> UC4
    Farmer --> UC4
    
    Buyer --> UC5
    
    Supplier --> UC6
    Buyer --> UC6
    
    Transporter --> UC7
    
    Buyer --> UC8
    Transporter --> UC8
```

---

## 4.10 Entity Relationship Diagram (ERD)

Shows the database structure and relationships between core models.

```mermaid
erDiagram
    USER ||--o{ PRODUCT : "creates"
    USER ||--o{ ORDER : "places (buyer)"
    USER ||--o{ ORDER : "receives (farmer)"
    USER ||--o{ CHAT_THREAD : "participates"
    
    PRODUCT ||--o{ ORDER_ITEM : "included in"
    AGRICULTURAL_INPUT ||--o{ ORDER_ITEM : "included in"
    
    ORDER ||--|{ ORDER_ITEM : "contains"
    ORDER ||--o| DELIVERY_REQUEST : "generates"
    
    TRANSPORTER_PROFILE |o--o{ DELIVERY_REQUEST : "accepts"
    USER ||--|| TRANSPORTER_PROFILE : "has"
    
    CHAT_THREAD ||--o{ NEGOTIATED_DEAL : "produces"
    NEGOTIATED_DEAL |o--o| ORDER : "converted to"

    USER {
        int id PK
        string username
        string user_type
        string phone
    }
    PRODUCT {
        int id PK
        string name
        float price
        int farmer_id FK
    }
    ORDER {
        int id PK
        string order_number
        float total_amount
        string status
        int buyer_id FK
        int farmer_id FK
    }
    ORDER_ITEM {
        int id PK
        int quantity
        float unit_price
        int order_id FK
        int product_id FK
    }
    DELIVERY_REQUEST {
        int id PK
        string status
        int order_id FK
        int transporter_id FK
    }
```

---

## 4.11 Dynamic Modeling

### 4.11.1 Activity Diagram (Order Placement Flow)

Shows the step-by-step activity of placing an order.

```mermaid
stateDiagram-v2
    [*] --> BrowseProducts
    BrowseProducts --> SelectProduct
    SelectProduct --> ActionChoice
    
    state ActionChoice <<choice>>
    ActionChoice --> CheckoutCart : Click Order Now
    ActionChoice --> Negotiate : Click Negotiate
    
    Negotiate --> DealAgreed
    DealAgreed --> CheckoutCart : Proceed to Checkout
    
    CheckoutCart --> SelectDelivery
    SelectDelivery --> ConfirmOrder
    
    ConfirmOrder --> SystemCreatesOrder
    
    state DeliveryChoice <<choice>>
    SystemCreatesOrder --> DeliveryChoice
    
    DeliveryChoice --> AutoCreateDelivery : Platform Transport Selected
    DeliveryChoice --> SkipDelivery : Self Pickup Selected
    
    AutoCreateDelivery --> EndOrder
    SkipDelivery --> EndOrder
    
    EndOrder --> [*]
```

### 4.11.2 Sequence Diagram (Delivery Automation)

Illustrates the time-based communication between objects when an order is placed and delivered.

```mermaid
sequenceDiagram
    actor Buyer
    participant System
    participant Farmer
    participant Transporter

    Buyer->>System: Place Order (Platform Delivery)
    activate System
    System-->>Farmer: Notification: New Order
    System->>System: Create Order (Status: Pending)
    System->>System: Auto-create DeliveryRequest (Status: Open)
    System-->>Transporter: Broadcast: Delivery Job Available
    System-->>Buyer: Order Confirmation Display
    deactivate System
    
    Transporter->>System: Accept Delivery Request
    activate System
    System->>System: Update Delivery (Status: Assigned)
    System-->>Buyer: Notification: Transporter Assigned
    deactivate System
    
    Transporter->>System: Mark as Delivered
    activate System
    System->>System: Update Order (Status: Delivered)
    System-->>Buyer: Notification: Please Confirm Receipt
    deactivate System
    
    Buyer->>System: Click "Confirm Receipt"
    activate System
    System->>System: Update Order (Status: Completed)
    System-->>Farmer: Notification: Order Completed & Funds Cleared
    deactivate System
```

### 4.11.3 Collaboration Diagram

Since Mermaid does not have a native Collaboration Diagram (Communication Diagram) syntax, we use a flowchart to represent the object interactions and sequence numbers.

```mermaid
flowchart TD
    B(1: Buyer Object)
    C(2: Checkout Controller)
    O(3: Order Model)
    D(4: DeliveryRequest Model)
    T(5: Transporter Object)

    B -->|1. submitOrder()| C
    C -->|2. create()| O
    O -->|3. save()| O
    C -->|4. autoRequest()| D
    D -->|5. notifyAvailable()| T
    T -->|6. acceptDelivery()| D
```

### 4.11.4 State Chart Diagram (Order Lifecycle)

Shows the various states an `Order` object goes through during its lifecycle.

```mermaid
stateDiagram-v2
    [*] --> Pending : Order Placed
    
    Pending --> Confirmed : Farmer Approves
    Pending --> Cancelled : Buyer Cancels
    
    Confirmed --> Processing : Farmer Prepares Goods
    Confirmed --> Cancelled : Order Terminated
    
    Processing --> Delivered : Transporter Drops Off
    
    Delivered --> Completed : Buyer Confirms Receipt
    
    Completed --> [*]
    Cancelled --> [*]
```
