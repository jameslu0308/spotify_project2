from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.mongo.hooks.mongo import MongoHook
import backendFunc

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 30),  # 设置为 4/29 的早上 12:05
    'retries': 1,
}

# get_artist ENDPOINT https://api.spotify.com/v1/artists/{id}
artist_endpoint = r'https://api.spotify.com/v1/artists/'

def get_connection():
    # 创建 MongoHook
    hook = MongoHook(mongo_conn_id='my_mongo_conn')
    # 连接到 MongoDB
    client = hook.get_conn()
    return client

def get_spotify_ids(client):
    # 访问数据库和集合
    db = client['Spotify']
    collection = db['new_rap_ID']

    # 使用聚合框架查询 Spotify IDs
    pipeline = [
        {"$group": {"_id": None, "spotify_ids": {"$push": "$spotify_id"}}},
        {"$project": {"_id": 0, "spotify_ids": 1}}
    ]
    results = list(collection.aggregate(pipeline))
    if results:
        spotify_ids = list(results)[0]['spotify_ids']

    else:
        print("No documents found in the collection.")
        spotify_ids = []


    return spotify_ids

def get_headers(client):
    db = client['Spotify']
    coll1 = db['spotify_token']

    infoToken = coll1.find_one({'id': ''})
    if infoToken:
        tokenGetime = infoToken['Token Retrieve date']
        tokenfromDB = infoToken['access_token']
        typefromDB = infoToken['token_type']

        # check if token expires
        timegap = timedelta(hours=1)
        timeNow = datetime.now()
        if (timeNow - tokenGetime) > timegap:
            res1 = backendFunc.getToken('')
            newToken = res1['access_token']
            # update db info
            #tokenCollection.update_one('access_token', tokenfromDB, newToken)
            coll1.delete_one({'id':''})
            coll1.insert_one(res1)

            type = typefromDB
            token = newToken
        else:
            type = typefromDB
            token = tokenfromDB
    else:
        res = backendFunc.getToken('')
        coll1.insert_one(res)
        # should rerun this if-else and get token only from DB, need to change code
        token = res['access_token']
        type = res['token_type']

    headers = {'Authorization': f"{type} {token}"}
    return headers


def main():
    client = get_connection()
    spotify_ids = get_spotify_ids(client)
    headers = get_headers(client)
    error_list = []
    for id in spotify_ids:
        try:
            res = backendFunc.requestUrl(artist_endpoint+id, headers, 'json')
        except:
            headers = get_headers()
            res = backendFunc.requestUrl(artist_endpoint+id, headers, 'json')
        try:
            db = client['Spotify']
            coll = db['new_rap_ID2']
            query = {'spotify_id': id}
            #old_data = coll.find_one(query)

            new_values = {
                '$set': {'followers': res['followers']['total'], 'popularity': res['popularity']}
                }  # 设置要更新的字段和新的值
            coll.update_one(query, new_values)
        
        except:
            error_list.append(id)

    client.close()

    print('error_list: ',error_list)

dag = DAG(
    dag_id = 'update_popularity',
    default_args=default_args,
    schedule_interval= '0 10 * * *',
    catchup=False
)

total_tasks = PythonOperator(
    task_id='main',
    python_callable=main,
    dag=dag,
)

total_tasks
