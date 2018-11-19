"""
====================Pit 1 Plot========================
"""
# x... precipitaton factor applied to model input precipitation
# y... output.. difference between manual and modelled HS in [cm] for the according precipitation factor


from matplotlib import pyplot as plt
import pandas as pd
import fnmatch
import numpy as np
from mpl_toolkits.basemap import Basemap
#Pit1:res = optimize.brute(diffHS, ((0.1,2.5),), args=(), Ns=20, full_output=True, finish=optimize.fmin, disp=True)
x = [0.1       , 0.22631579, 0.35263158, 0.47894737, 0.60526316,
       0.73157895, 0.85789474, 0.98421053, 1.11052632, 1.23684211,
       1.36315789, 1.48947368, 1.61578947, 1.74210526, 1.86842105,
       1.99473684, 2.12105263, 2.24736842, 2.37368421, 2.5       ]
y = [301.67, 274.24, 236.88, 204.42, 175.4 , 148.51, 120.8 ,  96.54,
        72.38,  47.5 ,  22.05,   0.57,  22.31,  48.14,  68.89,  93.84,
       114.85, 135.02, 159.98, 182.62]
plt.plot(x,y)
plt.show()


# #Pit1:res = optimize.brute(diffHS, ((0.1,2.5),), args=(), Ns=20, full_output=True, finish=optimize.minimize, disp=True)
# x = [0.1       , 0.22631579, 0.35263158, 0.47894737, 0.60526316,
#        0.73157895, 0.85789474, 0.98421053, 1.11052632, 1.23684211,
#        1.36315789, 1.48947368, 1.61578947, 1.74210526, 1.86842105,
#        1.99473684, 2.12105263, 2.24736842, 2.37368421, 2.5       ]
# y= [301.67, 274.24, 236.88, 204.42, 175.4 , 148.51, 120.8 ,  96.54,
#         72.38,  47.5 ,  22.05,   0.57,  22.31,  48.14,  68.89,  93.84,
#        114.85, 135.02, 159.98, 182.62]
# plt.plot(x,y)
# plt.show()

# #Pit1: res = optimize.brute(diffHS, ((0.1,2.5),), args=(), Ns=30, full_output=True, finish=optimize.fmin, disp=True)

# x = [0.1       , 0.18275862, 0.26551724, 0.34827586, 0.43103448,
#        0.5137931 , 0.59655172, 0.67931034, 0.76206897, 0.84482759,
#        0.92758621, 1.01034483, 1.09310345, 1.17586207, 1.25862069,
#        1.34137931, 1.42413793, 1.50689655, 1.58965517, 1.67241379,
#        1.75517241, 1.83793103, 1.92068966, 2.00344828, 2.0862069 ,
#        2.16896552, 2.25172414, 2.33448276, 2.41724138, 2.5       ]
# y = [301.44, 268.44, 236.78, 212.41, 192.59, 170.37, 151.89, 132.6 ,
#        116.44,  97.96,  78.82,  61.72,  45.77,  28.63,  12.22,   4.24,
#         20.15,  36.94,  51.33,  68.98,  88.37, 104.42, 120.35, 137.15,
#        154.99, 172.9 , 189.68, 209.85, 227.94, 244.31]
# plt.plot(x,y)
# plt.show()


# #Pit2: res = optimize.brute(diffHS, ((0.1,2.5),), args=(), Ns=20,full_output=True, finish=optimize.minimize, disp=True) 
# x = [0.1       , 0.22631579, 0.35263158, 0.47894737, 0.60526316,
#        0.73157895, 0.85789474, 0.98421053, 1.11052632, 1.23684211,
#        1.36315789, 1.48947368, 1.61578947, 1.74210526, 1.86842105,
#        1.99473684, 2.12105263, 2.24736842, 2.37368421, 2.5       ]
# y=[ 34.93,   9.19,  23.01,  52.87,  84.04, 109.56, 137.62, 161.07,
#        186.58, 212.19, 234.81, 257.56, 279.91, 303.25, 325.06, 347.21,
#        369.56, 391.84, 412.68, 437.13]
# plt.plot(x,y)
# plt.show()

# #Pit02: res = optimize.brute(diffHS, ((0.1,2.5),), args=(), Ns=20,full_output=True, finish=optimize.fmin, disp=True)
# x = [0.1       , 0.22631579, 0.35263158, 0.47894737, 0.60526316,
#        0.73157895, 0.85789474, 0.98421053, 1.11052632, 1.23684211,
#        1.36315789, 1.48947368, 1.61578947, 1.74210526, 1.86842105,
#        1.99473684, 2.12105263, 2.24736842, 2.37368421, 2.5       ]
# y = [ 34.93,   9.19,  23.01,  52.87,  84.04, 109.56, 137.62, 161.07,
#        186.58, 212.19, 234.81, 257.56, 279.91, 303.25, 325.06, 347.21,
#        369.56, 391.84, 412.68, 437.13]
# plt.plot(x,y)
# plt.show()

# # Pit02: res = optimize.brute(diffHS, ((0.1,2.5),), args=(), Ns=30,full_output=True, finish=optimize.fmin, disp=True)

# x = [0.1       , 0.18275862, 0.26551724, 0.34827586, 0.43103448,
#        0.5137931 , 0.59655172, 0.67931034, 0.76206897, 0.84482759,
#        0.92758621, 1.01034483, 1.09310345, 1.17586207, 1.25862069,
#        1.34137931, 1.42413793, 1.50689655, 1.58965517, 1.67241379,
#        1.75517241, 1.83793103, 1.92068966, 2.00344828, 2.0862069 ,
#        2.16896552, 2.25172414, 2.33448276, 2.41724138, 2.5       ]
# y = [ 34.93,  15.36,   1.91,  20.96,  42.17,  60.81,  82.04,  98.57,
#        117.96, 134.92, 152.13, 165.65, 183.48, 199.27, 213.82, 229.96,
#        245.61, 261.55, 275.72, 291.24, 305.79, 320.27, 334.44, 348.96,
#        362.92, 376.87, 393.04, 407.79, 420.44, 437.13]
# plt.plot(x,y)
# plt.show()

dat = pd.read_csv('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/opt_output/res1.txt', sep = ',',index_col = 0)
# dat = dat.assign(fRRx = np.nan)
for i in range(0,len(dat.fRR)):
	if fnmatch.fnmatch(dat.fRR[i],'*[*'):
		dat.fRR[i] = dat.fRR[i].replace('[','')
	if fnmatch.fnmatch(dat.fRR[i],'*]*'):
		dat.fRR[i] = dat.fRR[i].replace(']','')
plt.plot(dat.index, dat.diffHS)
plt.title('Pit01')
plt.xlabel('Num of iteration')
plt.ylabel('Difference HS')
plt.show()
plt.plot(dat.fRR,dat.diffHS)
plt.title('Pit01')
plt.xlabel('fRR')
plt.ylabel('Difference HS')
plt.show()
plt.plot(dat.fRR, dat.index)
plt.title('Pit01')
plt.xlabel('fRR')
plt.ylabel('Num of iteration')
plt.show()

dat = pd.read_csv('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/opt_output/res2.txt', sep = ',',index_col = 0)
# dat = dat.assign(fRRx = np.nan)
for i in range(0,len(dat.fRR)):
	if fnmatch.fnmatch(dat.fRR[i],'*[*'):
		dat.fRR[i] = dat.fRR[i].replace('[','')
	if fnmatch.fnmatch(dat.fRR[i],'*]*'):
		dat.fRR[i] = dat.fRR[i].replace(']','')
plt.plot(dat.index, dat.diffHS)
plt.title('Pit02')
plt.xlabel('Num of iteration')
plt.ylabel('Difference HS')
plt.show()
plt.plot(dat.fRR,dat.diffHS)
plt.title('Pit02')
plt.xlabel('fRR')
plt.ylabel('Difference HS')
plt.show()
plt.plot(dat.fRR, dat.index)
plt.title('Pit02')
plt.xlabel('fRR')
plt.ylabel('Num of iteration')
plt.show()

# dat = pd.read_csv('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/opt_output/res3.txt', sep = ',',index_col = 0)
# # dat = dat.assign(fRRx = np.nan)
# for i in range(0,len(dat.fRR)):
# 	if fnmatch.fnmatch(dat.fRR[i],'*[*'):
# 		dat.fRR[i] = dat.fRR[i].replace('[','')
# 	if fnmatch.fnmatch(dat.fRR[i],'*]*'):
# 		dat.fRR[i] = dat.fRR[i].replace(']','')
# plt.plot(dat.index, dat.diffHS)
# plt.title('Pit03')
# plt.xlabel('Num of iteration')
# plt.ylabel('Difference HS')
# plt.show()
# plt.plot(dat.fRR,dat.diffHS)
# plt.title('Pit03')
# plt.xlabel('fRR')
# plt.ylabel('Difference HS')
# plt.show()
# plt.plot(dat.fRR, dat.index)
# plt.title('Pit03')
# plt.xlabel('fRR')
# plt.ylabel('Num of iteration')
# plt.show()

# dat = pd.read_csv('/home/user/Desktop/Masterarbeit/SnowPACK/Masterarbeit/opt_output/res4.txt', sep = ',',index_col = 0)
# # dat = dat.assign(fRRx = np.nan)
# for i in range(0,len(dat.fRR)):
# 	if fnmatch.fnmatch(dat.fRR[i],'*[*'):
# 		dat.fRR[i] = dat.fRR[i].replace('[','')
# 	if fnmatch.fnmatch(dat.fRR[i],'*]*'):
# 		dat.fRR[i] = dat.fRR[i].replace(']','')
# plt.plot(dat.index, dat.diffHS)
# plt.title('Pit04')
# plt.xlabel('Num of iteration')
# plt.ylabel('Difference HS')
# plt.show()
# plt.plot(dat.fRR,dat.diffHS)
# plt.title('Pit04')
# plt.xlabel('fRR')
# plt.ylabel('Difference HS')
# plt.show()
# plt.plot(dat.fRR, dat.index)
# plt.title('Pit04')
# plt.xlabel('fRR')
# plt.ylabel('Num of iteration')
# plt.show()