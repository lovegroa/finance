import pymongo
import os


class Database(object):
    URI = os.environ.get("MONGOLAB_URI")
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client.get_default_database()

    @staticmethod
    def insert(collection, data):

        try:
            Database.DATABASE[collection].insert(data)
        except:
            print('fail')

    @staticmethod
    def update(collection, query, data):
        Database.DATABASE[collection].update(query, data)

    @staticmethod
    def remove(collection, query):
        Database.DATABASE[collection].remove(query)

    @staticmethod
    def find(collection, query, sort):
        return Database.DATABASE[collection].find(query).sort([(sort, pymongo.ASCENDING)])

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
