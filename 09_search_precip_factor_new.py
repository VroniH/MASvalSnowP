# Script to find best precipitation factor for each pit location 


# IMPORT MODULES -----------------------------------------------

import pandas as pd
import datetime as dt
import numpy as np
import subprocess # to run SNOWPACK shell command via python script
import os 		  	
import timeit
import fnmatch
from my_func import create_SMET, create_SNO, create_INI

start_time = timeit.default_timer()

# IMPORT DATA -------------------------------------------------

# Import manual snow profile data 

Pits_manual = pd.read_csv('/home/user/Desktop/Masterarbeit/Schneeprofile/Profildaten_LAWIS/profiles_hatvan.csv',
 sep = ';', header = [0])
Pits_layers = pd.read_csv('/home/user/Desktop/Masterarbeit/Schneeprofile/Profildaten_LAWIS/profiles_hatvan_schichten.csv',
 sep = ',', header = [0])
# print(Pits_layers['vonhoehe'][1])

# Import data from AWS Adventdalen (AVD)
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

# Import data from radiation measurements Adventdalen 
AVD_rad_all = pd.read_csv('raw_data/Adventdalen_New_Fem_minutt.dat', 
	skiprows = [0,2,3],index_col = 0, parse_dates = True, na_values = 'NAN',header = 0,
	names = ['TIMESTAMP','RECORD','SWin_Wpm2','LWin_Wpm2','SWout_Wpm2','LWout_Wpm2','CNR1_temp_gr_C_Avg'])

# Radiaton data is available in 5min steps, create hourly mean values of the radiation components. 
# shift(1) - shift the whole dataset by one timestep so that a value at each timestep is the mean of the previous hour
AVD_rad_data = pd.DataFrame.from_items([
	('SWin_Wpm2',AVD_rad_all['SWin_Wpm2'].resample('H').mean().shift(1)), #opp..upward looking instrument measuring SW down
	('SWout_Wpm2', AVD_rad_all['SWout_Wpm2'].resample('H').mean().shift(1)), #ned..downward looking instrument measuring SW up
	('LWin_Wpm2', AVD_rad_all['LWin_Wpm2'].resample('H').mean().shift(1)),
	('LWout_Wpm2', AVD_rad_all['LWout_Wpm2'].resample('H').mean().shift(1))])

# Import data from AWS Gruvefjellet (GF)
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

# Import ERA5 precipitation data
ERA5_all = pd.read_csv('data/ERA5_GF.txt', index_col = 0, parse_dates = True,
	na_values = 'NaN', header = 0, names = ['TIMESTAMP', 'HS', 'RR', 'RRmm',
	'T2m', 'ptype'])

# Choose period
# Period beginning in summer to also cover first snow fall, last pit on the 2nd of April 2017
GF_data = GF_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']			 	
AVD_rad_data = AVD_rad_data['2016-08-01 00:00:00':'2017-04-03 00:00:00'] 
ERA5 = ERA5_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']
AVD_data = AVD_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']

# Adapt timestamp format to SNOWPACK's requirements
GF_data.index = GF_data.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_rad_data.index = AVD_rad_data.index.strftime('%Y-%m-%dT%H:%M:%S')
ERA5.index = ERA5.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_data.index = AVD_data.index.strftime('%Y-%m-%dT%H:%M:%S')

# CREATE .SMET FILES -------------------------------------------
# vary precipitation factor to find the best fit of snow depth to manual observations
# set a fixed temperature gradient, derived from examination of measurements from AVD and GF

# Create list of precipitation factors fRR to apply to ERA5 data
# fRR = np.arange(0.5,2.6,0.1)
fRR = [1.5]

# Create a name list for fRR to add to name of SMET file
nfRR = [None]*len(fRR)
for i in range(len(fRR)): 
	nfRR[i] = 'f'+str(round(fRR[i],1)).replace('.','')

# define names and metadata for SMET files
names = ['PIT01','PIT02','PIT03','PIT04',
'PIT05','PIT06','PIT07','PIT08','PIT09','PIT10','PIT11']
ID = ['PIT01','PIT02','PIT03','PIT04',
'PIT05','PIT06','PIT07','PIT08','PIT09','PIT10','PIT11']
latitude = ['78.2027','78.2171','78.2046','78.21','78.2144','78.2096',
'78.2122','78.2062','78.2044','78.1966','78.1978']
longitude =['15.6118','15.6092','15.6121','15.6278','15.6537','15.5866',
'15.5932','15.6266','15.5738','15.5784','15.5909']
easting =['513963','513887','513968','514320','514905','513380','513528',
'514297','513094','513208','513492']
northing =['8681064','8682671','8681276','8681883','8682380','8681828',
'8682120','8681458','8681245','8680376','8680512']
slope = ['32','30','29','26','25','25','28','28','27','26','31']
azi =['270','135','315','315','0','135','135','0','90','315','315']
GF_height = 464 #[masl] Height Gruvefjellet AWS
# heights = [258, 75, 190, 108, 172, 128, 135, 285, 149, 142, 162] #[masl] height according to each PIT
heights = [75]

# Calculate ILWR according to location of pit
sigma = 5.67*10**(-8)    				#[Wm^(-2)K^(-4)] Stefan-Boltzmann constant
ILWR_AVD = AVD_rad_data.LWin_Wpm2       # measured LWIN at AVD, adjust to new temperature, first calc original eps
eps = ILWR_AVD/(sigma*(AVD_data.T2m_Rotron_Avg+273.15)**4)  # Calculate eps.. emissivity of the sky, from original Data at AVD
# print(eps[eps>1].count())
# print(eps[eps>1])
eps[eps>1] = np.NaN
T = GF_data.T3m_minutt_Avg + 273.15 
for i in range(0,len(fRR)):  
	for j in range(0,len(heights)) :     
		dh = GF_height - heights[j]             # calculate height difference GF/ PitX
		TA = T + 0.0065*dh                      # Calculate temperature change due to moistadiabatic gradient (0.0065 K/m)
		ILWR_PITx = sigma*eps*(TA)**4			# calculate ILWR with adjusted temperature and original eps

	# Create SMET input data
		SMET_data = pd.DataFrame.from_items([
			('TA',TA.round(2)), 
			('RH',GF_data.round(2)['LF_minutt_Avg']),
			('VW',GF_data.round(2)['ff_mps_avg']),
			('VW_MAX',GF_data.round(2)['ff_mps_Max']),
			('DW',GF_data.round(2)['dd']),
			('ISWR',AVD_rad_data.round(2)['SWin_Wpm2']),
			('ILWR',ILWR_PITx.round(2)),
			('PSUM',ERA5.round(2)['RRmm']*fRR[i])])

		SMET_file = create_SMET(names[j],nfRR[i],ID[j],latitude[j],longitude[j],easting[j],northing[j],heights[j],SMET_data)
		SNO_file = create_SNO(names[j],nfRR[i],ID[j],latitude[j],longitude[j],easting[j],northing[j],heights[j],slope[j],azi[j])

# elapsed = timeit.default_timer() - start_time	
# print(elapsed)

# Create .INI file -------------------------------------------------

for i in range(0,len(heights)):
	for j in range(0,len(fRR)):
		INI_file = create_INI(names[i],nfRR[j])
		
	# RUN SNOWPACK -------------------------------------------------

		os.chdir('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/')	# change working directory 
		subprocess.call('snowpack -c cfgfiles/PitX_fXX.ini -m research -e 2017-04-03T00:00', shell = True)	# run SNOWPACK 

	# COMPARE manual and modelled HS -------------------------------


	# Read HS data from manual profiles

		files = []
		for file in os.listdir('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/output_sensitivity/'):
			if file.endswith(".pro"):
				files.append(file)
		paths = [os.path.join('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/output_sensitivity', basename) for basename in files]
		latest =  max(paths, key=os.path.getctime)

		for k in range(0, 11):
			if k < 9:
				fn = '*PIT0'+str(k+1)+'*'
			else:
				fn = '*PIT'+str(k+1)+'*'
			if fnmatch.fnmatch(latest,fn):
				Date = Pits_manual['Datum'][k]
				Date = dt.datetime.strptime(Date, '%Y-%m-%d %H:%M:%S')
				Date = Date.replace(second=0,minute=0)
				Date =  Date.strftime('%d.%m.%Y %H:%M:%S')
				PitID = Pits_manual['Profil-ID'][k]
				HS_man = max(Pits_layers['vonhoehe'][Pits_layers['profil_id'] == PitID])
				print(latest,Date,PitID,HS_man)

	# Read HS data from modelled profiles	

				with open(latest,'r') as file:
					for (l, line) in enumerate(file):
						line = line.rstrip()
						if '0500,'+ Date == line:
							HS_mod = file.next()
							HS_mod = HS_mod.split(',')[-1]
							print(l, line, HS_mod)
							print(HS_man,float(HS_mod))
							diffHS = HS_man - float(HS_mod)											
							print(diffHS)