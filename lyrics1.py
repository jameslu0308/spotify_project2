import os
import backendFunc
import pandas as pd
import numpy as np
from DB import Spotify
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)



def genArtist(artName, songName):
    # count = 1
    while True:
        genToken = os.getenv('GENIUS_ACCESS_TOKEN')
        srcUrl = f'https://api.genius.com/search?q={songName}'
        # srcUrl = f'https://api.genius.com/search?q={name}&per_page=50&type_=album&page={count}'   # maximum result return is 20, many pages
        # srcUrl = f'https://api.genius.com/search?q={name}&per_page=50&type_=album&page=100'
        # srcUrl = f'https://api.genius.com/search?q={name}&type=album'
        headers = {'Authorization': f"Bearer {genToken}"}

        res1 = backendFunc.requestUrl(srcUrl, headers, 'json')['response']['hits']
        if len(res1) == 0:
            break

        df1 = pd.DataFrame(res1)
        # tname = 'genius_sing_information'
        # _table = Spotify(tname)

        for i in range(df1.shape[0]):
            res2 = df1['result'].iloc[i]
            if res2['artist_names'] == artName:
                print(res2['path'])
                return res2['path']
            break
            # _table.insert_one(res2)
        # print(count)
        # count+=1

        

def genPackage():
    import lyricsgenius
    genius = lyricsgenius.Genius()
    # srcArt = genius.artist()
    srcArt = genius.search_artist('Tyler, The Creator',max_songs=3 , sort='popularity')
    print(srcArt)



if __name__ == '__main__':
    # name = 'Tyler, The Creator'
    name = 'Kendrick Lamar'
    genArtist(name)

    # genPackage()