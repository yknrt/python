import pandas as pd
import const
from icecream import ic

def read_matrix(info):
    df_matrix = pd.read_csv(info['file']['input']['matrix'], header=2)
    matrixT = pd.read_csv(info['file']['input']['matrix'], header=2, usecols=[0,1])

    header = pd.read_csv(info['file']['input']['matrix'], header=None, nrows=3)
    headerHs = header.dropna(axis=1)
    num = len(headerHs.columns)

    dTs = matrixT.loc[1, 'Ts'] - matrixT.loc[0, 'Ts']
    dHs = float(df_matrix.columns[3]) - float(df_matrix.columns[2])

    dict_matrix = {}
    if num >= 2:
        for i, ncol in enumerate(headerHs.columns):
            if i == num - 1:
                ncol1 = len(df_matrix.columns)
            else:
                ncol1 = headerHs.columns[i+1]
            matrixH = df_matrix.iloc[:, ncol:ncol1]
            col = header.iloc[2, ncol:ncol1]
            matrixH.columns = col
            matrixH.index = matrixT.loc[:, 'Ts']
            matrixH = matrixH.astype('float')
            dict_matrix[headerHs.loc[0, ncol]] = matrixH
    else:
        matrixH = df_matrix.drop(columns=['Tp','Ts'])
        matrixH = matrixH.astype('float')
        dict_matrix[headerHs.loc[0, 2]] = matrixH
    return dict_matrix, dTs, dHs


def interpolation_matrix():
    def extract_num(l_delta):
        idx = [i for i, x in enumerate(l_delta) if x < dTs]
        if len(idx) == 0:
            min_delta = l_delta.index(min(l_delta))
            if min_delta == 0:
                idx = [min_delta, min_delta + 1]
            else:
                idx = [min_delta - 1, min_delta]
        elif len(idx) == 1:
            if idx[0] == 0:
                idx = [idx[0], idx[0] + 1]
            elif idx[0] == len(l_delta) - 1:
                idx = [idx[0] - 1, idx[0]]
        return idx

    output_row = [row['DateTime'], row['Hs'], row['Ts']]
    for _, matrix in dict_matrix.items():
        deltaTs = matrix.index - row['Ts']
        deltaTs = [abs(t) for t in deltaTs]
        idx_Ts = extract_num(deltaTs)

        deltaHs = [float(h) - row['Hs'] for h in matrix.columns]
        deltaHs = [abs(h) for h in deltaHs]
        idx_Hs = extract_num(deltaHs)

        query = matrix.iloc[idx_Ts, idx_Hs]
        if len(query)==1:
            q_dTs = dTs
        else:
            q_dTs = float(query.index[1]) - float(query.index[0])
        if len(query.columns)==1:
            q_dHs = dHs
        else:
            q_dHs = float(query.columns[1]) - float(query.columns[0])

        sratio = round((row['Hs'] - float(query.columns[0])) / q_dHs, 3)
        tratio = round((row['Ts'] - float(query.index[0])) / q_dTs, 3)

        if len(query.columns) == 2:
            move1 = (1 - sratio) * query.iloc[0,0] + sratio * query.iloc[0,1]
            if len(query) == 2:
                move2 = (1 - sratio) * query.iloc[1,0] + sratio * query.iloc[1,1]
            else:
                move2 = 0
        else:
            move1 = query.iloc[0,0]
            if len(query) == 2:
                move2 = query.iloc[1,0]
            else:
                move2 = 0
        move3 = round((1 - tratio) * move1 + tratio * move2, 3)
        if move3 < 0:
            move3 = 0
        output_row.append(move3)
    output_row = pd.DataFrame([output_row], columns=output_col)
    return output_row

def anomaly():
    l_val = [row['DateTime'], row['Hs'], row['Ts']]
    for _ in dict_matrix:
        l_val.append(9999)
    ic(len(l_val))
    output_row = pd.DataFrame([l_val], columns=output_col)
    return output_row

#ファイル読み込み
info = const.CONST
df = pd.read_csv(info['file']['input']['data'], header=[1])
df['DateTime'] = pd.to_datetime(df['DateTime'])

dict_matrix, dTs, dHs = read_matrix(info)

output_col = ['DateTime','Hs','Ts']
output_col.extend(list(dict_matrix.keys()))
output_df = pd.DataFrame()
for i, row in df.iterrows():
    if (row['Hs'] == 9999) or (row['Ts'] == 9999):
        output_row = anomaly()
    else:
        output_row = interpolation_matrix()
    output_df = pd.concat([output_df, output_row], axis=0)
output_df.to_csv(info['file']['output']['henkan'], index=None, encoding='shift-jis')
