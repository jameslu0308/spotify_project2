from airflow.decorators import dag, task
from datetime import datetime, timedelta
from airflow.providers.mongo.hooks.mongo import MongoHook
import backendFunc

artist_endpoint = r'https://api.spotify.com/v1/artists/'

default_args = {
    "start_date": datetime(2024, 4, 30),
    "retries": 1,
}
# client 物件 不能序列化給xcom傳遞
@dag(schedule_interval='0 10 * * *', default_args=default_args, catchup=False)
def update_popularity_taskflow():
    
    @task
    def get_connection():
        """
        Creates and returns a MongoDB connection
        """
        hook = MongoHook(mongo_conn_id='my_mongo_conn')
        client = hook.get_conn()
        return client

    @task
    def connect_and_get_spotify_ids(client):
        """
        Creates and returns a MongoDB connection
        """
        hook = MongoHook(mongo_conn_id='my_mongo_conn')
        client = hook.get_conn()
        """
        Retrieves Spotify IDs from MongoDB
        """
        db = client['Spotify']
        collection = db['new_rap_ID']
        pipeline = [
            {"$group": {"_id": None, "spotify_ids": {"$push": "$spotify_id"}}},
            {"$project": {"_id": 0, "spotify_ids": 1}}
        ]
        results = list(collection.aggregate(pipeline))
        if results:
            spotify_ids = results[0]['spotify_ids']
        else:
            print("No documents found in the collection.")
            spotify_ids = []
        return spotify_ids

    @task
    def get_headers(client):
        """
        Retrieves and updates the authorization headers
        """
        db = client['Spotify']
        coll1 = db['spotify_token']
        infoToken = coll1.find_one({'id': ''})

        if infoToken:
            tokenGetime = infoToken['Token Retrieve date']
            tokenfromDB = infoToken['access_token']
            typefromDB = infoToken['token_type']

            # Check if token expires
            timegap = timedelta(hours=1)
            timeNow = datetime.now()
            if (timeNow - tokenGetime) > timegap:
                res1 = backendFunc.getToken('')
                newToken = res1['access_token']
                coll1.delete_one({'id': ''})
                coll1.insert_one(res1)

                token = newToken
            else:
                token = tokenfromDB

            type = typefromDB
        else:
            res = backendFunc.getToken('')
            coll1.insert_one(res)
            token = res['access_token']
            type = res['token_type']

        headers = {'Authorization': f"{type} {token}"}
        return headers

    @task
    def update_popularity(client, spotify_ids, headers):
        """
        Updates popularity data in the MongoDB
        """
        error_list = []
        for id in spotify_ids:
            try:
                res = backendFunc.requestUrl(artist_endpoint + id, headers, 'json')
            except:
                headers = get_headers(client)  # Renew headers if request fails
                res = backendFunc.requestUrl(artist_endpoint + id, headers, 'json')
            try:
                db = client['Spotify']
                coll = db['new_rap_ID2']
                query = {'spotify_id': id}

                new_values = {
                    '$set': {'followers': res['followers']['total'], 'popularity': res['popularity']}
                }
                coll.update_one(query, new_values)
            except:
                error_list.append(id)

        client.close()
        print('error_list: ', error_list)

    # Task dependencies
    client = get_connection()
    spotify_ids = get_spotify_ids(client)
    headers = get_headers(client)
    update_popularity(client, spotify_ids, headers)

update_popularity_taskflow()
