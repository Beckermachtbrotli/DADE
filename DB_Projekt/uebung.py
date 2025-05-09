import math
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc

# new: plotly template="plotly_white", https://plotly.com/python/templates/

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.DataFrame(
    {'y': np.random.normal(loc=0, scale=10, size=1000), 'x': np.random.normal(loc=10, scale=2, size=1000)})

app.layout = html.Div([html.Div([html.H1("Dashboard 3")], className="header"), html.Div([dcc.Tabs(id="tabs", children=[

    dcc.Tab(label='Tab One', id="tab_1_graphs", children=[html.Div([
        dbc.Row(
            [dbc.Col([dcc.Dropdown(options=['red', 'green', 'blue'], value='red', id='color', multi=False)], width=6),
             dbc.Col([dcc.Slider(min=math.floor(df['y'].min()), max=math.ceil(df['y'].max()), id="min_value")],
                     width=6)]),
        dbc.Row([dbc.Col([dcc.Graph(id="graph_1")], width=6),
                 dbc.Col([dcc.Graph(id="graph_2")], width=6)])], className="tab_content"), ]),

    dcc.Tab(label='Tab Two', id="tab_2_graphs", children=[html.Div([], className="tab_content")]), ])],
                                                                                        className="content")])


@callback(Output(component_id="graph_1", component_property="figure"), Input(component_id="color", component_property="value"))
def update_graph_1(dropdown_value_color):
    fig = px.histogram(df, x="y", color_discrete_sequence=[dropdown_value_color])
    fig.update_layout(template="plotly_white")
    return fig


@callback(Output(component_id="graph_2", component_property="figure"), Input(component_id="min_value", component_property="value"))
def update_graph_2(min_value):
    if min_value:
        dff = df[df['y'] > min_value]
    else:
        dff = df
    fig = px.scatter(dff, x='x', y='y')
    fig.update_layout(template="plotly_white")
    return fig


if __name__ == '__main__':
    app.run(debug=False, port=8000)
