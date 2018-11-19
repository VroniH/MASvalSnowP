#Script to read data from ERA5 files

#Import modules---------------------------
import xarray as xr 
import os
import fnmatch
import pandas as pd
import numpy as np 


if os.path.isfile('/home/user/Documents/Programming/Python/Masterarbeit/data/ERA5_GF.txt'): 
	os.remove('/home/user/Documents/Programming/Python/Masterarbeit/data/ERA5_GF.txt')

# if os.path.isfile('/home/user/Documents/Programming/Python/Masterarbeit/data/ERA5_AVD.txt'): 
# 	os.remove('/home/user/Documents/Programming/Python/Masterarbeit/data/ERA5_AVD.txt')
#Import data------------------------------

lof = os.listdir('/home/user/Documents/Programming/Python/Masterarbeit/ERA5/data')
filenames = []

for names in lof:
	if fnmatch.fnmatch(names,'*fc*'):
		filenames.append(names)
		filenames.sort()

# Create Dataframe to write ------------
datelist = pd.date_range(start='2015-08-01 00:00:00', end='2017-08-01 00:00:00',
 periods=None, freq='H', tz=None, normalize=False, name='DateTime', closed=None)
ERA5_data = pd.DataFrame({'DateTime': datelist,'RR': np.nan, 'RRmm':np.nan, 'T2m': np.nan, 'HS': np.nan, 'ptype': np.nan})
ERA5_data.set_index('DateTime',inplace = True, drop=True)

for dataset in filenames:
	read_data = xr.open_dataset('/home/user/Documents/Programming/Python/Masterarbeit/ERA5/data/' + dataset,
		decode_times=True)

#location of Gruvefjellet AWS is 78 12,024'N (78.2004 N) 15 37,463'E(15.624383 E), look for the
#closest grid point in ERA5 data --> method = nearest
#For comparison with ERA5: Same data if you choose location of airport, closest gridpoint is equal

	read_data = read_data.sel(longitude = 15.624383, latitude = 78.2004,
		method = 'nearest')
	precip = read_data['tp'].to_series()
	T = read_data['t2m'].to_series()
	HS = read_data['sd'].to_series()
	ptype = read_data['ptype'].to_series()

	# for i in range(0,len(precip.index)):
	# 	if precip.index[i] == ptype.index[i]:
	# 		print(True)	
	# 	else:
	# 		print(False)

# For the comparison between ERA5 and Adventdalen choose different location

	# read_data = read_data.sel(longitude = 15.8310, latitude = 78.2022,
	# 	method = 'nearest')
	# precip = read_data['tp'].to_series()
	# T = read_data['t2m'].to_series()
	# HS = read_data['sd'].to_series()
	# ptype = read_data['ptype'].to_series()

# In order to prevent overlapping data from the two model runs, use the 06UTC run for the time
# from 07UTC to 18 UTC and the 18 UTC run from 19UTC to 06 UTC
# Choose data accordingly and write into file:

	if fnmatch.fnmatch(dataset, '*06Z*'):
		select = np.logical_and(precip.index.hour >= 7, precip.index.hour <= 18)
		precip = precip[select == True]
		T = T[select == True]
		HS = HS[select == True]
		ptype = ptype[select ==True]

	
	 	for i in range(0,len(precip)):
			for j in range(0,len(ERA5_data)):
				if precip.index[i] == ERA5_data.index[j]:
					ERA5_data['RR'][j] = precip[i]
					ERA5_data['T2m'][j] = T[i]
					ERA5_data['HS'][j] = HS[i]
					ERA5_data['ptype'][j] = ptype[i]
					print(i,j)
					break

	if fnmatch.fnmatch(dataset, '*18Z*'):
		select = np.logical_or(precip.index.hour <= 6, precip.index.hour >= 19)
		precip = precip[select == True]
		T = T[select == True]
		HS = HS[select == True]
		ptype = ptype[select ==True]

	 	for i in range(0,len(precip)):
			for j in range(0,len(ERA5_data)):
				if precip.index[i] == ERA5_data.index[j]:
					ERA5_data['RR'][j] = precip[i]
					ERA5_data['T2m'][j] = T[i]
					ERA5_data['HS'][j] = HS[i]
					ERA5_data['ptype'][j] = ptype[i]
					print(i,j)
					break

ERA5_data.RRmm = ERA5_data.RR.multiply(10**3) # convert to [mm], needed by Snowpack
ERA5_data.RRmm = ERA5_data.RRmm.round(2) #round to two decimal places
ERA5_data.RR = ERA5_data.RR.round(2)
ERA5_data.HS = ERA5_data.HS.round(2)
ERA5_data.T2m = ERA5_data.T2m.round(2)
ERA5_data.ptype = ERA5_data.ptype.round(2)

ERA5_data.to_csv(path_or_buf='/home/user/Documents/Programming/Python/Masterarbeit/data/ERA5_GF.txt',
 sep=",", na_rep='NaN', index = True, header=True, mode='a') 

# For data from Adventdalen:
# ERA5_data.to_csv(path_or_buf='/home/user/Documents/Programming/Python/Masterarbeit/data/ERA5_AVD.txt',
#  sep=",", na_rep='NaN', index = True, header=True, mode='a')
