# Analzse WS 2017/18 
# Get a feeling for meteorological conditions during this WS
# Describe WS 17/18 in the thesis, consider local differences within the valley
# author: Veronika Hatvan

# IMPORT MODULES ----------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import interactive
import seaborn

# IMPORT DATA -------------------------------------------

# Import data from AWS Adventdalen (AVD)
AVD_data = pd.read_csv('raw_data/Adventdalen_Hour.dat', 
	skiprows = [0,2,3],index_col = 0,parse_dates = True, na_values = 'NAN', header = 0 ,
	names = ['TIMESTAMP','RECORD','ID','T2m_PT1000_Max','T2m_PT1000_Min','T2m_PT1000_Avg',
	'T10m_PT1000_Max','T10m_PT1000_Min','T10m_PT1000_Avg',
	'T2m_Rotron_Max','T2m_Rotron_Min','T2m_Rotron_Avg',
	'LF2m_Rotron_Max','LF2m_Rotron_Avg','T10m_Rotron_Max',
	'T10m_Rotron_Min', 'T10m_Rotron_Avg', 'LF10m_Rotron_Max',
	'LF10m_Rotron_Avg','P_mbar','ff2m_mps_Max','ff2m_10min',
	'ff2m_mps_avg', 'dd2m', 'ff10m_sek_Max', 'ff10m_10min',
	'ff10m_mps_Avg','dd10m','Batt_V_Min'])

# Import data from radiation measurements Adventdalen 
AVD_rad_all = pd.read_csv('raw_data/Adventdalen_New_Fem_minutt.dat', 
	skiprows = [0,2,3],index_col = 0, parse_dates = True, na_values = 'NAN',header = 0,
	names = ['TIMESTAMP','RECORD','SWin_Wpm2','LWin_Wpm2','SWout_Wpm2','LWout_Wpm2','CNR1_temp_gr_C_Avg'])

# Radiaton data is available in 5min steps, create hourly mean values of the radiation components. 
# shift(1) - shift the whole dataset by one timestep so that a value at each timestep is the mean of the previous hour
AVD_rad_data = pd.DataFrame.from_dict({
	'SWin_Wpm2':AVD_rad_all['SWin_Wpm2'].resample('H').mean().shift(1), #opp..upward looking instrument measuring SW down
	'SWout_Wpm2': AVD_rad_all['SWout_Wpm2'].resample('H').mean().shift(1), #ned..downward looking instrument measuring SW up
	'LWin_Wpm2': AVD_rad_all['LWin_Wpm2'].resample('H').mean().shift(1),
	'LWout_Wpm2': AVD_rad_all['LWout_Wpm2'].resample('H').mean().shift(1)})
# Import data from AWS Gruvefjellet (GF)
GF_data = pd.read_csv('raw_data/Gruvefjellet_Res_data.dat', 
	skiprows = [0,2,3], index_col = 0,parse_dates = True, na_values = 'NAN', header = 0 ,
	names = ['TIMESTAMP','RECORD','ID','T10cm_minutt_Max','T10cm_minutt_Min','T10cm_minutt_Avg',
	'T1m_minutt_Max','T1m_minutt_Min','T1m_minutt_Avg',
	'T3m_minutt_Max','T3m_minutt_Min','T3m_minutt_Avg',
	'LF_minutt_Max','LF_minutt_Avg','p_mbar','ff_mps_Max','ff_10min',
	'ff_mps_avg', 'dd','NB_time','SD_m','SD_kval','TSS','T_soil_1m',
	'T_soil_2m','T_soil_3m','T_soil_4m','T_soil_5m','T_soil_6m',
	'R_surf_ohm','R_1m_ohm', 'R_2m_ohm', 'R_3m_ohm', 'R_4m_ohm',
	'R_5m_ohm', 'R_6m_ohm', 'Batt_V_Min'])

GF_data = GF_data['2016-08-01 00:00:00':'2017-07-31 23:00:00']			 	
# AVD_rad_data = AVD_rad_data['2016-08-01 00:00:00':'2017-04-03 00:00:00'] 
# ERA5 = ERA5_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']
AVD_data = AVD_data['2016-08-01 00:00:00':'2017-07-31 23:00:00']


diff = GF_data.T3m_minutt_Avg - AVD_data.T2m_PT1000_Avg
fig1,ax1 = plt.subplots(figsize = (12,5))
seaborn.boxplot(diff.index.strftime("%b\'%y") ,diff,ax=ax1)
interactive(True)
plt.show(fig1)

groups = diff.groupby(pd.Grouper(freq='M'))
months = pd.concat([pd.DataFrame(x[1].values) for x in groups], axis=1)
months = pd.DataFrame(months)
months.columns = [8,9,10,11,12,1,2,3,4,5,6,7]
f2 = months.boxplot()
plt.show(f2)
interactive(False)

raw_stats={}
raw_stats['davg_diff'] = diff.resample('D').mean()
raw_stats['mavg_diff'] = diff.resample('M').mean()
raw_stats['yavg_diff'] = diff.resample('Y').mean()
print(raw_stats['mavg_diff'].index.month)
daterange = pd.date_range(start='2016-08-01 00:00:00',
	end='2017-06-01 00:00:00', periods=None, freq='D',
	normalize=False, name='DateTime', closed=None)
mavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
yavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
for i in range(0, len(raw_stats['mavg_diff'])):
	for j in range(0,len(daterange)):
		if np.logical_and(mavg_diff.index.month[j] == raw_stats['mavg_diff'].index.month[i],
		 mavg_diff.index.year[j] == raw_stats['mavg_diff'].index.year[i]):
			mavg_diff[j] = raw_stats['mavg_diff'][i]
print(mavg_diff, raw_stats['mavg_diff'])
for i in range(0, len(raw_stats['yavg_diff'])):
	for j in range(0,len(daterange)):
		if yavg_diff.index.year[j] == raw_stats['yavg_diff'].index.year[i]:
			yavg_diff[j] = raw_stats['yavg_diff'][i]

f9, (ax1,ax2) = plt.subplots(nrows=2, ncols=1, figsize = (15,10), sharex=True, sharey=False, squeeze=True, subplot_kw=None, gridspec_kw=None)
ax1.plot(GF_data.index, GF_data.T3m_minutt_Avg.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'Gruvefjellet 3m(GF)')
ax1.plot(AVD_data.index, AVD_data.T2m_PT1000_Avg.rolling(window=24).mean(), color = 'r', linewidth = 1, label = 'Adventdalen 2m(AVD)')
ax1.set_ylim(-35,20)
ax1.grid()
ax1.set_ylabel('Temperature [degC]')
ax1.legend(loc = 'lower center')
ax1.set_title('24h Rolling mean')
ax2.plot(raw_stats['davg_diff'], color = 'k',label = 'Daily', linewidth = 2)
ax2.plot(mavg_diff, color = 'r',label = 'Monthly', linewidth = 2)
ax2.plot(yavg_diff, color = 'b', label = 'Yearly', linewidth = 2)
ax2.grid()
ax2.set_ylim(-10,10)
ax2.set_xlabel('Time')
ax2.set_ylabel('Temperature difference [degC]')
ax2.legend(loc = 'lower center')
ax2.set_title('Mean differences GF3m-AVD2m')
plt.show()
# f9.savefig('figures/T_meanDiff2m3m.png', bbox_inches='tight')
# plt.close(f9)

plt.boxplot(raw_stats['mavg_diff'])
plt.show()