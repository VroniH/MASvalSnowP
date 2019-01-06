import os
import fnmatch
import pandas as pd 
import datetime as dt

#Create dataframe to write whole RR timeseries

datelist_LFH_RR = pd.date_range(start='2016-08-01 06:00',
	end='2017-04-30 18:00', periods=None, freq='12H',
	normalize=False, name='DateTime', closed=None)
datelist_AVD_RR = pd.date_range(start='2016-11-01 06:00',
	end='2017-04-30 18:00', periods=None, freq='12H',
	normalize=False, name='DateTime', closed=None)
datelist_LFH_T = pd.date_range(start='2016-08-01 00:00',
	end='2017-04-30 18:00', periods=None, freq='6H',
	normalize=False, name='DateTime', closed=None)
print(datelist_LFH_T)
datelist_AVD_T = pd.date_range(start='2016-11-01 00:00',
	end='2017-04-30 18:00', periods=None, freq='6H',
	normalize=False, name='DateTime', closed=None)

LFH_RR_ts = pd.DataFrame(index=datelist_LFH_RR, columns=['RR','ff'],
	dtype=None, copy=False)
AVD_RR_ts = pd.DataFrame(index=datelist_AVD_RR, columns=['RR','ff'],
	dtype=None, copy=False)
LFH_T_ts = pd.Series(index=datelist_LFH_T, name='T',
	dtype=None, copy=False)
AVD_T_ts = pd.Series(index=datelist_AVD_T, name='T',
	dtype=None, copy=False)
print(AVD_T_ts.index.date)

# Read available data files in directory according to given pattern
lof = os.listdir(
'/home/user/Documents/Programming/Python/Masterarbeit/raw_data') #list of files in given directory
filenames = []

for names in lof:
	 if fnmatch.fnmatch(names, '*TA_N_RR*'):		#match names in lof to given pattern
		  filenames.append(names)					#append matched names to list				
		  filenames.sort()							#sort list
# print(filenames)
#Create files with timeseries of precipitation, one file per location (Lufthaven/Adventdalen)
#Column names for read_csv
col_names = [
'Date','TA01','fTA01','TA07','fTA07','TA13',
'fTA13','TA19','fTA19','TAM','fTAM','TAX',
'fTAX','TAN','fTAN','NN01','fNN01','NN07',
'fNN07','NN13','fNN13','NN19','fNN19','RR01',
'fRR01','RR07','fRR07','RR13','fRR13','RR19',
'fRR19','RR','fRR']

#read all available files
# for i in range(0, 11):
for name in filenames:
	dataset = name
	read_data = pd.read_csv(
		'/home/user/Documents/Programming/Python/Masterarbeit/raw_data/' + dataset,
		skiprows = range(0,33),
		header = None,  
		decimal = '.', 
		na_values = ['-999','x'],
		sep = '\t',
		names = col_names,
		# engine = 'python', 
		index_col = False)
	# print read_data
# note: The number after the element code (e.g. TA 07) indicates
#		the observation time in Norwegian Mean Time (NMT=UTC+1).

	cont = True
	for i in range(0,32):
		if read_data.loc[i,'Date'] != str(i+1) and cont==True:
			precip_data = pd.DataFrame.from_dict({
				"Date":range(1,i+1),
				'RR06Z':read_data.loc[0:i-1,'RR07'],
				'RR18Z':read_data.loc[0:i-1,'RR19'],
				'RR':read_data.loc[0:i-1,'RR'],
				'ff06Z':read_data.loc[0:i-1,'fRR07'],
				'ff18Z':read_data.loc[0:i-1,'fRR19'],
				'ff':read_data.loc[0:i-1,'fRR']})
			temp_data = pd.DataFrame.from_dict({
				'T00Z':read_data.loc[0:i-1,'TA01'],
				'T06Z':read_data.loc[0:i-1,'TA07'],
				'T12Z':read_data.loc[0:i-1,'TA13'],
				'T18Z':read_data.loc[0:i-1,'TA19']})
			cont = False
			final_day = i
	# Replace '.', for 'no precipitation at all' with '0.0'. 
	# In the dataset '0.0' or '0' is used for fog or <0.1mm,
	# by replacing '.' with '0.0' we set no precipitation and 
	# traces equal, what anyways will not influence later 
	# calculations
	precip_data.replace(to_replace = '.', value = '0.0', 
			inplace = True)	


	month = ['01','02','03','04','08','09','10','11','12']
	year = ['2016','2017']

	for j in year:
		for k in month:
			strjk = '*'+k+j+'*'
			if fnmatch.fnmatch(name, strjk):
				# print(j,k,name,final_day)
				start_date = dt.date(int(j),int(k),1)
				end_date = dt.date(int(j),int(k),final_day)
				index = pd.date_range(start=start_date, end=end_date, 
				freq='D', tz='UTC')
				precip_data['Date'] = index.date
				temp_data['Date'] = index.date

				new_name = ''
				if fnmatch.fnmatch(name,'*AVD*'):
					new_name_RR = j + k + '_AVD_RR'
					new_name_T = j + k + '_AVD_T'
				if fnmatch.fnmatch(name,'*LFH*'):
					new_name_RR = j + k + '_LFH_RR'
					new_name_T = j + k + '_LFH_T'



				# create a timeline of RR measurements at LFH
				for l in range(0,len(index)):
					for m in range(0,len(LFH_RR_ts),2):
						if fnmatch.fnmatch(name,'*LFH*') and index.date[l] == LFH_RR_ts.index.date[m]:
							# print(index.date[l], LFH_RR_ts.index[m],l,m,name)
							LFH_RR_ts.RR[m] = float(precip_data.RR06Z[l])
							LFH_RR_ts.RR[m+1] = float(precip_data.RR18Z[l])
							LFH_RR_ts.ff[m] = float(precip_data.ff06Z[l])
							LFH_RR_ts.ff[m+1] = float(precip_data.ff18Z[l])

				for l in range(0,len(index)):
					for m in range(0,len(LFH_T_ts),4):
						if fnmatch.fnmatch(name,'*LFH*') and index.date[l] == LFH_T_ts.index.date[m]:
							LFH_T_ts.T[m] = float(temp_data.T00Z[l])
							LFH_T_ts.T[m+1] = float(temp_data.T06Z[l])
							LFH_T_ts.T[m+2] = float(temp_data.T12Z[l])
							LFH_T_ts.T[m+3] = float(temp_data.T18Z[l])

				for l in range(0,len(index)):
					for m in range(0,len(AVD_RR_ts),2):
						if fnmatch.fnmatch(name,'*AVD*') and index.date[l] == AVD_RR_ts.index.date[m]:
							# print(index.date[l], AVD_RR_ts.index[m],l,m,name)
							AVD_RR_ts.RR[m] = float(precip_data.RR06Z[l])
							AVD_RR_ts.RR[m+1] = float(precip_data.RR18Z[l])
							AVD_RR_ts.ff[m] = float(precip_data.ff06Z[l])
							AVD_RR_ts.ff[m+1] = float(precip_data.ff18Z[l])

				for l in range(0,len(index)):
					for m in range(0,len(AVD_T_ts),4):
						if fnmatch.fnmatch(name,'*AVD*') and index.date[l] == AVD_T_ts.index.date[m]:
							AVD_T_ts.T[m] = float(temp_data.T00Z[l])
							AVD_T_ts.T[m+1] = float(temp_data.T06Z[l])
							AVD_T_ts.T[m+2] = float(temp_data.T12Z[l])
							AVD_T_ts.T[m+3] = float(temp_data.T18Z[l])



	# print precip_data
# write data to monthly file
	new_file_path = '/home/user/Documents/Programming/Python/Masterarbeit/data/'
	precip_data_path = new_file_path + new_name_RR + '.txt'
	temp_data_path = new_file_path + new_name_T + '.txt'
	precip_data.to_csv(precip_data_path, sep = ',', na_rep = 'NaN', index = False) 
	temp_data.to_csv(temp_data_path, sep = ',', na_rep = 'NaN', index = False) 	

	LFH_RR_ts.to_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/LFH_RR_ts.txt',
		sep=",", na_rep='NaN', columns=None, header=True, index=True, index_label=None,
		mode='w', encoding=None, compression=None, quoting=None, quotechar='"',
		line_terminator='\n', chunksize=None, tupleize_cols=None,
		date_format=None, doublequote=True, escapechar=None, decimal='.')
	
	LFH_T_ts.to_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/LFH_T_ts.txt',
		sep=",", na_rep='NaN', header=True, index=True, index_label=None,
		mode='w', decimal='.')

	AVD_RR_ts.to_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/AVD_RR_ts.txt',
		sep=",", na_rep='NaN', columns=None, header=True, index=True, index_label=None,
		mode='w', encoding=None, compression=None, quoting=None, quotechar='"',
		line_terminator='\n', chunksize=None, tupleize_cols=None,
		date_format=None, doublequote=True, escapechar=None, decimal='.')

	AVD_T_ts.to_csv('/home/user/Documents/Programming/Python/Masterarbeit/data/AVD_T_ts.txt',
		sep=",", na_rep='NaN', header=True, index=True, index_label=None,
		mode='w', decimal='.')