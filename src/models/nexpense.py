import uuid
from datetime import datetime

from flask import session

try:
    from common.database import Database
except:
    from src.common.database import Database


class NExpense(object):
    def __init__(
        self,
        user_id,
        name,
        account_id,
        start_date,
        end_date,
        paid_dates,
        frequency,
        created_date=datetime.utcnow(),
        amount=0,
        debit=1,
        _id=None,
    ):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.user_id = user_id
        self.name = name
        self.created_date = created_date
        self.start_date = start_date
        self.end_date = end_date
        self.amount = amount
        self.debit = debit
        self.account_id = account_id
        self.paid_dates = paid_dates
        self.frequency = frequency

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def save_to_mongo(self):

        Database.insert(collection="nexpenses", data=self.json())

    def json(self):

        return {
            "_id": self._id,
            "user_id": self.user_id,
            "name": self.name,
            "created_date": self.created_date,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "amount": self.amount,
            "debit": self.debit,
            "account_id": self.account_id,
            "paid_dates": self.paid_dates,
            "frequency": self.frequency,
        }

    @classmethod
    def from_mongo(cls, id):
        post_data = Database.find_one(collection="nexpenses", query={"_id": id})
        return cls(**post_data)

    def update_mongo(self):
        Database.update(
            collection="nexpenses", query={"_id": self._id}, data=self.json()
        )

    @staticmethod
    def remove_from_mongo(id):
        Database.remove(collection="nexpenses", query={"_id": id})

    @staticmethod
    def find_nexpenses(id):
        return [
            expense
            for expense in Database.find(
                collection="nexpenses", query={"user_id": id}, sort="start_date"
            )
        ]

    @staticmethod
    def total_nexpenses(nexpenses):

        expense_total = 0
        for expense in nexpenses:
            if expense["debit"] == 0:
                expense_total = float(expense_total) - float(expense["amount"])
            else:
                expense_total = float(expense_total) + float(expense["amount"])

        return expense_total
