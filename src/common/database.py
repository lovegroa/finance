import pymongo
import os


class Database(object):
    #URI = "mongodb://lovegroa:Terr0r58!@ds029969.mlab.com:29969/heroku_53p67mrn"
    #URI = "mongodb://lovegroa:Terr0r58!@cluster0-shard-00-02.bvcvs.mongodb.net:27017/heroku_53p67mrn"
    #URI = "mongodb+srv://lovegroa:Terr0r58!@cluster0.bvcvs.mongodb.net/heroku_53p67mrn?retryWrites=true&w=majority"
    URI = "mongodb://lovegroa:Terr0r58!@cluster0-shard-00-00.bvcvs.mongodb.net:27017/heroku_53p67mrn?ssl=true&replicaSet=atlas-dec4aj-shard-0&authSource=admin&retryWrites=true&w=majority"

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
