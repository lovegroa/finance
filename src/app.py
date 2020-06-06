from datetime import datetime, timedelta, date
import json
from dateutil.relativedelta import *

from flask import Flask, render_template, session, request, make_response

from src.common.database import Database
from src.models.account import Account
from src.models.chart import Chart
from src.models.expense import Expense
from src.models.target import Target
from src.models.user import User

app = Flask(__name__)
app.secret_key = "alex"


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/')
def home_template():
    if session.get('email') is None:

        return render_template('login.html')

    else:

        user = User.get_by_email(session['email'])

        # Total accounts
        accounts = Account.find_accounts(user._id)
        account_total = Account.total_accounts(accounts)

        expenses = Expense.find_expenses(user._id)
        expense_total = 0

        targets = Target.from_mongo(user._id)
        print('expenses type')

        expenses_in_period = []

        for expense in expenses:

            if expense['expense_date'] <= targets.target_date and expense['paid'] == 0:
                expenses_in_period.append(expense)
                if expense['debit'] == 1:
                    expense_total = expense_total + float(expense['amount'])

                else:
                    expense_total = expense_total - float(expense['amount'])
        start_date = date.today().strftime("%Y-%m-%d")
        datetime.strptime(targets.target_date, '%Y-%m-%d').date()
        days = (datetime.strptime(targets.target_date, '%Y-%m-%d').date() - datetime.strptime(start_date,
                                                                                              '%Y-%m-%d').date()).days + 1

        cash_remaining = account_total - float(targets.amount) - expense_total
        print(cash_remaining)
        cash_per_day = cash_remaining / days

        base = datetime.today()
        chart_labels = [(base + timedelta(days=x)).strftime("%d %m") for x in range(days)]

        charts = Chart(accounts=accounts, expenses=expenses)

        data_list = charts.amount_chart(cash_per_day=cash_per_day, days=days, account_total=account_total)

        print(data_list)

        return render_template('home.html', datalist=data_list, chart_labels=chart_labels, account_total=account_total,
                               cash_remaining=cash_remaining,
                               cash_per_day=cash_per_day, days=days, targets=targets, expenses=expenses,
                               expense_total=expense_total, start_date=start_date,
                               expenses_in_period=expenses_in_period, accounts=accounts)


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route('/auth/login', methods=['POST'])
def login_user():
    #email = request.form['email']
    #password = request.form['password']

    #if User.login_valid(email, password):
    #    User.login(email)
    #else:
    #    session['email'] = None

    #return make_response(home_template())
    return make_response(login_template())


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.route('/auth/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']

    User.register(email, password)

    return render_template("home.html", email=session['email'])


@app.route('/accounts')
def accounts_template():
    user = User.get_by_email(session['email'])
    accounts = Account.find_accounts(user._id)
    account_total = Account.total_accounts(accounts)

    return render_template('accounts.html', accounts=accounts, account_total=account_total)


@app.route('/accounts/add', methods=['POST', 'GET'])
def add_account():
    if request.method == 'GET':
        return make_response(accounts_template())
    else:
        name = request.form['name']
        amount = 0 if request.form['amount'] == '' else request.form['amount']
        min_amount = 0 if request.form['min_amount'] == '' else request.form['min_amount']
        debit = 1 if request.form['debit'] == 'Debit' else 0
        colour = '#FFFFFF' if request.form['colour'] == '' else request.form['colour']
        priority = 1 if "priority" in request.form else 0
        include_in_calculations = 1 if "include_in_calculations" in request.form else 0
        user = User.get_by_email(session['email'])

        new_account = Account(user_id=user._id, name=name, amount=amount, min_amount=min_amount, debit=debit,
                              colour=colour, priority=priority, include_in_calculations=include_in_calculations)

        new_account.save_to_mongo()

        return make_response(accounts_template())


@app.route('/accounts/update', methods=['POST', 'GET'])
def update_account():
    if request.method == 'GET':
        return make_response(accounts_template())
    else:
        id = request.form['id']
        name = request.form['name']
        amount = 0 if request.form['amount'] == '' else request.form['amount']
        min_amount = 0 if request.form['min_amount'] == '' else request.form['min_amount']
        debit = 1 if request.form['debit'] == 'Debit' else 0
        colour = '#FFFFFF' if request.form['colour'] == '' else request.form['colour']
        priority = 1 if "priority" in request.form else 0
        include_in_calculations = 1 if "include_in_calculations" in request.form else 0
        user = User.get_by_email(session['email'])

        new_account = Account(_id=id, user_id=user._id, name=name, amount=amount, min_amount=min_amount, debit=debit,
                              colour=colour, priority=priority, include_in_calculations=include_in_calculations)

        new_account.update_mongo()

        return make_response(accounts_template())


@app.route('/accounts/remove', methods=['POST', 'GET'])
def remove_account():
    if request.method == 'GET':
        return make_response(accounts_template())
    else:
        id = request.form['id']

        Account.remove_from_mongo(id)

        return make_response(accounts_template())


@app.route('/targets')
def targets_template():
    user = User.get_by_email(session['email'])

    targets = Target.from_mongo(user._id)
    return render_template('targets.html', targets=targets)


@app.route('/targets/update', methods=['POST', 'GET'])
def update_target():
    if request.method == 'GET':
        return make_response(targets_template())
    else:
        id = request.form['id']
        amount = request.form['amount']
        target_date = datetime.utcnow().strftime("%Y-%m-%d") if request.form['target_date'] == '' else request.form[
            'target_date']

        user = User.get_by_email(session['email'])

        new_target = Target(_id=id, user_id=user._id, amount=amount, target_date=target_date)

        new_target.update_mongo()

        return make_response(home_template())


@app.route('/targets/add', methods=['POST', 'GET'])
def add_target():
    if request.method == 'GET':
        return make_response(targets_template())
    else:

        amount = request.form['amount']
        target_date = datetime.utcnow().strftime("%Y-%m-%d") if request.form['target_date'] == '' else request.form[
            'target_date']

        user = User.get_by_email(session['email'])

        new_target = Target(user_id=user._id, amount=amount, target_date=target_date)

        new_target.save_to_mongo()

        return make_response(targets_template())


@app.route('/expenses')
def expenses_template():
    user = User.get_by_email(session['email'])

    expenses = Expense.find_expenses(user._id)
    expense_total = Expense.total_expenses(expenses)

    # required to list the accounts in the form
    accounts = Account.find_accounts(user._id)

    return render_template('expenses.html', expenses=expenses, accounts=accounts, expense_total=expense_total)


@app.route('/expenses/add', methods=['POST', 'GET'])
def add_expenses():
    if request.method == 'GET':
        return make_response(accounts_template())
    else:
        name = request.form['name']
        debit = 1 if request.form['debit'] == 'Debit' else 0
        amount = 0 if request.form['amount'] == '' else request.form['amount']
        account_id = request.form['account_id']
        frequency = request.form['frequency']
        start_date = datetime.utcnow() if request.form['start_date'] == '' else datetime.strptime(
            request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.utcnow() if request.form['end_date'] == '' else datetime.strptime(request.form['end_date'],
                                                                                              '%Y-%m-%d').date()
        paid = 1 if "paid" in request.form else 0

        user = User.get_by_email(session['email'])

        if frequency == 'Once':

            temp_expense_date = start_date.strftime("%Y-%m-%d")
            new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
                                  expense_date=temp_expense_date, paid=paid)
            new_expense.save_to_mongo()

        elif frequency == 'Daily':

            expense_date = start_date
            while expense_date <= end_date:
                temp_expense_date = expense_date.strftime("%Y-%m-%d")
                new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
                                      expense_date=temp_expense_date, paid=paid)
                new_expense.save_to_mongo()
                expense_date = expense_date + timedelta(days=1)

        elif frequency == 'Weekly':

            expense_date = start_date
            while expense_date <= end_date:
                temp_expense_date = expense_date.strftime("%Y-%m-%d")
                new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
                                      expense_date=temp_expense_date, paid=paid)
                new_expense.save_to_mongo()
                expense_date = expense_date + timedelta(days=7)

        elif frequency == 'Monthly':

            expense_date = start_date
            count = 1
            while expense_date <= end_date:
                temp_expense_date = expense_date.strftime("%Y-%m-%d")
                new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
                                      expense_date=temp_expense_date, paid=paid)
                new_expense.save_to_mongo()
                expense_date = start_date + relativedelta(months=+count)
                count = count + 1

        elif frequency == 'Yearly':

            expense_date = start_date
            count = 1
            while expense_date <= end_date:
                print(expense_date)
                temp_expense_date = expense_date.strftime("%Y-%m-%d")
                new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
                                      expense_date=temp_expense_date, paid=paid)
                new_expense.save_to_mongo()
                expense_date = start_date + relativedelta(years=+count)
                count = count + 1

        return make_response(expenses_template())


@app.route('/expenses/update', methods=['POST', 'GET'])
def update_expense():
    if request.method == 'GET':
        return make_response(expenses_template())
    else:
        id = request.form['id']
        name = request.form['name']
        debit = 1 if request.form['debit'] == 'Debit' else 0
        amount = 0 if request.form['amount'] == '' else request.form['amount']
        account_id = request.form['account_id']
        temp_expense_date = datetime.utcnow() if request.form['expense_date'] == '' else datetime.strptime(
            request.form['expense_date'], '%Y-%m-%d').date()
        paid = 1 if "paid" in request.form else 0

        expense_date = temp_expense_date.strftime("%Y-%m-%d")

        user = User.get_by_email(session['email'])

        new_expense = Expense(_id=id, user_id=user._id, name=name, amount=amount, account_id=account_id, debit=debit,
                              expense_date=expense_date, paid=paid)

        new_expense.update_mongo()

        return make_response(expenses_template())


@app.route('/expenses/remove', methods=['POST', 'GET'])
def remove_expense():
    if request.method == 'GET':
        return make_response(expenses_template())
    else:
        id = request.form['id']

        Expense.remove_from_mongo(id)

        return make_response(expenses_template())


@app.template_filter('formatdatetime')
def format_datetime(value):
    if value is None:
        return ""
    datetime_object = datetime.strptime(value, '%Y-%m-%d')
    return datetime_object.strftime('%a %d %b %Y')


if __name__ == '__main__':
    app.run(port=5000)
