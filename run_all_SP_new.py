


# IMPORT MODULES -----------------------------------------------
import pandas as pd
import datetime as dt
import numpy as np
import subprocess # to run SNOWPACK shell command via python script
import os 		  	
import timeit
import fnmatch
import glob
from my_func import create_SMET, create_SNO, create_INI_case1, create_INI_case2
from scipy import optimize

# Delete files from ealier runs

for file in os.listdir('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/'):
	if fnmatch.fnmatch(file, 'res*'):
		os.remove('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/' + file)

# DEFINE FUNCTION(S) -------------------------------------------

# Create .SMET/.SNO/.INI files
# vary precipitation factor to find the best fit of snow depth to manual observations
# set a fixed temperature gradient, derived from examination of measurements from AVD and GF

def diffHS(fRR):

	print('fRR:',fRR)
	# fRR = fRR.round(2)

	# Set nfRR to adjust name of SMET file accordingly
	nfRR = 'f'+str(fRR).replace('.','_')
	# print('nfRR:',nfRR)

	# Create SMET input data
	SMET_data = pd.DataFrame.from_items([
		('TA',TA.round(2)), 
		('RH',GF_data.round(2)['LF_minutt_Avg']),
		('VW',GF_data.round(2)['ff_mps_avg']),
		('VW_MAX',GF_data.round(2)['ff_mps_Max']),
		('DW',GF_data.round(2)['dd']),
		('ISWR',AVD_rad_data.round(2)['SWin_Wpm2']),
		('ILWR',ILWR_PITx.round(2)),
		#('PSUM',ERA5.round(2)['RRmm']*fRR)])
		('PSUM',eklima.round(2)['RR']*fRR)])

	create_SMET(names[i],nfRR,ID[i],latitude[i],longitude[i],easting[i],northing[i],heights[i],SMET_data)
	create_SNO(names[i],nfRR,ID[i],latitude[i],longitude[i],easting[i],northing[i],heights[i],slope[i],azi[i])
	INI_file = create_INI_case2(names[i],nfRR)

	# Remove output files--------------------------------------------------
	# remove previously built output files, so memory is not swampt with unnecessary files 
	# for files in os.listdir('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/output_sensitivity/'):
	# 	os.remove('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/output_sensitivity/' + files)
	# RUN SNOWPACK -------------------------------------------------

	os.chdir('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/')	# change working directory 
	subprocess.call('snowpack -c cfgfiles/'+INI_file+' -m research -e 2017-04-03T00:00', shell = True)	# run SNOWPACK 

	# COMPARE manual and modelled HS -------------------------------

	# Read HS data from manual profiles
	files = []
	for file in os.listdir('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/output_sensitivity/'): # list files in output directory
		if file.endswith(".pro"): 
			files.append(file)  # get list of .pro files
	paths = [os.path.join('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/output_sensitivity', basename) for basename in files] # create file path
	latest =  max(paths, key=os.path.getctime) # find newest file in folder to get HS data from file

	for k in range(0, 11):					# find name of file to choose right data from 
		if k < 9:
			fn = '*PIT0'+str(k+1)+'*'			
		else:
			fn = '*PIT'+str(k+1)+'*'
		if fnmatch.fnmatch(latest,fn):					# if file name matches pattern, choose data from manual snow pit file
			Date = Pits_manual['Datum'][k]				# find date of manual profile, later use it to get modelled data out of .pro
			Date = dt.datetime.strptime(Date, '%Y-%m-%d %H:%M:%S')	#format data
			Date = Date.replace(second=0,minute=0)
			Date =  Date.strftime('%d.%m.%Y %H:%M:%S')
			PitID = Pits_manual['Profil-ID'][k]			# find pit id
			HS_man = max(Pits_layers['vonhoehe'][Pits_layers['profil_id'] == PitID]) # find HS of snowpit
			# print(latest,Date,PitID,HS_man)

			# Read HS data from modelled profiles	
			with open(latest,'r') as file:				# open latest (newest) .pro file
				for (l, line) in enumerate(file):		# read lines
					line = line.rstrip()				# removes whitespace characters from end of line
					if '0500,'+ Date == line:			# finde right entry, according to date of manual snowpit
						HS_mod = file.next()			# jump to next line
						HS_mod = HS_mod.split(',')[-1]	# split entries by sep = , save last value (-1) in line
						# print(l, line, HS_mod)
						# print(HS_man,float(HS_mod))
						diff_HS = abs(HS_man - float(HS_mod))	# write difference manual - modelled HS to variable
						x.append(fRR)							# write list of rain factors
						f_x.append(diff_HS) 						# write list of HS_diff manual -  modelled
						print('diffHS:',diff_HS)					# print difference
	return diff_HS							# hand difference over to script

						
# IMPORT DATA -------------------------------------------------

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

eklima_all = pd.read_csv('data/LFH_RR_ts.txt', index_col=0,parse_dates = True,
na_values='NaN',header=0, names= ['RR','ff'])


# Import manual snow profile data 
Pits_manual = pd.read_csv('/home/user/Desktop/Masterarbeit/Schneeprofile/Profildaten_LAWIS/profiles_hatvan.csv',
 sep = ';', header = [0])
Pits_layers = pd.read_csv('/home/user/Desktop/Masterarbeit/Schneeprofile/Profildaten_LAWIS/profiles_hatvan_schichten.csv',
 sep = ',', header = [0])
# print(Pits_layers['vonhoehe'][1])

# Choose period
# Period beginning in summer to also cover first snow fall, last pit on the 2nd of April 2017
GF_data = GF_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']			 	
AVD_rad_data = AVD_rad_data['2016-08-01 00:00:00':'2017-04-03 00:00:00'] 
ERA5 = ERA5_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']
AVD_data = AVD_all['2016-08-01 00:00:00':'2017-04-03 00:00:00']
eklima = eklima_all['2016-08-01 06:00:00':'2017-04-03 18:00:00']

# Adapt timestamp format to SNOWPACK's requirements
GF_data.index = GF_data.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_rad_data.index = AVD_rad_data.index.strftime('%Y-%m-%dT%H:%M:%S')
ERA5.index = ERA5.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_data.index = AVD_data.index.strftime('%Y-%m-%dT%H:%M:%S')
eklima.index = eklima.index.strftime('%Y-%m-%dT%H:%M:%S')

# Provide information/metadata for SMET/SNO/INI Files
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
heights = [258, 75, 190, 108, 172, 128, 135, 285, 149, 142, 162] #[masl] height according to each PIT

# Calculate ILWR according to location of pit
sigma = 5.67*10**(-8)    				#[Wm^(-2)K^(-4)] Stefan-Boltzmann constant
ILWR_AVD = AVD_rad_data.LWin_Wpm2       # measured LWIN at AVD, adjust to new temperature, first calc original eps
eps = ILWR_AVD/(sigma*(AVD_data.T2m_Rotron_Avg+273.15)**4)  # Calculate eps.. emissivity of the sky, from original Data at AVD
# print(eps[eps>1].count())
# print(eps[eps>1])
eps[eps>1] = np.NaN						# set all eps >1 to NaN, so they don't disturb further calculations
T = GF_data.T3m_minutt_Avg + 273.15 	# Set temperature data to Kelvin			
# for i in range(0,len(heights)):		# Run through all pits, adapt temperature accordingly
# for i in range(0,2):
i = 2	  								# Try for single pits
dh = GF_height - heights[i]             # calculate height difference GF/ PitX
TA = T + 0.0037*dh                      # Calculate temperature change due to height difference, gradient chosen from measurements - mean TG between AVD and GF
ILWR_PITx = sigma*eps*(TA)**4			# calculate ILWR with adjusted temperature and original eps
x=[]
f_x=[]
opt = optimize.brute(diffHS, ((0.1,2.5),), args=(), Ns=24,
 full_output=True, disp=True, finish = None) 	# optimization process, runs function diffHS with rain factor values
 															# between 0.1 -2.5, with 30 grid points inbetween(Ns), after frist optimization
 															# with "brute force method" run another optimization "minimize" to with result of 
 															# brute force method as initial guess to obtain more precise results
# x0 = 1.0								# initial guess for the optimization process
# bnds = ((0.1,2.5),)						# bounds for the input (fRR) for the optimization process
# res = optimize.minimize_scalar(diffHS,bounds = (0.1, 2.50), options ={'maxiter': 10}) # wofuer gebe ich bounds an, wenn Werte ausserhalb dieser Grenzen als Input fuer die Fnktion gewaehlt werden
# res = optimize.minimize(diffHS, [x0], bounds=bnds)
# res = optimize.minimize(diffHS, x0, bounds=bnds, options={'maxiter':10, 'disp': True}, method = 'CG')
# print('result:',res,'x:',x,'f_x:',f_x)
print('result:',opt,'x:',x,'f_x:',f_x)

res = open('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/res'+str(i+1)+'.txt', mode = 'a')
data = pd.DataFrame.from_items([
	('fRR', x),
	('diffHS',f_x)])
data.to_csv(res,sep = ',', header = True, index = True, na_rep = '-999', mode = 'a')
 


	