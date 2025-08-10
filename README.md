# Orderlla – Full-Stack Order Management System (OMS)

> A comprehensive digital solution for small businesses to manage orders, inventory, and analytics—built with Python/Flask and Vanilla JavaScript.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)  
[![Flask Version](https://img.shields.io/badge/flask-3.0-black.svg)](https://flask.palletsprojects.com/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Live Demo

*(Link to your deployed application goes here)*

---

## 📋 Project Overview

Orderlla replaces manual, spreadsheet-based order tracking with a unified platform that handles product management, order lifecycle, and real-time analytics.

**Target Audience:** Potential employers and technical reviewers assessing full-stack development proficiency.

**Unique Highlights:**
- **Hybrid Frontend Architecture**: SSR-based admin panel with an SPA-style customer dashboard.
- **Asynchronous Background Tasks**: Hourly automated order-status updates.
- **Data-Driven Analytics**: Interactive KPI widgets and Chart.js-powered reports.

---

## ✨ Features

- **Customer Authentication**: Secure registration & login with hashed passwords.  
- **Dynamic Product Catalog**: Browse, filter, and view detailed product listings.  
- **Real-Time Shopping Cart**: Add, update, and remove items without page reloads.  
- **Full Order Workflow**: Place, track, and cancel orders; inventory auto-restores on cancellations.  
- **Live Order History**: Track status from “Order Received” → “Delivered.”  
- **Admin Dashboard**: CRUD operations for products, orders, and customers.  
- **Interactive Analytics**: KPI widgets (Sales, AOV, Pending Orders) link to detailed Chart.js visualizations.  
- **Returns Management Ready**: Database schema includes a `returns` table for future enhancements.

---

## 🛠️ Tech Stack

| Layer         | Technologies                                  |
|---------------|-----------------------------------------------|
| **Backend**   | Python 3.8+ & Flask 2.x, SQLAlchemy           |
| **Database**  | SQLite (development) → PostgreSQL (production)|
| **Frontend**  | HTML5, CSS3, Vanilla JavaScript (Fetch API)  |
| **Templating**| Jinja2                                        |
| **Charting**  | Chart.js                                      |
| **Security**  | Werkzeug password hashing, Flask sessions     |
| **Deployment**| Render / Heroku, Gunicorn, Nginx             |

---

## ⚡ Getting Started

### Prerequisites

- Python 3.8+  
- Git  
- SQLite 3 command-line tool  

### Installation & Setup

```bash
# 1. Clone
git clone https://github.com/<your-username>/orderlla-oms.git
cd orderlla-oms

# 2. Virtual Environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Database Initialization (one-time)
sqlite3 database.db < populate_data.sql
# PowerShell:
Get-Content populate_data.sql | sqlite3 database.db

# 5. Run Locally
python app.py
```

Open your browser at **http://127.0.0.1:8080**  
_Default admin: `admin` / `admin123` (change immediately!)_

---

## 📖 Usage Examples

### Customer Dashboard  
Experience a seamless, app-style interface for browsing, cart management, and order tracking without reloads.  
*(Insert GIF/screenshot here)*

### Admin Analytics  
An at-a-glance dashboard with clickable KPI widgets linking to detailed, interactive reports.  
*(Insert GIF/screenshot here)*

---

## 🏗️ Project Architecture

### Folder Structure

```
/
├── app.py
├── database.db
├── populate_data.sql
├── requirements.txt
├── static/
│   ├── css/style.css
│   ├── images/… 
│   └── js/customer_dashboard.js
└── templates/
    ├── admin_base.html
    ├── admin_dashboard.html
    ├── … (other admin pages)
    ├── customer_dashboard.html
    └── login.html, register.html, etc.
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
         │ ORM (SQLAlchemy)
┌────────▼────────────┐
│  SQLite / PostgreSQL│
│  Tables:            │
│  customers, products│
│  orders, admin,returns│
└─────────────────────┘
```

### ER Diagram

```erDiagram
    CUSTOMERS {
      int id PK
      string username UNIQUE
      string password
      string name
      string address
      string contact
    }
    ORDERS {
      int id PK
      int customer_id FK
      JSON items_json
      real total
      string payment_method
      string status
      date order_date
      date delivery_date
      date actual_delivery_date
      string cancellation_refund
    }
    PRODUCTS {
      int id PK
      string name
      string description
      real price
      int stock
      string image_url
    }
    ADMIN {
      int id PK
      string username UNIQUE
      string password
    }
    RETURNS {
      int id PK
      int order_id FK
      date return_date
      string status
    }

    CUSTOMERS ||--o{ ORDERS : places
    PRODUCTS ||--o{ ORDERS : included_in
    ORDERS ||--o{ RETURNS : may_have
```

---

## 🔐 Authentication & Security

- Passwords hashed with **Werkzeug** (PBKDF2-SHA256).  
- Session data signed by `app.secret_key`.  
- Route protection via Flask session decorators.  
- CSRF mitigation via session tokens (future: Flask-WTF).

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

**Portfolio:** <your-portfolio-url>  
**LinkedIn:** <your-linkedin>  
**Email:** <your-email>  

> ⭐ If you find Orderlla useful, please give it a star!
