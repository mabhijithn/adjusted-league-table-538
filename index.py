#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 22:17:29 2021

@author: user123
"""

from app import app
from app import server
import pandas as pd
import math
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output
from helperfns import buildadjustedtable

leagueNames = ['Barclays Premier League','Spanish Primera Division','German Bundesliga',
               'Italy Serie A','French Ligue 1']
titleMd = dcc.Markdown(''' ## Adjusted English Premier League Table''')
description = dcc.Markdown('''### Using [FiveThirtyEight's](https://projects.fivethirtyeight.com/soccer-predictions/) xG, non-shot xG and adjusted score metrics
                           
##### **Disclaimer:** The data shown here is for personal consumption. Please leave feedback replying to my twitter profile [@Ituralde](https://twitter.com/Ituralde) and give a follow once you are there :-) 
                           ''')
                           
line1 = dcc.Markdown('''#### Steps:

An average score of a match is calculated''')
line2 = dcc.Markdown('''**average-score** = average(xG, non-shot xG, adjusted-score)''')
line3 = dcc.Markdown('''**Match Result** :''')
line4 = dcc.Markdown('''
                     1. *Team 1* wins if average-score(team-1) - average-score(team-2) > **tolerance**
                     2. *Team 2* wins if average-score(team-2) - average-score(team-1) > **tolerance**
                     3. *Otherwise Draw*
                     ''')
tolerancetext = dcc.Markdown('''
                             #### Tolerance:
                             '''
    )
app.layout = html.Div([ titleMd,
                       description,line1,line2,line3,line4,
                       tolerancetext,
                       dcc.Slider(id='tolerance-selection',
                                  min=0.1, max=0.5,step=None,
    marks={
        0.1: '0.1',
        0.2: '0.2',
        0.3: '0.3',
        0.4: '0.4',
        0.5: '0.5'
    },
    value=0.2
                                  ),
                       html.Br(),
                       dcc.Markdown('''#### Select League:
                                    '''),                       
                       dcc.Dropdown(id='league-dropdown',
                                    options=[{'label':i,'value':i} for i in leagueNames],
                                    value='Barclays Premier League'),
                       html.Br(),
                       html.Tr([
                       html.Button('Generate Table','gen-table-button')
                       ]),
                       html.Br(),
                       dash_table.DataTable(id='adjusted-table',
                       style_cell={'textAlign': 'left'},
                       style_data_conditional=[
                            {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                            },
                            {
                            'if': {
                                'filter_query': '{Point Diff} < 0',
                                'column_id': 'Point Diff'
                                  },
                            'backgroundColor': 'tomato',
                            'color': 'black'
                            },
                            {
                            'if': {
                                'filter_query': '{Point Diff} > 0',
                                'column_id': 'Point Diff'
                                  },
                            'backgroundColor': 'green', 
                            'color': 'black'
                            },
                           ],
                       style_header={
                           'backgroundColor': 'rgb(230, 230, 230)',
                           'fontWeight': 'bold'
                           }
                       )
    ])
@app.callback(
    Output('adjusted-table','columns'),
    Output('adjusted-table','data'),
    Input('tolerance-selection','value'),
    Input('league-dropdown','value'),
    Input('gen-table-button','n_clicks')
    )
def update_table(tolerance,leagueName, n_clicks):
    #leagueName = 'Barclays Premier League'
    change_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    columnnames = ['Avg Score Position','Original Position','Club','Matches','Original Points','Avg Score Points','Point Difference','Avg Score Won',
                   'Avg Score Draw','Avg Score Losses']
    columnlist = ['Avg Score Position','Original Position','Club','Matches','Actual Points','avg Score Points','Point Diff','avg Score Won','avg Score Draw','avg Score Loss']                
    columns = [{'name':columnnames[count],'id':i} for count,i in enumerate(columnlist)]
    if 'gen-table-button' in change_id:
        otherTable = buildadjustedtable(leagueName,tolerance)            
    else:
        otherTable = pd.DataFrame(columns=columnlist)
    data = otherTable.to_dict('records')
    return(columns,data)
if __name__ == '__main__':
    app.run_server(debug=True,port=1234)