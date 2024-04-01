import os
import requests
import time
from bs4 import BeautifulSoup
from backendFunc import requestUrl

# get rapper name source
genre = 'rap'
# nameUrl = 'https://boardroom.tv/most-streamed-rappers-on-spotify-2023/'
nameUrl = 'https://raptology.com/rappers-a-z/'
soup = requestUrl(nameUrl, resType = 'soup')

# based on html structure, retrieve name
a_name_tags = soup.select('section ul a')
# a_name_tags = soup.find_all('a')
nameList = []
for idx, element in enumerate(a_name_tags):
    nameList.append(element.text)
# print(nameList)

# save file into txt calling saveFile.py
import saveFile
dateNow = time.strftime("%Y%m%d", time.localtime())
txtPath = f'files/source/{genre}'
txtName = f'artistlist{dateNow}.txt'
saveFile.saveTxt(nameList, txtPath, txtName,'w')