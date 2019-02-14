import pandas as pd 
import datetime as dt
import numpy as np


ek_LF = pd.read_csv('data/LFH_RR_ts.txt',
na_values='NaN',header=0, names= ['datetime','RR','ff'])
# ek_AD = pd.read_csv('data/AVD_RR_ts.txt', index_col=0,parse_dates = True,
# na_values='NaN',header=0, names= ['RR','ff'])


ek_LF['datetime'] = pd.to_datetime(ek_LF['datetime'])
ek_LF = ek_LF.set_index('datetime').resample('1h').first().reset_index().reindex(columns = ek_LF.columns)

# Fill all missing timesteps with 0 as if there was no precipitation during that timesteps
ek_LF_fill0 = pd.DataFrame()
ek_LF_fill0['datatime'] = ek_LF['datetime']
ek_LF_fill0['RR'] = ek_LF['RR'].fillna(0.0)
ek_LF_fill0['ff'] = ek_LF['ff']

# Equally distribute 12h sums over the previous 12h
ek_LF_equal = pd.DataFrame()
ek_LF_equal['datatime'] = ek_LF['datetime']
ek_LF_equal['RR'] = np.nan
ek_LF_equal['ff'] = ek_LF['ff']
# print(ek_LF_equal)
# print(np.isnan(ek_LF_equal['RR'][12]))
# print(ek_LF['RR'][12])
# print(max(ek_LF['RR']))
# print(ek_LF[ek_LF['RR']>0.0])

for i in range(0,len(ek_LF['RR'])+1,12):
    if i == 0:
        ek_LF_equal['RR'][i] = 0.0
    print(i)
    if i+12<=6540:
        # print(ek_LF['RR'][i+12])
        if np.isnan(ek_LF['RR'][i+12]) == False and ek_LF['RR'][i+12] != 0.0:
            if ek_LF['RR'][i+12] >= 1.2:
                # print('case1')
                # print(ek_LF['RR'][i+12])
                for step in range(1,13):
                    ek_LF_equal['RR'][i+step] = round(ek_LF['RR'][i+12]/12,1)
            if ek_LF['RR'][i+12] <= 1.2:
                # print('case2')
                # print(ek_LF['RR'][i+12])
                x = ek_LF['RR'][i+12]/0.1
                for step in range(1,13-int(x)):
                    ek_LF_equal['RR'][i+step] = 0.0 
                for step in range(12-int(x),13):
                    ek_LF_equal['RR'][i+step] = 0.1
        elif np.isnan(ek_LF['RR'][i+12]) == False and ek_LF['RR'][i+12] == 0.0:
            # print('case3')
            for step in range(1,13):
                ek_LF_equal['RR'][i+step] = 0.0
        elif np.isnan(ek_LF['RR'][i+12]) == True:
            for step in range(1,13):
                ek_LF_equal['RR'][i+step] = 0.0
            print('Nan entry at:',i)
print(np.nanmax(ek_LF_equal['RR']))


ek_LF_fill0.to_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/LFH_RR_ts_fill0.txt',
    sep=",", na_rep='NaN', columns=None, header=True, index=False, index_label=None,
    mode='w', encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator='\n', chunksize=None, tupleize_cols=None,
    date_format=None, doublequote=True, escapechar=None, decimal='.')
ek_LF_equal.to_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/LFH_RR_ts_equal.txt',
    sep=",", na_rep='NaN', columns=None, header=True, index=False, index_label=None,
    mode='w', encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator='\n', chunksize=None, tupleize_cols=None,
    date_format=None, doublequote=True, escapechar=None, decimal='.')
