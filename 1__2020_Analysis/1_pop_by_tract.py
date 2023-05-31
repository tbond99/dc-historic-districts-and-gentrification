"""
pop_by_tract.py (Script 1/3)
Date updated: 5/11/2023

Imports DC population data by census tract from Census API.
"""

"""
Requires:
    - Census API key, which can be acquired here: https://api.census.gov/data/key_signup.html

Output:
    - "pop_by_tract_2020.csv"
"""

#%%
##  Set working directory to script directory "2020_Analysis"

##  Note: Be sure that the required input files are located in the "2020_Analysis"
##  folder as well.

import os

os.chdir(os.path.dirname(__file__))

#%%
#  Import modules
import requests

import pandas as pd

import numpy as np

#%%
##  API call

#  Variable dictionary
variables = {'B02001_001E':'pop_total', 'B02001_002E':'pop_white',
             'B25003_001E':'housing_total', 'B25003_002E':'housing_owned',
             'B25003_003E':'housing_rental'}

#  Variable list
var_list = variables.keys()

#  Variable string (comma-separated)
var_string = ",".join(var_list)

#  URL
api = 'https://api.census.gov/data/2020/acs/acs5'

#  Set geographic unit
for_clause = 'tract:*'

#  Select NY
in_clause = 'state:11 county:001'

key_value = 'f382fd0108eba2b32808ba82bcccc82861d0b53a'

#  API call
payload = {'get':var_string, 'for':for_clause, 'in':in_clause, 'key':key_value}

response = requests.get(api, payload)

if response.status_code == 200:
    print('\nAPI Request: Success\n')
else:
    print(f'\nRequest status code: {response.status_code}\n{response.text}\n')
    assert False
    
#%%
##  Convert JSON to Dataframe

#  List of rows
row_list = response.json()

#  Set column names
colnames = row_list[0]

#  Set data rows
datarows = row_list[1:]

#  Pandas dataframe
pop = pd.DataFrame(columns=colnames, data=datarows)

#%%
##  Prepare data

#  Replace missing data with NaN
pop = pop.replace(-666666666, np.nan)

#  Rename columns
pop = pop.rename(columns=variables)

#  GEOID column
pop['GEOID'] = pop['state'] + pop['county'] + pop['tract']

#  Set index to GEOID
pop = pop.set_index('GEOID')

#  Drop columns
keep_cols = variables.values()

pop = pop[keep_cols]

#%%
##  Write population by census tract to CSV
pop.to_csv('pop_by_tract_2020.csv')

print("\nDownloaded 'pop_by_tract_2020.csv'")
