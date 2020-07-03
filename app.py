import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine


engine = create_engine("mysql+mysqlconnector://root:1q2w3e4r@localhost/tsa_claim?host=localhost?port=3306")
conn = engine.connect()
result = conn.execute('SELECT * from tsa_dashboard').fetchall()

tsa = pd.DataFrame(result, columns = result[0].keys())
df = tsa.copy()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def generate_table(dataframe, page_size = 10):
     return dash_table.DataTable(
                id = 'dataTable',
                columns = [{
                    'name': i, 'id': i
                } for i in dataframe.columns],
                data = dataframe.to_dict('records'),
                style_table = {'overflowX': 'scroll'},
                page_action = "native",
                page_current = 0,
                page_size = page_size,
            )

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.H1(
        children='Ujian Modul 2 Dashboard TSA',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dashboard by Dicky Alamsyah', style={
        'textAlign': 'center',
        'color': colors['text']}
    ),

    html.Br(),
    html.Div([html.Div(children =[
        dcc.Tabs(value = 'Tabs', id = 'Tabs', children = [
            
            dcc.Tab(value = 'Tabel', label = 'DataFrame Table', children =[
                html.Center(html.H1('DATAFRAME TSA')),
                html.Div(children =[
                    html.Div(children =[
                        html.P('Claim Site:'),
                            dcc.Dropdown(
                                value = '',
                                id='filter-site',
                                options = [
                                        {'label': 'Motor Vehicle', 'value': 'Motor Vehicle'},
                                        {'label': 'Checked Baggage', 'value': 'Checked Baggage'},
                                        {'label': 'Checkpoint', 'value': 'Checkpoint'},
                                        {'label': 'Bus Station', 'value': 'Bus Station'},
                                        {'label': 'Other', 'value': 'Other'},
                                        {'label': 'All', 'value': ''}])
                    ], className = 'col-3'),

                    html.Div([
                        html.P('Max Rows : '),
                        dcc.Input(
                            id = 'filter-row',
                            type = 'number',
                            value = 10,
                        )
                    ], className = 'col-3'),
                
                    html.Div(children = [
                        html.Button('search',id = 'filter', className = 'btn btn-outline-warning', style= {'marginTop':'2em', 'marginLeft': '0'})
                    ])

                ], className = 'row'),

                html.Br(), 

                html.Div(id = 'div-table', children = [generate_table(tsa)])
            ]),

            dcc.Tab(value = 'Tab-1', label = 'Bar-Chart', children= [
                html.Div(children = [
                    html.Div(children = [
                        html.P('Y1:'),    
                        dcc.Dropdown(
                            id = 'y-axis-1',
                            value = 'Claim Amount',
                            options = [{'label': i, 'value': i} for i in df.select_dtypes('number').columns], 
                        )
                    ], className = 'col-3'),

                    html.Div(children =[
                        html.P('Y2:'),    
                        dcc.Dropdown(
                            id = 'y-axis-2', 
                            value = 'Close Amount',
                            options = [{'label': i, 'value': i} for i in df.select_dtypes('number').columns], 
                        )
                    ], className = 'col-3'),

                    html.Div(children =[
                        html.P('X:'),    
                        dcc.Dropdown(
                            id = 'x-axis-1',
                            value = 'Claim Type',
                            options = [{'label': i, 'value': i} for i in ['Claim Type', 'Claim Site', 'Disposition']], 
                        )
                    ], className = 'col-3')    
                ], className = 'row'),

                html.Div([
                    dcc.Graph(
                        id = 'graph-bar',
                        figure ={
                            'data' : [
                                {'x': df['Claim Type'], 'y': df['Claim Amount'], 'type': 'bar', 'name' :'Claim Amount'},
                                {'x': df['Claim Type'], 'y': df['Close Amount'], 'type': 'bar', 'name': 'Close Amount'}
                            ], 
                            'layout': {
                                'title': 'Bar Chart',
                                'plot_bgcolor': colors['background'],
                                'paper_bgcolor': colors['background'],
                                'font': {
                                'color': colors['text']}  
                            }
                        }
                    )])
            ]),

            dcc.Tab(value = 'Tab-2', label = 'Scatter-Chart', children = [
                html.Div(children = dcc.Graph(
                    id = 'graph-scatter',
                    figure = {'data': [
                        go.Scatter(
                            x = df[df['Claim Type'] == i]['Claim Amount'],
                            y = df[df['Claim Type'] == i]['Close Amount'],
                            text = df[df['Claim Type'] == i]['Status'],
                            mode='markers',
                            name = '{}'.format(i)
                        ) for i in df['Claim Type'].unique()
                    ],
                    'layout':
                        go.Layout(
                            xaxis= {'title': 'Claim Amount'},
                            yaxis={'title': 'Close Amount'},
                            hovermode='closest',
                            title= 'TSA Claim Scatter based Claim Type',
                            paper_bgcolor= colors['background'],
                            plot_bgcolor='rgba(0,0,0,0)',
                            font = dict(color = colors['text'])
                        )
                    }
                ))
            ]),

            dcc.Tab(value = 'Tab-3', label ='Pie-Chart', children = [
                html.Div(
                    dcc.Dropdown(
                        id ='pie-dropdown',
                        value = 'Claim Amount',
                        options = [{'label': i, 'value': i} for i in df.select_dtypes('number').columns]), className = 'col-3'),
                
                html.Div([
                    dcc.Graph(
                        id = 'Pie',
                        figure ={
                            'data' : [
                                go.Pie(
                                    labels = ['{}'.format(i) for i in list(df['Claim Type'].unique())], 
                                                values = [df.groupby('Claim Type').mean()['Claim Amount'][i] for i in list(df['Claim Type'].unique())],
                                                sort = False)
                            ], 
                            'layout':
                                go.Layout(
                                    title = 'Mean Pie Chart',
                                    paper_bgcolor= colors['background'],
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font = dict(color = colors['text']))
                        }
                    )
                ])   
            ])
        ], content_style = {
                'fontFamily': 'Arial',
                'borderBottom': '1px solid #d6d6d6',
                'borderLeft': '1px solid #d6d6d6',
                'borderRight': '1px solid #d6d6d6',
                'padding': '44px'}
        )
    ])
    ])
], style ={
        'maxWidth': '1200px',
        'margin': '0 auto'
    })

@app.callback(
    Output(component_id = 'div-table', component_property = 'children'),
    [Input(component_id = 'filter', component_property = 'n_clicks')],
    [State(component_id = 'filter-row', component_property = 'value'),
    State(component_id = 'filter-site', component_property = 'value')]
)

def update_table(n_clicks, row, site):
    if site == '':
        children = [generate_table(tsa, page_size = row)]
    else:
        children = [generate_table(tsa[tsa['Claim Site'] == site], page_size = row)]            
    return children

@app.callback(
    Output(component_id = 'graph-bar', component_property = 'figure'),
    [Input(component_id = 'y-axis-1', component_property = 'value'),
    Input(component_id = 'y-axis-2', component_property = 'value'),
    Input(component_id = 'x-axis-1', component_property = 'value'),]
)
def create_graph_bar(y1, y2, x1):
    figure = {
        'data' : [
            {'x': df[x1], 'y': df[y1], 'type': 'bar', 'name' :y1},
            {'x': df[x1], 'y': df[y2], 'type': 'bar', 'name': y2}
        ], 
        'layout': {
            'title': 'Bar Chart',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']}
            }  
        }
    return figure                


@app.callback(
    Output(component_id = 'Pie', component_property = 'figure'),
    [Input(component_id = 'pie-dropdown', component_property = 'value')]
)
def create_graph_pie(x):
    figure = {
        'data' : [
            go.Pie(labels = ['{}'.format(i) for i in list(df['Claim Type'].unique())], 
                            values = [df.groupby('Claim Type').mean()[x][i] for i in list(df['Claim Type'].unique())],
                            sort = False)
        ], 
        'layout':
            go.Layout(
                title = 'Mean Pie Chart',
                paper_bgcolor= colors['background'],
                plot_bgcolor='rgba(0,0,0,0)',
                font = dict(color = colors['text']))       
    }
    return figure   

if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='127.0.0.1')