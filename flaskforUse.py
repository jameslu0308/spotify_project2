from DB import Spotify
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
from flask import Flask, render_template, redirect, request, url_for, jsonify, make_response
import dataAnalysis
from genius1 import findLyrics
app = Flask(__name__)

# MVC架構中的controller功能
# 將資料從model中獲得，並且將數據傳到view，它包含應用程式的業務邏輯
@app.route("/", methods=['POST', 'GET'])
def hello():
    text = "Hello, World! Searching for music?"
    if request.method == 'POST':
        srcItem = request.form['srcFilter']
        return redirect(url_for('showStats', srcFilter=srcItem))
    else:
        return render_template('welcomepage.html', text=text)
#<string> 是一種轉換器，它將 URL 路徑中的部分轉換為字符串作為參數傳遞
@app.route("/stats/<string:srcFilter>")
def showStats(srcFilter):
    title, rap_dict, genres_dict = dataAnalysis.sortPopularity2(srcFilter)
    return render_template('rankingstats.html', value1=title, 
                           value2=rap_dict, value3=genres_dict)

@app.route("/artist/<string:name>")
def query_artist(name):
    if name:
        try:
            info = Spotify('new_rap_ID2').collection.find_one({'name':name})
            # choose 320*320
            src = info['images'][1]['url']
            return render_template('rapper_info.html', artist=info, img=src)
        except:
            return 'No artist found!'


# 輸入artist name
# 回傳 album list 頁面
@app.route("/album/<string:name>")
def query_ablum(name):
    res = dataAnalysis.albumData2(name)
    if res == 0:
        return 'No album information found!'
    else:
        modify_col = ['Disc_cover', 'Disc_name', 'Disc_type', 'Release_date', \
                      'Total_tracks', 'Total_artists', 'External_url']
        return render_template('disc_list.html', artistName = res[0], table_data = res[1], colname = modify_col)
        

@app.route('/tracks/<string:artName>/<string:albName>')  # fisrt one is artist's name, second one is album name
def trackinfoGen(artName, albName):
    res = Spotify('new_album_info2').collection.find_one(
        {'main_artist': artName,
         'album_name': albName}
        )
    album_id  = res['album_id']

    res1 = dataAnalysis.trackData2(album_id)

    #res = dataAnalysis.trackDataGen(artName, albName)
    if res1 == 0:
        return 'No track information yet!'
    else:
        ##########################
        #要修改這邊
        modify_col = ['Track_name','Disc_number', 'Track_number',\
                      'Duration(m)','Popularity','Artists_number',\
                        'Artists','External_urls']
        return render_template('track_list.html', albumName = res1[0], albumID = album_id, \
                               table_data = res1[3], colname = modify_col, artName = artName,\
                                imgUrl = res1[1])
        

@app.route("/tracks/detail/<string:albumID>")
def trackDetail(albumID):
    albName, imgUrl, colName, list = dataAnalysis.trackData(albumID)
    return render_template('trackInfo2.html', albumName = albName, imgUrl = imgUrl, table_data = list, colname = colName)

# 未完成
@app.route("/tracks/lyrics/<string:artName>/<string:tracName>")
def lyricsShow(artName, tracName):
    res = findLyrics(artName, tracName)
    if res == 0:
        return 'No lyrics information found!'
    else:
        return render_template('trackLyrics.html', table_data = res, tracName = tracName)
        


app.run(port=5000, debug=True, host='0.0.0.0')