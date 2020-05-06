#--------Importing required Libraries ---------

import requests
from pandas.io.json import json_normalize
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly as py
import plotly.graph_objs as go
init_notebook_mode(connected=True)


#----------- Table styling ------------------
style_cell = {
    'fontFamily': 'Open Sans',
    'textAlign': 'center',
    'height': '30px',
    'padding': '10px 22px',
    'whiteSpace': 'inherit',
    'overflow': 'hidden',
                'textOverflow': 'ellipsis',
}
style_cell_conditional = [
    {
        'if': {'column_id': 'State'},
        'textAlign': 'left'
    },
]
style_header = {
    'fontWeight': 'bold',
    'backgroundColor': "#3D9970",
    'fontSize': '16px'
}
style_data_conditional = [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(248, 248, 248)'
    }]
style_table = {
    'maxHeight': '70ex',
    'overflowY': 'scroll',
    'width': '100%',
    'minWidth': '100%',
}

#----- Global data set------
url = 'https://api.covid19api.com/summary'
r = requests.get(url)
dictr = r.json()
header = dictr['Countries']
df = json_normalize(header)
df = df.drop(df.index[[0,224]])
df = df.drop(columns = 'Slug')
df = df.sort_values(by=['TotalConfirmed'], ascending=False)

#Summing per column
tot_cases = df.TotalConfirmed.sum()
nw_cases = df.NewConfirmed.sum()
tot_deaths = df.TotalDeaths.sum()
new_deaths = df.NewDeaths.sum()
tot_recover = df.TotalRecovered.sum()
new_recover = df.NewRecovered.sum()
diff = tot_cases - nw_cases
diff2 = tot_recover - new_recover
diff3 = tot_deaths - new_deaths 

#Separating columns

#Corona  cases: Total and New
df_tot_cases = df.loc[:,['Country','TotalConfirmed']].sort_values(by='TotalConfirmed', ascending=False)
df_new_cases = df.loc[:,['Country','NewConfirmed']]

#Death Cases: Total and New 
df_tot_death = df.loc[:,['Country','TotalDeaths']]
df_new_death = df.loc[:,['Country','NewDeaths']]

#Recovery cases: Total and new
df_tot_recover = df.loc[:,['Country','TotalRecovered']]
df_new_recover = df.loc[:,['Country','NewRecovered']]

#Sorting cases by total
df_cases = df_tot_cases.merge(df_new_cases, on='Country').sort_values(by=['TotalConfirmed'],
                                                                      ascending=False)
df_death = df_tot_death.merge(df_new_death, on='Country').sort_values(by=['TotalDeaths'],
                                                                      ascending=False)
df_recover = df_tot_recover.merge(df_new_recover, on='Country').sort_values(by=['TotalRecovered'], 
                                                                            ascending=False)

# total cases indicator
fig1 = go.Figure(go.Indicator(
    
    value = tot_cases,
    delta = {'reference': diff},
    gauge = {
        'axis': {'visible': False}},
    domain = {'row': 0, 'column': 0}))

fig1 = fig1.update_layout(
    template = {'data' : {'indicator': [{
        'title': {'text': "Total Cases"},
        'mode' : "number+delta+gauge",
        }]
                         }})

#Recoveries indicator
fig2 = go.Figure(go.Indicator(
    mode = "number+delta",
    value = tot_recover,
    delta = {'reference': diff2},
    domain = {'row': 0, 'column': 1}))
fig2 = fig2.update_layout(
    template = {'data' : {'indicator': [{
        'title': {'text': "Recoveries"}
        }]
                         }})

# total deaths indicator
fig3 = go.Figure(go.Indicator(
    
    value = tot_deaths,
    delta = {'reference': diff3},
    gauge = {
        'axis': {'visible': False}},
    domain = {'row': 0, 'column': 0}))

fig3 = fig3.update_layout(
    template = {'data' : {'indicator': [{
        'title': {'text': "Total Deaths"},
        'mode' : "number+delta+gauge",
        }]
                         }})

#----- Feature Creation from existing data ----
df['Active Cases'] = df['TotalConfirmed'] - df['TotalRecovered'] - df['TotalDeaths']
df['Closed Cases'] = df['TotalRecovered'] + df['TotalDeaths']
df['Recovery Rate'] = (df['TotalRecovered'] / df['TotalConfirmed'])*100
df['Case Fatality Rate'] = (df['TotalDeaths'] / df['TotalConfirmed']) * 100


