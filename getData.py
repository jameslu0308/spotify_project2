import os
import requests
from googlesearch import search
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
from DB import Spotify
import backendFunc
import random
import time


'''
search Artist Spotify ID
'''
# decide if this function can be modualized??
def getArtistId(filePath):
    genre = filePath.replace('files/source/', '').split('/')[0]
    with open(filePath, 'r') as f:
        content = f.read().splitlines()#[32:]
    colName = ['artist_ID_url', 'playlist_ID_url']
    tempList = []
    collName = f'{genre}_ID'
    # collName = f'rap_ID'

    '''start searching'''
    for idx1, name in enumerate(content):
        smallist = []
        print(idx1)
        try:
            result = search(f'{name} spotify', sleep_interval= random.randint(3,13), num_results=2)

            # so far filter is no use, need to modify
            filter1 = 'https://open.spotify.com/artist'
            filter2 = 'https://open.spotify.com/playlist'

            # save the first 2 results only
            for idx2, element in enumerate(result):
                if idx2 < 2:
                    if element.find(filter1) or element.find(filter2):
                        smallist.append(element)
                else:
                    continue
            dict1 = {'id': name, colName[0]: smallist[0], colName[1]: smallist[1]}
            tempList.append(dict1)

            if len(tempList) > 20:
                # save ID into DB
                _table = Spotify(collName)
                _table.insert_many(tempList)
                tempList = []
                # print('Save spotify artist ID completed!')

            elif (len(tempList) < 20) and (idx1+1 == len(content)):
                _table = Spotify(collName)
                _table.insert_many(tempList)

        except Exception as e:
            _table = Spotify(collName)
            _table.insert_many(tempList)

            print('Save last batch before error!')
            print(e)
            break

    print('Search and save ID completed!')
    return collName


'''
search through Spotify API
'''
"""
search type: 
search_collection: data scratch from _
new_collection_name: convert scratched data and save to another new collection
 """
def InfoFromSpotify(search_Type, search_collection, new_collection_name):
    if search_Type == 'artist': 
        _collection = Spotify(search_collection)

        # remove duplicate and garbage data
        search_Field = 'id'
        df1 = pd.DataFrame(_collection.aggregate_number_search(search_Field, sortType='count'))
        print(df1.shape[0])
        startRow = 2
        # print(df1)
        df1 = df1.iloc[startRow:]
        totalNum = df1.shape[0]
        url = f'https://api.spotify.com/v1/artists'
        trashData = []

        '''check missing artist, re-search'''
        # list1 = df1['_id'].values.tolist()
        # with open('/home/ellie/mineProject/spotify/files/source/rap/20231128/artistlist20231128.txt', 'r') as f:
        #     content = f.read().splitlines()
        # list2 = list(dict.fromkeys(content))
        # list_dif = [i for i in list1 + list2 if i not in list1 or i not in list2]
        
        # from saveFile import saveTxt
        # saveTxt(list_dif, 'files/source', 'missingArtist.txt', 'w')


    elif search_Type == 'album':
        collection1 = Spotify(search_collection)
        # 要呈現的 field
        search_Field = ['name', 'id']
        # eg. {'_id': 0, 'name': 1, 'id': 1}

        df1 = pd.DataFrame(collection1.get_collection_search_specific_fields(search_Field))
        print(df1)
        totalNum = df1.shape[0]
        url = f'https://api.spotify.com/v1/artists'

        nextList = 0
        # nextList = 2
    # 回傳每首歌的 json
    elif search_Type == 'trackGen':
        if not pd.DataFrame(Spotify(new_collection_name).aggregate_number_search('href','count')).empty:
            listPath = '/home/ellie/mineProject/spotify/files/source/rap/20240202/yetSearchTrackAlbumID.txt'
            with open(listPath, 'r') as f:
                flatList = f.read().splitlines()#[8744:]
        else:
            collection1 = Spotify(search_collection)
            search_Field = 'items.id'
            startRow = 1
            # dfList 會抓出 album lists id by rapper
            # list 中元素是 album list id(也是 list) eg [[],...[],[]] 
            dfList = pd.DataFrame(collection1.aggregate_number_search(search_Field, 'count'))['_id'][startRow:].values.tolist()   # retrieve album ID for tracks search
            # 根據每個 rapper 抓出每個 album id ，合併成 list
            # -> total album id list
            flatList = [item for sublist in dfList for item in sublist]  # flatten list in list situation
        # delete duplicates album id 
        df1 = pd.Series(flatList).drop_duplicates().reset_index(drop=True)
        # print(df1)
        # print(df1[df1 == '7idQyUTLu0eUJdAOAvR8nh'])
        totalNum = df1.shape[0]
        print(totalNum)

        url = f'https://api.spotify.com/v1/albums'

        nextList = 0
        # nextList = 2

    '''search information with Spotify API'''
    try:
        type, token = backendFunc.checkToken(tokenCollection='spotify_token', \
                                             name = 'james')
        headers = {'Authorization': f"{type} {token}"}

        # 控制迴圈 / 每筆資料都可以被處理到 / 記錄到處理到哪裡
        count = 0
        # count = 4100
        templist = []
        while count < totalNum:
            time.sleep(random.randint(1,3))
            if search_Type == 'artist':
                name = df1['_id'][startRow]
                print(name)
                idGet = _collection.get_collection_search_by_FV('id', name)['artist_ID_url']
                id1 = idGet.split('/')[-1]
                result1 = idGet.replace(id1, '')

                if result1 != 'https://open.spotify.com/artist/':
                    trashData.append(name)
                    count+=1
                    startRow+=1
                    continue
                else:
                    srcUrl = f'{url}/{id1}'

            elif search_Type == 'album':
                id = df1['id'][count]
                name = df1['name'][count]
                if nextList == 0:
                    srcUrl = f'{url}/{id}/albums?limit=50&offset=0'
                elif nextList == 2:
                    srcUrl = 'https://api.spotify.com/v1/artists/0e3TXa6cyJQl5vE6DFHfjT/albums?include_groups=album,single,compilation,appears_on&offset=100&limit=50'

            elif search_Type == 'trackGen':
                id = df1[count]
                if nextList == 0:
                    srcUrl = f'{url}/{id}/tracks?limit=50&offset=0'
                elif nextList == 2:
                    # 中斷 記錄從上次抓到的 track id
                    srcUrl = 'https://api.spotify.com/v1/albums/7idQyUTLu0eUJdAOAvR8nh/tracks?limit=50&offset=0'

            '''start API search'''
            print(srcUrl)
            response = backendFunc.requestUrl(srcUrl, headers)
            
            # handle token expired scenario
            if response.status_code == 401:
                type, token = backendFunc.checkToken(tokenCollection='spotify_token', \
                                                    name = 'james')
                headers = {'Authorization': f"{type} {token}"}
                continue

            else:
                # response 成功或的的 json
                resSave = response.json()
                if response.status_code == 404:
                    break
                
                templist.append(resSave)
                # 20 筆 存一次
                if len(templist) == 20:
                    newCollection = Spotify(new_collection_name)
                    newCollection.insert_many(templist)
                    templist = []
                    print(f'Save data batch {count} !')
                # 最後一個 batch 抓的資料如果存的數字小於20筆
                # (判斷(count+1) == totalNum)
                elif (len(templist) < 20) and ((count+1) == totalNum):
                    newCollection = Spotify(new_collection_name)
                    newCollection.insert_many(templist)
                    print(f'Save last batch!')
                    break

                if 'startRow' in locals(): 
                    startRow+=1

                # if there is next url for continuous search, continue search
                if "nextList" in locals():
                    nextUrl = resSave['next']
                    if (nextUrl != 'null') and (nextUrl != None):
                        nextList=1
                        srcUrl = nextUrl
                        continue
                    else:
                        nextList=0
                        count+=1

        # save trash data for remove
        if search_Type == 'artist':
            from saveFile import saveTxt
            trashData.append(f'"Total people searched": {totalNum}, "Total_missing": {len(templist)}')
            saveTxt(trashData, 'files', 'trashRapperList.txt', 'w')

    except Exception as e:
        newCollection = Spotify(new_collection_name)
        newCollection.insert_many(templist)
        print(f'Save last batch!')
        print(e)

if __name__ == '__main__':
    # filePath = '/home/ellie/mineProject/spotify/files/source/20231206/missingArtist.txt'
    # collName = getArtistId(filePath)

    # infoType = 'artist'
    # sourceTab = 'rap_ID'
    # newTabName = 'rapper_information'
    # InfoFromSpotify(infoType, sourceTab, newTabName)

    # InfoFromSpotify(search_Type='album', 
    #                 search_collection='rapper_information', 
    #                 new_collection_name='rapper_album_information')

    InfoFromSpotify(search_Type='trackGen', 
                    search_collection='rapper_album_information', 
                    new_collection_name='rapper_track_general_information')