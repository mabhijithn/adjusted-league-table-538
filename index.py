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
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output
from helperfns import buildadjustedtable

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
    Input('tolerance-selection','value')
    )
def update_table(tolerance):
    leagueName = 'Barclays Premier League'
    otherTable = buildadjustedtable(leagueName,tolerance)
    
    columnlist = ['Avg Score Position','Original Position','Club','Matches','Actual Points','avg Score Points','Point Diff','avg Score Won','avg Score Draw','avg Score Loss']
    data = otherTable.to_dict('records')
    columnnames = ['Avg Score Position','Original Position','Club','Matches','Original Points','Avg Score Points','Point Difference','Avg Score Won',
                   'Avg Score Draw','Avg Score Losses']
    columns = [{'name':columnnames[count],'id':i} for count,i in enumerate(columnlist)]
    return(columns,data)
if __name__ == '__main__':
    app.run_server(debug=True,port=1234)