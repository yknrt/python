import numpy as np
import pandas as pd
import const

def interpolate_linear(df):
    df = df.replace(9999, float('nan'))
    # 補間（内挿）
    df = df.interpolate(limit_area='inside', limit=info['異常値'])
    # 補間（外挿）
    for v in info['中止基準']:
        df01 = df[v].dropna()
        dlt = df01.index[0] - df.index[0]
        if (dlt > 0) and (dlt <= info['異常値']):
            l_val = df01.to_list()
            linear = round((l_val[1] - l_val[0]) / (df01.index[1] - df01.index[0]), 3)
            val = l_val[0]
            for i in range(dlt, -1, -1):
                val -= linear
                val = round(val, 3)
                df.loc[i, v] = val
    for v in info['中止基準']:
        df01 = df[v].dropna()
        dlt = df.index[-1] - df01.index[-1]
        if (dlt > 0) and (dlt <= info['異常値']):
            l_val = df01.to_list()
            linear = round((l_val[-1] - l_val[-2]) / (df01.index[-1] - df01.index[-2]), 3)
            val = l_val[-1]
            for i in range(dlt):
                ii = df01.index[-1] + (i + 1)
                val += linear
                val = round(val, 3)
                df.loc[ii, v] = val
    df = df.replace(float('nan'), 9999)
    return df


info = const.CONST
df = pd.read_csv(info['file']['output']['henkan'], encoding='shift-jis')
df['DateTime'] = pd.to_datetime(df['DateTime'])
df = interpolate_linear(df)
#異常値データの除去
for v in info['中止基準']:
    reference = info['中止基準'][v]
    if reference == None:
        continue
    df = df[df[v] < 9999]

#稼働可否の判定
query = df.copy()
for v in info['中止基準']:
    reference = info['中止基準'][v]
    if reference == None:
        continue
    query = query[query[v] < reference]
query.reset_index(drop=True, inplace=True)

y4_min = df.iloc[0]['日時'].year
y4_max = df.iloc[-1]['日時'].year
query_td_all = pd.DataFrame()
for y4 in range(y4_min, y4_max + 1):
    for m2 in range(1, 13):
        query01 = query[(query['日時'].dt.year == y4) & (query['日時'].dt.month == m2)]
        query_td = query01.loc[:, '日時'].diff()
        query_td = query_td.dt.total_seconds() / 3600
        query_td_all = pd.concat([query_td_all, query_td], axis=0)
query_td_all.index = query.index
query_td_all.columns = ['timedelta']
query = pd.concat([query, query_td_all], axis=1)

#連続稼働時間
query_td_not_1h = query[query['timedelta'] != 1]
idx = query_td_not_1h.index
df_num = pd.DataFrame()
for n, i in enumerate(idx):
    if i == idx[-1]:
        query_event = query.loc[i:, :]
    else:
        query_event = query.loc[i:idx[n+1]-1 , :]
    arr = np.full(len(query_event), len(query_event))
    df_arr = pd.DataFrame(arr, columns=['num'], index=query_event.index)
    df_num = pd.concat([df_num, df_arr], axis=0)
query = pd.concat([query, df_num], axis=1)

#全年の月単位稼働率
dict_rate = {}
df_rate = pd.DataFrame()
for m2 in range(1, 13):
    df_m2 = df[df['DateTime'].dt.month == m2]
    if len(df_m2) == 0:
        continue
    query_m2 = query[query['DateTime'].dt.month == m2]
    list_rate = []
    list_col = []
    for n in range(info['連続静穏時間']['min'], info['連続静穏時間']['max']+1):
        list_col.append(n)
        query_m2_n = query_m2[query_m2['num'] >= n]
        rate = len(query_m2_n) / len(df_m2) * 100
        list_rate.append(rate)
    df_rate_y4 = pd.DataFrame([list_rate], columns=list_col, index=['{}月'.format(m2)])
    df_rate = pd.concat([df_rate, df_rate_y4], axis=0)
dict_rate['all'] = df_rate

#年ごとの月単位稼働率
y4_min = df.iloc[0]['DateTime'].year
y4_max = df.iloc[-1]['DateTime'].year
for y4 in range(y4_min, y4_max + 1):
    df_rate = pd.DataFrame()
    df_y4 = df[df['DateTime'].dt.year == y4]
    if len(df_y4) == 0:
        continue
    query_y4 = query[query['DateTime'].dt.year == y4]
    for m2 in range(1, 13):
        df_y4_m2 = df_y4[df_y4['DateTime'].dt.month == m2]
        if len(df_y4_m2) == 0:
            continue
        query_y4_m2 = query_y4[query_y4['DateTime'].dt.month == m2]
        list_rate = []
        list_col = []
        for n in range(info['連続静穏時間']['min'], info['連続静穏時間']['max']+1):
            list_col.append(n)
            query_y4_m2_n = query_y4_m2[query_y4_m2['num'] >= n]
            rate = len(query_y4_m2_n) / len(df_y4_m2) * 100
            list_rate.append(rate)
        df_rate_y4 = pd.DataFrame([list_rate], columns=list_col, index=['{}月'.format(m2)])
        df_rate = pd.concat([df_rate, df_rate_y4], axis=0)
    df_rate.index.name = '{}年'.format(y4)
    dict_rate['{}年'.format(y4)] = df_rate

#P50
for p in info['percentile']:
    dict_quantile = {}
    dict_quantile[p] = pd.DataFrame()
for m2 in range(1, 13):
    idx = '{}月'.format(m2)
    df_input = pd.DataFrame()
    for d in dict_rate:
        if d == 'all':
            continue
        df_rate = dict_rate[d]
        if len(df_rate) < 12:
            continue
        df_rate_m2 = df_rate.loc['{}月'.format(m2), :]
        df_rate_m2 = pd.DataFrame([df_rate_m2])
        df_input = pd.concat([df_input, df_rate_m2], axis=0)

    df_output = df_input.quantile(info['percentile'], interpolation=info['interpolation'])
    for p in info['percentile']:
        df_quantile = df_output.loc[p, :]
        df_quantile.name = idx
        df_quantile = pd.DataFrame([df_quantile])
        dict_quantile[p] = pd.concat([dict_quantile[p], df_quantile], axis=0)

#データ出力
df_output = pd.DataFrame()
for k in dict_quantile:
    df = dict_quantile[k]
    idx = 'P{}'.format(int(k*100))
    df.index.name = idx
    df.reset_index(inplace=True)
    df.loc[9999] = float('nan')
    df_col = pd.DataFrame([df.columns])
    new_col = np.arange(len(df.columns))
    df.columns = new_col
    df_output = pd.concat([df_output, df_col, df], axis=0)
    
for k in dict_rate:
    df = dict_rate[k]
    idx = k
    df.index.name = idx
    df.reset_index(inplace=True)
    df.loc[9999] = float('nan')
    df_col = pd.DataFrame([df.columns])
    new_col = np.arange(len(df.columns))
    df.columns = new_col
    df_output = pd.concat([df_output, df_col, df], axis=0)

df_output.to_csv(info['file']['output']['kadou'], index=None, header=None, encoding='shift-jis')