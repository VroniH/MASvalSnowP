# Script to generate data for sensitivity analysis
# 
# Author: Veronika Hatvan

import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

# Import data from files
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
	# Radiaton data is available in 5min steps. Create hourly mean values of the radiation components. 
# Shift the whole dataset by one timestep so that a value at a specific timestep is the mean of the previous hour.
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
	'LF_minutt_Max','LF_minutt_Avg','p_mbar','ff_mps_Max','ff_10min',
	'ff_mps_avg', 'dd','NB_time','SD_m','SD_kval','TSS','T_soil_1m',
	'T_soil_2m','T_soil_3m','T_soil_4m','T_soil_5m','T_soil_6m',
	'R_surf_ohm','R_1m_ohm', 'R_2m_ohm', 'R_3m_ohm', 'R_4m_ohm',
	'R_5m_ohm', 'R_6m_ohm', 'Batt_V_Min'])

ERA5_all = pd.read_csv('data/ERA5_GF.txt', index_col = 0, parse_dates = True,
	na_values = 'NaN', header = 0, names = ['TIMESTAMP', 'HS', 'RR', 'RRmm',
	'T2m', 'ptype'])

# Choose period
# Period beginning in summer, so first snow is also covered. Last pit on the 2nd of April 2017.
# Don't need to simulate longer than this date
GF_data = GF_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']			 	
AVD_rad_data = AVD_rad_data['2016-08-01 00:00:00':'2017-04-03 00:00:00'] 
ERA5 = ERA5_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']
AVD_data = AVD_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']


gradT = ((GF_data.T3m_minutt_Avg + 273.15) - (AVD_data.T2m_Rotron_Avg + 273.15))/(464-15) # calculate temperature gradient per m
gradT_davg = gradT.resample('D').mean()			# calculate mean daily temperature gradients
TG_sysERR_pos = 0.0065 + gradT_davg.std()			# apply positiv systematic error to temperature gradient via std() of mean daily TG
TG_sysERR_neg = 0.0065 - gradT_davg.std()			# apply negative systematic error to temperature gradient
TG_rdmERR = np.random.normal(0.0065,gradT_davg.std(),len(GF_data.index)) # apply random error to temperature gradient
# plt.hist(TG_rdmERR,bins = 100)
# plt.show()

ERA5_all.RRmm *=1.57					#Set factor to adjust precipitation to measured snow height at PIT01 (reference pit)
GF_height = 464							#[masl] Height Gruvefjellet AWS
REF_height = 258 						#[masl] height according to each PIT
sigma = 5.67*10**(-8)    				#[Wm^(-2)K^(-4)] Stefan-Boltzmann constant
ILWR_AVD = AVD_rad_data.LWin_Wpm2       # measured LWIN at AVD, adjust to new temperature, first calc original eps
eps = ILWR_AVD/(sigma*(AVD_data.T2m_Rotron_Avg+273.15)**4)  # Calculate eps.. emissivity of the sky, from original Data at AVD
eps[eps>1] = np.NaN
# print(eps[eps>1].count())
# print(eps[eps>1])

GF_data.index = GF_data.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_rad_data.index = AVD_rad_data.index.strftime('%Y-%m-%dT%H:%M:%S')
ERA5.index = ERA5.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_data.index = AVD_data.index.strftime('%Y-%m-%dT%H:%M:%S')


# Create temperature series with different errors (systematic, random, no error)
T = GF_data.T3m_minutt_Avg + 273.15       		# T in [K]
dh = GF_height -REF_height	           			# calculate height difference GF/ PitX						 
TA = pd.DataFrame({})
TA['noERR']	= T + 0.0065*dh
TA['rdmERR'] = T + TG_rdmERR*dh
TA['sysERR_pos'] = T + TG_sysERR_pos*dh
TA['sysERR_neg'] = T + TG_sysERR_neg*dh

Ttyp = ['TnoERR', 'TrdmERR', 'TsysERR_pos', 'TsysERR_neg']
for i in range(0, len(Ttyp)):
	ILWR_PIT = sigma*eps*(TA.iloc[:,i])**4			# calculate ILWR with adjusted temperature and original eps
	SMET_data = pd.DataFrame.from_items([
		('TA',TA.iloc[:,i].round(2)), 
		('RH',GF_data.round(2)['LF_minutt_Avg']),
		('VW',GF_data.round(2)['ff_mps_avg']),
		('VW_MAX',GF_data.round(2)['ff_mps_Max']),
		('DW',GF_data.round(2)['dd']),
		('ISWR',AVD_rad_data.round(2)['SWin_Wpm2']),
		('ILWR',ILWR_PIT.round(2)),
		('PSUM',ERA5.round(2)['RRmm'])])

	SMET_file = open('/home/user/Documents/Programming/SnowPACK/Masterarbeit/input/'+'modREF_'+str(Ttyp[i])+'_era5f57.smet', mode='w')
	SNO_file = open('/home/user/Documents/Programming/SnowPACK/Masterarbeit/input/'+'modREF_'+str(Ttyp[i])+'_era5f57.sno', mode='w')


	ID = ['01']
	names = ['PIT01']
	latitude = ['78.2027']
	longitude =['15.6118']
	easting =['513963']
	northing =['8681064']
	heights =['258']
	slope = ['32']
	azi =['270']

	for i in range(0,len(names)):
		SMET_file.writelines(['SMET 1.1 ASCII\n',
			'[HEADER]\n',
			'station_id \t\t\t = '+str(ID[i])+'\n',
			'station_name \t\t = '+str(names[i])+'\n',
			'source \t\t\t\t = Raw data: Radiaton from AWS Adventdalen, MET-Data from AWS Gruvefjellet, adjust to pit location: T and ILWR\n',
			'latitude \t\t\t = '+str(latitude[i])+'\n',
			'longitude \t\t\t = '+str(longitude[i])+'\n',
			'easting \t\t\t = '+str(easting[i])+'\n',
			'northing \t\t\t = '+str(northing[i])+'\n',
			'epsg \t\t\t\t = 32633\n'
			# Documentation: (epsg codes as 32600+zoneNumber in the northern hemisphere)
			# Zone:33x
			'altitude \t\t\t = '+str(heights[i])+'\n',
			'nodata \t\t\t\t = -999\n',
			'fields \t\t\t\t = timestamp TA RH VW VW_MAX DW ISWR ILWR PSUM\n' ,
			'units_offset \t\t = 0 0 0 0 0 0 0 0 0\n',
			'units_multiplier \t = 1 1 0.01 1 1 1 1 1 1\n' #multiplication by 1.57, factor to adjust precipitation to reference profile Pit01 
			'creation \t\t\t = '+ str(format(dt.datetime.now(),'%Y-%m-%d %H:%M')),
			'\n[DATA]\n'])

		SMET_data.to_csv(SMET_file,sep = '\t', header = False, index = True, na_rep = '-999')

		SNO_file.writelines(['SMET 1.1 ASCII\n',
			'[HEADER]\n',
			'station_id \t\t\t = '+str(ID[i])+'\n',
			'station_name \t\t = '+str(names[i])+'\n',
			'source \t\t\t\t = Raw data: Radiaton from AWS Adventdalen, MET-Data from AWS Gruvefjellet, adjust to pit location: T and ILWR\n',
			'latitude \t\t\t = '+str(latitude[i])+'\n',
			'longitude \t\t\t = '+str(longitude[i])+'\n',
			'easting \t\t\t = '+str(easting[i])+'\n',
			'northing \t\t\t = '+str(northing[i])+'\n',
			'epsg \t\t\t\t = 32633\n'
			# Documentation: (epsg codes as 32600+zoneNumber in the northern hemisphere)
			#Zone:33x
			'altitude \t\t\t = '+str(heights[i])+'\n',
			'nodata \t\t\t\t\t = -999\n',
			'ProfileDate \t\t\t = 2016-08-01T00:00:00\n',
			'HS_Last \t\t\t\t = 0.000000\n',
			'SlopeAngle \t\t\t\t = '+str(slope[i])+'\n',
			'SlopeAzi \t\t\t\t = '+str(azi[i])+'\n',
			'nSoilLayerData \t\t\t = 0\n',
			'nSnowLayerData \t\t\t = 0\n',
			'SoilAlbedo \t\t\t\t = 0.09\n',
			'BareSoil_z0 \t\t\t = 0.200\n',
			'CanopyHeight \t\t\t = 0.00\n',
			'CanopyLeafAreaIndex \t = 0.000000\n',
			'CanopyDirectThroughfall  = 1.00\n',
			'WindScalingFactor \t\t = 1.00\n',
			'ErosionLevel \t\t\t = 0\n',
			'TimeCountDeltaHS \t\t = 0.218750\n',
			'fields \t\t\t\t\t = timestamp Layer_Thick  T  Vol_Frac_I  Vol_Frac_W  Vol_Frac_V  Vol_Frac_S Rho_S Conduc_S HeatCapac_S  rg  rb  dd  sp  mk mass_hoar ne CDot metamo\n',
			'[DATA]\n'])



