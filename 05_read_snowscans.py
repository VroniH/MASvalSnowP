import pandas as pd
import os
import fnmatch
import numpy as np 
import datetime as dt

if os.path.isfile('/home/user/Documents/Programming/Python/Masterarbeit/data/HS_data_all.txt'): 
	os.remove('/home/user/Documents/Programming/Python/Masterarbeit/data/HS_data_all.txt')

if os.path.isfile('/home/user/Documents/Programming/Python/Masterarbeit/data/HS_data_all_filled.txt'): 
	os.remove('/home/user/Documents/Programming/Python/Masterarbeit/data/HS_data_all_filled.txt')
#Import data------------------------------

lof = os.listdir('/home/user/Documents/Programming/Python/Masterarbeit/data')
filenames = []

for names in lof:
	if fnmatch.fnmatch(names,'*HS*'):
		filenames.append(names)
		filenames.sort()
# print(filenames)

datelist = pd.date_range(start='2016-12-02 00:00:00', end='2017-04-03 00:00:00',
 periods=None, freq='H', tz=None, normalize=False, name='DateTime', closed=None)
HS_data = pd.DataFrame({'DateTime': datelist,'HS_P1':np.nan, 'HS_P3NBP':np.nan, 'HS_P3CHP':np.nan, 
	'HS_P4':np.nan,'HS_P5':np.nan, 'HS_P6': np.nan, 'HS_P7': np.nan,'HS_P8':np.nan,
	'HS_P9': np.nan,'HS_P10': np.nan,'HS_P11': np.nan})
HS_data.set_index('DateTime',inplace = True, drop=True)

for dataset in filenames:
	read_data = pd.read_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/' + dataset, sep=',',
	header='infer', index_col= 1, usecols=None, na_values=['NaN','NA'], parse_dates=True)
	for i in range(0,len(read_data.index)):
		for j in range(0,len(datelist)):
			if fnmatch.fnmatch(dataset, '*STP*') and read_data.index[i] == HS_data.index[j]:
				HS_data.HS_P6[j] = read_data.HS_Pit6[i]
				HS_data.HS_P7[j] = read_data.HS_Pit7[i]
				HS_data.HS_P9[j] = read_data.HS_Pit9[i]
			if fnmatch.fnmatch(dataset, '*NBP*') and read_data.index[i] == HS_data.index[j]:
				HS_data.HS_P1[j] = read_data.HS_Pit1[i]
				HS_data.HS_P3NBP[j] = read_data.HS_Pit3[i]
				HS_data.HS_P10[j] = read_data.HS_Pit10[i]
				HS_data.HS_P11[j] = read_data.HS_Pit11[i]
			if fnmatch.fnmatch(dataset, '*CHP*') and read_data.index[i] == HS_data.index[j]:
				HS_data.HS_P3CHP[j] = read_data.HS_Pit3[i]
				HS_data.HS_P4[j] = read_data.HS_Pit4[i]
				HS_data.HS_P5[j] = read_data.HS_Pit5[i]
				HS_data.HS_P8[j] = read_data.HS_Pit8[i]
# pd.set_option('display.max_rows', 3000)	
HS_data = HS_data.round(2)	

#Create dataset where all the empty timesteps are filled with the previous measurement 
HS_data_filled = pd.DataFrame({'DateTime': datelist,'HS_P1':np.nan, 'HS_P3NBP':np.nan, 'HS_P3CHP':np.nan, 
	'HS_P4':np.nan,'HS_P5':np.nan, 'HS_P6': np.nan, 'HS_P7': np.nan,'HS_P8':np.nan,
	'HS_P9': np.nan,'HS_P10': np.nan,'HS_P11': np.nan})
HS_data_filled.set_index('DateTime',inplace = True, drop=True)


names = HS_data.columns.values
for i in range(0,len(names)):
	index = HS_data[names[i]].index[HS_data[names[i]].apply(pd.notnull)]

	for k in range(1,len(index)):
		for l in range(0,len(HS_data_filled.index)):
			if HS_data_filled.index[l] < index[0]:
				HS_data_filled[names[i]][l] = 0.0
			if np.logical_and(HS_data_filled.index[l]>=index[k-1], HS_data_filled.index[l]<index[k]):
				HS_data_filled[names[i]][l] = HS_data[names[i]][index[k-1]]
			if HS_data_filled.index[l] > index[-1]:
				HS_data_filled[names[i]][l] = HS_data[names[i]][index[-1]]
# print(HS_data_filled)

HS_data.to_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/HS_data_all.txt',
	sep=",", na_rep='NaN', columns=None, header=True, index=True)
HS_data_filled.to_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/HS_data_all_filled.txt',
	sep=",", na_rep='NaN', columns=None, header=True, index=True)

# HS_data_distr = pd.DataFrame({'DateTime': datelist,'HS_P1':np.nan, 'HS_P3NBP':np.nan, 'HS_P3CHP':np.nan, 
# 	'HS_P4':np.nan,'HS_P5':np.nan, 'HS_P6': np.nan, 'HS_P7': np.nan,'HS_P8':np.nan,
# 	'HS_P9': np.nan,'HS_P10': np.nan,'HS_P11': np.nan})
# HS_data_distr.set_index('DateTime',inplace = True, drop=True)
# ERA5 = pd.read_csv('data/ERA5_GF.txt',
#     index_col = 0, parse_dates = True, na_values = 'NaN')
# ERA5_RR = ERA5.RRmm
# # print(ERA5_RR)
# #Create Dataframe with 

# names = HS_data.columns.values
# for i in range(0,len(names)):
# 	index = HS_data[names[i]].index[HS_data[names[i]].apply(pd.notnull)]
# 	for j in range(1,len(index)):
# 		tdelta_h_scan = (index[j]-index[j-1])/np.timedelta64(1, 'h') # get number of hours (timesteps) between two scan measurements
# 		# for k in range(index[j-1],index[-1])
# 		# get number of timesteps with RR not 0
# 		start = index[j-1] 
# 		end = index[j]
# 		num_RR_h = ERA5_RR[start:end].nonzero()
# 		print(len(num_RR_h))
# 		# print(ERA5_RR[start:end]) #.apply(~ERA5_RR[2].isin('0.0'))
# 		print(num_RR_h)
# 		# print(index[j],index[j-1])
# 		# print(tdelta_h)


