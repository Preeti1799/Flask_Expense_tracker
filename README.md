# Flask Expense Tracker 🧾

A simple yet powerful expense tracking web application built using **Flask**, **Flask-Login**, and **SQLite**. This app lets you securely log, view, filter, and analyze your expenses with an intuitive interface.

## 🔒 Authentication
- User Sign Up & Login
- Password hashing with Flask-Login

## 💼 Features
- Add new expenses with category, amount, and description
- View all expenses
- Filter by category or date
- View total monthly expenses
- See top spending categories
- Delete specific expenses

## 🧱 Tech Stack
- Python (Flask Framework)
- SQLite + SQLAlchemy ORM
- HTML, CSS (Jinja Templates)
- Hosted on **Render**

## 🚀 Getting Started

### Requirements
\\\ash
pip install -r requirements.txt
\\\

### Run Locally
\\\ash
python app.py
\\\

## 🌐 Deployment
Deployed using **Render** with Gunicorn:

- Add a Procfile: web: gunicorn app:app
- Push code to GitHub
- Connect GitHub repo to Render

🔗 Live App: [https://flask-expense-tracker-en0l.onrender.com](https://flask-expense-tracker-en0l.onrender.com)

## 📂 Directory Structure
\\\
├── app.py
├── config.py
├── requirements.txt
├── templates/
├── static/
├── users.db
└── Procfile
\\\

## 👩‍💻 Author
Made with ❤️ by Preeti Paswan
