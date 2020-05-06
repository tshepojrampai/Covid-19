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

#---- Load in more datasets---->
url1 = 'https://api.covid19api.com/live/country/south-africa/status/confirmed/date/2020-03-21T13:13:30Z'
df1 = pd.read_json(url1, orient='columns')
url2 = 'https://api.covid19api.com/country/south-africa/status/confirmed'
df2 = pd.read_json(url2, orient='columns')
url3 = 'https://api.covid19api.com/country/south-africa/status/confirmed/live'
df3 = pd.read_json(url3, orient='columns')
url4 = 'https://covid19.soficoop.com/country/za'
url5 = 'https://api.covid19api.com/total/dayone/country/south-africa'
df5 = pd.read_json(url5, orient='columns')
df6 = pd.read_csv('datasets/covid.csv',delimiter=',')

#Daily Commulative dataframe 
df4 = requests.get(url4).json()
df4= pd.json_normalize(df4,record_path ='snapshots')


#SA commulative data
df_rsa = df6[df6.countriesAndTerritories == 'South_Africa'].reset_index()
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x = df4.timestamp,y= df4.active, name = 'Active Cases in SA'))
fig_line.update_layout(title = 'Commulative confirmed cases in SA as 17/03/2020')

df_rt = pd.read_csv('datasets/data-CiK32.csv')

#Effective reproduction
fig_rt = go.Figure()
fig_rt.add_trace(
    go.Scatter(
        y=df_rt['Possible low Rt'],
        x=df_rt.date,
        name= 'Possible low Rt'
    ))
fig_rt.add_trace(
    go.Scatter(
        y=df_rt['Most likely Rt'],
        x=df_rt.date,
       name= 'Most likely Rt'
    ))
fig_rt.add_trace(
    go.Scatter(
        y=df_rt['Possible High Rt'],
        x=df_rt.date,
        name= 'Possible High Rt'
    ))

fig_rt.update_layout(hovermode='x',
                     xaxis=dict(
                         rangeslider=dict(
                             visible = True),
        type='date'
    ))

# Provincial cases dataset
df_day = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv')
df_day = df_day.drop('source',axis = 1)
df_day = df_day.dropna()

#Commulative cases by province


fig_comm = go.Figure()
fig_comm.add_trace(
    go.Scatter(
        y=df_day['EC'],
        x=df_day.date,
        name= 'EC'
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['WC'],
        x=df_day.date,
        name= 'WC'
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['FS'],
        x=df_day.date,
        name= 'FS'
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['GP'],
        x=df_day.date,
        name= 'GP'
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['KZN'],
        x=df_day.date,
        name= "KZN"
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['NW'],
        x=df_day.date,
        name= 'NW'
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['LP'],
        x=df_day.date,
        name= 'LP'
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['MP'],
        x=df_day.date,
        name= 'MP'
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['NC'],
        x=df_day.date,
        name= 'NC'
    ))
fig_comm.add_trace(
    go.Scatter(
        y=df_day['UNKNOWN'],
        x=df_day.date,
        name='Unlocated'
    ))
# fig_comm.add_trace(
#     go.Scatter(
#         y=df_day['total'],
#         x=df_day.date,
#         name='Total Confirmed in SA'
#     ))

fig_comm.update_layout(hovermode='x',
                       title = 'Commulative confirmed cases by province',
                       xaxis=dict(
                         rangeslider=dict(
                             visible = True),
                           
       
                       
    ))





#Total confirmed world map
data = [ dict(
 type='choropleth',
 locations = df['Country'],
 autocolorscale = True,
 z = df['TotalConfirmed'],
 locationmode = 'country names',
 marker = dict(
 line = dict (
 color = 'rgb(155,155,155)',
 width = 4,
 )  ),
 colorbar = dict(
 title = 'Number of cases'
 )
 ) ]
layout = dict(
 autosize=True,
margin={"r":0,"t":0,"l":0,"b":0}
    
)
fig = go.Figure(data = data, layout = layout)

# Active cases world map

data1 = [ dict(
 type='choropleth',
 locations = df['Country'],
 autocolorscale = True,
 z = df['Active Cases'],
 locationmode = 'country names',
 marker = dict(
 line = dict (
 color = 'rgb(255,255,255)',
 width = 10,
 )  ),
 colorbar = dict(
 title = 'Active cases'
 )
 ) ]
layout = dict(
 autosize=True,
 margin={"r":0,"t":0,"l":0,"b":0}   
)




fig1_ = go.Figure(data = data1, layout = layout)

#Closed cases world map
data2 = [ dict(
 type='choropleth',
 locations = df['Country'],
 autocolorscale = True,
 z =df['Closed Cases'],
 locationmode = 'country names',
 marker = dict(
 line = dict (
 color = 'rgb(245, 197, 66)',
 width = 10,
 )  ),
 colorbar = dict(
 title = 'Closed Cases'
 )
 ) ]
layout = dict(
 autosize=True,
 margin={"r":0,"t":0,"l":0,"b":0}   
)
fig2_ = go.Figure(data = data2, layout = layout)

#Recovery Rate World Map

data3 = [ dict(
 type='choropleth',
 locations = df['Country'],
 autocolorscale = True,
 z =df['Recovery Rate'],
 locationmode = 'country names',
 marker = dict(
 line = dict (
 color = 'rgb(455,455,455)',
 width = 10,
 )  ),
 colorbar = dict(
 title = 'Recovery Rate (%)'
 )
 ) ]
layout = dict(
 autosize=True,
 margin={"r":0,"t":0,"l":0,"b":0}   
)
fig3_ = go.Figure(data = data3, layout = layout)


#Case fatality rate world map

data4 = [ dict(
 type='choropleth',
 locations = df['Country'],
 autocolorscale = True,
 z =df['Case Fatality Rate'],
 locationmode = 'country names',
 marker = dict(
 line = dict (
 color = 'rgb(555,555,555)',
 width = 10,
 )  ),
 colorbar = dict(
 title = 'Case Fatality Rate (%)'
 )
 ) ]
layout = dict(
    autosize=True,
    margin={"r":0,"t":0,"l":0,"b":0}
)
fig4_ = go.Figure(data = data4, layout = layout)
fig4_.show()

#Style sheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# ------------- App -------------------------------
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.layout = html.Div(children=[
        #header
    
    html.Div([
        html.Div([
           
        ], className="four columns"),
        

        html.Div([
            html.H3('Latest Covid 19 Update', style={
                                'fontFamily': 'Open Sans',
                                'textAlign': 'center',
                            }),
             
        ], className="four columns"),
        
        html.Div([
            html.H3('#StayAtHome', style={
                                'fontFamily': 'Open Sans',
                                'textAlign': 'right',
                            }),
            
            
        ], className="four columns")
    ], className="row"),
    
    dcc.Tabs(id='tabs-example', value='tab', children=[
        dcc.Tab(label='Global Map', value='tab-1'),
        dcc.Tab(label='South African cases', value='tab-2'),
        dcc.Tab(label='Analysis', value='tab-3'),
    ]),
    html.Div(id='tabs-example-content')
])


#----------- Main tab call back ----
@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):

    if tab == 'tab-1':
        return html.Div([
            html.Div([

                # VISUALISATIONS

                html.Div([
                      dcc.Graph(
                          id='figure',
                            figure=go.Figure(fig1)
                          
                        ),
                html.Div([
                    dash_table.DataTable(
                            id='table',
                            data=df_tot_cases.to_dict("rows"),
                            columns=[{"name": i, "id": i}
                                     for i in df_tot_cases.columns],
                            style_table=style_table,
                            style_cell=style_cell,
                            style_data_conditional=style_data_conditional,
                            style_header=style_header,
                            style_cell_conditional=style_cell_conditional,
                            filter_action="native"
                        )
                ])
                    
            ], className="row"),

                ], className="three columns"),
            
            html.Div([
                    dcc.Graph(
                          id='figure',
                            figure=go.Figure(fig2)
                        ),
                    html.Div([
                        dcc.Tabs(id='tabs-examples', value='tabs', children=[
                            dcc.Tab(label='Total Cases', value='tab-1.'),
                            dcc.Tab(label='Active Cases', value='tab-2.'),
                            dcc.Tab(label='Solved Cases', value='tab-3.'),
                            dcc.Tab(label='Recovery Rate', value='tab-4.'),
                            dcc.Tab(label='Case Fatality Rate', value='tab-5.')
                        ], colors={
                                "border": "white",
                                "primary": "gold",
                                "background": "cornsilk"
                            }),
                     html.Div(id='tabs-example-contents'),
            ], className="row"),
                ], className="six columns"),

                html.Div([
                     dcc.Graph(
                          id='figure',
                            figure=go.Figure(fig3)
                        ),


                    html.Div([
                        dcc.Graph(
                          id='figure',
                            figure=go.Figure(fig_line)
                        ),
                        
                        
                       
            ], className="row")

                ], className="three columns"),
            ], className="row")

            # fOOTER
        html.Div([
                html.Div([
                    html.H3('Footer'),

                ], className="six columns"),

                html.Div([
                    html.H3('Footer'),

                ], className="six columns"),
            ], className="row")
  

    elif tab == 'tab-2':
        return html.Div([
            dcc.Graph(
                id='figure',
                figure=go.Figure(fig2)
            ),
                    html.Div([
                        dcc.Graph(
                         id='figure',
                figure=go.Figure(fig_rt  )
                        ), 
                
            ], className="row"),
                ], className="six columns"),
    else:
        return html.H1('Critical trends and South African cases analyses!!!')
    
#---- Small tab call back -----

@app.callback(Output('tabs-example-contents', 'children'),
              [Input('tabs-examples', 'value')])
def render_content(tabs):
    
    if tabs == 'tab-1.':
        return dcc.Graph(

            id='figure',
            figure=
              go.Figure(fig)
            )
    elif tabs == 'tab-2.':   
        return dcc.Graph(

            id='figure',
            figure=
              go.Figure(fig1_)
            )
           
    elif tabs == 'tab-3.':   
        return dcc.Graph(

            id='figure',
            figure=
              go.Figure(fig2_)
            )
    elif tabs == 'tab-4.':
         return dcc.Graph(

                 id='figure',
            figure=
              go.Figure(fig3_)
            )
    else:
        return dcc.Graph(

            id='figure',
            figure=
              go.Figure(fig4_)
            )


if __name__ == '__main__':
    app.run_server()
