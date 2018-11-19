# Script to write all necessary data into one SMET file
# This file will late be used as input in SNOWPACK
# If changes to ERA5 Data are necessary, apply changes in read_ERA4_data.py 
# and run script again. Then run this script again.

# author: Veronika Hatvan


# Import Packages --------------------------
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import datetime as dt

# Import Data -----------------------------
# Data from Gruvefjellet AWS
GF_data_all = pd.read_csv('raw_data/Gruvefjellet_Res_data.dat', 
	skiprows = [0,2,3], index_col = 0,parse_dates = True, na_values = 'NAN')

# Data from Adventdalen AWS ----------------
AVD_data_all = pd.read_csv('raw_data/Adventdalen_Hour.dat', 
	skiprows = [0,2,3], index_col = 0, parse_dates = True, na_values = 'NAN')

# Data from Adventdalen radiation measurements -----------
AVD_rad_data_all = pd.read_csv('raw_data/Adventdalen_New_Fem_minutt.dat', 
    skiprows = [0,2,3],index_col = 0, parse_dates = True, na_values = 'NAN')

# Data from ERA5 (precipitation)
ERA5 = pd.read_csv('data/ERA5_GF.txt',
    index_col = 0, parse_dates = True, na_values = 'NaN')
# print(ERA5.index)
#Data from snow scans
HS_data = pd.read_csv('data/HS_data_all_filled.txt', index_col = 0,
 parse_dates = True, na_values = 'NaN')
# print HS_data.index

# Choose analysis period --------------------
# first Snow Scan on 02.12.2016 last profile on 02.04.2017
# HS_data = HS_data['2016-12-02 00:00:00 : 2017-04-03 00:00:00']
GF_data_all = GF_data_all['2016-08-01 00:00:00':'2017-06-27 00:00:00']			 	
AVD_data_all = AVD_data_all['2016-08-01 00:00:00':'2017-06-27 00:00:00']
AVD_rad_data_all = AVD_rad_data_all['2016-08-01 00:00:00':'2017-06-27 00:00:00'] 
ERA5 = ERA5['2016-08-01 00:00:00':'2017-06-27 00:00:00']

#Precip is in [m] to get [mm] multiply by 1000
# Multiplier given to smet file and applied by MeteoIO/SP
# ERA5_RR.RR = ERA5_RR.RR.multiply(10**3)

# Average radiation data ----------------------------------------
# resample().mean() ..downsample the data into hourly values and take the mean of all values falling into one hour
#.shift(1).. shift data by one hour, values given are the mean of the measurments in the hour previous to the timestep
AVD_rad_data = pd.DataFrame.from_items([
    ('SW_down',AVD_rad_data_all['CM3_opp_Wpm2_Avg'].resample('H').mean().shift(1)), #opp..upward looking instrument measuring SW down
    ('SW_up', AVD_rad_data_all['CM3_ned_Wpm2_Avg'].resample('H').mean().shift(1)), #ned..downward looking instrument measuring SW up
    ('LW_down', AVD_rad_data_all['CG3_opp_Wpm2_Avg'].resample('H').mean().shift(1)),
    ('LW_up', AVD_rad_data_all['CG3_ned_Wpm2_Avg'].resample('H').mean().shift(1))])


print(type(GF_data_all.index))
# Set format of DateTimeIndex to Snowpack requirements
GF_data_all.index = GF_data_all.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_rad_data.index = AVD_rad_data.index.strftime('%Y-%m-%dT%H:%M:%S')
ERA5.index = ERA5.index.strftime('%Y-%m-%dT%H:%M:%S')
HS_data.index = HS_data.index.strftime('%Y-%m-%dT%H:%M:%S')
AVD_data_all.index = AVD_data_all.index.strftime('%Y-%m-%dT%H:%M:%S')
print(type(GF_data_all.index))

# Wind direction perturbation
# dd=pd.DataFrame({'DateTime': GF_data_all.index,'dd': np.nan, 'VR':GF_data_all.VR_gr_framh})
# dd.set_index('DateTime',inplace = True, drop=True)
# for i in range(0,len(GF_data_all.index)):
#     if GF_data_all.VR_gr_framh[i] + 70 > 360:
#         dd.dd[i] = GF_data_all.VR_gr_framh[i]+70-360
#     if GF_data_all.VR_gr_framh[i] +70 < 360:
#         dd.dd[i] = GF_data_all.VR_gr_framh[i] +70
# print(dd)

# Relative humidity perturbation
# RH=pd.DataFrame({'DateTime': GF_data_all.index,'RH': np.nan, 'rh':GF_data_all.LF_minutt_Avg})
# RH.set_index('DateTime',inplace = True, drop=True)
# for i in range(0,len(GF_data_all.index)):
#     # RH.RH[i] = GF_data_all.LF_minutt_Avg[i] -5
#     if GF_data_all.LF_minutt_Avg[i] + 5 > 100:
#         RH.RH[i] = 100
#     if GF_data_all.LF_minutt_Avg[i] +5 < 100:
#         RH.RH[i] = GF_data_all.LF_minutt_Avg[i] +5

# Temperature perturbation
# T=pd.DataFrame({'DateTime': GF_data_all.index,'Ta': np.nan})
# T.set_index('DateTime',inplace = True, drop=True)
# for i in range(0,len(GF_data_all.index)):
#     T.Ta[i] = GF_data_all.LT3m_minutt_Avg[i] -1


# radiation direction perturbation
# LWIN=pd.DataFrame({'DateTime': AVD_rad_data.index,'LWIN': np.nan, 'LW_down':AVD_rad_data.LW_down})
# LWIN.set_index('DateTime',inplace = True, drop=True)
# for i in range(0,len(AVD_rad_data.index)):
#   LWIN.LWIN[i] = AVD_rad_data.LW_down[i]+150
    # if AVD_rad_data.LW_down[i] - 150 > 0:
    #     LWIN.LWIN[i] = AVD_rad_data.LW_down[i]-150
    # if AVD_rad_data.LW_down[i] - 150 <0:
    #     LWIN.LWIN[i] = 0

# LWOUT=pd.DataFrame({'DateTime': AVD_rad_data.index,'LWOUT': np.nan, 'LW_up':AVD_rad_data.LW_up})
# LWOUT.set_index('DateTime',inplace = True, drop=True)
# for i in range(0,len(AVD_rad_data.index)):
#   LWOUT.LWOUT[i] = AVD_rad_data.LW_up[i]+150
    # if AVD_rad_data.LW_up[i] - 150 > 0:
    #     LWOUT.LWOUT[i] = AVD_rad_data.LW_down[i]-150
    # if AVD_rad_data.LW_up[i] - 150 <0:
    #     LWOUT.LWOUT[i] = 0

# SWIN=pd.DataFrame({'DateTime': AVD_rad_data.index,'SWIN': np.nan, 'SW_down':AVD_rad_data.SW_down})
# SWIN.set_index('DateTime',inplace = True, drop=True)
# for i in range(0,len(AVD_rad_data.index)):
#   # SWIN.SWIN[i] = AVD_rad_data.SW_down[i]+150
#     if AVD_rad_data.SW_down[i] - 150 > 0:
#         SWIN.SWIN[i] = AVD_rad_data.SW_down[i]-150
#     if AVD_rad_data.SW_down[i] - 150 <0:
#         SWIN.SWIN[i] = 0

# SWOUT=pd.DataFrame({'DateTime': AVD_rad_data.index,'SWOUT': np.nan, 'SW_up':AVD_rad_data.SW_up})
# SWOUT.set_index('DateTime',inplace = True, drop=True)
# for i in range(0,len(AVD_rad_data.index)):
#   SWOUT.SWOUT[i] = AVD_rad_data.SW_up[i]+150
    # if AVD_rad_data.SW_up[i] - 150 > 0:
    #     SWOUT.SWOUT[i] = AVD_rad_data.SW_down[i]-150
    # if AVD_rad_data.SW_up[i] - 150 <0:
    #     SWOUT.SWOUT[i] = 0

# Wind speed perturbation
ff=pd.DataFrame({'DateTime': GF_data_all.index,'ff': np.nan, 'ff_max': np.nan})
ff.set_index('DateTime',inplace = True, drop=True)
for i in range(0,len(GF_data_all.index)):
  # ff.ff[i] = GF_data_all.VH_mps_mid[i]+4
    if GF_data_all.VH_mps_mid[i] - 4 > 0:
        ff.ff[i] = GF_data_all.VH_mps_mid[i]-4
        ff.ff_max[i] = GF_data_all.VH_mps_Max[i]-4
    if GF_data_all.VH_mps_mid[i] - 4 < 0:
        ff.ff[i] = 0
        ff.ff_max[i] = 0
# print(dd)



# print(HS_data.index)
# Create dataframe with all necessary dataseries (Gruvefjellet)------------------

GF_SMET_data = pd.DataFrame.from_items([
    ('TA',GF_data_all.round(2)['LT3m_minutt_Avg']), 
    # ('TA',T.round(2)['Ta']), 
	('RH',GF_data_all.round(2)['LF_minutt_Avg']),
    # ('RH',AVD_data_all.round(2)['LF1_prst_Avg']),
    # ('RH',RH.round(2)['RH']),    
    # ('VW',GF_data_all.round(2)['VH_mps_mid']),
    ('VW',ff.round(2)['ff']),
	('VW_MAX',GF_data_all.round(2)['VH_mps_Max']),
	('DW',GF_data_all.round(2)['VR_gr_framh']),
    # ('DW',dd.round(2)['dd']),
	('ISWR',AVD_rad_data.round(2)['SW_down']),
    # ('ISWR',SWIN.round(2)['SWIN']),
	# ('OSWR',AVD_rad_data.round(2)['SW_up']),
	# ('OSWR',SWOUT.round(2)['SWOUT']),
    ('ILWR',AVD_rad_data.round(2)['LW_down']),
    # ('ILWR',LWIN.round(2)['LWIN']),
	# ('OLWR',AVD_rad_data.round(2)['LW_up']),
    # ('OLWR',LWOUT.round(2)['LWOUT']),
    ('P', GF_data_all.round(2)['AT_mbar']),
    # ('HS', HS_data.round(2)['HS_P1']),
    ('PSUM',ERA5['RRmm'])])

# print(GF_SMET_data)
 
GF_SMET_data = GF_SMET_data.iloc[1:]
# pd.set_option('display.max_columns', 100)
# print(GF_data_all.head())
# print(AVD_rad_data_all.head())

# Save data from Gruvefjellet to file------------------------------------------------
# cdate =format(dt.datetime.now(),'%Y-%m-%d %H:%M') 
GF_SMET_file = open('/home/user/Documents/Programming/SnowPACK/Masterarbeit/input/GF_era5_ffmin4.smet', mode='w')
GF_SMET_file.writelines(['SMET 1.1 ASCII\n',
        '[HEADER]\n',
        'station_id \t\t\t = GF\n',
        'station_name \t\t = Gruvefjellet\n',
        'source \t\t\t\t = UNIS AWS Adventdalen (radiation data) and AWS Gruvefjellet (TA,RH, wind components, coordinates)\n',
        'latitude \t\t\t = 78.2004\n',
        'longitude \t\t\t = 15.624383\n',
        'easting \t\t\t = 514253\n',
        'northing \t\t\t = 8680811\n',
        'epsg \t\t\t\t = 32633\n'
        # Documentation: (epsg codes as 32600+zoneNumber in the northern hemisphere)
        # Zone:33N
        'altitude \t\t\t = 464\n',
        'nodata \t\t\t\t = -999\n',
        'fields \t\t\t\t = timestamp TA RH VW VW_MAX DW ISWR ILWR P PSUM\n' ,
        'units_offset \t\t = 0 273.15 0 0 0 0 0 0 0 0\n',
        'units_multiplier \t = 1 1 0.01 1 1 1 1 1 100 1\n' #mutliplication by 10^3 to get [mm] already applied to PSUM in 01_read_ERA5_data.py 
        'creation \t\t\t = '+ str(format(dt.datetime.now(),'%Y-%m-%d %H:%M')),
        '\n[DATA]\n'])

GF_SMET_data.to_csv(GF_SMET_file,sep = '\t', header = False, index = True, na_rep = '-999')

GF_SNO_file = open('/home/user/Documents/Programming/SnowPACK/Masterarbeit/input/GF_era5_ffmin4.sno', mode='w')
GF_SNO_file.writelines(['SMET 1.1 ASCII\n',
        '[HEADER]\n',
        'station_id \t\t\t\t = GF\n',
        'station_name \t\t\t = Gruvefjellet\n',
        'source \t\t\t\t\t = UNIS AWS Adventdalen (radiation data) and AWS Gruvefjellet (TA,RH, wind components, coordinates)\n',
        'latitude \t\t\t\t = 78.2004\n',
        'longitude \t\t\t\t = 15.624383\n',
        'easting \t\t\t\t = 514253\n',
        'northing \t\t\t\t = 8680811\n',
        'epsg \t\t\t\t\t = 32633\n'
        # Documentation: (epsg codes as 32600+zoneNumber in the northern hemisphere)
        #Zone:33N
        'altitude \t\t\t\t = 75\n',
        'nodata \t\t\t\t\t = -999\n',
        'ProfileDate \t\t\t = 2016-08-01T07:00:00\n',
        'HS_Last \t\t\t\t = 0.000000\n',
        'SlopeAngle \t\t\t\t = 0\n',
        'SlopeAzi \t\t\t\t = 0\n'
 ,       'nSoilLayerData \t\t\t = 0\n',
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



#Save data from Adventdalen to file ---------------------------------------------
# AVD_SMET_file = open('/home/user/Documents/Programming/Python/Masterarbeit/data/Adventdalen.smet', mode='w')
# AVD_SMET_file.writelines(['SMET 1.1 ASCII\n',
#         '[HEADER]\n',
#         'station_id \t\t\t = AVD\n',
#         'station_name \t\t\t = Adventdalen\n',
#         'source \t\t\t\t = This dataset includes data from the UNIS AWS in Adventdalen\n',
#         'latitude \t\t\t = 78.202778\n',
#         'longitude \t\t\t = 15.828056\n',
#         'altitude \t\t\t = 15\n',
#         'nodata \t\t\t\t = NAN\n',
#         'fields \t\t\t\t = timestamp TA RH VW VW_MAX DW ISWR OSWR ILWR OLWR PSUM\n',
#         'units_offset \t\t\t = 0 273.15 0 0 0 0 0 0 0 0\n',
#         '[DATA]\n'])

# Create dataframe with all necessary dataseries (Adventdalen)------------------
# AVD_SMET_data = pd.DataFrame.from_items([
# 	('TA',AVD_data_all['LT1_gr_C_Avg']), 
# 	('RH',AVD_data_all['LF1_prst_Avg']),
# 	('VW',AVD_data_all['VH1_10_min']),
# 	('VW_MAX',AVD_data_all['VH1_mps_Max']),
# 	('DW',AVD_data_all['VR1_gr_framh']),
# 	('ISWR',AVD_SW_down.round(3)),
# 	('OSWR',AVD_SW_up.round(3)),
# 	('ILWR',AVD_LW_down.round(3)),
# 	('OLWR',AVD_LW_up.round(3))])

# AVD_SMET_data = AVD_SMET_data.iloc[1:]

# AVD_SMET_data.to_csv(AVD_SMET_file,sep = '\t', header = False, index = True)
# print AVD_SMET_data