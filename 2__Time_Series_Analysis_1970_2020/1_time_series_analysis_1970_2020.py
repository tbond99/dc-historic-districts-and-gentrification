"""
time_series_analysis_1970_2020.py (Script 1/2)
Date updated: 5/11/2023

Uses time series data from NHGIS to study historic districts
and racial displacement in D.C.

Note that time series data provides significantly more detail than the 2020 analysis,
because there are up to 5 observations for each census tract instead of one.
"""

"""
Requires:
    - "hist_districts.gpkg": Located in 2020 Analysis folder
    A geopackage of historic districts in D.C., with designation year
    and years since designation.
    
    - "tracts_dc.gpkg": Located in 2020 Analysis folder
    A geopackage of D.C. census tracts, converted to D.C.'s official coordinate
    system (Maryland State Plane NAD 83)
    
    - "nhgis0001_csv.zip": Download using the instructions in the main folder.
    "Download_Instructions_RacialDemographicsByCensusTract.mkd"
    A dataset of racial data by census tract from the decennial census. Covers
    years: 1970, 1980, 1990, 2000, 2010, 2020
    
Outputs:
    - "pop.csv": D.C. population by census tract from 1970 to 2020
    
    - "by_hist_district_1970_2020.csv": D.C. population by historic district (approximate) from
    1970 to 2020
    
"""

#%%
##  Set working directory to script directory "2020_Analysis"

##  Note: Be sure that the required input files are located in the "2020_Analysis"
##  folder as well.

import os

os.chdir(os.path.dirname(__file__))

#%%
##  Import modules
import pandas as pd

import geopandas as gpd

import zipfile


#%%
##  Load data
hist_districts = gpd.read_file('hist_districts.gpkg')


#%%
##  Load 2020 census tract shapefile
tracts = gpd.read_file('tracts_dc.gpkg')


#%%
##  Load Racial Demographics by Census Tract
archive = zipfile.ZipFile('nhgis0001_csv.zip')

print( archive.namelist() )

fh1 = archive.open('nhgis0001_csv/nhgis0001_ts_nominal_tract.csv')

#  Create dataframe, set variable types to string
#  (This will prevent FIPS codes from being read as integers,
#   which would remove leading zeroes)
pop = pd.read_csv(fh1, dtype=str)


#%%
##  Prepare data

#  Filter for D.C.
pop = pop.query("STATEFP == '11'")

print(f"Records by Year: {pop.value_counts('YEAR')}")

pop.value_counts('YEAR')

#  Set numeric variables to integers
cols=['B18AA','B18AB','B18AC','B18AD','B18AE']

pop[cols] = pop[cols].apply(pd.to_numeric, errors='coerce')

#  Change column names
new_names = {'B18AA':'pop_white', #Persons: White (single race)
             'B18AB':'pop_black', #Persons: Black or African American (single race)
             'B18AC':'pop_native',#Persons: American Indian and Alaska Native (single race)
             'B18AD':'pop_aapi_other', #Persons: Asian and Pacific Islander and Other Race (single race)
             'B18AE':'pop_two_races'}  #Persons: Two or More Races

pop = pop.rename(columns=new_names)

#  Fill NAs with zeros in pop_two_races
pop['pop_two_races'] = pop['pop_two_races'].fillna(0)

#  (Note: Racial demographic data does not include "Hispanic," which is confusingly
#   considered by the U.S. Census to be an ethnicity, not a race. However, the
#   proportion of Hispanic/Latino residents in D.C. is very low and not the focus
#   of this analysis)


#%%
##  Find total population and people of color

#  Total population
pop['total_pop'] = pop['pop_white'] + pop['pop_black'] + pop['pop_native'] + pop['pop_aapi_other'] + pop['pop_two_races']

#  Population, people of color
pop['pop_poc'] = pop['total_pop'] - pop['pop_white']


#%%
##  Create GEOID variable
pop['GEOID'] = pop['STATEFP'] + pop['COUNTYFP'] + pop['TRACTA']

#  Set index to GEOID
pop = pop.set_index('GEOID')

#  Drop columns
keep_cols = ['YEAR', 'total_pop', 'pop_poc', 'pop_white']

pop = pop[keep_cols]

##  Write to CSV
pop.to_csv('pop.csv')

print("\nDownloaded 'pop.csv'\n")


#%%
##  Separate pop by year
print(pop['YEAR'].value_counts())

df_names = ['pop_1970', 'pop_1980', 'pop_1990', 'pop_2000', 'pop_2010', 'pop_2020']

years = ['1970', '1980', '1990', '2000', '2010', '2020']

#  Empty dictionaries
pop_dic = {}
tracts_dic = {}
slices_dic = {}
area_share_dic = {}
realloc_dic = {}
by_hist_district_dic = {}

#  Empty dataframe
by_hist_district_1970_2020 = pd.DataFrame()

#  Dissolve geometry by GEOID and Historic District ID, respectively
tracts = tracts.dissolve('GEOID')

hist_districts = hist_districts.dissolve('hist_district_ID').reset_index()


#%%
##  Loop over data from 1990, 2000, 2010, and 2020; overlay tracts and historic districts;
##  then recombine into one dataframe.
##  (See Footnote 1)

for year in years:
    
    ################################################################################################
    #  Separate population data by year collected
    
    # Filter for year (1990, 2000, 2010, 2020)
    pop_dic[year] = pop.query(f"YEAR == '{year}'")
    
    # Drop year column
    pop_dic[year] = pop_dic[year].drop(columns='YEAR').reset_index()
    
    
    ################################################################################################
    #  Merge population and tract data
    tracts_dic[year] = tracts.merge(pop_dic[year], how='inner', on='GEOID', indicator=True) # Merge with tracts
    
    print(f"\nMerge indicator for {year}:\n{tracts_dic[year].value_counts('_merge')}\n")
    
    tracts_dic[year] = tracts_dic[year].drop(columns='_merge')
    
    
    ################################################################################################
    #  Allocate to historic districs
    slices_dic[year] = tracts_dic[year].overlay(hist_districts, how='intersection', keep_geom_type=True)
    
    #  Drop if historic district does not have "total years" data
    #  (This will be important for the time analysis later.)
    slices_dic[year] = slices_dic[year].dropna(subset='tot_years')
    
    #  Set index to GEOID, historic district ID
    slices_dic[year] = slices_dic[year].set_index(['GEOID','hist_district_ID','des_year'])
    
    #  Area of each slice
    slices_dic[year]['s_area'] = slices_dic[year].area
    
    #  Determine each slice's share of its block group
    area_share_dic[year] = slices_dic[year]['s_area'] / slices_dic[year]['tract_area']


    ################################################################################################
    #  Allocate population to historic districts
    
    #  New dataframe
    realloc_dic[year] = pd.DataFrame()
    
    #  Set population index to GEOID
    pop_dic[year] = pop_dic[year].set_index('GEOID')

    for v in pop_dic[year].columns:
        realloc_dic[year][v] = slices_dic[year][v].mul(area_share_dic[year], axis='index')

    #  Reset index
    realloc_dic[year] = realloc_dic[year].reset_index()
    
    
    ################################################################################################
    #  Group by historic district
    by_hist_district_dic[year] = realloc_dic[year].groupby(['hist_district_ID','des_year']).sum()
    
    
    ################################################################################################
    #  Calculate "Years since designation"
    
    #  Remove "Year" from the index (This column will be used to calculate years since designation)
    by_hist_district_dic[year] = by_hist_district_dic[year].reset_index().set_index('hist_district_ID')
    
    #  Column for year
    by_hist_district_dic[year]['year'] = year
    
    by_hist_district_dic[year]['year'] = by_hist_district_dic[year]['year'].astype(float)
    
    #  Years since designation
    by_hist_district_dic[year]['years_since_des'] = by_hist_district_dic[year]['year'] - by_hist_district_dic[year]['des_year']

    #  Drop columns
    by_hist_district_dic[year] = by_hist_district_dic[year].drop(columns=['des_year'])
    
    ################################################################################################
    #  Recombine data from 1990, 2000, 2010, 2020 (Append)
    by_hist_district_1970_2020 = by_hist_district_1970_2020.append(by_hist_district_dic[year])
    

#%%
##  New variables for total population, perc_poc, perc_white

#  Percent P.O.C.
by_hist_district_1970_2020['perc_poc'] = 100* (by_hist_district_1970_2020['total_pop'] - by_hist_district_1970_2020['pop_white']) / by_hist_district_1970_2020['total_pop']

#  Percent White
by_hist_district_1970_2020['perc_white'] = 100* by_hist_district_1970_2020['pop_white'] / by_hist_district_1970_2020['total_pop']


#%%
## Save as CSV
by_hist_district_1970_2020.to_csv('by_hist_district_1970_2020.csv')

print("\nDownloaded 'by_hist_district_1970_2020.csv'\n")


#%%
#  Footnotes
# 1. Note that census tracts from 1970-2020 are matched nominally (by their names)
#  with 2020 census tracts. Census tract boundaries change over time so this
#  analysis is not perfect. In particular, the older the data, the less accurate.
#  1970 and 1980 census tracts are likely the most different from 2020 census tracts,
#  and therefore least accurate.
#  In a future version of this analysis I would prefer to use crosswalks.