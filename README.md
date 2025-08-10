# Orderlla - Full-Stack Order Management System
A comprehensive OMS built with Python/Flask and Vanilla JS.
## Features
- Customer Dashboard (Order, Track, Cancel)
- Admin Panel (Manage Orders, Products, Customers, View Analytics)
## Tech Stack
- Backend: Python, Flask
- Database: SQLite
- Frontend: HTML, CSS, Vanilla JS
## How to Run
1. `git clone <repo_url>`
2. `cd <repo_folder>`
3. `python -m venv .venv`
4. `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac/Linux)
5. `pip install -r requirements.txt`
6. `python app.py` (This creates the empty db)
7. Stop the server (Ctrl+C).
8. `sqlite3 database.db < populate_data.sql` (to add sample data)
9. `python app.py` (to run the app with data)