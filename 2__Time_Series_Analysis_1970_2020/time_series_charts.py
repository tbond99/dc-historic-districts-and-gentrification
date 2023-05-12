"""
time_series_charts.py (Script 2/2)
Date updated: 5/11/2023

Creates charts of time series population data from D.C. historic districts. Data
is from the decennial census in 1970, 1980, 1990, 2000, 2010, and 2020
"""

"""
Requires:
    - "by_hist_district_1970_2020.csv" (from Script 1)
    D.C. population by historic district (approximate) from 1970 to 2020.
    
Output:
    - "chart_poc_num_years.png": Chart of number of years since historic designation and percent people of color
    within the historic district.
    
    - "chart_regression.png": Regression of number of years since historic designation and percent people of color.
    
    - "chart_line_plot.png": Line plot showing each historic district's change in percent people of color over time.
    (Each historic district is a different color)
    
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

import seaborn as sns

import matplotlib.pyplot as plt

import scipy

#  Set default resolution
plt.rcParams['figure.dpi'] = 300


#%%
##  Read in data
by_hist_district_1970_2020 = pd.read_csv("by_hist_district_1970_2020.csv")


#%%
##  Prepare data for chart

#  Reset historic district index
plot_data = by_hist_district_1970_2020

#  Remove outliers
plot_data = plot_data.loc[plot_data['years_since_des']<60]

plot_data = plot_data.loc[plot_data['total_pop']>500]

#  Round population
plot_data['pop_total'] = round(plot_data['total_pop']).astype(int)

#  Change column labels
plot_data = plot_data.rename(columns={'total_pop':'Population',
                                      'years_since_des':'Years After Historic Designation',
                                      'perc_poc':'Percent People of Color'
                                      })


#%%
##  Chart of number of years since historic designation and percent people of color

#  SNS Relplot
fg = sns.relplot(data=plot_data, x='Years After Historic Designation',
                 y='Percent People of Color',
                 size='Population', sizes=(10,200),
                 hue='Years After Historic Designation', facet_kws={'despine':False,
                'subplot_kws':{'title': 'Racial Makeup Before & After Historic Designation'}})

#  Set axis limits
fg.set(ylim=(0,100))

#  Tight layout
fg.tight_layout()

#  Save
fg.savefig('chart_poc_num_years.png')

print("\nDownloaded 'chart_poc_num_years.png'")


#%%
##  Linear regression plot
##  Regresses number of years since historic designation on percent people of color.

##  Results: 10 years of historic designation is correlated with a
##  3-point decrease in percent people of color.

##  However, correlation does not prove causation. Maybe racial change
##  leads to historic designation (reverse causality), or an omitted variable
##  such as property values is responsible.

plot_data_regplot = plot_data.loc[plot_data['Years After Historic Designation']>0]

#  Axes
plt.figure()

#  Plot data
fig2 = sns.regplot(data=plot_data_regplot, x='Years After Historic Designation',
                y='Percent People of Color')

#  Set axis limits
fig2.set(ylim=(0,100))
fig2.set(xlim=(5,56))

#  Set title
fig2.set_title('Racial Displacement After Historic Designation')

#calculate slope and intercept of regression equation
slope, intercept, r, fg2, sterr = scipy.stats.linregress(x=fig2.get_lines()[0].get_xdata(),
                                                       y=fig2.get_lines()[0].get_ydata())

#  Add regression equation to plot
fig2.text(6, 87, 'y = ' + str(round(intercept,3)) + ' + ' + str(round(slope,3)) + 'x')

#  Save
plt.savefig('chart_regression.png')

print("\nDownloaded 'chart_regression.png'")


#%%
##  Linear regression plot #2
##  Regresses number of years prior to historic designation on percent people of color.

##  Results: Future historic districts experience a 8.5 point decrease in percent
##  people of color in the 10 years prior to historic designation. This result
##  emphatically shows that racial displacement of people of color is correlated
##  with eventual historic designation. 

plot_data_regplot2 = plot_data.loc[plot_data['Years After Historic Designation']<0]

#  Change variable name
plot_data_regplot2 = plot_data_regplot2.rename(columns={'Years After Historic Designation':
                                                        'Years Before Historic Designation'})

#  Axes
plt.figure()

#  Plot data
fig2 = sns.regplot(data=plot_data_regplot2, x='Years Until Historic Designation',
                y='Percent People of Color')

#  Set axis limits
fig2.set(ylim=(0,100))
fig2.set(xlim=(-45,0))

#  Set title
fig2.set_title('Racial Displacement Prior to Historic Designation')

#calculate slope and intercept of regression equation
slope, intercept, r, fg2, sterr = scipy.stats.linregress(x=fig2.get_lines()[0].get_xdata(),
                                                       y=fig2.get_lines()[0].get_ydata())

#  Add regression equation to plot
fig2.text(-43, 40, 'y = ' + str(round(intercept,3)) + ' + ' + str(round(slope,3)) + 'x')

#  Save
plt.savefig('chart_regression.png')

print("\nDownloaded 'chart_regression.png'")


#%%

##  Line plot showing each historic district's change in percent people of color over time.
##  (Each historic district is a different color)

#  Drop columns
keep_cols = ['Years After Historic Designation', 'hist_district_ID', 'Percent People of Color']

plot_data_lineplot = plot_data[keep_cols].reset_index(drop=True)

#  Drop duplicates
plot_data_lineplot = plot_data_lineplot.drop_duplicates(subset=['Years After Historic Designation', 'hist_district_ID'])

#  Pivot to wide-form
plot_data_lineplot = plot_data_lineplot.pivot("Years After Historic Designation", "hist_district_ID", "Percent People of Color")


#%%
##  Create figure
plt.figure()

#  Plot data
fg3 = sns.lineplot(data=plot_data_lineplot, legend=None)

#  Set axis labels
fg3.set_xlabel('Years After Historic Designation')
fg3.set_ylabel('Percent People of Color')

#  Set title
fg3.set_title('Racial Displacement Before & After Historic Designation')

#  Set axis limits
fg3.set(ylim=(0,100))
fg3.set(xlim=(-45,56))

#  Save
plt.savefig('chart_line_plot.png')

print("\nDownloaded 'chart_line_plot.png'")
