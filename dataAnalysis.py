import pandas as pd
import numpy as np
from DB import Spotify
import backendFunc
import os
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


'''return artist popularity sort'''

def sortPopularity(sorItem):
    if sorItem == 'followers':
        sort2 = 'popularity'
    elif sorItem == 'popularity':
        sort2 = 'followers'

    collection_name = 'rapper_information'
    _collection = Spotify(collection_name)
    dfPop = pd.DataFrame(_collection.sort_search(sorItem, 'desc'))

    # show top 50 data
    df_top50 = dfPop[:50]

    sortName = df_top50['name'].str.replace(',', '-').to_list()
    if sorItem == 'followers':
        # followers 數由大到小的list
        sortData = df_top50[sorItem].apply(lambda x: x['total']).to_list()
    elif sorItem == 'popularity':
        sortData = df_top50[sorItem].to_list()

    '''get genre data'''
    category = 'genres'
    m_style = df_top50[category].to_list()
    # 根據followers篩選 最高的前50個歌手的所有 tag 總和
    total_style = [item for sublist in m_style for item in sublist]

    style_counts = pd.Series(total_style).value_counts()
    style_name = list(style_counts.index)
    style_sum = list(style_counts)
    # print(sort2Data)

    # value to return
    titleList = [sorItem, sort2, category]
    dataList = dict(zip(sortName, sortData))
    # 根據風格標籤 統計總和 由大到小排序
    genreList = dict(zip(style_name, style_sum))
    # print(genreList)

    return titleList, dataList, genreList


def sortPopularity2(sorItem):
    if sorItem == 'followers':
        sort2 = 'popularity'
    elif sorItem == 'popularity':
        sort2 = 'followers'

    # 根據followers/popularity篩選 最高的前50個歌手的所有 tag 總和
    newrapID = Spotify('new_rap_ID2')
    # 定義聚合管道
    pipeline_1 = [
        { "$sort": { sorItem: -1 } },  # 按照 followers 字段降序排序
        { "$project": { "_id": 0, "name": 1, sorItem: 1 } },  # 只返回 name 和 followers 字段
        { "$limit": 50}    
    ]
    # 執行聚合操作並構建字典
    rap_dict = {}
    res1 = newrapID.collection.aggregate(pipeline_1)
    for doc in res1:
        rap_dict[doc['name']] = doc[sorItem]

    # 根據followers篩選 最高的前50個歌手的所有 tag 總和
    # 根據風格標籤 統計總和 由大到小排序
    pipeline_2 = [
        {'$sort':{sorItem:-1}},
        {'$limit':50},
        {'$unwind':'$genres'},
        {'$group': {"_id":"$genres", "count":{"$sum":1}}},
        {'$sort':{"count":-1}},
    ]
    # 執行聚合操作
    res2 = newrapID.collection.aggregate(pipeline_2)
    genres_dict ={}
    for d in res2:
        genres_dict[d['_id']] = d['count']

    # value to return
    titleList = [sorItem, sort2, 'genres']

    return titleList, rap_dict, genres_dict


'''
show track data in the album, sort by popularity
'''
def trackData(albumID):

    # 每首歌的 collection / 一筆資料為一張album / 裡面有很多item 是各別track
    _collection = Spotify('rapper_track_general_information')
    # 篩選出同一張專輯的歌
    filter_query = {"$regex":f"{albumID}"}
    #retrieve each track's api from DB
    # 篩選符合album id 的 每個track回來 (理論上為一張專輯的全部track)
    df1 = pd.DataFrame(_collection.get_collection_search_query('href', filter_query)['items']) 
    # print(df1)

    # request track information through API
    search_ID = os.getenv("SPOTIFY_TOKEN_OWNER")

    type, token = backendFunc.checkToken('spotify_token', search_ID)
    headers = {'Authorization': f"{type} {token}"}

    list1 = []
    for i in df1['href']:
        # 每首歌的資訊
        res = backendFunc.requestUrl(i, headers, 'json')
        list1.append(res)
    # 每首歌整理成 df
    df2 = pd.DataFrame.from_records(list1)
    columns = ['Track Name', 'Artists', 'Artist Number', 'Popularity', 'Duration (minutes)']
    list2 = []

    '''retrieve data from API call'''
    for j in range(df2.shape[0]):
        tmp_song = df2.iloc[j]

        if len(list2) == 0:
            albumName = tmp_song['album']['name']
            imgUrl = tmp_song['album']['images'][1]['url']
        # total singer by each song
        singer_lists = []
        for w in tmp_song['artists']:
            singer_lists.append(w['name'])

        artist_nums = len(tmp_song['artists'])
        # 60,000毫秒(1分鐘) 
        song_length = round((tmp_song['duration_ms']) / 60000, 2)
        list2.append({
            columns[0]: tmp_song['name'], # song name
            columns[1]: singer_lists, # total singer list
            columns[2]: artist_nums, # singer number
            columns[3]: tmp_song['popularity'], # song popularity
            columns[4]: song_length # song length
        })
    # total song dataframe
    dfshow = pd.DataFrame.from_dict(list2)
    dfshow = dfshow.sort_values(by='Popularity', ascending=False)
    dfDict = dfshow.to_dict('records')
    # print(dfDict)

    return albumName, imgUrl, columns, dfDict
# 輸出columns有增加，要更改
# 給 album id 
# 輸出所有 track
def trackData2(album_id):
    try:
        res1 = Spotify('new_album_info2').collection.find_one({'album_id':album_id})
        albumName = res1['album_name']
        imgUrl = res1['album_images'][0]['url']
        tracks = []
        track_ids = [track['track_id'] for track in res1['tracks']]
        track_ids_str  =  ','.join(track_ids)
        # 抓取資料
        track_endpoint = f'https://api.spotify.com/v1/tracks?ids={track_ids_str}'
        search_ID = os.getenv("SPOTIFY_TOKEN_OWNER")
        type, token = backendFunc.checkToken('spotify_token', search_ID)
        headers = {'Authorization': f"{type} {token}"}
        track_ids_res = backendFunc.requestUrl(track_endpoint, headers, 'json')

        for i, v in enumerate(res1['tracks']):
            temp_track_dict = {}
            temp_track_dict['track_name'] = v['track_name']
            temp_track_dict['track_id'] = v['track_id']
            temp_track_dict['track_number'] = v['track_number']
            temp_track_dict['disc_number'] = v['disc_number']
            temp_track_dict['duration(minutes)'] = round((v['duration_ms']) / 60000, 2)

            # from spotify api
            temp_track_dict['popularity'] = track_ids_res['tracks'][i]['popularity']
            temp_track_dict['artist_number'] = len(track_ids_res['tracks'][i]['artists'])
            temp_track_dict['external_urls'] = track_ids_res['tracks'][i]['external_urls']['spotify']
            temp_track_dict['artists'] = [i['name'] for i in track_ids_res['tracks'][i]['artists']]
            tracks.append(temp_track_dict)

        columns = list(tracks[0].keys())
        returnList = [albumName, imgUrl, columns, tracks]
        return returnList
    except:
        return 0 


def albumData(artistName):
    if artistName:
        # columns=['Album_Name', 'Type', 'Total_tracks','Release_date', 'Artists', 'Available_markets','External_urls']
        columns=['Album_cover', 'Album_Name', 'Type', 'Release_date', 'Total_tracks', 'Artists','External_urls']

        # search album info using artist name and ID, for specific
        # 每筆 doc較雜亂無章，每筆 doc裡面有很多 item
        # 可能是rapper 本人的 album，也有可能是他出現在別人的那張album
        collection1 = Spotify('rapper_album_information')
        collection2 = Spotify('rapper_information')

        try:
            # 透過 rapper information 找 id
            artistID = collection2.get_collection_search_query('name', artistName)['id']
            query = {'items.artists.name': artistName, 
                     'items.artists.id': artistID}
            # 找所有符合的 album(歌手全部的album)
            df = pd.DataFrame(
                collection1.get_collection_search_query_multiple_conditions(query, 'and')
                )
            if not df.empty:
                templist1 = []
                # 每筆document(可能是他自己的專輯/ 或是他有出線的專輯)
                for doc in df['items']:
                    # 每個 item
                    for j in doc:
                        artist_list = []
                        for idx, x in enumerate(j['artists']):
                            if artistName in x.values():
                                len1 = len(j['artists'])
                                for y in range(len1):
                                    artist_list.append(j['artists'][y]['name'])
                                templist1.append({columns[0]: j['images'][0]['url'], 
                                                columns[1]: j['name'], 
                                                columns[2]: j['album_type'], 
                                                columns[3]: j['release_date'], 
                                                columns[4]: j['total_tracks'], 
                                                columns[5]: artist_list, 
                                                columns[6]: j['external_urls']['spotify']})
            
            dfshow = pd.DataFrame.from_dict(templist1)

            # remove duplicated data and sort by release date in descending order
            dfshow['Release_date'] = pd.to_datetime(dfshow['Release_date'], format='%Y%m%d', errors='ignore')
            # 刪除重複資料
            dfshow = dfshow.loc[dfshow.astype(str).drop_duplicates().index].sort_values(by='Release_date', ascending=False).reset_index(drop=True)
            dfDict = dfshow.to_dict('records')

            returnList = [artistName, dfDict, columns]
            """ 
            輸入artist name 回傳範例
            dfDict 為可搜尋到的所有album如下 eg.
            很多筆
            [{},
              {'Album_cover': 'https://i.scdn.co/image/ab67616d0000b2735580eed61be56d710c5eac31',
                'Album_Name': 'Vultures',
                'Type': 'single',
                'Release_date': '2023-11-18',
                'Total_tracks': 1,
                'Artists': ['¥$', 'Kanye West', 'Ty Dolla $ign'],
                'External_urls': 'https://open.spotify.com/album/2mT5CGX436a2WbCUMuR20Y'},
                ...,
                {}         
            ]
            """
            return returnList
        except:
            return 0
        
# 輸出columns有增加，要更改
# give artsit name
# return 所有專輯和singles列表
# ['disc_type',
#  'release_date',
#  'total_artists',
#  'disc_image',
#  'disc_name',
#  'disc_id',
#  'total_tracks',
#  'external_urls']
def albumData2(artistName):
    if artistName:
        try:
            r1 = Spotify('new_rap_ID').collection.find_one({'name':artistName})
            # artistName = r1['name']
            # album_lists = []
            rapper_all_songs = []
            for i, v in enumerate(r1['singles']+r1['albums']):
                temp_dict = {}
                temp_dict['disc_type'] = v['album_type']
                temp_dict['release_date'] = v['release_date']
                temp_dict['total_artists'] = [i['name'] for i in v['total_artists']]
                temp_dict['disc_image'] = v['images'][0]['url']
                
                if temp_dict['disc_type']=='single':
                    temp_dict['disc_name'] = v['single_name']
                    temp_dict['disc_id'] = v['single_id']
                    temp_dict['total_tracks'] = v['total_singles_num']
                else: # album
                    temp_dict['disc_name'] = v['album_name']
                    temp_dict['disc_id'] = v['album_id']
                    temp_dict['total_tracks'] = v['total_tracks_num']

                temp_dict['external_urls'] = f"https://open.spotify.com/album/{temp_dict['disc_id']}"
                rapper_all_songs.append(temp_dict)
            columns = list(rapper_all_songs[0].keys())
            returnList = [artistName, rapper_all_songs, columns]
            return returnList
        except:
            return 0


# 回傳的東西比 trackData2 還要少，
# first one is artist's name, second one is album name
def trackDataGen(artName, albName):
    try:
        collection1 = Spotify('rapper_album_information')
        collection2 = Spotify('rapper_track_general_information')

        filter1 = {'items.name': albName, 
                  'items.artists.name': artName}
        df1 = pd.DataFrame(
            collection1.get_collection_search_query_multiple_conditions(filter1, 'and'))
        list1 = df1.loc[0]['items']
        df2 = pd.DataFrame.from_records(list1)
        albumID = df2[df2['name'] == albName]['id'].iloc[0]


        '''columns to retrieve'''
        cols = ['Track Name', 'Artists', 'External_urls']
        res = collection2\
            .get_collection_search_query('href',
                                         {"$regex":f"{albumID}"})
        templist = []
        for i in res['items']:
            singerlist = []
            for j in i['artists']:
                singerlist.append(j['name'])
            templist.append({cols[0]: i['name'],
                            cols[1]: singerlist,
                            cols[2]: i['external_urls']['spotify']
                            })

        returnList = [albName, albumID, templist, cols, artName]
        return returnList

    except:
        return 0
    

    

if __name__ == '__main__':
    # sort = 'followers'
    # sortPopularity(sort)
    albumID = '1GG6U2SSJPHO6XsFiBzxYv'
    trackData(albumID)