"""
charts.py (Script 3/3)
Date updated: 5/11/2023

Create charts of racial demographics in historic districts.
"""

"""
Requires:
    - "by_hist_district.csv": A listing of D.C. historic districts with demographic data.
      (from script 2)
    
    - "by_hist_status.csv": Demographics in D.C. historic districts and non-historic districts.
      (from script 2)
      
Output:
    - "chart_poc_renters.png": A chart of percent renters and persons of color within historic
      districts, compared to non-historic districts
      
    - "chart_poc_regression.png": Linear regression of years since designation and percent people of color
    
    - "chart_poc_years.png": DC Neighborhood Makeup by Years since Historic Designation
    
"""

#%%
##  Set working directory to script directory "2020_Analysis"
import os

os.chdir(os.path.dirname(__file__))

#%%
#  Import modules
import pandas as pd

import matplotlib.pyplot as plt

import seaborn as sns

import scipy

#  Set default resolution
plt.rcParams['figure.dpi'] = 300

#%%
#  Import data

#  By historic district
by_hist_district = pd.read_csv('by_hist_district.csv')

#  By historic status (Yes or No)
by_hist_status = pd.read_csv('by_hist_status.csv')


#%%
#  DC Totals
dc_totals = by_hist_district.sum()

#  Percent POC in DC
dc_pct_poc = 100*dc_totals['pop_poc'] / dc_totals['pop_total']

print(f"\nD.C. percent persons of color (POC): {round(dc_pct_poc)}%\n")

#  Percent renter in DC
dc_pct_rental = 100*dc_totals['housing_rental'] / dc_totals['housing_total']

print(f"\nD.C. percent renters: {round(dc_pct_rental)}%\n")


#%%
#  Prepare data for graph

#  Reset historic district index
plot_data = by_hist_status.reset_index()

#  Rename columns
plot_data = plot_data.rename(columns={'in_hist_district':'In Historic District'})

#  Round population
plot_data['pop_total'] = round(plot_data['pop_total']).astype(int)

#  Change column label for population
plot_data = plot_data.rename(columns={'pop_total':'Population',
                                      'in_hist_district':'In Historic District',
                                      'tot_years':'Years After Historic Designation',
                                      'pct_poc':'Percent People of Color',
                                      'pct_rental':'Percent Renters'})
                                      

#%%
##  Construct chart "D.C. Neighborhood Makeup by Historic Status"

##  This chart shows the percent renters and persons of color within historic
##  districts, compared to non-historic districts.

##  The results demonstrate that historic districts and have significantly less
##  persons of color as a percentage of population, but they are similar in
##  renter composition.

#  Create figure
plt.figure()

#  SNS Relplot
fg = sns.relplot(data=plot_data, x='Percent Renters', y='Percent People of Color',
                 size='Population', sizes=(10,200),
                 hue='In Historic District', facet_kws={'despine':False,
                'subplot_kws':{'title': 'D.C. Racial Makeup by Historic Status'}})

#  Set Axis limits to 0 and 1
fg.set(xlim=(0,100))
fg.set(ylim=(0,100))

#  Reference lines at County overall percentages
fg.refline(x=dc_pct_rental, y=dc_pct_poc)

#  Tight layout
fg.tight_layout()

#  Save
plt.savefig('chart_poc_renters.png')

print("\nDownloaded 'chart_poc_renters.png'")


#%%
##  Examine racial demographics & years since designation

##  Prepare data for chart


#  Remove historic districts with <500 residents
#  (These areas are mostly non-residential)
by_hist_district = by_hist_district.loc[by_hist_district['pop_total']>500]

#  Reset historic district index
plot_data = by_hist_district.reset_index()

#  Remove historic districts without a value for "years since designation"
plot_data = plot_data.loc[plot_data['tot_years']!=-666666]

#  Rename columns
plot_data = plot_data.rename(columns={'in_hist_district':'In Historic District',
                                      'tot_years':'Years After Historic Designation',
                                      'pct_poc':'Percent People of Color'})

#  Round population
plot_data['pop_total'] = round(plot_data['pop_total']).astype(int)

#  Change column label for population
plot_data['Population'] = plot_data['pop_total']

#%%
##  Run linear regression of years since designation and percent people of color

##  These preliminary results show that 10 years of historic designation is correlated
##  with a 1.1 point decrease in percent people of color.

#  Create figure
plt.figure()

#  Plot data
fig2 = sns.regplot(data=plot_data, x='Years After Historic Designation',
                y='Percent People of Color')

#  Set x/y axis limits
fig2.set(ylim=(0,100))
fig2.set(xlim=(4,60))

#  Set title
fig2.set_title('Racial Displacement After Historic Designation')

# Calculate slope and intercept of regression equation
slope, intercept, r, fg2, sterr = scipy.stats.linregress(x=fig2.get_lines()[0].get_xdata(),
                                                       y=fig2.get_lines()[0].get_ydata())

#  Add regression equation to plot
fig2.text(6, 95, 'y = ' + str(round(intercept,3)) + ' + ' + str(round(slope,3)) + 'x')

#  Save
plt.savefig('chart_poc_regression.png')

print("\nDownloaded 'chart_poc_regression.png'")


#%%
## Construct chart of DC Neighborhood Makeup by Years since Historic Designation

#  Create figure
plt.figure()

#  Plot data using SNS relplot
fg3 = sns.relplot(data=plot_data, x='Percent People of Color', y='Years After Historic Designation',
                 size='Population', sizes=(10,200),
                 hue='Years After Historic Designation',)

#  Set axis labels
fg3.set_axis_labels('Years After Historic Designation', 'Percent People of Color')

#  Set Axis limits to 0 and 100
fg3.set(ylim=(0,100))

#  Tight layout
fg3.tight_layout()

#  Save
plt.savefig('chart_poc_years.png')

print("\nDownloaded 'chart_poc_years.png'")
