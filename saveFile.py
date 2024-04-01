import os
import json
import pandas as pd
import time

# get raw data from getdata
# save content into txt
def saveTxt(data, path, name, mode):
    dateNow = time.strftime("%Y%m%d", time.localtime())
    os.makedirs(f'{path}/{dateNow}', exist_ok=True)
    newPath = f'{path}/{dateNow}'
    f = open(os.path.join(newPath, name), mode)
    if isinstance(data, list):
        for i in data:
            f.write(i + '\n')
    # elif isinstance(data, str):
    #     f.write(f'{data}\n')
    else:
        f.write(f'{data}\n')
    f.close()
    # print(f'Save {name} done!')


# save content into csv
def saveCsv(data, type, genre):
    dateNow = time.strftime("%Y%m%d", time.localtime())
    os.makedirs(f'files/{dateNow}', exist_ok=True)
    file = f'files/{dateNow}/{type}_{genre}{dateNow}.csv'
    data.to_csv(file)
    # print(f'Save {file} done!')