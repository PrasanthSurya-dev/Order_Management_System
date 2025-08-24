# Orderlla – Order Management System (OMS)

> A comprehensive digital solution for small businesses to manage orders, inventory, and analytics—built with Python/Flask and Vanilla JavaScript.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)  
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)    
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-lightgrey.svg)](https://sqlite.org)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Live Demo

**[https://orderlla-oms-4116a2547cd5.herokuapp.com/](https://orderlla-oms-4116a2547cd5.herokuapp.com/)**

---

## 📋 Project Overview

Orderlla is a unified platform that gives businesses complete control over their sales by centralizing the entire order lifecycle—from product management and order tracking to real-time sales analytics—eliminating the errors and inefficiencies of manual, spreadsheet-based methods.

**Target Audience:** This project is a portfolio piece aimed at potential employers and technical reviewers, showcasing the ability to build a complete, data-driven web application from the ground up.

**Key Differentiators:**

- **Hybrid Frontend Architecture**:  Demonstrates architectural flexibility by combining a classic, server-rendered admin panel (for robust control) with a dynamic, API-driven customer dashboard (for a fast, modern user experience).
- **Asynchronous Processing**: Features an independent background thread that simulates real-world cron jobs by automatically updating order statuses, showcasing an understanding of processes outside the standard request-response cycle.
- **Business Intelligence Engine**: Moves beyond simple data entry by providing a rich analytics and reporting suite, including interactive KPI widgets and Chart.js-powered visualizations to help business owners make informed, data-driven decisions.
---

## ✨ Features

- **Authentication & Authorization**: Features a role-based login for Customers and Admins with secure, user-specific data access.
- **Dynamic Product Catalog**: Browse, filter, and view detailed product listings.  
- **Real-Time Shopping Cart**: Add, update, and remove items without page reloads.  
- **Full Order Workflow**: Place, track, and cancel orders; inventory auto-restores on cancellations.  
- **Live Order History**: Track status from “Order Received” → “Delivered.”  
- **Admin Dashboard**: CRUD operations for products, orders, and customers.  
- **Interactive Analytics**: KPI widgets (Sales, AOV, Pending Orders) link to detailed Chart.js visualizations.

---

## 🛠️ Tech Stack

| Layer         | Technologies                                  |
|---------------|-----------------------------------------------|
| **Backend**   | Python 3.13 & Flask 2.x,                      |
| **Database**  | SQLite (development) → PostgreSQL (on Supabase for production)|
| **Database Drivers**| `sqlite3` (built-in), `psycopg2` (for PostgreSQL) |
| **Frontend**  | HTML5, CSS3, Vanilla JavaScript (Fetch API)  |
| **Templating**| Jinja2                                        |
| **Charting**  | Chart.js                                      |
| **Deployment**| Heroku, Gunicorn                              |

---

## ⚡ Getting Started

### Prerequisites

- Python 3.8+  
- Git  
- SQLite 3 command-line tool  

### Installation & Setup

1.  **Clone the repository**
    ```bash
    # TODO: Replace <your-username> with your actual GitHub username
    git clone [https://github.com/](https://github.com/)<your-username>/orderlla-oms.git
    cd orderlla-oms
    ```

2.  **Create and activate a virtual environment**
    ```bash
    # Create the environment
    python -m venv .venv
    # Activate on Windows: .venv\Scripts\activate
    # Activate on Mac/Linux: source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up and seed the local database**
    *(This requires a `populate_data.sql` file in your root directory.)*

    Run the command below that matches your terminal.

    ```bash
    # If you are on Mac, Linux, or the old Windows Command Prompt (cmd.exe), use this:
    sqlite3 database.db < populate_data.sql

    # If you are on the modern Windows PowerShell, use this instead:
    Get-Content populate_data.sql | sqlite3 database.db
    ```

6.  **Run the application**
    ```bash
    python app.py
    ```
    The app will be running at **http://127.0.0.1:8080**
    _Default admin: `admin` / `adminpass`_

---

## 📖 Usage Examples

### Customer Dashboard  
Experience a seamless, app-style interface for browsing, cart management, and order tracking without reloads.  
*Customer Dashboard* <img width="2880" height="1520" alt="image" src="https://github.com/user-attachments/assets/1818fb04-3adb-4c18-b680-596b8f0eafa6" />
*Order History* <img width="2878" height="1542" alt="image" src="https://github.com/user-attachments/assets/418b958f-1af6-4f9f-92a9-2b3c8eb31346" />



### Admin Analytics  
An at-a-glance dashboard with clickable KPI widgets linking to detailed, interactive reports.  
*Sales Data* <img width="2880" height="1530" alt="image" src="https://github.com/user-attachments/assets/40cb7e3e-95e4-4fd8-901c-7f7a4085c079" />
*Order Status Distribution* <img width="2878" height="1532" alt="image" src="https://github.com/user-attachments/assets/ee8f8f43-4fc9-47ee-b57d-3b70df51ad34" />
*Payment Method Distribution* <img width="2876" height="1524" alt="image" src="https://github.com/user-attachments/assets/099fcddf-b3a3-463c-9fc9-28f2b491051f" />





---

## 🏗️ Project Architecture

### Folder Structure

```
/Orderlla-OMS
├── app.py
├── populate_data.sql
├── requirements.txt
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── customer_dashboard.js
└── templates/
    ├── admin_aov_report.html
    ├── admin_awaiting_refund.html
    ├── admin_base.html
    ├── admin_customers_list.html
    ├── admin_customer_detail.html
    ├── admin_dashboard.html
    ├── admin_edit_product.html
    ├── admin_orders.html
    ├── admin_order_detail.html
    ├── admin_products.html
    ├── admin_reports.html
    ├── cancel_confirmation.html
    ├── customer_dashboard.html
    ├── login.html
    └── register.html
```

---

## 🔍 System Architecture & Database

```
┌───── Frontend ──────┐
│ • Customer SPA      │
│ • Admin SSR Panels  │
└────────┬────────────┘
         │ REST/JSON
┌────────▼────────────┐
│     Flask API       │
│ • Routes & Sessions │
│ • Background Tasks  │
└────────┬────────────┘
         │ 
┌────────▼────────────┐
│  SQLite / PostgreSQL│
│  Tables:            │
│  customers, products│
│  orders, admin,returns│
└─────────────────────┘
```

### ER Diagram
![ER Diagram](https://github.com/user-attachments/assets/d0aab151-543b-47b8-942b-55a8f576b597)



---

## 🔄 Business Logic & Reports

- **Automated Status Updates**: Hourly thread marks "In Transit" → "Delivered".  
- **Inventory Management**: Stock decremented on order placement; restored on cancellation.  
- **Refund Workflow**: Tracks cancellation and refund initiation via admin route.  
- **KPI Widgets**: Live metrics—Sales Today, Pending Orders, AOV MoM.  
- **Report Visuals**: Bar, pie, and progress-bar charts with date filters.

---

## 🛠️ Error Handling & Testing

- **Backend**: `try…except` for DB ops; `flask.flash()` for user messages.  
- **Frontend**: Fetch error checks with `.then()` & `alert()`.  
- **Testing**: *Recommended*—pytest unit tests for logic, Flask test client for routes.

---

## ⚙️ Performance & Scalability

- Dev: Flask dev server + SQLite (single-user).  
- Prod: Gunicorn/uWSGI + Nginx; PostgreSQL for concurrency & scale; optional Redis caching.

---

## 🚀 Deployment

1. Push to GitHub.  
2. Provision web service on Render/Heroku; link repo.  
3. Build: `pip install -r requirements.txt`  
4. Start: `gunicorn app:app`  
5. Configure `DATABASE_URL` & `SECRET_KEY` env vars.  
6. Seed production DB with modified SQL script.

---

## 🔮 Future Enhancements

- Email/SMS notifications  
- Advanced inventory alerts  
- Payment gateway integration  
- Multi-vendor support  
- PWA + mobile app  
- Full returns management

---

## 🤝 Contributing

Fork, branch, commit, and submit a pull request. Issues and suggestions welcome.

---

## 📝 License

MIT License – see [LICENSE](LICENSE).

---

## 📫 Contact

**LinkedIn:** https://www.linkedin.com/in/suryaprasanth001/  
**Email:** suryaprasanthmedidi3@gmail.com

> ⭐ If you find Orderlla useful, please give it a star!
