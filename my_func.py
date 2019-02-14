# Collection of functions
import numpy as np
import pandas as pd 
import datetime as dt


# Create .SMET file for SNOWPACK input
def create_SMET(name,fact,ID,lat,lon,east,north,height,data,pathin):
	SMET_file = open(pathin+str(name)+'_'+str(fact)+'.smet', mode='w')
	SMET_file.writelines(['SMET 1.1 ASCII\n',
		'[HEADER]\n',
		'station_id \t\t\t = '+str(ID)+'\n',
		'station_name \t\t = '+str(name)+'\n',
		'source \t\t\t\t = Raw data: Radiaton from AWS Adventdalen, MET-Data from AWS Gruvefjellet, adjust to pit location: T and ILWR\n',
		'latitude \t\t\t = '+str(lat)+'\n',
		'longitude \t\t\t = '+str(lon)+'\n',
		'easting \t\t\t = '+str(east)+'\n',
		'northing \t\t\t = '+str(north)+'\n',
		'epsg \t\t\t\t = 32633\n'
		# Documentation: (epsg codes as 32600+zoneNumber in the northern hemisphere)
		# Zone:33x
		'altitude \t\t\t = '+str(height)+'\n',
		'nodata \t\t\t\t = -999\n',
		'fields \t\t\t\t = timestamp TA RH VW VW_MAX DW ISWR ILWR PSUM\n' ,
		'units_offset \t\t = 0 0 0 0 0 0 0 0 0\n',
		'units_multiplier \t = 1 1 0.01 1 1 1 1 1 1\n' #mutliplication by 10^3 to get [mm] already applied to PSUM in 01_read_ERA5_data.py 
		'creation \t\t\t = '+ str(format(dt.datetime.now(),'%Y-%m-%d %H:%M')),
		'\n[DATA]\n'])

	data.to_csv(SMET_file,sep = '\t', header = False, index = True, na_rep = '-999')
	SMET_file.close()

# Create .SNO file for SNOWPACK input
def create_SNO(name,fact,ID,lat,lon,east,north,height,slope,azi, pathin):
	SNO_file = open(pathin+str(name)+'_'+str(fact)+'.sno', mode='w')
	SNO_file.writelines(['SMET 1.1 ASCII\n',
		'[HEADER]\n',
		'station_id \t\t\t = '+str(ID)+'\n',
		'station_name \t\t = '+str(name)+'\n',
		'source \t\t\t\t = Raw data: Radiaton from AWS Adventdalen, MET-Data from AWS Gruvefjellet, adjust to pit location: T and ILWR\n',
		'latitude \t\t\t = '+str(lat)+'\n',
		'longitude \t\t\t = '+str(lon)+'\n',
		'easting \t\t\t = '+str(east)+'\n',
		'northing \t\t\t = '+str(north)+'\n',
		'epsg \t\t\t\t = 32633\n'
		# Documentation: (epsg codes as 32600+zoneNumber in the northern hemisphere)
		#Zone:33x
		'altitude \t\t\t = '+str(height)+'\n',
		'nodata \t\t\t\t\t = -999\n',
		'ProfileDate \t\t\t = 2016-08-01T06:00:00\n',
		'HS_Last \t\t\t\t = 0.000000\n',
		'SlopeAngle \t\t\t\t = '+str(slope)+'\n',
		'SlopeAzi \t\t\t\t = '+str(azi)+'\n',
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
	SNO_file.close()

# Create .INI file for SNOWPACK input
def create_INI(name,fact,pathini,pathin,pathout):
	INI_file = open(pathini+
	name+'_'+fact+'.ini', mode = 'w')	
	INI_file.writelines(['[GENERAL]\n',
	'BUFF_CHUNK_SIZE	=	370\n',
	'BUFF_BEFORE	=	1.5\n\n',
	'[INPUT]\n',
	'COORDSYS	=	UTM\n',
	'COORDPARAM	=	33x\n',
	'TIME_ZONE	=	1\n',
	'METEO	=	SMET\n',
	'METEOPATH	=	'+pathin+'\n',
	'STATION1	=	'+str(name)+'_'+str(fact)+'.smet\n',
	'ISWR_IS_NET	=	FALSE\n',
	'SNOWPATH	=	'+pathin+'\n',
	'SNOW	=	SMET\n',
	'SNOWFILE1	=	'+str(name)+'_'+str(fact)+'.sno\n',

	'[OUTPUT]\n',
	'COORDSYS	=	UTM\n',
	'COORDPARAM	=	33X\n',
	'TIME_ZONE	=	1\n',
	'METEOPATH	=	'+pathout+'\n',
	'EXPERIMENT	=	'+str(fact)+'\n',
	'SNOW	=	SMET\n',
	'SNOWPATH	=	'+pathout+'\n',
	'BACKUP_DAYS_BETWEEN	=	365\n',
	'FIRST_BACKUP	=	400\n',
	'PROF_WRITE	=	TRUE\n',
	'PROFILE_FORMAT	=	PRO\n',
	'PROF_START	=	0\n',
	'PROF_DAYS_BETWEEN	=	0.042\n',
	'HARDNESS_IN_NEWTON	=	FALSE\n',
	'CLASSIFY_PROFILE	=	FALSE\n',
	'TS_WRITE	=	TRUE\n',
	'TS_START	=	0.0\n',
	'TS_DAYS_BETWEEN	=	0.041666\n',
	'AVGSUM_TIME_SERIES	=	TRUE\n',
	'CUMSUM_MASS	=	FALSE\n',
	'PRECIP_RATES	=	TRUE\n',
	'OUT_CANOPY	=	FALSE\n',
	'OUT_HAZ	=	TRUE\n',
	'OUT_SOILEB	=	FALSE\n',
	'OUT_HEAT	=	TRUE\n',
	'OUT_T	=	TRUE\n',
	'OUT_LW	=	TRUE\n',
	'OUT_SW	=	TRUE\n',
	'OUT_MASS	=	TRUE\n',
	'OUT_METEO	=	TRUE\n',
	'OUT_STAB	=	TRUE\n\n',

	'[SNOWPACK]\n',
	'CALCULATION_STEP_LENGTH	=	15\n',
	'ROUGHNESS_LENGTH	=	0.002\n',
	'HEIGHT_OF_METEO_VALUES	=	3\n',
	'HEIGHT_OF_WIND_VALUE	=	3\n',
	'ENFORCE_MEASURED_SNOW_HEIGHTS	=	FALSE\n',
	'SW_MODE	=	INCOMING\n',
	'ATMOSPHERIC_STABILITY	=	NEUTRAL_MO\n',
	'CANOPY	=	FALSE\n',
	'MEAS_TSS	=	FALSE\n',
	'CHANGE_BC	=	FALSE\n',
	'SNP_SOIL	=	FALSE\n\n',

	'[SNOWPACKADVANCED]\n',
	'ASSUME_RESPONSIBILITY	=	AGREE\n',
	'VARIANT	=	DEFAULT\n',
	'SNOW_EROSION	=	FALSE\n',
	'WIND_SCALING_FACTOR	=	1.0\n',
	'NUMBER_SLOPES	=	1\n',
	'PERP_TO_SLOPE	=	FALSE\n',
	'THRESH_RAIN	=	1.2\n',
	'FORCE_RH_WATER	=	TRUE\n',
	'THRESH_RH	=	0.5\n',
	'THRESH_DTEMP_AIR_SNOW	=	3.0\n',
	'HOAR_THRESH_TA	=	1.2\n',
	'HOAR_THRESH_RH	=	0.97\n',
	'HOAR_THRESH_VW	=	3.5\n',
	'HOAR_DENSITY_BURIED	=	125.0\n',
	'HOAR_MIN_SIZE_BURIED	=	2.0\n',
	'HOAR_DENSITY_SURF	=	100.0\n',
	'MIN_DEPTH_SUBSURF	=	0.07\n',
	'T_CRAZY_MIN	=	210.0\n',
	'T_CRAZY_MAX	=	340.0\n',
	'METAMORPHISM_MODEL	=	DEFAULT\n',
	'NEW_SNOW_GRAIN_SIZE	=	0.3\n',
	'STRENGTH_MODEL	=	DEFAULT\n',
	'VISCOSITY_MODEL	=	DEFAULT\n',
	'SALTATION_MODEL	=	SORENSEN\n',
	'WATERTRANSPORTMODEL_SNOW	=	BUCKET\n',
	'WATERTRANSPORTMODEL_SOIL	=	BUCKET\n',
	'SW_ABSORPTION_SCHEME	=	MULTI_BAND\n',
	'HARDNESS_PARAMETERIZATION	=	MONTI\n',
	'DETECT_GRASS	=	FALSE\n',
	'PLASTIC	=	FALSE\n',
	'JAM	=	FALSE\n',
	'WATER_LAYER	=	FALSE\n',
	'HEIGHT_NEW_ELEM	=	0.02\n',
	'MINIMUM_L_ELEMENT	=	0.0025\n',
	'COMBINE_ELEMENTS	=	TRUE\n',
	'ADVECTIVE_HEAT	=	FALSE\n\n',

	'[INTERPOLATIONS1D]\n',
	'WINDOW_SIZE	=	43200\n'
	])
	INI_file.close()
	return name+'_'+fact+'.ini'



# CALCULATIONS: 

# Calculate moistadiabatic temperature change due to height difference
def calc_T_moistadiabat(T,dH):  # T is a temperature in [K] or [degC], dH is a height difference in [m]
	T = np.array(T) 			# convert input T to numpy array
	T += 0.0065 * dH			# Add 0.0065[K]/[m]
	return T 					# Output T

# Calculate incoming longwave radiation based on temperature changes
def calc_ILWR(T,eps): 			# T is a temperature in [K], eps is the emissivity of the sky - must be known
	T = np.array(T)				# convert input T to numpy array
	eps = np.array(eps)			# convert input eps to numpy array
	sigma = 5.67*10**(-8) 		# [Wm^(-2)K^(-4)] Stefan-Boltzmann constant
	ILWR = sigma*eps*T**4		# Calculate incoming longwave radiation
	return ILWR 				# Output ILWR

# Calculate emissivity of the sky from incoming longwave radiation and T series
def calc_eps(T, ILWR):			# T is a temperature in [K], ILWR is the incoming longwave radiation in [Wm^(-2)]
	T = np.array(T)				# convert input T to numpy array
	ILWR = np.array(ILWR)		# convert input ILWR to numpy array
	sigma = 5.67*10**(-8) 		# [Wm^(-2)K^(-4)] Stefan-Boltzmann constant
	eps = ILWR/(sigma*T**4) 	# Calculate eps from known T and ILWR
	return eps 					# Output eps

# # Calculate the saturation water vapor pressure at given temperature

# def calc_e_s(T)					# T is a temperature series given in [K]
# 	T = np.array(T)				# convert input T to numpy array
# 	Lv = 2.5*10**6 				# [Jkg**(-1)] Latent heat of vaporisation
# 	Ls = 2.8*10**6 				# [Jkg**(-1)] Latent heat of sublimation
# 	Rv = 462 					# [J(kgK)**-1] individual gas constant for water vapor
# 	T0 = 273.15 				# [K] reference Temperature
# 	e_s = 611* exp((Lv/Rv*((1/T0)-(1/(T))))) # Calculate saturation water vapor pressure


# PLOTS:

