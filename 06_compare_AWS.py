# Compare meteorological data from AWS Avd and GF 

#Import modules
import pandas as pd 
import datetime as dt 
import matplotlib.pyplot as plt 
from sklearn import metrics
import numpy as np 
import seaborn as sns
from math import exp
import statsmodels.api as sm
from scipy import stats


#import data

AVD_all = pd.read_csv('raw_data/Adventdalen_Hour.dat', 
	skiprows = [0,2,3],index_col = 0,parse_dates = True, na_values = 'NAN', header = 0 ,
	names = ['TIMESTAMP','RECORD','ID','T2m_PT1000_Max','T2m_PT1000_Min','T2m_PT1000_Avg',
	'T10m_PT1000_Max','T10m_PT1000_Min','T10m_PT1000_Avg',
	'T2m_Rotron_Max','T2m_Rotron_Min','T2m_Rotron_Avg',
	'LF2m_Rotron_Max','LF2m_Rotron_Avg','T10m_Rotron_Max',
	'T10m_Rotron_Min', 'T10m_Rotron_Avg', 'LF10m_Rotron_Max',
	'LF10m_Rotron_Avg','P_mbar','ff2m_mps_Max','ff2m_10min',
	'ff2m_mps_avg', 'dd2m', 'ff10m_sek_Max', 'ff10m_10min',
	'ff10m_mps_Avg','dd10m','Batt_V_Min'])
AVD_rad_all = pd.read_csv('raw_data/Adventdalen_New_Fem_minutt.dat', 
    skiprows = [0,2,3],index_col = 0, parse_dates = True, na_values = 'NAN',header = 0,
    names = ['TIMESTAMP','RECORD','SWin_Wpm2','LWin_Wpm2','SWout_Wpm2','LWout_Wpm2','CNR1_temp_gr_C_Avg'])

AVD_rad_data = pd.DataFrame.from_items([
    ('SWin_Wpm2',AVD_rad_all['SWin_Wpm2'].resample('H').mean().shift(1)), #opp..upward looking instrument measuring SW down
    ('SWout_Wpm2', AVD_rad_all['SWout_Wpm2'].resample('H').mean().shift(1)), #ned..downward looking instrument measuring SW up
    ('LWin_Wpm2', AVD_rad_all['LWin_Wpm2'].resample('H').mean().shift(1)),
    ('LWout_Wpm2', AVD_rad_all['LWout_Wpm2'].resample('H').mean().shift(1))])

GF_all = pd.read_csv('raw_data/Gruvefjellet_Res_data.dat', 
	skiprows = [0,2,3], index_col = 0,parse_dates = True, na_values = 'NAN', header = 0 ,
	names = ['TIMESTAMP','RECORD','ID','T10cm_minutt_Max','T10cm_minutt_Min','T10cm_minutt_Avg',
	'T1m_minutt_Max','T1m_minutt_Min','T1m_minutt_Avg',
	'T3m_minutt_Max','T3m_minutt_Min','T3m_minutt_Avg',
	'LF_minutt_Max','LF_minutt_Avg','P_mbar','ff_mps_Max','ff_10min',
	'ff_mps_avg', 'dd','NB_time','SD_m','SD_kval','TSS','T_soil_1m',
	'T_soil_2m','T_soil_3m','T_soil_4m','T_soil_5m','T_soil_6m',
	'R_surf_ohm','R_1m_ohm', 'R_2m_ohm', 'R_3m_ohm', 'R_4m_ohm',
	'R_5m_ohm', 'R_6m_ohm', 'Batt_V_Min'])

GF_data = GF_all['2016-01-01 00:00:00':'2017-06-27 00:00:00']			 	
AVD_data = AVD_all['2016-01-01 00:00:00':'2017-06-27 00:00:00']
AVD_rad_data = AVD_rad_data['2016-01-01 00:00:00':'2017-06-27 00:00:00'] 

GF_data['month'] = GF_data.index.month
AVD_data['month'] = AVD_data.index.month


#----------------------Calculate potential temperature------------------------------------------


# print(RH_calc_AVD)

pd.options.display.max_rows = 140000
# print(AVD_data)

#----------------------------Rel. Humidity-------------------------------------------------------
#RH measurement height at Gruvefjellet unknown, compare to data from 2m Adventdalen measurement

#----------------------Correct relative humidity for T<0-----------------------------------------
# need RH above ice not above water, probably RH values are raw data without correction. 
# First step, calculate actual water vapor pressure e 
RH_calc_GF=pd.DataFrame({'DateTime':GF_data.index,'e_s':np.nan,'e':np.nan, 'absH': np.nan, 'RH_corr':np.nan, 'RH':GF_data.LF_minutt_Avg})
RH_calc_GF.set_index('DateTime',inplace = True, drop=True)
RH_calc_AVD=pd.DataFrame({'DateTime':AVD_data.index,'e_s':np.nan,'e':np.nan, 'absH':np.nan, 'RH_corr':np.nan, 'RH':AVD_data.LF2m_Rotron_Avg})
RH_calc_AVD.set_index('DateTime',inplace = True, drop=True)
Lv = 2.5*10**6 #Jkg**(-1) Latent heat of vaporisation
Ls = 2.8*10**6 #Jkg**(-1) Latent heat of sublimation
Rv = 462 #J(kgK)**-1 individual gas constant for water vapor
T0 = 273.15 #K reference Temperature

for i in range(0,len(GF_data.index)):
	# Calculation of saturation water vapor pressure over water for given temperature from AWS
	RH_calc_GF.e_s[i] = 611* exp((Lv/Rv*((1/T0)-(1/(GF_data.T1m_minutt_Avg[i]+273.15)))))
	# Calculation of actual water vapor pressure	
	RH_calc_GF.e[i] = (GF_data.LF_minutt_Avg[i]*RH_calc_GF.e_s[i])/100
	# Calculation of the absolute humidity 
	RH_calc_GF.absH[i] = RH_calc_GF.e[i]/(Rv*(GF_data.T1m_minutt_Avg[i]+273.15))
	# print(RH_calc_GF.absH[i])
	# If the temperature is below 0 degrees the saturation water vapor pressure over ice is needed
	if GF_data.T1m_minutt_Avg[i] <0:
	# For these cases overwrite the previous calculation by saturation over ice
		RH_calc_GF.e_s[i] = 611* exp((Ls/Rv*((1/T0)-(1/(GF_data.T1m_minutt_Avg[i]+273.15)))))
	# Calculate relative Humidity from actual water vapor pressure and saturation water vapor pressure with corrected values for T<0
	RH_calc_GF.RH_corr[i] = (RH_calc_GF.e[i]/RH_calc_GF.e_s[i])*100	
	# Set RH>100 to 100
	if RH_calc_GF.RH_corr[i] > 100:
		RH_calc_GF.RH_corr[i] = 100



# print(RH_calc_GF)

for i in range(0,len(AVD_data.index)):
	# Calculation of saturation water vapor pressure over water for given temperature from AWS
	RH_calc_AVD.e_s[i] = 611* exp((Lv/Rv*((1/T0)-(1/(AVD_data.T2m_Rotron_Avg[i]+273.15))))) 
	# Calculation of actual water vapor pressure
	RH_calc_AVD.e[i] = (AVD_data.LF2m_Rotron_Avg[i]*RH_calc_AVD.e_s[i])/100
	# Calculation of the absolute humidity 
	RH_calc_AVD.absH[i] = RH_calc_AVD.e[i]/(Rv*(AVD_data.T2m_Rotron_Avg[i]+273.15))
	# print(RH_calc_AVD.absH[i])
	# If the temperature is below 0 degrees the saturation water vapor pressure over ice is needed
	if AVD_data.T2m_Rotron_Avg[i] <0:
	# For these cases overwrite the previous calculation by saturation over ice
		RH_calc_AVD.e_s[i] = 611* exp((Ls/Rv*((1/T0)-(1/(AVD_data.T2m_Rotron_Avg[i]+273.15)))))
	# Calculate relative Humidity from actual water vapor pressure and saturation water vapor pressure with corrected values for T<0	
	RH_calc_AVD.RH_corr[i] = (RH_calc_AVD.e[i]/RH_calc_AVD.e_s[i])*100	

	if RH_calc_AVD.RH_corr[i] > 100:
		RH_calc_AVD.RH_corr[i] = 100

# Calculate mean deviation
# For raw data: 
raw_stats={}
diff = GF_data.LF_minutt_Avg - AVD_data.LF2m_Rotron_Avg
raw_stats['davg_diff'] = diff.resample('D').mean()
raw_stats['mavg_diff'] = diff.resample('M').mean()
raw_stats['yavg_diff'] = diff.resample('Y').mean()

daterange = pd.date_range(start='2016-01-01 00:00:00',
	end='2017-06-27 00:00:00', periods=None, freq='D',
	normalize=False, name='DateTime', closed=None)
mavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
yavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
for i in range(0, len(raw_stats['mavg_diff'])):
	for j in range(0,len(daterange)):
		if np.logical_and(mavg_diff.index.month[j] == raw_stats['mavg_diff'].index.month[i],
		 mavg_diff.index.year[j] == raw_stats['mavg_diff'].index.year[i]):
			mavg_diff[j] = raw_stats['mavg_diff'][i]
for i in range(0, len(raw_stats['yavg_diff'])):
	for j in range(0,len(daterange)):
		if yavg_diff.index.year[j] == raw_stats['yavg_diff'].index.year[i]:
			yavg_diff[j] = raw_stats['yavg_diff'][i]



f1, (ax1, ax2) = plt.subplots(nrows = 2, ncols=1, sharex=True, figsize = (15,10))
ax1.plot(GF_data.index, GF_data.LF_minutt_Avg, color = 'g', linewidth = 1, label = 'Gruvefjellet (GF)')
ax1.plot(AVD_data.index, AVD_data.LF2m_Rotron_Avg, color = 'r', linewidth = 1, label = 'Adventdalen (AVD)')
ax1.set_ylim(30,105)
ax1.grid()
ax1.set_ylabel('rel. Humidity [%]')
ax1.legend(loc = 'lower center')
ax1.set_title('Raw data')
ax2.plot(RH_calc_GF.index, RH_calc_GF.RH_corr, color ='g', linewidth =1, label = 'GF RH_corr')
ax2.plot(RH_calc_AVD.index, RH_calc_AVD.RH_corr, color = 'r', linewidth = 1, label = 'AVD RH_corr')
ax2.set_ylim(30,105)
ax2.grid()
ax2.set_ylabel('rel. Humidity [%]')
ax2.legend(loc = 'lower center')
ax2.set_title('Corr')
f1.savefig('figures/RH_rawVScorr.png', bbox_inches='tight')
plt.close(f1)
# plt.show()


f2, (ax1,ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize = (15,10))
ax1.plot(GF_data.index, GF_data.LF_minutt_Avg.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'Gruvefjellet (GF)')
ax1.plot(AVD_data.index, AVD_data.LF2m_Rotron_Avg.rolling(window=24).mean(), color = 'r', linewidth = 1, label = 'Adventdalen (AVD)')
ax1.set_ylim(30,105)
ax1.grid()
ax1.set_ylabel('rel. Humidity [%]')
ax1.legend(loc = 'lower center')
ax1.set_title('24h Rolling mean raw')
ax2.plot(RH_calc_GF.index, RH_calc_GF.RH_corr.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'Gruvefjellet (GF)')
ax2.plot(RH_calc_AVD.index, RH_calc_AVD.RH_corr.rolling(window=24).mean(), color = 'r', linewidth = 1, label = 'Adventdalen (AVD)')
ax2.set_ylim(30,105)
ax2.grid()
ax2.set_ylabel('rel. Humidity [%]')
ax2.legend(loc = 'lower center')
ax2.set_title('24h Rolling mean corr')
f2.savefig('figures/RH_rollm24h_rawVScorr.png', bbox_inches='tight')
plt.close(f2)

f3, (ax1,ax2) = plt.subplots(nrows=2, ncols=1, figsize = (15,10), sharex=True, sharey=False, squeeze=True, subplot_kw=None, gridspec_kw=None)
ax1.plot(GF_data.index, GF_data.LF_minutt_Avg.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'Gruvefjellet (GF)')
ax1.plot(GF_data.index, AVD_data.LF2m_Rotron_Avg.rolling(window=24).mean(), color = 'r', linewidth = 1, label = 'Adventdalen (AVD)')
ax1.set_ylim(30,105)
ax1.grid()
ax1.set_ylabel('rel. Humidity [%]')
ax1.legend(loc = 'lower center')
ax1.set_title('24h Rolling mean')
ax2.plot(raw_stats['davg_diff'], color = 'k',label = 'Daily', linewidth = 2)
ax2.plot(mavg_diff, color = 'r',label = 'Monthly', linewidth = 2)
ax2.plot(yavg_diff, color = 'b', label = 'Yearly', linewidth = 2)
ax2.grid()
ax2.set_ylim(-40,25)
ax2.set_xlabel('Time')
ax2.set_ylabel('rel. humidity difference [%]')
ax2.legend(loc = 'lower center')
ax2.set_title('Mean differences GF-AVD')
f3.savefig('figures/RH_meanDiff.png', bbox_inches='tight')
plt.close(f3)

slope, intercept, r_value, p_value, std_err = stats.linregress(GF_data.LF_minutt_Avg, AVD_data.LF2m_Rotron_Avg)
f4, ax1 = plt.subplots(nrows = 1, ncols =1)
ax1.plot(GF_data.LF_minutt_Avg, AVD_data.LF2m_Rotron_Avg, 'o', label='GF vs. AVD', alpha =0.5)
ax1.plot(GF_data.LF_minutt_Avg, intercept + slope*GF_data.LF_minutt_Avg, 'r', label='lin. Regression')
ax1.legend(loc ='lower right')
ax1.set_xlabel('RH [%] GF')
ax1.set_ylabel('RH [%] AVD')
ax1.set_xlim(35,102)
ax1.set_ylim(35,102)
plt.text(37, 99, 'y = '+str(intercept.round(2))+'+'+str(slope.round(2))+'*x' ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
plt.text(37, 95, 'R ='+str(r_value.round(2)) ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
f4.savefig('figures/RH_GFvsAVD.png', bbox_inches='tight')
plt.close(f4)

slope, intercept, r_value, p_value, std_err = stats.linregress(RH_calc_GF.absH, RH_calc_AVD.absH)
f4, ax1 = plt.subplots(nrows = 1, ncols =1)
ax1.plot(RH_calc_GF.absH, RH_calc_AVD.absH, 'o', label='GF vs. AVD', alpha =0.5)
ax1.plot(RH_calc_GF.absH, intercept + slope*RH_calc_GF.absH, 'r', label='lin. Regression')
ax1.legend(loc ='lower right')
ax1.set_xlabel('abs. Hum [kg/m3] GF')
ax1.set_ylabel('abs. Hum [kg/m3] AVD')
ax1.set_xlim(0,0.01)
ax1.set_ylim(0,0.01)
plt.text(0, 0.0097, 'y = '+str(intercept.round(2))+'+'+str(slope.round(2))+'*x' ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
plt.text(0, 0.0092, 'R ='+str(r_value.round(2)) ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
f4.savefig('figures/absHum_GFvsAVD.png', bbox_inches='tight')
plt.show(f4)

raw_stats={}
diff = RH_calc_GF.absH - RH_calc_AVD.absH
raw_stats['davg_diff'] = diff.resample('D').mean()
raw_stats['mavg_diff'] = diff.resample('M').mean()
raw_stats['yavg_diff'] = diff.resample('Y').mean()

daterange = pd.date_range(start='2016-01-01 00:00:00',
	end='2017-06-27 00:00:00', periods=None, freq='D',
	normalize=False, name='DateTime', closed=None)
mavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
yavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
for i in range(0, len(raw_stats['mavg_diff'])):
	for j in range(0,len(daterange)):
		if np.logical_and(mavg_diff.index.month[j] == raw_stats['mavg_diff'].index.month[i],
		 mavg_diff.index.year[j] == raw_stats['mavg_diff'].index.year[i]):
			mavg_diff[j] = raw_stats['mavg_diff'][i]
for i in range(0, len(raw_stats['yavg_diff'])):
	for j in range(0,len(daterange)):
		if yavg_diff.index.year[j] == raw_stats['yavg_diff'].index.year[i]:
			yavg_diff[j] = raw_stats['yavg_diff'][i]



f3, (ax1,ax2) = plt.subplots(nrows=2, ncols=1, figsize = (15,10), sharex=True, sharey=False, squeeze=True, subplot_kw=None, gridspec_kw=None)
ax1.plot(GF_data.index, RH_calc_GF.absH, color = 'g', linewidth = 1, label = 'Gruvefjellet (GF)')
ax1.plot(GF_data.index, RH_calc_AVD.absH, color = 'r', linewidth = 1, label = 'Adventdalen (AVD)')
ax1.set_ylim(0,0.01)
ax1.grid()
ax1.set_ylabel('abs. Humidity [%]')
ax1.legend(loc = 'lower center')
# ax1.set_title()
ax2.plot(raw_stats['davg_diff'], color = 'k',label = 'Daily', linewidth = 2)
ax2.plot(mavg_diff, color = 'r',label = 'Monthly', linewidth = 2)
ax2.plot(yavg_diff, color = 'b', label = 'Yearly', linewidth = 2)
ax2.grid()
ax2.set_ylim(-0.002,0.002)
ax2.set_xlabel('Time')
ax2.set_ylabel('abs. humidity difference [%]')
ax2.legend(loc = 'lower center')
ax2.set_title('Mean differences GF-AVD')
f3.savefig('figures/absH_meanDiff.png', bbox_inches='tight')
plt.show(f3)


# #-------------------------------------------Radiation---------------------------------
f5, (ax1, ax2) = plt.subplots(nrows = 2, ncols=1, figsize= (15,10))
ax1.plot(AVD_rad_data.index, AVD_rad_data.SWin_Wpm2.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'SWin')
ax1.plot(AVD_rad_data.index, AVD_rad_data.SWout_Wpm2.rolling(window=24).mean(), color = 'r', linewidth = 1, label = 'SWout')
ax1.set_ylim(-5,700)
ax1.grid()
ax1.set_ylabel('SW Radiation [Wm-2]')
ax1.legend(loc = 'upper center')
albedo = AVD_rad_data.SWout_Wpm2/AVD_rad_data.SWin_Wpm2

for i in range(0, len(AVD_rad_data.index)):
	if np.logical_or(albedo[i]>1,albedo[i]<0):
		albedo[i] = np.NaN 

ax2.plot(AVD_rad_data.index,albedo.rolling(window=24).mean(),color = 'k', linewidth = 1, label = 'Albedo')
ax2.set_ylim(0,1)
ax2.grid()
ax2.set_ylabel('Albedo')
ax2.legend(loc = 'upper center')
f5.savefig('figures/SW_Albedo_roll24h.png', bbox_inches='tight')
plt.close(f5)

f6, (ax1, ax2) = plt.subplots(nrows = 2, ncols=1, figsize= (15,10))
ax1.plot(AVD_rad_data.index, AVD_rad_data.SWin_Wpm2, color = 'g', linewidth = 1, label = 'SWin')
ax1.plot(AVD_rad_data.index, AVD_rad_data.SWout_Wpm2, color = 'r', linewidth = 1, label = 'SWout')
ax1.set_ylim(-5,700)
ax1.grid()
ax1.set_ylabel('SW Radiation [Wm-2]')
ax1.legend(loc = 'upper center')
albedo = AVD_rad_data.SWout_Wpm2/AVD_rad_data.SWin_Wpm2

for i in range(0, len(AVD_rad_data.index)):
	if np.logical_or(albedo[i]>1,albedo[i]<0):
		albedo[i] = np.NaN 

ax2.plot(AVD_rad_data.index,albedo,color = 'k', linewidth = 1, label = 'Albedo')
ax2.set_ylim(0,1)
ax2.grid()
ax2.set_ylabel('Albedo')
ax2.legend(loc = 'upper center')
f6.savefig('figures/SW_Albedo.png', bbox_inches='tight')
plt.close(f6)

f7, (ax1, ax2) = plt.subplots(nrows = 2, ncols=1, figsize = (15,10))
ax1.plot(AVD_rad_data.index, AVD_rad_data.SWin_Wpm2.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'SWin')
ax1.plot(AVD_rad_data.index, AVD_rad_data.SWout_Wpm2.rolling(window=24).mean(), color = 'r', linewidth = 1, label = 'SWout')
ax1.set_ylim(-5,700)
ax1.grid()
ax1.set_ylabel('SW Radiation [Wm-2]')
ax1.legend(loc = 'upper center')
ax2.plot(AVD_rad_data.index, AVD_rad_data.LWin_Wpm2.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'LWin')
ax2.plot(AVD_rad_data.index, AVD_rad_data.LWout_Wpm2.rolling(window=24).mean(), color = 'r', linewidth = 1, label = 'LWout')
ax2.set_ylim(100,420)
ax2.grid()
ax2.set_ylabel('LW Radiation [Wm-2]')
ax2.legend(loc = 'upper center')
f7.savefig('figures/SW_LW_roll24h.png', bbox_inches='tight')
plt.close(f7)

f8, (ax1, ax2) = plt.subplots(nrows = 2, ncols=1, figsize = (15,10))
ax1.plot(AVD_rad_data.index, AVD_rad_data.SWin_Wpm2, color = 'g', linewidth = 1, label = 'SWin')
ax1.plot(AVD_rad_data.index, AVD_rad_data.SWout_Wpm2, color = 'r', linewidth = 1, label = 'SWout')
ax1.set_ylim(-5,700)
ax1.grid()
ax1.set_ylabel('SW Radiation [Wm-2]')
ax1.legend(loc = 'upper center')
ax2.plot(AVD_rad_data.index, AVD_rad_data.LWin_Wpm2, color = 'g', linewidth = 1, label = 'LWin')
ax2.plot(AVD_rad_data.index, AVD_rad_data.LWout_Wpm2, color = 'r', linewidth = 1, label = 'LWout')
ax2.set_ylim(100,420)
ax2.grid()
ax2.set_ylabel('LW Radiation [Wm-2]')
ax2.legend(loc = 'upper center')
f8.savefig('figures/SW_LW.png', bbox_inches='tight')
plt.close(f8)


# #----------------------------------------Temperature---------------------------------------------------
# #Plot T - different mearsurement heights at Gruvefjellet (10cm,1m,3m) and Adventdalen (2m,10m)

raw_stats={}
diff = GF_data.T3m_minutt_Avg - AVD_data.T2m_PT1000_Avg
raw_stats['davg_diff'] = diff.resample('D').mean()
raw_stats['mavg_diff'] = diff.resample('M').mean()
raw_stats['yavg_diff'] = diff.resample('Y').mean()

daterange = pd.date_range(start='2016-01-01 00:00:00',
	end='2017-06-27 00:00:00', periods=None, freq='D',
	normalize=False, name='DateTime', closed=None)
mavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
yavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
for i in range(0, len(raw_stats['mavg_diff'])):
	for j in range(0,len(daterange)):
		if np.logical_and(mavg_diff.index.month[j] == raw_stats['mavg_diff'].index.month[i],
		 mavg_diff.index.year[j] == raw_stats['mavg_diff'].index.year[i]):
			mavg_diff[j] = raw_stats['mavg_diff'][i]
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
f9.savefig('figures/T_meanDiff2m3m.png', bbox_inches='tight')
plt.close(f9)

raw_stats={}
diff = GF_data.T1m_minutt_Avg - AVD_data.T2m_PT1000_Avg
raw_stats['davg_diff'] = diff.resample('D').mean()
raw_stats['mavg_diff'] = diff.resample('M').mean()
raw_stats['yavg_diff'] = diff.resample('Y').mean()
daterange = pd.date_range(start='2016-01-01 00:00:00',
	end='2017-06-27 00:00:00', periods=None, freq='D',
	normalize=False, name='DateTime', closed=None)
mavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
yavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
for i in range(0, len(raw_stats['mavg_diff'])):
	for j in range(0,len(daterange)):
		if np.logical_and(mavg_diff.index.month[j] == raw_stats['mavg_diff'].index.month[i],
		 mavg_diff.index.year[j] == raw_stats['mavg_diff'].index.year[i]):
			mavg_diff[j] = raw_stats['mavg_diff'][i]
for i in range(0, len(raw_stats['yavg_diff'])):
	for j in range(0,len(daterange)):
		if yavg_diff.index.year[j] == raw_stats['yavg_diff'].index.year[i]:
			yavg_diff[j] = raw_stats['yavg_diff'][i]

f10, (ax1,ax2) = plt.subplots(nrows=2, ncols=1, figsize = (15,10), sharex=True, sharey=False, squeeze=True, subplot_kw=None, gridspec_kw=None)
ax1.plot(GF_data.index, GF_data.T1m_minutt_Avg.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'Gruvefjellet 1m(GF)')
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
ax2.set_title('Mean differences GF1m-AVD2m')
f10.savefig('figures/T_meanDiff1m2m.png', bbox_inches='tight')
plt.close(f10)

slope, intercept, r_value, p_value, std_err = stats.linregress(GF_data.T1m_minutt_Avg, AVD_data.T2m_PT1000_Avg)
f11, ax1 = plt.subplots(nrows = 1, ncols =1)
ax1.plot(GF_data.T1m_minutt_Avg, AVD_data.T2m_PT1000_Avg, 'o', label='GF vs. AVD', alpha =0.5)
ax1.plot(GF_data.T1m_minutt_Avg, intercept + slope*GF_data.T1m_minutt_Avg, 'r', label='lin. Regression')
ax1.legend(loc ='lower right')
ax1.set_xlabel('T1m GF [degC]')
ax1.set_ylabel('T2m AVD [degC]')
ax1.set_xlim(-35,20)
ax1.set_ylim(-35,20)
plt.text(-33, 17, 'y = '+str(intercept.round(2))+'+'+str(slope.round(2))+'*x' ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
plt.text(-33, 13, 'R ='+str(r_value.round(2)) ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
f11.savefig('figures/T_GF1mvsAVD2m.png', bbox_inches='tight')
plt.close(f11)

slope, intercept, r_value, p_value, std_err = stats.linregress(GF_data.T3m_minutt_Avg, AVD_data.T2m_PT1000_Avg)
f12, ax1 = plt.subplots(nrows = 1, ncols =1)
ax1.plot(GF_data.T3m_minutt_Avg, AVD_data.T2m_PT1000_Avg, 'o', label='GF vs. AVD', alpha =0.5)
ax1.plot(GF_data.T3m_minutt_Avg, intercept + slope*GF_data.T1m_minutt_Avg, 'r', label='lin. Regression')
ax1.legend(loc ='lower right')
ax1.set_xlabel('T3m GF [degC]')
ax1.set_ylabel('T2m AVD [degC]')
ax1.set_xlim(-35,20)
ax1.set_ylim(-35,20)
plt.text(-33, 17, 'y = '+str(intercept.round(2))+'+'+str(slope.round(2))+'*x' ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
plt.text(-33, 13, 'R ='+str(r_value.round(2)) ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
f12.savefig('figures/T_GF3mvsAVD2m.png', bbox_inches='tight')
plt.close(f12)



#-------------------------------------------Wind Speed---------------------------------
# Plot wind speed - measurement heights at GF and AVD

slope, intercept, r_value, p_value, std_err = stats.linregress(GF_data.ff_mps_avg, AVD_data.ff2m_mps_avg)
f13, ax1 = plt.subplots(nrows = 1, ncols =1)
ax1.plot(GF_data.ff_mps_avg, AVD_data.ff2m_mps_avg, 'o', label='GF vs. AVD', alpha =0.5)
ax1.plot(GF_data.ff_mps_avg, intercept + slope*GF_data.ff_mps_avg, 'r', label='lin. Regression')
ax1.legend(loc ='lower right')
ax1.set_xlabel('ff GF [m/s]')
ax1.set_ylabel('ff2m AVD [m/s]')
ax1.set_xlim(0,25)
ax1.set_ylim(0,25)
plt.text(1, 23, 'y = '+str(intercept.round(2))+'+'+str(slope.round(2))+'*x' ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
plt.text(1, 20, 'R ='+str(r_value.round(2)) ,verticalalignment='top', horizontalalignment='left', fontsize = 15)
f13.savefig('figures/ff_GFvsAVD2m.png', bbox_inches='tight')
plt.close(f13)

raw_stats={}
diff = GF_data.ff_mps_avg - AVD_data.ff2m_mps_avg
raw_stats['davg_diff'] = diff.resample('D').mean()
raw_stats['mavg_diff'] = diff.resample('M').mean()
raw_stats['yavg_diff'] = diff.resample('Y').mean()
daterange = pd.date_range(start='2016-01-01 00:00:00',
	end='2017-06-27 00:00:00', periods=None, freq='D',
	normalize=False, name='DateTime', closed=None)
mavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
yavg_diff = pd.Series(np.nan, index=daterange, dtype=None, name=None, copy=False, fastpath=False)
for i in range(0, len(raw_stats['mavg_diff'])):
	for j in range(0,len(daterange)):
		if np.logical_and(mavg_diff.index.month[j] == raw_stats['mavg_diff'].index.month[i],
		 mavg_diff.index.year[j] == raw_stats['mavg_diff'].index.year[i]):
			mavg_diff[j] = raw_stats['mavg_diff'][i]
for i in range(0, len(raw_stats['yavg_diff'])):
	for j in range(0,len(daterange)):
		if yavg_diff.index.year[j] == raw_stats['yavg_diff'].index.year[i]:
			yavg_diff[j] = raw_stats['yavg_diff'][i]

f14, (ax1,ax2) = plt.subplots(nrows=2, ncols=1, figsize = (15,10), sharex=True, sharey=False, squeeze=True, subplot_kw=None, gridspec_kw=None)
ax1.plot(GF_data.index, GF_data.ff_mps_avg.rolling(window=24).mean(), color = 'g', linewidth = 1, label = 'Gruvefjellet (GF)')
ax1.plot(AVD_data.index, AVD_data.ff2m_mps_avg.rolling(window=24).mean(), color = 'r', linewidth = 1, label = 'Adventdalen 2m(AVD)')
ax1.set_ylim(-0,20)
ax1.grid()
ax1.set_ylabel('Wind speed [m/s]')
ax1.legend(loc = 'lower center')
ax1.set_title('24h Rolling mean')
ax2.plot(raw_stats['davg_diff'], color = 'k',label = 'Daily', linewidth = 2)
ax2.plot(mavg_diff, color = 'r',label = 'Monthly', linewidth = 2)
ax2.plot(yavg_diff, color = 'b', label = 'Yearly', linewidth = 2)
ax2.grid()
ax2.set_ylim(-10,10)
ax2.set_xlabel('Time')
ax2.set_ylabel('Wind speed difference [m/s]')
ax2.legend(loc = 'lower center')
ax2.set_title('Mean differences GF-AVD2m')
f14.savefig('figures/ff_meanDiff1m2m.png', bbox_inches='tight')
plt.close(f14)


