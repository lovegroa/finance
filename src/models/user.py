from datetime import datetime, timedelta
import uuid

from flask import session

from common.database import Database
from models.target import Target


class User(object):
    def __init__(self, email, password, first_name="nothing", last_name='nothing', _id=None):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):

        data = Database.find_one('users', {'email': email})
        if data is not None:
            #print((**data))
            return cls(**data)

    @classmethod
    def account_exists(cls, email):
        data = Database.find_one('users', {'email': email})
        if data is not None:
            return True
        else:
            return False

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one('users', {'_id': _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        user = User.get_by_email(email)
        if user is not None:
            return user.password == password
        return False

    @classmethod
    def register(cls, email, password, first_name, last_name):
        #user = cls.get_by_email(email)

        if not User.account_exists(email):

            print('1234')
            new_user = cls(email, password, first_name, last_name)
            new_user.save_to_mongo()
            session['email'] = email
            target_date = (datetime.today() + timedelta(10)).strftime("%Y-%m-%d")
            target = Target(user_id=new_user._id, target_date=target_date)
            target.save_to_mongo()
            return True
        else:
            return False

    @staticmethod
    def login(user_email):
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    def json(self):
        return {
            'email': self.email,
            '_id': self._id,
            'password': self.password,
            'first_name': self.first_name,
            'last_name': self.last_name
        }

    def save_to_mongo(self):
        Database.insert('users', self.json())
