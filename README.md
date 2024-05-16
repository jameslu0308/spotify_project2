# Spotify-project

## Getting started
### 前置作業
* 建立Spotify app 後取得client ID 和Secret
  * 至 https://developer.spotify.com/documentation/web-api ，登入自己的Spotify帳號
  * 依照 **Getting Started** 步驟建立app，取得client ID 和Secret
* 以VMWare建立 Ubuntu 2204 linux 環境
* 透過Docker建立 NoSQL container 

###### 配置檔 .env
```
CLIENT_ID = ""
CLIENT_SECRET = ""
DB_ROOT_USERNAME = ''
DB_ROOT_PASSWORD = ''
DB_HOST = localhost
DB_PORT = 27017
DB_NAME = "Spotify"
SPOTIFY_TOKEN_OWNER = ''
```
#### 啟動環境
- pip install -r requirements.txt  
- docker compose config  _# check docker-compose.yml output with environment variables_  
- docker compose up -d  _# 啟動開發用資料庫_

#### 資料蒐集步驟
* Main程式為"getData.py"
1. 蒐集歌手名單 --->> 可參考**getArtist.py**
2. 執行getData.py 裡的**def getArtistId** ，取得歌手的Spotify ID 並存入DB
3. 執行getData.py 裡的**def InfoFromSpotify**，讀取 ID 進行 Spotify API 搜尋後將資訊存入DB，建立collection new_rap_ID，每筆document為一位嘻哈歌手相關資訊，fields包含專輯數、人氣
4. **getArtist_prac.ipynb**更新 new_rap_ID 每位歌手為唯一，刪除重複與無效資料
5. **cleanDB.ipynb**透過new_rap_ID讀取每位歌手_ID抓取每位歌手的album，存為另一個
collection new_album_info，每筆document為一張專輯，fields包含發行日、歌曲數、每首歌相關資訊

#### 前後端呈現
1. 以 **Flask** 建立Web後端應用，**Javascript**、**HTML**語法建立前端頁面呈現
2. 頁面 1. 根據人氣排序水平長條圖 2. 根據歌手統計各類風格比例圓餅圖

#### ETL
1. docker compose 建立**airflow**，串接NoSQL，每天更新歌手人氣等相關資料

#### Overall page example
1. followers/popularity page
![image](https://github.com/jameslu0308/spotify_project2/blob/main/img/followers.png =400x300)

2. rapper page
![image](https://github.com/jameslu0308/spotify_project2/blob/main/img/rapper_page.png =400x300)

3. disc page
![image](https://github.com/jameslu0308/spotify_project2/blob/main/img/disc_page.png =400x300)

4. album page
![image](https://github.com/jameslu0308/spotify_project2/blob/main/img/album_page.png =400x300)

