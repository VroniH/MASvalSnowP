# Date: 17.03.2018
# Author: Veronika Hatvan
# Last update: 17.03.2018

# Purpose:
# Compare ERA5 precipitation data and data downloaded from the eklima webpage for the stations Lufthaven
# and Adventdalen
# When difference is not too large, use ERA5 precipitation for input in SNOWPACK
#---------------------------------------------------------------------------------------------------------

import pandas as pd 
import matplotlib.pyplot as plt
from math import sqrt
# Load datasets:
# Note: ek = eklima data, RR1h = Precipitation data with 1h resolution, 
#		RR12h = Precipitation data with 12h resolution, gives the sum of the 12h before

ek_LFH = pd.read_csv('data/LFH_RR_ts.txt', na_values = 'NaN')
ek_LFH.DateTime = pd.to_datetime(ek_LFH.DateTime)
ek_LFH.set_index('DateTime',inplace=True)

ek_AVD = pd.read_csv('data/AVD_RR_ts.txt', na_values = 'NaN')
ek_AVD.DateTime = pd.to_datetime(ek_AVD.DateTime)
ek_AVD.set_index('DateTime',inplace=True)
# For comparison between ERA5 and LFH use same date as for Gruvefjellet (GF) because
# nearest grid point in ERA5 is the same
ERA5_RR1h_LFH = pd.read_csv('data/ERA5_GF.txt', na_values = 'NaN')
ERA5_RR1h_LFH['DateTime'] = pd.to_datetime(ERA5_RR1h_LFH['DateTime'])
ERA5_RR1h_LFH.set_index('DateTime',inplace=True)

# For comparison between ERA5 and AVD
ERA5_RR1h_AVD = pd.read_csv('data/ERA5_AVD.txt', na_values = 'NaN')
ERA5_RR1h_AVD['DateTime'] = pd.to_datetime(ERA5_RR1h_AVD['DateTime'])
ERA5_RR1h_AVD.set_index('DateTime',inplace=True)

# Get 12h sum at 06Z and 18Z for ERA5 data, also take care of units conversion. 
# ERA5 data originally is hourly accumulation [m], ek data is 12h accumulation in [mm]
# Change unit of ERA5 data to [mm] ([m/12h])
ERA5_RR12h_LFH = ERA5_RR1h_LFH.RRmm.resample('12H', base = 6).sum()#.multiply(10**3)
ERA5_RR12h_LFH = ERA5_RR12h_LFH['2016-08-01 18:00:00':'2017-04-30 18:00:00']
ERA5_RR12h_AVD = ERA5_RR1h_AVD.RRmm.resample('12H', base = 6).sum()#.multiply(10**3)
ERA5_RR12h_AVD = ERA5_RR12h_AVD['2016-11-01 18:00:00':'2017-04-30 18:00:00']
ek_LFH = ek_LFH['2016-08-01 18:00:00':'2017-04-30 18:00:00']
ek_AVD = ek_AVD['2016-11-01 18:00:00':'2017-04-30 18:00:00']
# print('ERA5_12h:', ERA5_RR12h.describe())
# print('ek_LFH:', ek_LFH.RR.describe())
# print('ek_AVD:',ek_AVD.RR.describe())

diff_LFH_ERA5 = ek_LFH.RR - ERA5_RR12h_LFH
diff_AVD_ERA5 = ek_AVD.RR - ERA5_RR12h_AVD
diff_AVD_ERA5_SE = diff_AVD_ERA5**2
diff_LFH_ERA5_SE = diff_LFH_ERA5**2
diff_AVD_ERA5_MSE = diff_AVD_ERA5_SE.mean()
diff_LFH_ERA5_MSE = diff_LFH_ERA5_SE.mean()

print('LFH - ERA5:',diff_LFH_ERA5.describe(),'MAE',	abs(diff_LFH_ERA5.mean()),
	'MSE',diff_LFH_ERA5_MSE, 'RMSE', sqrt(diff_LFH_ERA5_MSE))
print('AVD - ERA5:',diff_AVD_ERA5.describe(),'MAE', abs(diff_AVD_ERA5.mean()),
	'MSE',diff_AVD_ERA5_MSE, 'RMSE', sqrt(diff_AVD_ERA5_MSE))

# ERA5_RR12h_LFH.plot()
# plt.show()
plt.figure(num=1)
plt.plot(ERA5_RR12h_LFH,'r-', label = 'ERA5')
plt.plot(ek_LFH.RR,'k-', label = 'LFH')
plt.legend()
plt.xlabel('Date')
plt.ylabel('RR12h [mm]')


plt.figure(num=2)
plt.plot(ERA5_RR12h_AVD,'r-', label = 'ERA5')
plt.plot(ek_AVD.RR,'k-', label = 'AVD')
plt.legend()
plt.xlabel('Date')
plt.ylabel('RR12h [mm]')

plt.figure(num=3)
plt.plot(diff_LFH_ERA5,'r-',label = 'LFH - ERA5')
plt.plot(diff_AVD_ERA5,'k-',label = 'AVD - ERA5')
plt.legend()
plt.xlabel('Date')
plt.ylabel(r'$\Delta_{RR12h}$ [mm]')
plt.show()