#!/usr/bin/env python
# coding: utf-8
import os
import numpy as np
import pandas as pd
import OrcFxAPI
import const #const.py(定数設定ファイル)をインポート


def createCase(info):
    # step1：入力ケースのテキストファイルを作成
    waveHeights = info['case']['Heights']
    wavePeriods = info['case']['Periods']
    waveDegree = info['case']['Degrees']

    listHeight = []
    listPeriod = []
    listDegree = []

    for H in waveHeights:
        for T in wavePeriods:
            listHeight.append(H)
            listPeriod.append(T)
            listDegree.append(waveDegree)

    df_case = pd.DataFrame({'Height':listHeight, 'Period':listPeriod, 'Degree':listDegree})
    df_case.to_csv(info['case']['file'], index=None)


def analysis(info):
    # step2：OrcaFlexによる解析．解析前データ(.dat)，解析済みデータ(.sim)，時系列データの出力
    OrcFxInfo = info['OrcaFlex']

    df_case = pd.read_csv(info['case']['file'])
    model = OrcFxAPI.Model(OrcFxInfo['model'])
    model.environment.SelectedWaveTrain = model.environment.WaveName[0]

    df_minMax = pd.DataFrame()
    for _, row in df_case.iterrows():
        H = row['Height']
        T = row['Period']
        D = row['Degree']
        print('H =', H, ',T =', T, ',Deg =', D)
        model.environment.WaveHeight = H
        model.environment.WavePeriod = T
        model.environment.WaveDirection = D
        id = OrcFxInfo['id']

        if OrcFxInfo['save']['dat']:
            fileNamedat = OrcFxInfo['output'] + 'case{0:03d},H={1:.3f},T={2:.2f},Deg={3:.1f}.dat'.format(id, H, T, D)
            model.SaveData(fileNamedat)

        model.CalculateStatics()
        model.RunSimulation()
        if OrcFxInfo['save']['sim']:
            fileNamesim = OrcFxInfo['output'] + 'case{0:03d},H={1:.3f},T={2:.2f},Deg={3:.1f}.sim'.format(id, H, T, D)
            model.SaveSimulation(fileNamesim)

    ##################################################################################
        period = OrcFxAPI.SpecifiedPeriod(OrcFxInfo['period'][0], OrcFxInfo['period'][1])
        times = model.SampleTimes(period)
        df_data = pd.DataFrame(times, columns=['Period'])

        dict_obj = {}
        for obj in OrcFxInfo['object']:
            objInfo = OrcFxInfo['object'][obj]
            for data in objInfo['data']:
                key = '{}_{}'.format(objInfo['name'], data)
                if 'R' in data:
                    timeHistory = model[obj].TimeHistory(data, period)
                    # linkedStatistics = model[obj].LinkedStatistics([data], period)
                else:
                    if obj == 'body':
                        oe = OrcFxAPI.oeVessel(objInfo['xyz'][0], objInfo['xyz'][1], objInfo['xyz'][2])
                    elif obj == 'MP':
                        oe = OrcFxAPI.oeBuoy(objInfo['xyz'][0], objInfo['xyz'][1], objInfo['xyz'][2])
                    timeHistory = model[obj].TimeHistory(data, period, oe)
                    # linkedStatistics = model[obj].LinkedStatistics([data], period, oe)
                #任意の時系列結果を保存する
                if data in objInfo['save']:
                    df = pd.DataFrame(timeHistory, columns=[key])
                    df_data = pd.concat([df_data, df], axis=1)
                dict_obj[key] = timeHistory

        # 時系列結果の出力
        if len(df_data.columns) > 1:
            df_data.to_csv(OrcFxInfo['output'] + 'case{0:03d},H={1:.3f},T={2:.2f},Deg={3:.1f}.csv'.format(id, H, T, D), index=None)

        # 時系列結果の最大最小を取得し出力する
        listCol = []
        listVal = []
        for k, v in dict_obj.items():
            listCol.append('{}_max'.format(k))
            listVal.append(max(v))
            listCol.append('{}_min'.format(k))
            listVal.append(min(v))
        listIdx = ['H={0:.3f},T={1:.2f},Deg={2:.1f}'.format(H, T, D)]
        df = pd.DataFrame([listVal], index=listIdx, columns=listCol)
        df.index.name = 'parameter'
        df_minMax = pd.concat([df_minMax, df], axis=0)
        df_minMax.to_csv(OrcFxInfo['output'] + 'max_min.csv')


def matrixTable(info):
    OrcFxInfo = info['OrcaFlex']
    # マトリックス表の作成，マトリックス値はmax-minで算出
    df_minMax = pd.read_csv(OrcFxInfo['output'] + 'max_min.csv')

    listKey = []
    for obj in OrcFxInfo['object']:
        objInfo = OrcFxInfo['object'][obj]
        for data in objInfo['data']:
            listKey.append('{}_{}'.format(objInfo['name'], data))

    listIdx = df_minMax.iloc[:, 0]
    listH = []
    listTs = []
    listD = []
    for idx in listIdx:
        split_idx = idx.split(',')
        for s in split_idx:
            val = float(s.split('=')[1])
            if 'H' in s:
                if val not in listH:
                    listH.append(val)
            elif 'T' in s:
                if val not in listTs:
                    listTs.append(val)
            elif 'Deg' in s:
                if val not in listD:
                    listD.append(val)
    listTp = [Ts * 1.05 for Ts in listTs]

    df_main = pd.DataFrame({0:listTp, 1:listTs})
    df_header = pd.DataFrame(np.full((2, 2), ''))
    listHs = ['Tp', 'Ts']
    for key in listKey:
        df = pd.DataFrame(np.full((2, len(listH)), ''))
        df.iloc[0,0] = key
        df.iloc[1,0] = 'Hs'
        df_header = pd.concat([df_header, df], axis=1)

        sub = df_minMax[key + '_max'] - df_minMax[key + '_min']
        arr_sub = sub.to_numpy()
        arr_sub_2d = arr_sub.reshape(len(listH), len(listTs))
        df_table = pd.DataFrame(arr_sub_2d)
        df_table = df_table.T
        df_table = df_table.round(2)
        df_main = pd.concat([df_main, df_table], axis=1)

        listHs.extend(listH)

    df_header.columns = [int(i) for i in range(len(df_header.columns))]
    df_Hs = pd.DataFrame([listHs])
    df_main.columns = [int(i) for i in range(len(df_main.columns))]

    df_matrix = pd.concat([df_header, df_Hs, df_main], axis=0)
    df_matrix.to_csv(OrcFxInfo['output'] + 'Matrix.csv', header=None, index=None)


#const.pyで設定した定数を使用できるようにする
info = const.CONST

if info['case']['create']:
    createCase(info)
print('start analyze')
analysis(info)
print('end analyze')
matrixTable(info)