import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Daten einlesen
df_original = pd.read_excel('Datensatz_public_emdat_incl_hist_20250409_modified_2.xlsx',
                            sheet_name='EM-DAT Data (Original)')

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Impact of disasters worldwide"),

    html.Div([
        # Linke Spalte mit zwei Dropdowns nebeneinander und darunter die Karte
        html.Div([
            # Zwei Dropdowns nebeneinander
            html.Div([
                html.Div([
                    html.Label("Select Disaster Group:"),
                    dcc.Dropdown(
                        id='disaster-group-dropdown',
                        options=[
                            {'label': 'All', 'value': 'All'},
                            {'label': 'Natural', 'value': 'Natural'},
                            {'label': 'Technological', 'value': 'Technological'}
                        ],
                        value='All',
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '10%'}),

                html.Div([
                    html.Label("Select Metric:"),
                    dcc.Dropdown(
                        id='metric-dropdown',
                        options=[
                            {'label': 'Total Deaths', 'value': 'Total Deaths'},
                            {'label': 'Number Disaster', 'value': 'Count'},
                            {'label': 'Total Damages', 'value': 'Total Damages'}
                        ],
                        value='Total Deaths',
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'width': '48%', 'display': 'inline-block'})
            ], style={'display': 'flex', 'marginBottom': '30px'}),

            # Year Slider
            html.Div([
                html.Label("Select Year:"),
                dcc.Slider(
                    id="year-slider",
                    min=1900,
                    max=2025,
                    value=2020,
                    step=1,
                    marks={year: {'label': str(year), 'style': {'fontSize': '10px'}} for year in range(1900, 2025, 10)},
                    tooltip={"placement": "bottom", "always_visible": False}
                ),
            ], style={'marginBottom': '30px'}),

            dcc.Graph(id='map-fig')
        ], style={'width': '60%', 'display': 'inline-block', 'paddingRight': '2%', 'verticalAlign': 'top'}),

        # Rechte Spalte mit zwei Grafiken
        html.Div([
            dcc.Graph(id='bar-fig'),
            dcc.Graph(id='line-fig')
        ], style={'width': '38%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ])
])

# Callback zur Aktualisierung der Diagramme
@app.callback(
    Output('map-fig', 'figure'),
    Output('bar-fig', 'figure'),
    Output('line-fig', 'figure'),
    Input('disaster-group-dropdown', 'value')
)
def update_graphs(selected_group):
    if selected_group == 'All':
        df = df_original.copy()
    else:
        df = df_original[df_original['Disaster Group'] == selected_group]

    # Weltkarte
    map_df = df.groupby('Country', as_index=False)['Total Deaths'].sum()
    map_fig = px.choropleth(
        map_df,
        locations='Country',
        locationmode='country names',
        color='Total Deaths',
        color_continuous_scale='Reds',
        title=f'Total Deaths by Country ({selected_group})',
        template='simple_white'
    )
    map_fig.update_layout(
        height=600,
        coloraxis_colorbar=dict(
            orientation='h',  # horizontal
            x=0.5,  # zentriert (x von 0 bis 1)
            xanchor='center',
            y=-0.0,  # unterhalb der Karte
            yanchor='top',
            title='Total Deaths'
        )
    )

    # Balkendiagramm
    grouped = df.groupby('Disaster Subtype', as_index=False)['Total Deaths'].sum()
    top5 = grouped.sort_values('Total Deaths', ascending=False).head(7)
    bar_fig = px.bar(
        top5.sort_values('Total Deaths'),
        x='Total Deaths',
        y='Disaster Subtype',
        template='simple_white',
        orientation='h',
        title=f'Top 7 Disaster Subtypes by Total Deaths ({selected_group})'
    )
    bar_fig.update_traces(marker_color='#a63603')

    # Liniendiagramm
    line_df = df.groupby('Start Year', as_index=False)['Total Deaths'].sum()
    line_fig = px.line(
        line_df,
        x='Start Year',
        y='Total Deaths',
        template='simple_white',
        title=f'Total Deaths per Year ({selected_group})'
    )
    line_fig.update_traces(line_color='#fdae6b')
    line_fig.update_layout(xaxis_title='Year', yaxis_title='Total Deaths')

    return map_fig, bar_fig, line_fig

if __name__ == '__main__':
    app.run(debug=True)
