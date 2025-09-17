# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 14:53:42 2022

@author: yknrt
"""

import requests
import pandas as pd
import datetime
import time
import traceback
import json
import os
from requests.exceptions import HTTPError
import const


def read_json(URL):
    MAX_RETRY = 3
    for i in range(MAX_RETRY):
        try:
            r = requests.get(URL)  ##　requestsを使って、webから取得
            r.encoding = r.apparent_encoding
            r.raise_for_status() # エラーチェック
            data = r.json()
        except HTTPError:
            time.sleep(5)
            if i == MAX_RETRY - 1:
                return False
        except:
            time.sleep(5)
            if i == MAX_RETRY - 1:
                traceback.print_exc()
                return False
        else:
            with open('../wl.json', mode='w', encoding='shift-jis') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            break
    return data

def get_time(curr_time):
    m = (curr_time.minute // 5) * 5
    curr_time = datetime.datetime(curr_time.year, curr_time.month, curr_time.day, curr_time.hour, m)
    return curr_time


INFO = const.CONST

curr_time = datetime.datetime.now()
curr_time = get_time(curr_time)

for obs in INFO['URL']:
    for it in range(3):
        url_time = curr_time - datetime.timedelta(minutes = (5 * it))
        URL = INFO['URL'][obs].format(url_time.year, url_time.month, url_time.day, url_time.hour, url_time.minute)
        data = read_json(URL)
        if data != False:
            break
    try:
        data_list = data['min10Values']
    except:
        continue

    dt_list = []
    wl_list = []
    for dict_data in data_list:
        dt_list.append(dict_data['obsTime'])
        if obs == '玉川':
            wl_list.append(dict_data['stg'])
        else:
            wl_list.append(dict_data['stgHght'])
    if obs == '玉川':
        df = pd.DataFrame({'time':dt_list, '水位（m）':wl_list})
    else:
        df = pd.DataFrame({'time':dt_list, '堤防天端からの高さ（m）':wl_list})
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.sort_index(inplace=True)
    df.dropna(inplace=True)
    dt = df.index[-1]

    filepath = INFO['dir']['output'] + obs + '.csv'
    if os.path.isfile(filepath):
        df_all = pd.read_csv(filepath, index_col=['time'], parse_dates=True, encoding='shift-jis')
        pre_dt = df_all.index[-1]
    else:
        df_all = pd.DataFrame()
        pre_dt = datetime.datetime(2022, 1, 1)
    if pre_dt < dt:
        # df_all = df_all.append(df)
        df_all = pd.concat([df_all, df], axis=0)
        df_all = df_all.loc[~df_all.index.duplicated(keep = "last"),:]
        df_all.sort_index(inplace=True)
        df_all.to_csv(filepath, encoding='shift-jis')
    
