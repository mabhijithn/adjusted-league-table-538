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
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from tqdm import tqdm

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
                        # The memory store reverts to the default on every page refresh
                        dcc.Store(id='memory'),
                        # The local store will take the initial data
                        # only the first time the page is loaded
                        # and keep it until it is cleared.
                        dcc.Store(id='local', storage_type='local'),
                        # Same as the local store but will lose the data
                        # when the browser/tab closes.
                        dcc.Store(id='session', storage_type='session'),
                        html.Table([
                            html.Thead([
                                html.Tr(html.Th('Click to store in:', colSpan="3")),
                                html.Tr([
                                    html.Th(html.Button('memory', id='memory-button')),
                                    html.Th(html.Button('localStorage', id='local-button')),
                                    html.Th(html.Button('sessionStorage', id='session-button'))
                                ]),
                                html.Tr([
                                    html.Th('Memory clicks'),
                                    html.Th('Local clicks'),
                                    html.Th('Session clicks')
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td(0, id='memory-clicks'),
                                    html.Td(0, id='local-clicks'),
                                    html.Td(0, id='session-clicks')
                                ])
                            ])
                        ]),
                    # Page content starts below
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
                       html.Tr([
                       html.Th (html.Button('Generate Table', id='gen-table'))
                       ]),
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
    Input('gen-table','n_clicks')
    )
def update_table(tolerance,n_clicks):
    if n_clicks is None:
        # prevent the None callbacks is important with the store component.
        # you don't want to update the store for nothing.
        raise PreventUpdate
    else:
        soccermatchesurl = 'https://projects.fivethirtyeight.com/soccer-api/club/spi_matches_latest.csv'
        soccerspi = pd.read_csv(soccermatchesurl)
        eplName = 'Barclays Premier League'
        season = 2020
        matches = soccerspi.loc[(soccerspi['league']==eplName) & (soccerspi['season']==season),:]
        clubnames = list(matches['team1'].unique())
        matchesDict = matches.to_dict('records')
        otherTable = pd.DataFrame(columns=['Club','xG Won','xG Draw','xG Loss','xG For','xG Against','xG Points','nsxG For','nsxG Against','nsxG Won','nsxG Draw','nsxG Loss','nsxG Points'])
        otherTable['Club'] = clubnames
        otherTable['GScored'] = 0
        otherTable['GConceded'] = 0
        otherTable['GD'] = 0
        otherTable['Won'] = 0
        otherTable['Draw'] = 0
        otherTable['Lost'] = 0
        otherTable['xG Won'] = 0
        otherTable['xG Draw'] = 0
        otherTable['xG Loss'] = 0
        otherTable['Matches'] = 0
        otherTable['Actual Points'] = 0
        otherTable.loc[:,'xG For'] = 0
        otherTable.loc[:,'xG Against'] = 0
        otherTable.loc[:,'xG Points'] = 0
        otherTable.loc[:,'nsxG For'] = 0
        otherTable.loc[:,'nsxG Against'] = 0
        otherTable.loc[:,'nsxG Points'] = 0
        otherTable['nsxG Won'] = 0
        otherTable['nsxG Draw'] = 0
        otherTable['nsxG Loss'] = 0
        
        otherTable.loc[:,'avg Score For'] = 0
        otherTable.loc[:,'avg Score Against'] = 0
        otherTable.loc[:,'avg Score Points'] = 0
        otherTable['avg Score Won'] = 0
        otherTable['avg Score Draw'] = 0
        otherTable['avg Score Loss'] = 0
        
        matchesDictUpdated = []
        
        for matchcount in tqdm(range(len(matchesDict))):
            match = matchesDict[matchcount]
            if not (math.isnan(match['xg1']) & math.isnan(match['xg2'])):
                xGdiff = match['xg1']-match['xg2']
                if xGdiff>=0.25:
                    otherTable.loc[otherTable['Club']==match['team1'],'xG Won'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'xG Loss'] += 1
                elif (xGdiff<0.25) & (xGdiff>-0.25):
                    otherTable.loc[otherTable['Club']==match['team1'],'xG Draw'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'xG Draw'] += 1
                else:
                    otherTable.loc[otherTable['Club']==match['team2'],'xG Won'] += 1
                    otherTable.loc[otherTable['Club']==match['team1'],'xG Loss'] += 1
            if not (math.isnan(match['nsxg1']) & math.isnan(match['nsxg2'])):
                otherTable.loc[otherTable['Club']==match['team1'],'Matches'] += 1
                otherTable.loc[otherTable['Club']==match['team2'],'Matches'] += 1
                otherTable.loc[otherTable['Club']==match['team1'],'GScored'] += match['score1']
                otherTable.loc[otherTable['Club']==match['team2'],'GConceded'] += match['score2']
                if match['score1']>match['score2']:
                    otherTable.loc[otherTable['Club']==match['team1'],'Actual Points'] += 3
                    otherTable.loc[otherTable['Club']==match['team1'],'Won'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'Lost'] += 1
                    match['result'] = 'team1'
                elif match['score1']<match['score2']:
                    otherTable.loc[otherTable['Club']==match['team2'],'Actual Points'] += 3
                    otherTable.loc[otherTable['Club']==match['team2'],'Won'] += 1
                    otherTable.loc[otherTable['Club']==match['team1'],'Lost'] += 1
                    
                    match['result'] = 'team2'
                else:
                    otherTable.loc[otherTable['Club']==match['team1'],'Actual Points'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'Actual Points'] += 1
                    otherTable.loc[otherTable['Club']==match['team1'],'Draw'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'Draw'] += 1
                    match['result'] = 'draw'
                adjScoreDiff = match['nsxg1']-match['nsxg2']
                if adjScoreDiff>=0.25:
                    otherTable.loc[otherTable['Club']==match['team1'],'nsxG Won'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'nsxG Loss'] += 1
                    
                elif (adjScoreDiff<0.25) & (adjScoreDiff>-0.25):
                    otherTable.loc[otherTable['Club']==match['team1'],'nsxG Draw'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'nsxG Draw'] += 1
                    
                else:
                    otherTable.loc[otherTable['Club']==match['team2'],'nsxG Won'] += 1
                    otherTable.loc[otherTable['Club']==match['team1'],'nsxG Loss'] += 1
                otherTable.loc[otherTable['Club']==match['team1'],'xG For'] += match['xg1']
                otherTable.loc[otherTable['Club']==match['team1'],'xG Against'] += match['xg2']
                otherTable.loc[otherTable['Club']==match['team2'],'xG For'] += match['xg2']
                otherTable.loc[otherTable['Club']==match['team2'],'xG Against'] += match['xg1']
                
                otherTable.loc[otherTable['Club']==match['team1'],'nsxG For'] += match['xg1']
                otherTable.loc[otherTable['Club']==match['team1'],'nsxG Against'] += match['xg2']
                otherTable.loc[otherTable['Club']==match['team2'],'nsxG For'] += match['xg2']
                otherTable.loc[otherTable['Club']==match['team2'],'nsxG Against'] += match['xg1']
                
                avgScore1 = (match['xg1']+match['nsxg1']+match['adj_score1'])/3
                avgScore2 = (match['xg2']+match['nsxg2']+match['adj_score2'])/3
                match['avgscore1'] = avgScore1
                match['avgscore2'] = avgScore2
                
                matchesDictUpdated.append(match)
                
                otherTable.loc[otherTable['Club']==match['team1'],'avg Score For'] += avgScore1
                otherTable.loc[otherTable['Club']==match['team1'],'avg Score Against'] += avgScore2
                otherTable.loc[otherTable['Club']==match['team2'],'avg Score For'] += avgScore2
                otherTable.loc[otherTable['Club']==match['team2'],'avg Score Against'] += avgScore1
                
                avgScoreDiff = avgScore1-avgScore2
                if avgScoreDiff>tolerance:
                    otherTable.loc[otherTable['Club']==match['team1'],'avg Score Won'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'avg Score Loss'] += 1
                    match['avgscoreres'] = 'team1'
                elif (avgScoreDiff<tolerance) & (avgScoreDiff>-1*tolerance):
                    otherTable.loc[otherTable['Club']==match['team1'],'avg Score Draw'] += 1
                    otherTable.loc[otherTable['Club']==match['team2'],'avg Score Draw'] += 1
                    match['avgscoreres'] = 'draw'
                else:
                    otherTable.loc[otherTable['Club']==match['team2'],'avg Score Won'] += 1
                    otherTable.loc[otherTable['Club']==match['team1'],'avg Score Loss'] += 1
                    match['avgscoreres'] = 'team2'
        otherTable.loc[:,'xG Points'] = (otherTable.loc[:,'xG Won']*3) + (otherTable.loc[:,'xG Draw']*1)
        otherTable.loc[:,'nsxG Points'] = (otherTable.loc[:,'nsxG Won']*3) + (otherTable.loc[:,'nsxG Draw']*1)
        otherTable.loc[:,'avg Score Points'] = (otherTable.loc[:,'avg Score Won']*3) + (otherTable.loc[:,'avg Score Draw']*1)
        otherTable.loc[:,'Point Diff'] = otherTable.loc[:,'Actual Points']-otherTable.loc[:,'avg Score Points']
        otherTable.loc[:,'GD'] = otherTable.loc[:,'GScored']-otherTable.loc[:,'GConceded']
        otherTable.sort_values(by=['Actual Points','GD','GScored'],ascending=False,inplace=True)
        origpositions = range(1,21)
        otherTable.loc[:,'Original Position'] = origpositions
        otherTable.sort_values(by=['avg Score Points','avg Score For'],ascending=False,inplace=True)
        avgscorepos = range(1,21)
        otherTable.loc[:,'Avg Score Position'] = avgscorepos
        matchesUpdated = pd.DataFrame.from_dict(matchesDictUpdated)
        columnlist = ['Avg Score Position','Original Position','Club','Matches','Actual Points','avg Score Points','Point Diff','avg Score Won','avg Score Draw','avg Score Loss']
        data = otherTable.to_dict('records')
        columnnames = ['Avg Score Position','Original Position','Club','Matches','Original Points','Avg Score Points','Point Difference','Avg Score Won',
                       'Avg Score Draw','Avg Score Losses']
        columns = [{'name':columnnames[count],'id':i} for count,i in enumerate(columnlist)]
    return(columns,data)

# Create two callback for every store.
for store in ('memory', 'local', 'session'):

    # add a click to the appropriate store.
    @app.callback(Output(store, 'data'),
                  Input('{}-button'.format(store), 'n_clicks'),
                  State(store, 'data'))
    def on_click(n_clicks, data):
        if n_clicks is None:
            # prevent the None callbacks is important with the store component.
            # you don't want to update the store for nothing.
            raise PreventUpdate

        # Give a default data dict with 0 clicks if there's no data.
        data = data or {'clicks': 0}

        data['clicks'] = data['clicks'] + 1
        return data

    # output the stored clicks in the table cell.
    @app.callback(Output('{}-clicks'.format(store), 'children'),
                  # Since we use the data prop in an output,
                  # we cannot get the initial data on load with the data prop.
                  # To counter this, you can use the modified_timestamp
                  # as Input and the data as State.
                  # This limitation is due to the initial None callbacks
                  # https://github.com/plotly/dash-renderer/pull/81
                  Input(store, 'modified_timestamp'),
                  State(store, 'data'))
    def on_data(ts, data):
        if ts is None:
            raise PreventUpdate

        data = data or {}

        return data.get('clicks', 0)


if __name__ == '__main__':
    app.run_server(debug=True,port=1234)