CONST = {
    # ↓↓↓マトリックス表算出に用いる設定↓↓↓
    'case':{
        'file': '../input/LoadCaseData.csv',
        'create': True, #入力ケースのエクセルを作成する場合はTrue，しない場合はFalse
        'Heights': [0.5, 1.0, 1.5, 2.0],
        'Periods': [2.0, 2.5, 3.0, 3.5, 4.0],
        'Degrees': 0.0
        },
    'OrcaFlex':{
        'analyze': True, # 既存のマトリックス表を使用する場合はFalse
        'id': 1, #ケース番号
        'model': '../input/Cal_MPa_RW_H=2.0_T=5.0_Deg=0.dat',
        'output': '../output/step/', #出力ファイル保存先ディレクトリ
        'save':{
            'dat':True, # 解析前データを保存する場合はTrue，しない場合はFalse
            'sim':False, # 解析済みデータを保存する場合はTrue，しない場合はFalse
            },
        'period':[400, 500],
        'object':{
            'MP':{
                'name':'MP',
                'xyz':[0.0, 0.0, 88.1],
                'data':['Dynamic x', 'Dynamic y', 'Dynamic z', 'Dynamic Rx', 'Dynamic Ry', 'Dynamic Rz'],
                'save':[], # 上'data'の内，出力したい時系列データを記述する
            },
            'body':{
                'name':'vessel',
                'xyz':[-7.957, 0.0, 11.248],
                'data':['Dynamic x', 'Dynamic y', 'Dynamic z', 'Dynamic Rx', 'Dynamic Ry', 'Dynamic Rz'],
                'save':[], # 上'data'の内，出力したい時系列データを記述する
            },
        },
    },

    # ↓↓↓動揺量変換，稼働率計算に用いる設定↓↓↓
    'file':{
        'input':{
            'data': '../input/Akita_P11_2009.csv',
            'matrix': '../output/step/Matrix.csv'
        },
        'output':{
            'henkan': '../output/step/converged.csv',
            'kadou': '../output/operatingRate.csv'
        }
    },
    '中止基準':{#考慮しなくて良い中止基準値があれば，None にする
        'Hs': 2.0,
        'Ts': None,
        'MP_Dynamic x': 2.0, 
        'MP_Dynamic y': 2.0, 
        'MP_Dynamic z': 2.0, 
        'MP_Dynamic Rx': 2.0, 
        'MP_Dynamic Ry': 2.0, 
        'MP_Dynamic Rz': 2.0,
        'vessel_Dynamic x': 2.0, 
        'vessel_Dynamic y': 2.0, 
        'vessel_Dynamic z': 2.0, 
        'vessel_Dynamic Rx': 2.0, 
        'vessel_Dynamic Ry': 2.0, 
        'vessel_Dynamic Rz': 2.0,
    },
    '異常値': 3, #連続する異常値は何個まで補間するか
    '連続静穏時間':{
        'min': 1,
        'max': 15,
    },
    'percentile': [0.5], #分位数・パーセンタイル（複数指定も可能）
    'interpolation': 'linear', #補間方法（'linear'：前後の値から線形補間した値，'midpoint'：前後の値の中間の値（平均値））
}