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
titleMd = dcc.Markdown(''' ## Performance Adjusted English Premier League Table''')
description = dcc.Markdown('''### Using [FiveThirtyEight's](https://projects.fivethirtyeight.com/soccer-predictions/) xG, non-shot xG and adjusted score metrics
                           
##### **Disclaimer:** The data shown here is for personal consumption. Please leave feedback replying to my twitter profile [@Ituralde](https://twitter.com/Ituralde) and give a follow once you are there :-) 
                           ''')
                           
line1 = dcc.Markdown('''#### Context:

The american data based news website [FiveThirtyEight](https://projects.fivethirtyeight.com/soccer-predictions/) 
is a popular webpage where they showcase their football predictions. Though 
these predictions are at times divisive, the models they use to estimate 
individual match performances are founded on strong principles. They use three
metrics to evaluate a team’s performance after each match
_adjusted goals_, _shot-based expected goals (xG)_ and _non-shot expected goals_ (nsxG)

The **how** abnd **why** of xG and nsxG can be found [here](https://projects.fivethirtyeight.com/soccer-predictions/).
The above metrics are quite popular with **xG** going mainstream even on BBC's MOTD.
However, **adjusted goals** is a bit different as this metric in-fact adjusts the
actual final goals of a match based on game situation. For e.g. lower value for 
a goal if a team was already leading and higher value for a goal if the team
was playing with 10-men.

Here, I calculated **average goals** in each match by taking the average of
all the three above metrics. Using this average goals, a win,loss or a draw
is assigned to each match. I hope this would better reflect underlying 
match performance compared to using just xG or adjusted goals. As the former
does not include actual goals scored and the latter ignores match performance.''')
line2 = dcc.Markdown('''**average-goals** = average(xG, non-shot xG, adjusted-goals)''')
line3 = dcc.Markdown('''**Match Result** :''')
line4 = dcc.Markdown('''
                     1. *Team 1* wins if average-goals(team-1) - average-goals(team-2) > **tolerance**
                     2. *Team 2* wins if average-goals(team-2) - average-goals(team-1) > **tolerance**
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
                                           sort_action='native',
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
                                               'fontWeight': 'bold',
                                               'whiteSpace': 'normal',
                                               'height': 'auto',
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
    columnnames = ['Average Goals Position','Original Position','Club','Matches','Original Points','Average Goals Points','Point Difference',
                   'Average Goals Scored','xG Scored','Actual Goals Scored',
                   'Average Goals Conceded','xG Conceded','Actual Goals Conceded']
    columnlist = ['Avg Score Position','Original Position','Club','Matches','Actual Points','avg Score Points','Point Diff',
                  'avg Score For','xG For','GScored','avg Score Against','xG Against','GConceded']                
    columns = [{'name':columnnames[count],'id':i} for count,i in enumerate(columnlist)]
    if 'gen-table-button' in change_id:
        otherTable = buildadjustedtable(leagueName,tolerance)            
    else:
        otherTable = pd.DataFrame(columns=columnlist)
        
    goalsColumns = ['avg Score For','xG For','GScored','avg Score Against',
                    'xG Against','GConceded']
    for g in goalsColumns:
        otherTable.loc[:,g] = otherTable.loc[:,g].round(1)
    data = otherTable.to_dict('records')
    return(columns,data)
if __name__ == '__main__':
    app.run_server(debug=True,port=1234)