# import pymongo
# # Replace the uri string with your MongoDB deployment's connection string.
# conn_str = "mongodb://root:root@192.168.74.128:27017/admin?retryWrites=true&w=majority"
# # set a 5-second connection timeout
# client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
# try:
#     print(client.server_info())
# except Exception as e:
#     print(e, "Unable to connect to the server.")

from airflow.providers.mongo.hooks.mongo import MongoHook

hook = MongoHook(mongo_conn_id='my_mongo_conn')
client = hook.get_conn()

try:
    print(client.server_info())
except Exception as e:
    print(e, "Unable to connect to the server.")