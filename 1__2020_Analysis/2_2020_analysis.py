"""
2020_analysis.py (Script 2/3)
Date updated: 5/11/2023

Identify population in historic districts, create charts and maps.
"""

"""
Requires:
    - "Historic_Districts.zip" - Shapefile of D.C. historic districts downloaded
    from D.C. Open Data: https://opendata.dc.gov/datasets/a443bfb6d078439e9e1941773879c7f6/about
    
    - "tl_2020_11_tract.zip" - The Tiger/LINE file for D.C., which can be downloaded here:
        https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2020&layergroup=Census+Tracts
        Select 2020, then Census Tracts, then District of Columbia
    
    - "pop_by_tract_2020.csv" - Located in the GitHub folder for this analysis.
    
    - "Historic_District_dates.csv" - Located in the GitHub folder for this analysis.
    (I compiled this CSV of historic district designation dates using information
     from DC Open Data. There is a bug in the download which means the "Designation Dates"
     column is left out.)
    
Output:
    - "hist_districts.gpkg": A geopackage of Historic Districts with geographic coordinates,
    designation date, and years since designation.
    
    - "tracts.gpkg": A geopackage of D.C. census tracts, converted to D.C.'s official coordinate
    system (Maryland State Plane NAD 83)
    
    - "by_hist_districts.csv": A listing of D.C. historic districts with demographic data.

    - "by_hist_status.csv": Demographics in D.C. historic districts and non-historic districts,
    compared side-by-side.
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

import numpy as np

import datetime

#  Today's date
today = datetime.datetime.now()

#%%
##  Read historic district data from DC Open Data

#  Parcels data
hist_districts = gpd.read_file('Historic_Districts.zip')

#  Set index, rename columns
hist_districts = hist_districts.rename(columns={'UNIQUEID':'hist_district_ID',
                                                'DESIGNATIO':'designation_date',
                                                'EDIT_DATE':'edit_date'})

hist_districts = hist_districts.set_index('hist_district_ID')

#  Fill NAs
hist_districts = hist_districts.fillna(np.nan)

#  Reproject to Maryland State Plane NAD 83
#  (See here: https://octo.dc.gov/page/coordinate-system-standards)
hist_districts = hist_districts.to_crs(epsg=2248)

#%%
##  Read in designation dates
## (These are the dates when historic districts were originally established.
## See Footnote 1)

designation_dates = pd.read_csv('Historic_District_dates.csv')

#  Adjust columns
designation_dates = designation_dates.rename(columns={'designation_date':'year',
                                                      'UNIQUEID':'hist_district_ID'})

#  Set index to historic district ID
designation_dates = designation_dates.set_index('hist_district_ID')

#  Drop unneeded columns
designation_dates = designation_dates.drop(columns='NAME')


#%%
## Add designation year to historic district geographic data

hist_districts['des_year'] = designation_dates['year']

#  Find years since designation
hist_districts['tot_years'] = (today.year - designation_dates['year']).astype(int, errors='ignore')

#  Reset index
hist_districts = hist_districts.reset_index(drop=False)

#  Save geopackage of D.C. historic districts, which now includes designation date
#  and years since designation.
hist_districts.to_file("hist_districts.gpkg")


#%%
##  Read in population data
pop = pd.read_csv('pop_by_tract_2020.csv', dtype={'GEOID':str}).set_index('GEOID')

#  Population, people of color (POC)
pop['pop_poc'] = pop['pop_total'] - pop['pop_white']


#%%
##  Read in census tract shapefile

#  Block group shapefile
tracts = gpd.read_file('tl_2020_11_tract.zip')

# Drop columns
keep_cols = ['GEOID', 'geometry']
tracts = tracts[keep_cols]

#  Change coordinate system to match the historic districts
# (Maryland State Plane NAD 83)
tracts = tracts.to_crs(hist_districts.crs)

#  Calculate area of each block group
tracts['tract_area'] = tracts.area

#  Save as shapefile
tracts.to_file('tracts_dc.gpkg')


#%%
##  Merge census tracts with population data
tracts = tracts.merge(pop, on='GEOID', validate='1:1', indicator=True)

print(f"\nCensus Tracts & Population Data merged.\n\nMerge indicator:\n{tracts['_merge'].value_counts()}\n")


#%%
##  Intersect historic districts with census tracts, to find the demographics of
##  each historic district.

slices = tracts.overlay(hist_districts, how='union', keep_geom_type=True)

#  Filter out rows with empty 'GEOID
slices = slices.dropna(subset='GEOID')

#  Replace hist_district NA with NA value
slices['hist_district_ID'] = slices['hist_district_ID'].fillna('NA')

#  Set index to GEOID, historic district ID
slices = slices.set_index(['GEOID','hist_district_ID','tot_years'])

#  Area of each slice
slices['s_area'] = slices.area

#  Determine each slice's share of its block group
area_share = slices['s_area'] / slices['tract_area']

#  Allocate population to historic districts
realloc = pd.DataFrame()

for v in pop.columns:
    realloc[v] = slices[v].mul(area_share, axis='index')

#  Reset index
realloc = realloc.reset_index()

print(f"\nRealloc columns:\n{realloc.columns}\n")

#  Fill empty cells
values = {'hist_district_ID':'NA', #Fill str with 'NA'
          'tot_years':-666666}     #Fill int with -666666

by_hist_district = realloc.fillna(value=values)

#  Group by historic district
by_hist_district = by_hist_district.groupby(['hist_district_ID','tot_years']).sum()


#%%
##  Percentages of POC and renters by historic district

#  Characteristics by historic district
#  Percent POC
by_hist_district['pct_poc'] = 100*by_hist_district['pop_poc'] / by_hist_district['pop_total']

#  Percent renter
by_hist_district['pct_rental'] = 100*by_hist_district['housing_rental'] / by_hist_district['housing_total']

#  Write to CSV
by_hist_district.to_csv('by_hist_district.csv')

print("\nDownloaded 'by_hist_district.csv'")


#%%
#  Group by historic status
#  (in historic district vs. not in historic district)

#  Reset index to historic district idenifier
#  (Remove years_since_des, which will not be necessary in this section
#  since we are aggregating data from all historic districts)
by_hist_status = by_hist_district.reset_index(drop=False)
by_hist_status = by_hist_status.set_index('hist_district_ID')

#  Identifier for block groups in historic districts
by_hist_status['in_hist_district'] = by_hist_status.index

by_hist_status['in_hist_district'] = np.where(by_hist_status['in_hist_district']== "NA",
                                                "No", "Yes")

#  Group by historic status
sum_vars = ['pop_total','pop_white','pop_poc','housing_total','housing_owned',
            'housing_rental']

by_hist_status = by_hist_status.groupby('in_hist_district')[sum_vars].sum()


#%%
#  Percentages of POC and renters

#  Characteristics by historic district
#  Percent POC
by_hist_status['pct_poc'] = 100*by_hist_status['pop_poc'] / by_hist_status['pop_total']

#  Percent renter
by_hist_status['pct_rental'] = 100*by_hist_status['housing_rental'] / by_hist_status['housing_total']

#  Write to CSV
by_hist_status.to_csv('by_hist_status.csv')

print("\nDownloaded 'by_hist_status.csv'\n")


#%%
#  Footnotes
#  1. There are several historic districts where no designation date was found.
#  They are parks and areas with not very small populations, therefore they are
#  not relevant to this analysis.