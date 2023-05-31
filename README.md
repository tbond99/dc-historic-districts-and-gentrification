# D.C. Historic Districts and Gentrification
Evaluates whether D.C. historic districts contribute to gentrification and racial displacement using geographic and demographic analysis.


## Part 1: 2020 Historic District Analysis


### pop_by_tract.py (1/3)
Imports DC population data by census tract from Census API.

Requires:
- Census API key, which can be acquired here: https://api.census.gov/data/key_signup.html


### 2020_analysis.py (2/3)
Identify population in historic districts, create charts and maps.

Requires:
- "Historic_Districts.zip": Shapefile of D.C. historic districts downloaded from D.C. Open Data: https://opendata.dc.gov/datasets/a443bfb6d078439e9e1941773879c7f6/about
    
- "tl_2020_11_tract.zip": The Tiger/LINE file for D.C., which can be downloaded here: https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2020&layergroup=Census+Tracts
Select 2020, then Census Tracts, then District of Columbia


### charts.py (3/3)
Create charts of racial demographics in historic districts.
      
Output:
    
    - "chart_poc_renters.png": Percent renters and persons of color within historic districts, compared to non-historic districts
      
    - "chart_poc_regression.png": Linear regression of years since designation and percent people of color
    
    - "chart_poc_years.png": DC Neighborhood Makeup by Years since Historic Designation


## Part 2: Time-Series Analysis 1970-2020


### time_series_analysis_1970_2020.py (1/2)
Uses time series data from NHGIS to study historic districts and racial displacement in D.C. Time series data provides significantly more detail than the 2020 analysis, because there are up to 5 observations for each census tract instead of one. (See Footnote 1)

Requires:
- "hist_districts.gpkg": Located in 2020 Analysis folder. A geopackage of historic districts in D.C., with designation year and years since designation.

- "tracts_dc.gpkg": Located in 2020 Analysis folder. A geopackage of D.C. census tracts, converted to D.C.'s official coordinate system (Maryland State Plane NAD 83)

- "nhgis0004_csv.zip": Download using the instructions in the main folder."Download_Instructions_RacialDemographicsByCensusTract.mkd". A dataset of racial data by census tract from the decennial census. Covers years: 1970, 1980, 1990, 2000, 2010, 2020


## time_series_charts.py (2/2)
Creates charts of time series population data from D.C. historic districts. Data is from the decennial census in 1970, 1980, 1990, 2000, 2010, and 2020
    
Output:
    
    - "chart_poc_num_years.png": Chart of number of years since historic designation and percent people of color within the historic district.
    
    - "chart_regression.png": Regression of number of years since historic designation and percent people of color.
    
    - "chart_line_plot.png": Line plot showing each historic district's change in percent people of color over time. (Each historic district is a different color)


## Footnotes
1. Census tracts from 1970-2020 are matched nominally (by their names) with 2020 census tracts. Census tract boundaries change over time so this analysis is not perfect. In particular, the older the data, the less accurate: 1970 and 1980 census tracts are likely the most different from 2020 census tracts. In a future version of this analysis I would prefer to use crosswalks.




