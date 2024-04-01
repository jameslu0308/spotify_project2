# Spotify-project

## Getting started
### 前置作業
* 建立Spotify app 後取得client ID 和Secret
  * 至 https://developer.spotify.com/documentation/web-api ，登入自己的Spotify帳號
  * 依照 **Getting Started** 步驟建立app，取得client ID 和Secret
* 安裝Docker

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
3. 執行getData.py 裡的**def InfoFromSpotify**，讀取 ID 進行 Spotify API 搜尋後將資訊存入DB
