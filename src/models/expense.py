import uuid
from datetime import datetime

from flask import session

from src.common.database import Database


class Expense(object):
    def __init__(
        self,
        user_id,
        name,
        account_id,
        nexpense_id,
        expense_date=datetime.utcnow(),
        created_date=datetime.utcnow(),
        amount=0,
        paid=0,
        debit=1,
        _id=None,
    ):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.user_id = user_id
        self.name = name
        self.created_date = created_date
        self.expense_date = expense_date
        self.amount = amount
        self.debit = debit
        self.account_id = account_id
        self.paid = paid
        self.nexpense_id = nexpense_id

    def save_to_mongo(self):

        Database.insert(collection="expenses", data=self.json())

    def json(self):

        return {
            "_id": self._id,
            "user_id": self.user_id,
            "name": self.name,
            "created_date": self.created_date,
            "expense_date": self.expense_date,
            "amount": self.amount,
            "debit": self.debit,
            "account_id": self.account_id,
            "nexpense_id": self.nexpense_id,
            "paid": self.paid,
        }

    @classmethod
    def from_mongo(cls, id):
        post_data = Database.find_one(collection="expenses", query={"_id": id})
        return cls(**post_data)

    def update_mongo(self):
        Database.update(
            collection="expenses", query={"_id": self._id}, data=self.json()
        )

    @staticmethod
    def remove_from_mongo(id):
        Database.remove(collection="expenses", query={"_id": id})

    @staticmethod
    def find_expenses(id):
        return [
            expense
            for expense in Database.find(
                collection="expenses", query={"user_id": id}, sort="expense_date"
            )
        ]

    @staticmethod
    def total_expenses(expenses):

        expense_total = 0
        for expense in expenses:
            if expense["debit"] == 0:
                expense_total = float(expense_total) - float(expense["amount"])
            else:
                expense_total = float(expense_total) + float(expense["amount"])

        return expense_total
