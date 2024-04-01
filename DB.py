import os
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import urllib
import bson

def connectDB():
    userName = urllib.parse.quote(os.getenv('DB_ROOT_USERNAME'))
    userPass = urllib.parse.quote(os.getenv('DB_ROOT_PASSWORD'))
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    dbName = os.getenv('DB_NAME')
    client = MongoClient(f'mongodb://{userName}:{userPass}@{host}:{port}')
    return client[dbName]


def buildeCollection(collectionName):
    return connectDB()[collectionName]

class Spotify:
    def __init__(self, collectionName):
        self.collectionName = collectionName
        self.collection = buildeCollection(collectionName)

    def insert_one(self, data):
        return self.collection.insert_one(data)
    
    def insert_many(self, data):
        return self.collection.insert_many(data)
    
    def update_one(self, search_item, oriValue, newValue):
        oriItem = {search_item: oriValue}
        newItem = {"$set" : {search_item: newValue}}
        return self.collection.update_one(oriItem, newItem)
    
    # 根據 id 名字篩選出來
    # 根據 field value 來尋找值
    def get_collection_search_by_FV(self,search_field , search_value):
        query = {search_field: search_value}
        return self.collection.find_one(query)
    
    def get_collection_search_query(self, field_Name, search_item):
        query = {field_Name: search_item}
        return self.collection.find_one(query)

    def get_collection_search_query_many(self, query):
        return self.collection.find(query)
    
    def get_collection_search_query_multiple_conditions(self, query, type):
        srcQuery = {
            f'${type}': [query]
        }
        return self.collection.find(srcQuery)
    
    def get_collection_search_specific_fields(self, field_Name):
        # 要不要顯示的dict，_id: 0 不顯示，給1的代表要顯示
        srcDict = {'_id':0}
        for i in field_Name:
            srcDict[i] = 1
        return self.collection.find({}, srcDict)
    
    def aggregate_number_search(self, search_field, sortType, filtquery = None):
        search_item = '$'+search_field
        if sortType == 'count':
            sortCol2 = '$sum'

        if filtquery != None:
            
            # need to adjust if-else
            col2 = '$'+list(filtquery.keys())[0]
            
            # need to define name as an operator
            pipeline = [
                {"$match": filtquery},
                {"$group": {'_id': search_item, 'name': {"$first": col2}, sortType: {sortCol2: 1}}},
                {"$sort": bson.SON([(sortType, -1)])}
                ]
        else:
            pipeline = [
                {"$group": {'_id': search_item, sortType: {sortCol2: 1}}},
                {"$sort": bson.SON([(sortType, -1)])}
                ]
        return self.collection.aggregate(pipeline)
    
    def sort_search(self, search_item, sort=None):
        if sort == 'asc':
            sort = None
        elif sort == 'desc':
            sort = -1
        return self.collection.find().sort(search_item, sort)#.allow_disk_use(True)
    
    def delete_one_by_id_name(self, search_item):
        query = {"id": search_item}
        return self.collection.delete_one(query)