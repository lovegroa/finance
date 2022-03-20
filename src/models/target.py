import uuid
from datetime import datetime

from flask import session

try:
    from common.database import Database
except:
    from src.common.database import Database


class Target(object):
    def __init__(
        self, user_id, target_date, created_date=datetime.utcnow(), amount=0, _id=None
    ):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.user_id = user_id
        self.created_date = created_date
        self.target_date = target_date
        self.amount = amount

    def save_to_mongo(self):

        Database.insert(collection="targets", data=self.json())

    def json(self):

        return {
            "_id": self._id,
            "user_id": self.user_id,
            "created_date": self.created_date,
            "target_date": self.target_date,
            "amount": self.amount,
        }

    @classmethod
    def from_mongo(cls, id):
        post_data = Database.find_one(collection="targets", query={"user_id": id})
        return cls(**post_data)

    def update_mongo(self):
        Database.update(collection="targets", query={"_id": self._id}, data=self.json())

    @staticmethod
    def remove_from_mongo(id):
        Database.remove(collection="targets", query={"_id": id})

    @staticmethod
    def find_targets(id):
        return [
            target
            for target in Database.find(
                collection="targets", query={"user_id": id}, sort="target_date"
            )
        ]
