import os
import backendFunc
import pandas as pd
import numpy as np
from DB import Spotify
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def form1():

    '''
    save data in DB
    '''
    tname = 'genius_sing_information'
    _table = Spotify(tname)
    col1 = ['title', 'api_path', 'artist_names', 'full_title', 'lyrics_state', 'header_image_url', 'stats.hot']
    res1 = _table.get_collection_search_specific_columns(col1)
    df1 = pd.DataFrame(res1)
    df1.to_csv('output/test2.csv', index=False)
    # print(df1.iloc[28])


def genLyrPath(artName, songName):
    count = 1
    while True:
        genToken = os.getenv('GENIUS_ACCESS_TOKEN')
        srcUrl = f'https://api.genius.com/search?q={songName}&per_page=50&page={count}'
        # srcUrl = f'https://api.genius.com/search?q={name}&per_page=50&type_=album&page={count}'   # maximum result return is 20, many pages

        headers = {'Authorization': f"Bearer {genToken}"}
        res1 = backendFunc.requestUrl(srcUrl, headers, 'json')['response']['hits']
        if len(res1) == 0:
            return 0

        df1 = pd.DataFrame(res1)
        for i in range(df1.shape[0]):
            res2 = df1['result'].iloc[i]
            if res2['artist_names'] == artName:
                src = res2['path']
                lyrUrl = f'https://genius.com{src}'
                print(lyrUrl)
                return lyrUrl
            break
        count+=1



def findLyrics(artName, tracName):
    # src1 = 'https://api.genius.com'
    # apiPath = '/songs/51801'
    # url1 = f'{src1}{apiPath}'
    # genToken = os.getenv('GENIUS_ACCESS_TOKEN')
    # headers = {'Authorization': f"Bearer {genToken}"}
    # res1 = backendFunc.requestUrl(url1, headers, 'json')['response']['song']['url']
    # print(res1)

    '''get the lyrics'''
    lyricContent = []
    url = genLyrPath(artName, tracName)
    if url == 0:
        return 0
    res2 = backendFunc.requestUrl(url, None, 'soup')
    if len(res2) == 0:
        return 0
    else:
        # data1 = res2.select('a span')
        data1 = res2.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
        for i in data1:
            for j in i:
                if len(j) == 0:
                    continue
                lyricContent.append(j.text)
        # print(lyricContent)
        return lyricContent




# if __name__ == '__main__':
#     # form1()
#     # findLyrics('Tyler, The Creator', 'EARFQUAKE')
#     findLyrics('Post Malone', 'Circles')