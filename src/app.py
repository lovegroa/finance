from datetime import datetime, timedelta, date
import json
from dateutil.relativedelta import *

from flask import Flask, render_template, session, request, make_response


try:

    from common.database import Database
    from models.account import Account
    from models.chart import Chart
    from models.expense import Expense
    from models.target import Target
    from models.user import User
    from models.nexpense import NExpense


except:

    from src.common.database import Database
    from src.models.account import Account
    from src.models.chart import Chart
    from src.models.expense import Expense
    from src.models.target import Target
    from src.models.user import User
    from src.models.nexpense import NExpense

app = Flask(__name__)
app.secret_key = "alex"


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route("/")
def home_template():
    if session.get("email") is None:

        return render_template("login.html")

    else:
        print("home")

        user = User.get_by_email(session["email"])
        first = user.first_name

        # Total accounts
        accounts = Account.find_accounts(user._id)
        account_total = Account.total_accounts(accounts)
        primary = Account.primary_account(accounts)

        expenses = []
        nexpenses = NExpense.find_nexpenses(user._id)
        expense_total = 0

        targets = Target.from_mongo(user._id)
        print("expenses type")

        expenses_in_period = []

        for nexpense in nexpenses:

            expense_date = nexpense["start_date"]
            count = 1
            while expense_date <= nexpense["end_date"]:
                temp_expense_date = expense_date.strftime("%Y-%m-%d")

                paid = 0
                for paid_date in nexpense["paid_dates"]:
                    if temp_expense_date == paid_date:
                        paid = 1

                new_expense = Expense(
                    user_id=user._id,
                    name=nexpense["name"],
                    account_id=nexpense["account_id"],
                    amount=nexpense["amount"],
                    debit=nexpense["debit"],
                    expense_date=temp_expense_date,
                    nexpense_id=nexpense["_id"],
                    paid=paid,
                )

                expenses.append(new_expense)

                if nexpense["frequency"] == "Once":
                    break
                elif nexpense["frequency"] == "Daily":
                    expense_date = expense_date + timedelta(days=1)

                elif nexpense["frequency"] == "Weekly":

                    expense_date = expense_date + timedelta(days=7)

                elif nexpense["frequency"] == "Monthly":

                    expense_date = nexpense["start_date"] + relativedelta(months=+count)
                    count = count + 1

                elif nexpense["frequency"] == "Yearly":

                    expense_date = nexpense["start_date"] + relativedelta(years=+count)
                    count = count + 1

        # take second element for sort
        def takeSecond(elem):
            return elem.expense_date

        # random list
        # random = [(2, 2), (3, 4), (4, 1), (1, 3)]

        # sort list with key
        expenses.sort(key=takeSecond)

        # # print list
        # print('Sorted list:', random)

        for expense in expenses:

            if expense.expense_date <= targets.target_date and expense.paid == 0:
                expenses_in_period.append(expense)
                if expense.debit == 1:
                    expense_total = expense_total + float(expense.amount)

                else:
                    expense_total = expense_total - float(expense.amount)

        start_date = date.today().strftime("%Y-%m-%d")
        datetime.strptime(targets.target_date, "%Y-%m-%d").date()
        days = (
            datetime.strptime(targets.target_date, "%Y-%m-%d").date()
            - datetime.strptime(start_date, "%Y-%m-%d").date()
        ).days + 1

        cash_remaining = account_total - float(targets.amount) - expense_total
        cash_per_day = cash_remaining / days
        cash_per_week = cash_per_day * 7

        base = datetime.today()
        chart_labels = [
            (base + timedelta(days=x)).strftime("%d %m") for x in range(days + 1)
        ]

        charts = Chart(accounts=accounts, expenses=expenses)

        data_list = charts.amount_chart(
            cash_per_day=cash_per_day,
            days=days,
            account_total=account_total,
            first=first,
        )
        data_list2 = charts.min_amount_chart(cash_per_day=cash_per_day, days=days)
        data_list3 = charts.amount_account_chart(cash_per_day=cash_per_day, days=days)
        target_max = round(float(account_total) - float(expense_total))
        target_min = round(float(targets.amount) - cash_remaining)
        print(f" min:{target_max} max:{target_min}")

        return render_template(
            "home.html",
            target_max=target_max,
            target_min=target_min,
            datalist=data_list,
            datalist2=data_list2,
            datalist3=data_list3,
            chart_labels=chart_labels,
            account_total=account_total,
            cash_remaining=cash_remaining,
            cash_per_day=cash_per_day,
            days=days,
            targets=targets,
            expenses=expenses,
            expense_total=expense_total,
            start_date=start_date,
            expenses_in_period=expenses_in_period,
            accounts=accounts,
            first=user.first_name,
            primary=primary,
            cash_per_week=cash_per_week,
        )


@app.route("/login")
def login_template():
    return render_template("login.html")


def round(n):
    # Smaller multiple
    a = (n // 10) * 10

    # Larger multiple
    b = a + 10

    # Return of closest of two
    return b if n - a > b - n else a


@app.route("/auth/login", methods=["POST"])
def login_user():
    email = request.form["email"]
    password = request.form["password"]
    print(password)

    if not User.account_exists(email=email):
        print("test2")
        return make_response(register_template())

    print(User.get_by_email(email=email))

    if User.get_by_email(email=email) is not None:
        print("test2")
        if User.login_valid(email, password):
            print("test1")
            User.login(email)
            return make_response(home_template())
        else:
            print("test4")
            session["email"] = None
            return make_response(login_template())


@app.route("/register")
def register_template():
    return render_template("register.html")


@app.route("/auth/register", methods=["POST"])
def register_user():
    email = request.form["email"]
    password = request.form["password"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]

    User.register(email, password, first_name, last_name)

    return make_response(home_template())


@app.route("/accounts")
def accounts_template():
    user = User.get_by_email(session["email"])
    accounts = Account.find_accounts(user._id)
    account_total = Account.total_accounts(accounts)

    return render_template(
        "accounts.html",
        accounts=accounts,
        account_total=account_total,
        first=user.first_name,
    )


@app.route("/accounts/add", methods=["POST", "GET"])
def add_account():
    if request.method == "GET":
        return make_response(accounts_template())
    else:
        name = request.form["name"]
        amount = 0 if request.form["amount"] == "" else request.form["amount"]
        min_amount = (
            0 if request.form["min_amount"] == "" else request.form["min_amount"]
        )
        debit = 1 if request.form["debit"] == "Debit" else 0
        colour = "#FFFFFF" if request.form["colour"] == "" else request.form["colour"]
        priority = 1 if "priority" in request.form else 0
        include_in_calculations = 1 if "include_in_calculations" in request.form else 0
        user = User.get_by_email(session["email"])
        print("test")

        new_account = Account(
            user_id=user._id,
            name=name,
            amount=amount,
            min_amount=min_amount,
            debit=debit,
            colour=colour,
            priority=priority,
            include_in_calculations=include_in_calculations,
        )

        new_account.save_to_mongo()

        return make_response(accounts_template())


@app.route("/accounts/update", methods=["POST", "GET"])
def update_account():
    if request.method == "GET":
        return make_response(accounts_template())
    else:
        id = request.form["id"]
        name = request.form["name"]
        amount = 0 if request.form["amount"] == "" else request.form["amount"]
        min_amount = (
            0 if request.form["min_amount"] == "" else request.form["min_amount"]
        )
        debit = 1 if request.form["debit"] == "Debit" else 0
        colour = "#FFFFFF" if request.form["colour"] == "" else request.form["colour"]
        priority = 1 if "priority" in request.form else 0
        include_in_calculations = 1 if "include_in_calculations" in request.form else 0
        user = User.get_by_email(session["email"])

        new_account = Account(
            _id=id,
            user_id=user._id,
            name=name,
            amount=amount,
            min_amount=min_amount,
            debit=debit,
            colour=colour,
            priority=priority,
            include_in_calculations=include_in_calculations,
        )

        new_account.update_mongo()

        return make_response(accounts_template())


@app.route("/accounts/remove", methods=["POST", "GET"])
def remove_account():
    if request.method == "GET":
        return make_response(accounts_template())
    else:
        id = request.form["id"]

        Account.remove_from_mongo(id)

        return make_response(accounts_template())


@app.route("/targets")
def targets_template():
    user = User.get_by_email(session["email"])

    targets = Target.from_mongo(user._id)
    return render_template("targets.html", targets=targets, first=user.first_name)


@app.route("/targets/update", methods=["POST", "GET"])
def update_target():
    if request.method == "GET":
        return make_response(targets_template())
    else:
        id = request.form["id"]
        amount = request.form["amount"]
        target_date = (
            datetime.utcnow().strftime("%Y-%m-%d")
            if request.form["target_date"] == ""
            else request.form["target_date"]
        )

        user = User.get_by_email(session["email"])

        new_target = Target(
            _id=id, user_id=user._id, amount=amount, target_date=target_date
        )

        new_target.update_mongo()

        return make_response(home_template())


@app.route("/targets/add", methods=["POST", "GET"])
def add_target():
    if request.method == "GET":
        return make_response(targets_template())
    else:

        amount = request.form["amount"]
        target_date = (
            datetime.utcnow().strftime("%Y-%m-%d")
            if request.form["target_date"] == ""
            else request.form["target_date"]
        )

        user = User.get_by_email(session["email"])

        new_target = Target(user_id=user._id, amount=amount, target_date=target_date)

        new_target.save_to_mongo()

        return make_response(targets_template())


@app.route("/expenses")
def expenses_template():
    user = User.get_by_email(session["email"])

    expenses = NExpense.find_nexpenses(user._id)
    expense_total = 0
    income_total = 0

    for expense in expenses:
        if expense["frequency"] == "Monthly" and expense["debit"] == 1:
            expense_total = expense_total + float(expense["amount"])
        if expense["frequency"] == "Daily" and expense["debit"] == 1:
            expense_total = expense_total + float(expense["amount"]) * 30
        if expense["frequency"] == "Weekly" and expense["debit"] == 1:
            expense_total = expense_total + float(expense["amount"]) * 4
        if expense["frequency"] == "Yearly" and expense["debit"] == 1:
            expense_total = expense_total + float(expense["amount"]) / 12
        if expense["frequency"] == "Monthly" and expense["debit"] == 0:
            income_total = income_total + float(expense["amount"])
        if expense["frequency"] == "Daily" and expense["debit"] == 0:
            income_total = income_total + float(expense["amount"]) * 30
        if expense["frequency"] == "Weekly" and expense["debit"] == 0:
            income_total = income_total + float(expense["amount"]) * 4
        if expense["frequency"] == "Yearly" and expense["debit"] == 0:
            income_total = income_total + float(expense["amount"]) / 12

    print(expense_total)
    print(income_total)
    surplus = income_total - expense_total

    # expenses = Expense.find_expenses(user._id)
    # expense_total = Expense.total_expenses(expenses)

    # required to list the accounts in the form
    accounts = Account.find_accounts(user._id)

    return render_template(
        "expenses.html",
        expenses=expenses,
        accounts=accounts,
        expense_total=expense_total,
        first=user.first_name,
        surplus=surplus,
        income_total=income_total
    )


@app.route("/expenses/add", methods=["POST", "GET"])
def add_expenses():
    if request.method == "GET":
        return make_response(accounts_template())
    else:
        name = request.form["name"]
        debit = 1 if request.form["debit"] == "Debit" else 0
        amount = 0 if request.form["amount"] == "" else request.form["amount"]
        account_id = request.form["account_id"]
        frequency = request.form["frequency"]
        start_date = (
            datetime.utcnow()
            if request.form["start_date"] == ""
            else datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        )
        end_date = (
            datetime.utcnow()
            if request.form["end_date"] == ""
            else datetime.strptime(request.form["end_date"], "%Y-%m-%d")
        )
        # paid = 1 if "paid" in request.form else 0
        paid_dates = []
        user = User.get_by_email(session["email"])

        new_expense = NExpense(
            user_id=user._id,
            name=name,
            account_id=account_id,
            amount=amount,
            frequency=frequency,
            debit=debit,
            start_date=start_date,
            end_date=end_date,
            paid_dates=paid_dates,
        )
        new_expense.save_to_mongo()

        # if frequency == 'Once':

        #     temp_expense_date = start_date.strftime("%Y-%m-%d")
        #     new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
        #                           expense_date=temp_expense_date, paid=paid)
        #     new_expense.save_to_mongo()

        # elif frequency == 'Daily':

        #     expense_date = start_date
        #     while expense_date <= end_date:
        #         temp_expense_date = expense_date.strftime("%Y-%m-%d")
        #         new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
        #                               expense_date=temp_expense_date, paid=paid)
        #         new_expense.save_to_mongo()
        #         expense_date = expense_date + timedelta(days=1)

        # elif frequency == 'Weekly':

        #     expense_date = start_date
        #     while expense_date <= end_date:
        #         temp_expense_date = expense_date.strftime("%Y-%m-%d")
        #         new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
        #                               expense_date=temp_expense_date, paid=paid)
        #         new_expense.save_to_mongo()
        #         expense_date = expense_date + timedelta(days=7)

        # elif frequency == 'Monthly':

        #     expense_date = start_date
        #     count = 1
        #     while expense_date <= end_date:
        #         temp_expense_date = expense_date.strftime("%Y-%m-%d")
        #         new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
        #                               expense_date=temp_expense_date, paid=paid)
        #         new_expense.save_to_mongo()
        #         expense_date = start_date + relativedelta(months=+count)
        #         count = count + 1

        # elif frequency == 'Yearly':

        #     expense_date = start_date
        #     count = 1
        #     while expense_date <= end_date:
        #         print(expense_date)
        #         temp_expense_date = expense_date.strftime("%Y-%m-%d")
        #         new_expense = Expense(user_id=user._id, name=name, account_id=account_id, amount=amount, debit=debit,
        #                               expense_date=temp_expense_date, paid=paid)
        #         new_expense.save_to_mongo()
        #         expense_date = start_date + relativedelta(years=+count)
        #         count = count + 1

        return make_response(expenses_template())


@app.route("/expenses/update", methods=["POST", "GET"])
def update_expense():
    if request.method == "GET":
        return make_response(expenses_template())
    else:
        id = request.form["id"]
        name = request.form["name"]
        debit = 1 if request.form["debit"] == "Debit" else 0
        amount = 0 if request.form["amount"] == "" else request.form["amount"]
        account_id = request.form["account_id"]
        temp_expense_date = (
            datetime.utcnow()
            if request.form["expense_date"] == ""
            else datetime.strptime(request.form["expense_date"], "%Y-%m-%d").date()
        )
        paid = 1 if "paid" in request.form else 0

        expense_date = temp_expense_date.strftime("%Y-%m-%d")

        user = User.get_by_email(session["email"])

        new_expense = Expense(
            _id=id,
            user_id=user._id,
            name=name,
            amount=amount,
            account_id=account_id,
            debit=debit,
            expense_date=expense_date,
            paid=paid,
        )

        new_expense.update_mongo()

        return make_response(expenses_template())


@app.route("/home/expenses/update", methods=["POST", "GET"])
def home_update_expense():
    if request.method == "GET":
        return make_response(expenses_template())
    else:
        id = request.form["id"]
        name = request.form["name"]
        debit = 1 if request.form["debit"] == "Debit" else 0
        amount = 0 if request.form["amount"] == "" else request.form["amount"]
        account_id = request.form["account_id"]
        temp_expense_date = (
            datetime.utcnow()
            if request.form["expense_date"] == ""
            else datetime.strptime(request.form["expense_date"], "%Y-%m-%d").date()
        )
        paid = 1 if "paid" in request.form else 0

        expense_date = temp_expense_date.strftime("%Y-%m-%d")

        user = User.get_by_email(session["email"])

        new_expense = Expense(
            _id=id,
            user_id=user._id,
            name=name,
            amount=amount,
            account_id=account_id,
            debit=debit,
            expense_date=expense_date,
            paid=paid,
        )

        new_expense.update_mongo()

    return make_response(home_template())


@app.route("/home/expenses/paid", methods=["POST", "GET"])
def home_paid_expense():
    if request.method == "GET":
        return make_response(expenses_template())
    else:
        updated_expense = NExpense.from_mongo(request.form["nexpense_id"])
        updated_expense.paid_dates.append(request.form["expense_date"])
        updated_expense.update_mongo()

    return make_response(home_template())


@app.route("/expenses/remove", methods=["POST", "GET"])
def remove_expense():
    if request.method == "GET":
        return make_response(expenses_template())
    else:
        id = request.form["id"]

        NExpense.remove_from_mongo(id)

        return make_response(expenses_template())


@app.route("/home/expenses/remove", methods=["POST", "GET"])
def home_remove_expense():
    if request.method == "GET":
        return make_response(expenses_template())
    else:
        id = request.form["id"]

        Expense.remove_from_mongo(id)

        return make_response(home_template())


@app.template_filter("formatdatetime")
def format_datetime(value):
    if value is None:
        return ""
    datetime_object = datetime.strptime(value, "%Y-%m-%d")
    return datetime_object.strftime("%a %d %b %Y")


if __name__ == "__main__":
    app.run(port=5000)
