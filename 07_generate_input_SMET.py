# Script to generate one input file per pit location
# Use meteorological data from Gruvefjellet (GF) weather station and 
# radiation data from Adventdalen. Can assume that most parameters are
# approx. the same within the area of investigation.
# Need to adjust temperature and incoming longwave radiation to height of pit location.
# Author: Veronika Hatvan

import pandas as pd
import datetime as dt
import numpy as np
from my_func import calc_T_moistadiabat, calc_eps, calc_ILWR
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
ERA5_all.RRmm *=0.35
# Choose period
# Period beginning in summer, so first snow is also covered. Last pit on the 2nd of April 2017.
# Don't need to simulate longer than this date
GF_data = GF_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']			 	
AVD_rad_data = AVD_rad_data['2016-08-01 00:00:00':'2017-04-03 00:00:00'] 
ERA5 = ERA5_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']
AVD_data = AVD_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']

GF_data.index = GF_data.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_rad_data.index = AVD_rad_data.index.strftime('%Y-%m-%dT%H:%M:%S')
ERA5.index = ERA5.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_data.index = AVD_data.index.strftime('%Y-%m-%dT%H:%M:%S')

# define names for .SMET Files
# format: PIT[XX]_[precipINPUTtype]
# precipINPUTtype could later be: ERA5, ERA5skaliert, ECMWF, scans?, local measurements?
precipINPUTtype = ['era5']
names = ['PIT01','PIT02','PIT03','PIT04',
'PIT05','PIT06','PIT07','PIT08','PIT09','PIT10','PIT11']
ID = ['01','02','03','04','05','06','07','08','09','10','11',]
latitude = ['78.2027','78.2171','78.2046','78.21','78.2144','78.2096','78.2122','78.2062','78.2044','78.1966','78.1978']
longitude =['15.6118','15.6092','15.6121','15.6278','15.6537','15.5866','15.5932','15.6266','15.5738','15.5784','15.5909']
easting =['513963','513887','513968','514320','514905','513380','513528','514297','513094','513208','513492']
northing =['8681064','8682671','8681276','8681883','8682380','8681828','8682120','8681458','8681245','8680376','8680512']
slope = ['32','30','29','26','25','25','28','28','27','26','31']
azi =['270','135','315','315','0','135','135','0','90','315','315']
GF_height = 464 #[masl] Height Gruvefjellet AWS
heights = [258, 75, 190, 108, 172, 128, 135, 285, 149, 142, 162] #[masl] height according to each PIT

sigma = 5.67*10**(-8)    				#[Wm^(-2)K^(-4)] Stefan-Boltzmann constant
ILWR_AVD = AVD_rad_data.LWin_Wpm2       # measured LWIN at AVD, adjust to new temperature, first calc original eps
eps = ILWR_AVD/(sigma*(AVD_data.T2m_Rotron_Avg+273.15)**4)  # Calculate eps.. emissivity of the sky, from original Data at AVD
# print(eps[eps>1].count())
# print(eps[eps>1])
eps[eps>1] = np.NaN
T = GF_data.T3m_minutt_Avg + 273.15   
# for i in range(0,len(heights)) :
for i in range(1,2):     
	dh = GF_height - heights[i]             # calculate height difference GF/ PitX
	TA = T + 0.0037*dh                      # Calculate temperature change due to moistadiabatic gradient (0.0065 K/m)
	ILWR_PITx = sigma*eps*(TA)**4			# calculate ILWR with adjusted temperature and original eps


	SMET_data = pd.DataFrame.from_items([
		('TA',TA.round(2)), 
		('RH',GF_data.round(2)['LF_minutt_Avg']),
		('VW',GF_data.round(2)['ff_mps_avg']),
		('VW_MAX',GF_data.round(2)['ff_mps_Max']),
		('DW',GF_data.round(2)['dd']),
		('ISWR',AVD_rad_data.round(2)['SWin_Wpm2']),
		('ILWR',ILWR_PITx.round(2)),
		('PSUM',ERA5.round(2)['RRmm'])])

	SMET_file = open('/home/user/Documents/Programming/SnowPACK/Masterarbeit/input/'+str(names[i])+'_era5.smet', mode='w')
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
		'units_multiplier \t = 1 1 0.01 1 1 1 1 1 1\n' #mutliplication by 10^3 to get [mm] already applied to PSUM in 01_read_ERA5_data.py 
		'creation \t\t\t = '+ str(format(dt.datetime.now(),'%Y-%m-%d %H:%M')),
		'\n[DATA]\n'])

	SMET_data.to_csv(SMET_file,sep = '\t', header = False, index = True, na_rep = '-999')

	SNO_file = open('/home/user/Documents/Programming/SnowPACK/Masterarbeit/input/'+str(names[i])+'_era5.sno', mode='w')
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