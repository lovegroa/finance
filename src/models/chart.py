from datetime import datetime, timedelta
import json


class Chart(object):
    def __init__(self, accounts, expenses):
        self.accounts = accounts
        self.expenses = expenses

    def min_amount_chart(self, cash_per_day, days):

        data_list = []

        for account in self.accounts:

            if account['include_in_calculations']:

                data_temp = []
                account_temp = account['name']
                account_colour = account['colour']
                account_total_temp = float(account['amount']) - float(account['min_amount']) if account[
                    'debit'] else float(account['min_amount']) - float(account['amount'])
                data_temp.append(account_total_temp)
                for day in range(days):
                    period_date = (datetime.today() + timedelta(days=day)).strftime("%Y-%m-%d")
                    expense_total_temp = cash_per_day if account['priority'] else 0
                    for expense in self.expenses:
                        if day == 0:
                            if period_date >= expense['expense_date'] and account['_id'] == expense[
                                'account_id'] and not \
                                    expense['paid']:
                                if expense['debit']:
                                    expense_total_temp = expense_total_temp + float(expense['amount'])
                                else:
                                    expense_total_temp = expense_total_temp - float(expense['amount'])
                        else:
                            if period_date == expense['expense_date'] and account['_id'] == expense[
                                'account_id'] and not \
                                    expense['paid']:
                                if expense['debit']:
                                    expense_total_temp = expense_total_temp + float(expense['amount'])
                                else:
                                    expense_total_temp = expense_total_temp - float(expense['amount'])
                    account_total_temp = account_total_temp - expense_total_temp
                    data_temp.append(account_total_temp)

                x = f'{{ "label":"{account_temp}", "data":{data_temp}, "backgroundColor":"{account_colour}"}}'

                data_list.append(json.loads(x))

        return data_list

    def amount_account_chart(self, cash_per_day, days):

        data_list = []

        for account in self.accounts:

            if account['include_in_calculations']:

                data_temp = []
                account_temp = account['name']
                account_colour = account['colour']
                account_total_temp = float(account['amount']) if account[
                    'debit'] else - float(account['amount'])
                data_temp.append(account_total_temp)
                for day in range(days):
                    period_date = (datetime.today() + timedelta(days=day)).strftime("%Y-%m-%d")
                    expense_total_temp = cash_per_day if account['priority'] else 0
                    for expense in self.expenses:
                        if day == 0:
                            if period_date >= expense['expense_date'] and account['_id'] == expense[
                                'account_id'] and not \
                                    expense['paid']:
                                if expense['debit']:
                                    expense_total_temp = expense_total_temp + float(expense['amount'])
                                else:
                                    expense_total_temp = expense_total_temp - float(expense['amount'])
                        else:
                            if period_date == expense['expense_date'] and account['_id'] == expense[
                                'account_id'] and not \
                                    expense['paid']:
                                if expense['debit']:
                                    expense_total_temp = expense_total_temp + float(expense['amount'])
                                else:
                                    expense_total_temp = expense_total_temp - float(expense['amount'])
                    account_total_temp = account_total_temp - expense_total_temp
                    data_temp.append(account_total_temp)

                x = f'{{ "label":"{account_temp}", "data":{data_temp}, "backgroundColor":"{account_colour}"}}'

                data_list.append(json.loads(x))

        return data_list

    def amount_chart(self, account_total, cash_per_day, days):

        user = User.get_by_email(session['email'])

        data_list = []

        data_temp = []
        total_temp = float(account_total)
        data_temp.append(account_total)
        for day in range(days):
            period_date = (datetime.today() + timedelta(days=day)).strftime("%Y-%m-%d")
            expense_total_temp = 0
            for account in self.accounts:

                if account['include_in_calculations']:

                    expense_total_temp = expense_total_temp + cash_per_day if account['priority'] else expense_total_temp
                    for expense in self.expenses:
                        if day == 0:
                            if period_date >= expense['expense_date'] and account['_id'] == expense[
                                'account_id'] and not \
                                    expense['paid']:
                                if expense['debit']:
                                    expense_total_temp = expense_total_temp + float(expense['amount'])
                                else:
                                    expense_total_temp = expense_total_temp - float(expense['amount'])
                        else:
                            if period_date == expense['expense_date'] and account['_id'] == expense[
                                'account_id'] and not \
                                    expense['paid']:
                                if expense['debit']:
                                    expense_total_temp = expense_total_temp + float(expense['amount'])
                                else:
                                    expense_total_temp = expense_total_temp - float(expense['amount'])
            total_temp = total_temp - expense_total_temp
            data_temp.append(total_temp)

        x = f'{{ "label": "{user.first_name}", "data":{data_temp}, "backgroundColor":"rgba(247,75,83,0.6)"}}'

        data_list.append(json.loads(x))

        return data_list
