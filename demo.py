"""
demo.py
Spring 2022 PJW

Demonstrate the Pandas where() and fillna() methods, and
also show several methods for cleaning up messy data.
"""

import pandas as pd

#
#  Read the test data
#

raw = pd.read_csv('demo.csv')

print('\nOriginal data:')
print(raw)

#%%
#
#  Make names consistent in case and spacing
#

mod = raw.copy()

name = mod['name'].str.lower()
name_parts = name.str.split()
name_clean = name_parts.apply(' '.join)

mod['name'] = name_clean

print('\nAfter removing leading and trailing spaces from name:')
print(mod)

#%%
#
#  Now separate numbers and units that are mixed in the values column.
#
#  Uses two "regular expressions" (REs) to match classes of characters:
#
#     \d matches digits 0-9
#     \D matches anything that is NOT a digit
#     \s matches whitespace (spaces, tabs, newlines)
#
#     \D|\s matches a non-digit OR a space
#     \d|\s matches a digit OR a space
#
#  Regular expressions are VERY powerful but can be a little
#  tricky to use for more complex cases. For example, this would be
#  more involved if the numbers could be negative or have decimal
#  points.
#
#

values = mod['value']

#  Make two variables, one with the non-digits removed, leaving the
#  numbers, and one with the digits removed, leaving the units

value_part = values.str.replace(r'\D|\s','',regex=True)
unit_part  = values.str.replace(r'\d|\s','',regex=True)

#  Put the columns into the dataframe to show what happened

mod['value_part'] = value_part
mod['unit_part'] = unit_part

print('\nAfter splitting combined value entries:')
print( mod )

#%%
#
#  Combine the extracted units with the original unit column using
#  .where()
#

mod['comb_units'] = unit_part.where( unit_part!='' , mod['units'] )

print('\nAfter combining with original units:')
print( mod )

#%%
#
#  Now fill in any missing values in the units column. Here we'll assume
#  that the default unit is feet when nothing is specified.
#

mod['comb_units'] = mod['comb_units'].fillna('feet')

print('\nAfter filling missing units:')
print( mod )

#%%
#
#  Now make the units more consistent. Convert everything to lower case,
#  remove punctuation using another RE, and then replace some
#  abbreviations. The RE used in the replace step is \W:
#
#     \w matches word characters: letters, numbers, and underscores
#     \W matches anything other than word characters
#
#  \w isn't used here but is included for reference.
#

units = mod['comb_units']

units = units.str.lower()
units = units.str.replace(r'\W','',regex=True)
units = units.str.strip()

spellout = {'ft':'feet',
            'yds':'yards'}

units = units.replace(spellout)

mod['std_units'] = units

print('\nAfter standardizing units:')
print(mod)

#%%
#
#  Now build a consistent measurement column using where()
#

val = mod['value_part'].astype(int)

mod['feet'] = val.where( mod['std_units']=='feet', val*3 )

print('\nAdded column in feet:')
print(mod)

trim = mod[['name','feet']]

print('\nFinished data:')
print(trim)
