#! /bin/python3
#  Spring 2020 (PJW)
#
#  To run this please download demo.csv from the class Google 
#  drive for this exercise.
#

import pandas as pd

#
#  Show all components of multindexes
#

pd.set_option('display.multi_sparse',False)
#
#  Read energy data from EIA
#

energy = pd.read_csv('demo.csv')
print(energy)

#%%

#
#  Set the index columns
#

energy.set_index(['State','Year','Source'],inplace=True)

print('\nDataframe:\n',energy)
print('\nIndex:\n',energy.index)
print('\nColumns:\n',energy.columns)

#%%

#
#  Unstack the last index column, Source
#

wide = energy.unstack()

print('\nDataframe:\n',wide)
print('\nIndex:\n',wide.index)
print('\nColumns:\n',wide.columns)

#%%

#
#  Pick out the Gbtu columns and compute total production
#

gbtu = wide['Gbtu'].copy()

gbtu['total'] = gbtu['wind'] + gbtu['solar']

print(gbtu)
print(gbtu.index)
print(gbtu.columns)
