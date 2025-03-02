from flask import Blueprint, render_template, request, redirect, url_for, flash, session,make_response
from .models import db, User,Income,Expense,Goal,Budget
from flask_login import login_user, logout_user, login_required, current_user
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from prettytable import PrettyTable
# API routes
api = Blueprint('api', __name__)

@api.route('/')
def index():
    return render_template('landing.html')  # Your landing page

@api.route('/login_page')
def login_page():
    return render_template('login.html')

@api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Form data:", request.form)  # Debugging line
        username = request.form.get('username')  # Use .get() to avoid KeyError
        password = request.form.get('password')  # Use .get() to avoid KeyError
        
        if username is None or password is None:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('api.login'))

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main_routes.home'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
            return redirect(url_for('api.login'))

    return render_template('login.html')

@api.route('/register', methods=['GET','POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Check if the user already exists
    if User.query.filter_by(username=username).first():
        flash('Username already exists. Please choose a different one.', 'danger')
        return redirect(url_for('api.register'))  # Redirect back to index.html

    # Create a new user
    new_user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    flash('Registration successful! You can now log in.', 'success')
    return redirect(url_for('api.login'))  # Redirect back to index.html

@api.route('/about')
def about():
    return render_template('about.html')

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/home')
@login_required  # Protect this route
def home():
    user_id = current_user.id
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    current_budget = Budget.query.filter_by(user_id=user_id).first()
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    if current_budget:
        expendable_balance = (current_budget.limit if current_budget else 0) - current_budget.spent
        return render_template('home.html', incomes=incomes, expenses=expenses, total_income=total_income, total_expense=total_expense, expendable_balance=expendable_balance)
    return render_template('home.html', incomes=incomes, expenses=expenses, total_income=total_income, total_expense=total_expense)


@api.route('/privacy')
def privacy():
    return render_template('terms_privacy.html')

@api.route('/profile')
@login_required 
def profile():
    user = current_user
    return render_template('profile.html',user=user)

@api.route('/update_account', methods=['POST'])
@login_required
def update_account():
    current_user.username = request.form['username']
    current_user.email = request.form['email']
    current_user.bio = request.form['bio']  # Assuming you have a bio field in your User model
    db.session.commit()
    flash('Account updated successfully!', 'success')
    return redirect(url_for('api.profile'))

@api.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    db.session.delete(current_user)  # Delete the current user
    db.session.commit()
    flash('Account deleted successfully!', 'success')
    return redirect(url_for('api.index'))  # Redirect to landing page after deletion

@api.route('/database')
def database():
    users=User.query.all()
    table=PrettyTable()
    table.field_names = ["ID", "Username", "Email","created date"]
    for user in users:
        table.add_row([user.id, user.username, user.email,user.created_at])
    print(table)
    return redirect(url_for('api.index')+ '#footer')

@api.route('/use')
def use():
    return render_template('use.html')

@api.route('/logout')
def logout():
    logout_user()
    session.pop('user_id', None) 
    return redirect(url_for('api.login_page'))

@api.route('/add_income', methods=['POST'])
@login_required
def add_income():
    source = request.form['source']
    amount = float(request.form['amount'])
    user_id = current_user.id  # Get the current user's ID
    new_income = Income(user_id=user_id, amount=amount, category=source, date=datetime.utcnow().date())
    db.session.add(new_income)
    db.session.commit()
    flash('Income added successfully!', 'success')
    return redirect(url_for('main_routes.home'))

@api.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    category = request.form['category']
    amount = float(request.form['amount'])
    user_id = current_user.id  # Get the current user's ID

    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    total_money=total_income-total_expense
    if amount>total_money:
        flash("alert..! you don't have money in your account for this expense")
        return redirect(url_for('main_routes.home'))
    new_expense = Expense(user_id=user_id, amount=amount, category=category, date=datetime.utcnow().date())
    db.session.add(new_expense)
    current_budget = Budget.query.filter_by(user_id=user_id, month=datetime.utcnow().strftime("%B %Y")).first()
    if current_budget:
        if current_budget.spent+amount > current_budget.limit :
            flash("alert..! you are exceeding the monthly budget amount")
            return redirect(url_for('main_routes.home'))
        current_budget.spent += amount  # Increment the spent amount
        db.session.commit()  
    db.session.commit()
    flash('Expense added successfully!', 'success')
    return redirect(url_for('main_routes.home'))

@main_routes.route('/records')
@login_required
def records():
    user_id = current_user.id
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    return render_template('records.html', incomes=incomes, expenses=expenses)

@api.route('/edit_income/<int:income_id>', methods=['POST'])
def edit_income(income_id):
    income = Income.query.get_or_404(income_id)
    income.category = request.form['source']
    income.amount = float(request.form['amount'])
    db.session.commit()
    flash('Income updated successfully!', 'success')
    return redirect(url_for('main_routes.records'))

@api.route('/delete_income/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    income = Income.query.get_or_404(income_id)
    db.session.delete(income)
    db.session.commit()
    flash('Income deleted successfully!', 'success')
    return redirect(url_for('main_routes.records'))

@api.route('/edit_expense/<int:expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    new_amount = float(request.form['amount'])
    category = request.form['category']
    user_id=current_user.id
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    total_money=total_income-total_expense
    if  (new_amount - expense.amount)>total_money:
        flash("alert..! you don't have money in your account for this expense")
        return redirect(url_for('main_routes.home'))
    # Update the budget's spent amount
    current_budget = Budget.query.filter_by(user_id=expense.user_id, month=datetime.utcnow().strftime("%B %Y")).first()
    if current_budget:
        # Adjust the spent amount
        current_budget.spent += (new_amount - expense.amount)  # Update spent amount
        db.session.commit()  # Commit the changes to the database

    # Update the expense
    expense.amount = new_amount
    expense.category = category
    db.session.commit()
    return redirect(url_for('main_routes.records'))

@api.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    user_id = expense.user_id
    current_budget = Budget.query.filter_by(user_id=user_id, month=datetime.utcnow().strftime("%B %Y")).first()
    if current_budget:
        current_budget.spent = (current_budget.spent or 0) - expense.amount  # Decrement the spent amount
        db.session.commit()
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('main_routes.records'))

@api.route('/goal')
@login_required
def goal():
    user_id = current_user.id  # Correctly assign user_id without a comma
    goals = Goal.query.filter_by(user_id=user_id).all()  # Fetch goals for the current user
    current_date = datetime.now().date()  # Get the current date
    current_budget = Budget.query.filter_by(user_id=user_id).first()

    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    current_budget = Budget.query.filter_by(user_id=user_id).first()
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    total_money=total_income-total_expense
    total_goal_money = sum(goal.current_amount for goal in goals)
    return render_template('goals.html', goals=goals, current_date=current_date, goal_money=total_goal_money,user=current_user,budget=current_budget,total_money=total_money)  # Pass goals and user to the template

@api.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    if request.method == 'POST':
        goal_name = request.form['goalName']
        target_amount = float(request.form['targetAmount'])
        current_amount = float(request.form['currentAmount'])
        deadline = request.form['deadline']

        if target_amount < current_amount:
            flash('Target amount must be greater than current amount.', 'danger')
            return redirect(url_for('api.goal'))  # Redirect to the same page to show the error
        user_id=current_user.id
        incomes = Income.query.filter_by(user_id=user_id).all()
        expenses = Expense.query.filter_by(user_id=user_id).all()
        total_income = sum(income.amount for income in incomes)
        total_expense = sum(expense.amount for expense in expenses)
        total_money=total_income-total_expense
        if total_money < current_amount :
            flash('you dont have funds to invest in goals.', 'danger')
            return redirect(url_for('api.goal'))
        new_goal = Goal(
            user_id=current_user.id,
            goal_name=goal_name,
            target_amount=target_amount,
            current_amount=current_amount,
            deadline=datetime.strptime(deadline, '%Y-%m-%d')
        )
        db.session.add(new_goal)
        db.session.commit()
        flash('Goal added successfully!', 'success')
        return redirect(url_for('api.goal'))  # Redirect to the goals page to show the updated list

    goals = Goal.query.filter_by(user_id=current_user.id).all()
    current_date = datetime.now().date()
    return render_template('goals.html', goals=goals, current_date=current_date, user=current_user)

@api.route('/goals/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully!', 'success')
    return '', 204  # No content response

@api.route('/goals/<int:goal_id>', methods=['POST'])
@login_required
def update_or_delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    if 'goalName' in request.form:  # Update operation

        goal.goal_name = request.form['goalName']
        goal.target_amount = float(request.form['targetAmount'])
        goal.current_amount = float(request.form['currentAmount'])
        goal.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
        db.session.commit()
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('api.goal'))

    else:# Delete operation
        db.session.delete(goal)
        db.session.commit()
        flash('Goal deleted successfully!', 'success')
        return redirect(url_for('api.goal'))

@api.route('/budget')
@login_required
def budget():
    user_id = current_user.id
    current_budget = Budget.query.filter_by(user_id=user_id).first()
    now = datetime.now()
    current_month = now.strftime("%B %Y")
    # Get the spent amount directly from the current budget
    spent_amount = current_budget.spent if current_budget else 0
    # Calculate savings
    savings = (current_budget.limit if current_budget else 0) - spent_amount
    previous_budgets = Budget.query.filter(Budget.user_id == user_id).all()  # Fetch all previous budgets

    return render_template(
        'budget.html',
        current_budget=current_budget,
        current_month=current_month,
        current_budget_id=current_budget.id if current_budget else None,
        total_expenses=spent_amount,  # Use spent amount as total expenses
        savings=savings,
        previous_budgets=previous_budgets
    )

@api.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    user_id = current_user.id
    new_budget_amount = request.form['new_budget']
    new_budget = Budget(user_id=user_id, month=datetime.now().strftime("%B %Y"), limit=new_budget_amount)
    db.session.add(new_budget)
    db.session.commit()
    
    return redirect(url_for('api.budget'))

@api.route('/edit_budget/<int:budget_id>', methods=['POST'])
@login_required
def edit_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    new_amount = request.form['new_budget']
    budget.limit = new_amount
    db.session.commit()
    return redirect(url_for('api.budget'))

@api.route('/delete_budget/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    db.session.delete(budget)
    db.session.commit()
    return redirect(url_for('api.budget'))

