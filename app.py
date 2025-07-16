
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import csv

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
print("Using database:", app.config['SQLALCHEMY_DATABASE_URI'])


db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

# ------------------------ EXPENSE TRACKER ------------------------
@app.route("/", methods=["GET"])
@login_required
def home():
    selected_month = request.args.get("month")
    selected_date = request.args.get("date")

    query = Expense.query.filter_by(user_id=current_user.id)

    if selected_month:
        try:
            year, month = map(int, selected_month.split("-"))
            query = query.filter(
                db.extract("year", Expense.date) == year,
                db.extract("month", Expense.date) == month
            )
        except ValueError:
            flash("Invalid month format. Use YYYY-MM.")

    if selected_date:
        try:
            selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            query = query.filter(Expense.date == selected_date_obj)
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.")

    expenses = query.order_by(Expense.date.desc()).all()
    total = sum(exp.amount for exp in expenses)

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        selected_month=selected_month,
        selected_date=selected_date
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        date = datetime.now().date()

        new_expense = Expense(
            user_id=current_user.id,
            date=date,
            amount=float(amount),
            category=category,
            description=description
        )

        db.session.add(new_expense)
        db.session.commit()
        flash("Expense added successfully.")
        return redirect(url_for("home")) 

    return render_template("add.html") 



@app.route("/view")
@login_required
def view_expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template("view.html", expenses=expenses)


@app.route("/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash("You are not authorized to delete this expense.")
        return redirect(url_for("home"))

    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.")
    return redirect(url_for("view_expenses"))


@app.route("/top-category")
@login_required
def top_spending_category():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    category_totals = {}

    for exp in expenses:
        category = exp.category.strip().title()
        category_totals[category] = category_totals.get(category, 0) + exp.amount

    sorted_totals = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    return render_template("top_category.html", sorted_totals=sorted_totals)


@app.route("/filter-category", methods=["GET", "POST"])
@login_required
def filter_by_category():
    expenses = []
    total = 0
    selected_category = ""

    if request.method == "POST":
        selected_category = request.form["category"].strip().lower()
        expenses = Expense.query.filter_by(user_id=current_user.id).filter(
            db.func.lower(Expense.category) == selected_category
        ).all()

        total = sum(exp.amount for exp in expenses)

    return render_template("filter_category.html", expenses=expenses, total=total, selected_category=selected_category)


# ------------------------ MAIN ------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
