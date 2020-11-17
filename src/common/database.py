import pymongo
import os


class Database(object):
    URI = "mongodb+srv://lovegroa:Terr0r58@cluster0.bvcvs.mongodb.net/heroku_53p67mrn?retryWrites=true&w=majority"

    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['heroku_53p67mrn']
        #Database.DATABASE = client.get_default_database()

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
