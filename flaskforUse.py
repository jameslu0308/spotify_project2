from DB import Spotify
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
from flask import Flask, render_template, redirect, request, url_for, jsonify, make_response
import dataAnalysis
from genius1 import findLyrics
app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def hello():
    text = "Hello, World! Searching for music?"
    if request.method == 'POST':
        srcItem = request.form['srcFilter']
        return redirect(url_for('showStats', srcFilter=srcItem))
    else:
        return render_template('welcomepage.html', text=text)

@app.route("/stats/<string:srcFilter>")
def showStats(srcFilter):
    title, srcData, genreData = dataAnalysis.sortPopularity(srcFilter)
    return render_template('stats1.html', value1=title, value2=srcData, value3=genreData)


@app.route("/artist/<string:name>")
def query_artist(name):
    if name:
        try:
            info = Spotify('rapper_information').get_collection_search_query('name', name)
            # choose 320*320
            src = info['images'][1]['url']
            return render_template('index.html', artist=info, img=src)
        except:
            return 'No artist found!'

@app.route("/album/<string:name>")
def query_ablum(name):
    res = dataAnalysis.ablumData(name)
    if res == 0:
        return 'No album information found!'
    else:
        return render_template('index2v2.html', artistName = res[0], table_data = res[1], colname = res[2])
        

@app.route('/tracks/<string:artName>/<string:albName>')  # fisrt one is artist's name, second one is album name
def trackinfoGen(artName, albName):
    res = dataAnalysis.trackDataGen(artName, albName)
    if res == 0:
        return 'No track information yet!'
    else:
        return render_template('trackInfo1.html', albumName = res[0], albumID = res[1], table_data = res[2], colname = res[3], artName = res[4])
        

@app.route("/tracks/detail/<string:albumID>")
def trackDetail(albumID):
    albName, imgUrl, colName, list = dataAnalysis.trackData(albumID)
    return render_template('trackInfo2.html', albumName = albName, imgUrl = imgUrl, table_data = list, colname = colName)


@app.route("/tracks/lyrics/<string:artName>/<string:tracName>")
def lyricsShow(artName, tracName):
    res = findLyrics(artName, tracName)
    if res == 0:
        return 'No lyrics information found!'
    else:
        return render_template('trackLyrics.html', table_data = res, tracName = tracName)
        


app.run(port=5000, debug=True, host='0.0.0.0')