import pymongo
import os
import certifi


class Database(object):
    URI = "mongodb+srv://test:test@cluster0.bvcvs.mongodb.net/test?retryWrites=true&w=majority"
# &ssl=true&ssl_cert_reqs=CERT_NONE
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI, tlsCAFile=certifi.where())
        Database.DATABASE = client.get_database('heart_money')

    @staticmethod
    def insert(collection, data):

        print (collection, data)


        try:
            Database.DATABASE[collection].insert_one(data)
        except:
            print('fail')

    @staticmethod
    def update(collection, query, data):
        Database.DATABASE[collection].update_one(query, {"$set":data})

    @staticmethod
    def remove(collection, query):
        Database.DATABASE[collection].delete_one(query)

    @staticmethod
    def find(collection, query, sort):
        return Database.DATABASE[collection].find(query).sort([(sort, pymongo.ASCENDING)])

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
