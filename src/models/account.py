import uuid
from datetime import datetime

from flask import session

from common.database import Database


class Account(object):
    def __init__(self, user_id, name, created_date=datetime.utcnow(), amount=0, min_amount=0, debit=1, colour='#6a0dad',
                 priority=False, include_in_calculations=True, _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.user_id = user_id
        self.name = name
        self.created_date = created_date
        self.amount = amount
        self.min_amount = min_amount
        self.debit = debit
        self.colour = colour
        self.priority = priority
        self.include_in_calculations = include_in_calculations

    def save_to_mongo(self):
        Database.insert(collection='accounts', data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'name': self.name,
            'created_date': self.created_date,
            'amount': self.amount,
            'min_amount': self.min_amount,
            'debit': self.debit,
            'colour': self.colour,
            'priority': self.priority,
            'include_in_calculations': self.include_in_calculations
        }

    @classmethod
    def from_mongo(cls, id):
        post_data = Database.find_one(collection='accounts', query={'_id': id})
        return cls(**post_data)

    def update_mongo(self):
        Database.update(collection='accounts', query={'_id': self._id}, data=self.json())

    @staticmethod
    def remove_from_mongo(id):
        Database.remove(collection='accounts', query={'_id': id})

    @staticmethod
    def find_accounts(id):
        return [account for account in Database.find(collection='accounts', query={'user_id': id}, sort='name')]

    @staticmethod
    def total_accounts(accounts):

        account_total = 0
        for account in accounts:
            if account['include_in_calculations'] == 1:
                if account['debit'] == 0:
                    account_total = float(account_total) - float(account['amount'])
                else:
                    account_total = float(account_total) + float(account['amount'])

        return account_total

    @staticmethod
    def primary_account(accounts):

        primary = ""
        for account in accounts:
            if account['priority'] == 1:
                primary = account['name']

        return primary