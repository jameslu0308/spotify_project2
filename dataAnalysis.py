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

    collName = 'rapper_information'
    _table = Spotify(collName)
    dfPop = pd.DataFrame(_table.sort_search(sorItem, 'desc'))

    # show top 50 data
    dfshow = dfPop[:50]

    sortName = dfshow['name'].str.replace(',', '-').to_list()
    if sorItem == 'followers':
        sortData = dfshow[sorItem].apply(lambda x: x['total']).to_list()
    elif sorItem == 'popularity':
        sortData = dfshow[sorItem].to_list()


    '''get genre data'''
    show1 = 'genres'
    showtmp = dfshow[show1].to_list()
    showtmp2 = [item for sublist in showtmp for item in sublist]
    showSer = pd.Series(showtmp2).value_counts()
    showName = list(showSer.index)
    showData = list(showSer)
    # print(sort2Data)

    # value to return
    titleList = [sorItem, sort2, show1]
    dataList = dict(zip(sortName, sortData))
    genreList = dict(zip(showName, showData))
    # print(genreList)

    return titleList, dataList, genreList


'''
show track data in the album, sort by popularity
'''

def trackData(albumID):
    collName = 'rapper_track_general_information'
    table = Spotify(collName)
    query = {"$regex":f"{albumID}"}
    df1 = pd.DataFrame(table.get_collection_search_query('href', query)['items'])  #retrieve each track's api from DB
    # print(df1)

    # request track information through API
    srcID = os.getenv("SPOTIFY_TOKEN_OWNER")
    collName = 'spotify_token'
    type, token = backendFunc.checkToken(collName, srcID)
    headers = {'Authorization': f"{type} {token}"}

    list1 = []
    for i in df1['href']:
        res = backendFunc.requestUrl(i, headers, 'json')
        list1.append(res)
    df2 = pd.DataFrame.from_records(list1)
    col = ['Track Name', 'Artists', 'Artist Number', 'Popularity', 'Duration (minutes)']
    list2 = []

    '''retrieve data from API call'''
    for j in range(df2.shape[0]):
        tmpSer = df2.iloc[j]

        if len(list2) == 0:
            albumName = tmpSer['album']['name']
            imgUrl = tmpSer['album']['images'][1]['url']
        singList = []
        for w in tmpSer['artists']:
            singList.append(w['name'])
        numArt = len(tmpSer['artists'])
        songLen = round((tmpSer['duration_ms']) / 60000, 2)
        list2.append({
            col[0]: tmpSer['name'],
            col[1]: singList,
            col[2]: numArt,
            col[3]: tmpSer['popularity'],
            col[4]: songLen
        })

    dfshow = pd.DataFrame.from_dict(list2)
    dfshow = dfshow.sort_values(by='Popularity', ascending=False)
    dfDict = dfshow.to_dict('records')
    # print(dfDict)

    return albumName, imgUrl, col, dfDict


def ablumData(artistName):
    if artistName:
        # columns=['Album_Name', 'Type', 'Total_tracks','Release_date', 'Artists', 'Available_markets','External_urls']
        columns=['Album_cover', 'Album_Name', 'Type', 'Release_date', 'Total_tracks', 'Artists','External_urls']

        # search album info using artist name and ID, for specific
        name1 = 'rapper_album_information'
        name2 = 'rapper_information'
        table1 = Spotify(name1)
        table2 = Spotify(name2)

        try:
            artistID = table2.get_collection_search_query('name', artistName)['id']
            query = {'items.artists.name': artistName, 'items.artists.id': artistID}
            df = pd.DataFrame(table1.get_collection_search_query_multiple_conditions(query, 'and'))
            if not df.empty:
                templist1 = []
                for i in df['items']:
                    for j in i:
                        artisList = []
                        for idx, x in enumerate(j['artists']):
                            if artistName in x.values():
                                len1 = len(j['artists'])
                                for y in range(len1):
                                    artisList.append(j['artists'][y]['name'])
                                templist1.append({columns[0]: j['images'][0]['url'], 
                                                columns[1]: j['name'], 
                                                columns[2]: j['album_type'], 
                                                columns[3]: j['release_date'], 
                                                columns[4]: j['total_tracks'], 
                                                columns[5]: artisList, 
                                                columns[6]: j['external_urls']['spotify']})
            
            dfshow = pd.DataFrame.from_dict(templist1)

            # remove duplicated data and sort by release date in descending order
            dfshow['Release_date'] = pd.to_datetime(dfshow['Release_date'], format='%Y%m%d', errors='ignore')
            dfshow = dfshow.loc[dfshow.astype(str).drop_duplicates().index].sort_values(by='Release_date', ascending=False).reset_index(drop=True)
            dfDict = dfshow.to_dict('records')
            returnList = [artistName, dfDict, columns]

            return returnList
        
        except:
            return 0
        

# fisrt one is artist's name, second one is album name
def trackDataGen(artName, albName):
    try:
        collName1 = 'rapper_album_information'
        collName2 = 'rapper_track_general_information'
        table1 = Spotify(collName1)
        table2 = Spotify(collName2)

        query1 = {'items.name': albName, 'items.artists.name': artName}
        df1 = pd.DataFrame(table1.get_collection_search_query_multiple_conditions(query1, 'and'))
        list1 = df1.loc[0]['items']
        df2 = pd.DataFrame.from_records(list1)
        albumID = df2[df2['name'] == albName]['id'].iloc[0]


        '''columns to retrieve'''
        cols = ['Track Name', 'Artists', 'External_urls']
        query2 = {"$regex":f"{albumID}"}
        res = table2.get_collection_search_query('href', query2)
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