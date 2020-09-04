import dash

app = dash.Dash('my app')

server = app.server

from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd
import numpy as np

soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,count(tree_id)' +\
        '&$group=spc_common').replace(' ', '%20')
soql_trees = pd.read_json(soql_url)
unique_trees = soql_trees['spc_common']
unique_trees = unique_trees.dropna()

app.layout = html.Div([

    html.H1('Arborist App'),

    dcc.Dropdown(id='Borough_Selection',
                 options=[
                 {'label': 'Brooklyn', 'value': 'Brooklyn'},
                 {'label': 'Bronx', 'value': 'Bronx'},
                 {'label': 'Manhattan', 'value': 'Manhattan'},
                 {'label': 'Queens', 'value': 'Queens'},
                 {'label': 'Staten Island', 'value': 'Staten Island'},
                 ], value = 'Brooklyn'),


    dcc.Dropdown(id='Species_Selection',
                 options=[
                 {'label': unique_trees[i], 'value': unique_trees[i]} for i in range(len(unique_trees))
                 ], value = unique_trees[0]),

    dcc.Graph(id = 'overall'),
    dcc.Graph(id = 'health'),
    dcc.Graph(id = 'stewardship')

])

@app.callback(
    Output('overall', 'figure'),
    Input('Borough_Selection', 'value'))
def update_graphs(borough):
    boro = borough
    soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,health,count(tree_id)' +\
        '&$where=boroname=\'{}\'' +\
        '&$group=spc_common,health').format(boro).replace(' ', '%20')
    df = pd.read_json(soql_url)
    tree_df = df
    tree_df['prop'] = tree_df.loc[:,'count_tree_id']/tree_df.groupby('spc_common')['count_tree_id'].transform(sum)
    trace1 = go.Bar(x=tree_df.loc[tree_df['health'] == 'Good','spc_common'], y=tree_df.loc[tree_df['health'] == 'Good','prop'])
    trace2 = go.Bar(x=tree_df.loc[tree_df['health'] == 'Fair','spc_common'], y=tree_df.loc[tree_df['health'] == 'Fair','prop'])
    trace3 = go.Bar(x=tree_df.loc[tree_df['health'] == 'Poor','spc_common'], y=tree_df.loc[tree_df['health'] == 'Poor','prop'])

    return {
    'data': [trace1, trace2, trace3],
    'layout':
    go.Layout(
        title='Tree Health in {}'.format(boro), barmode = 'stack')
    }

@app.callback(
    Output('health', 'figure'),
    [Input('Borough_Selection', 'value'), Input('Species_Selection', 'value')])
def update_graphs(borough, species):
    boro = borough
    soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,health,count(tree_id)' +\
        '&$where=boroname=\'{}\'' +\
        '&$group=spc_common,health').format(boro).replace(' ', '%20')
    df = pd.read_json(soql_url)
    tree_df = df[df['spc_common'] == species]
    tree_df['prop'] = tree_df.loc[:,'count_tree_id']/sum(tree_df.loc[:,'count_tree_id'])
    trace1 = go.Bar(x=tree_df.loc[:,'health'], y=tree_df.loc[:,'prop'])

    return {
    'data': [trace1],
    'layout':
    go.Layout(
        title='{} Tree Health in {} by proportion'.format(species, boro))
    }


@app.callback(
    Output('stewardship', 'figure'),
    [Input('Borough_Selection', 'value'), Input('Species_Selection', 'value')])
def update_graph2(borough, species):
    boro = borough
    soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,health,steward,count(tree_id)' +\
        '&$where=boroname=\'{}\'' +\
        '&$group=spc_common,health,steward').format(boro).replace(' ', '%20')
    df = pd.read_json(soql_url)
    tree_df = df[df['spc_common'] == species]
    trace1 = go.Bar(x=tree_df.loc[tree_df['health'] == 'Good', 'steward'], y=tree_df.loc[tree_df['health'] == 'Good','count_tree_id'], name = 'Good')
    trace2 = go.Bar(x=tree_df.loc[tree_df['health'] == 'Fair', 'steward'], y=tree_df.loc[tree_df['health'] == 'Good','count_tree_id'], name = 'Fair')
    trace3 = go.Bar(x=tree_df.loc[tree_df['health'] == 'Poor', 'steward'], y=tree_df.loc[tree_df['health'] == 'Good','count_tree_id'], name = 'Poor')

    return {
    'data': [trace1, trace2, trace3],
    'layout':
    go.Layout(
        title='{} Tree Health in {} by stewardship'.format(species, boro), barmode = 'stack')
    }

if __name__ == '__main__':
    app.run_server(debug = True)
