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
        # Linke Spalte
        html.Div([
            html.H1("Impact of disasters worldwide"),
            # Dropdown-Box bleibt einzeln
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
                            {'label': 'Total Damages', 'value': 'Total Damages'},
                            {'label': 'Number of Disasters', 'value': 'Count'}
                        ],
                        value='Total Deaths',
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'width': '48%', 'display': 'inline-block'})
            ], style={'display': 'flex', 'marginBottom': '30px'}),

            # Gemeinsame Box für Slider + Map
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
                dcc.Graph(id='map-fig')
            ], className='white-box'),

        ], style={'width': '60%', 'display': 'inline-block', 'paddingRight': '2%', 'verticalAlign': 'top'}),

        # Rechte Spalte mit Bar- und Line-Chart in Boxen
        html.Div([
            html.Div(
                [dcc.Graph(id='bar-fig', style={'height': '380px'})],
                className='white-box',
                style={'marginBottom': '20px'}  # Abstand zwischen den Boxen
            ),
            html.Div(
                [dcc.Graph(id='line-fig', style={'height': '380px'})],
                className='white-box'
            )
        ], style={'width': '38%', 'display': 'inline-block', 'verticalAlign': 'top'})

], className='app-background')


# Callback zur Aktualisierung der Diagramme
@app.callback(
    Output('map-fig', 'figure'),
    Output('bar-fig', 'figure'),
    Output('line-fig', 'figure'),
    Input('disaster-group-dropdown', 'value'),
    Input('year-slider', 'value'),
    Input('metric-dropdown', 'value')
)
def update_graphs(selected_group, selected_year, selected_metric):
    # Filter nach Gruppe
    if selected_group == 'All':
        df = df_original.copy()
    else:
        df = df_original[df_original['Disaster Group'] == selected_group]

    # Filter nach Jahr für die Karte
    df_map = df[df['Start Year'] == selected_year]

    # Aggregation je nach gewählter Metrik
    if selected_metric == 'Count':
        map_df = df_map.groupby('Country', as_index=False).size()
        map_df.columns = ['Country', 'Number of Disasters']
        color_column = 'Number of Disasters'
    else:
        map_df = df_map.groupby('Country', as_index=False)[selected_metric].sum()
        color_column = selected_metric

    # Weltkarte
    map_fig = px.choropleth(
        map_df,
        locations='Country',
        locationmode='country names',
        color=color_column,
        color_continuous_scale='Reds',
        title=f'{color_column} by Country in {selected_year} ({selected_group})',
        template='simple_white'
    )
    map_fig.update_layout(
        height=600,
        title_x=0.08,
        title_y=0.88,
        coloraxis_colorbar=dict(
            orientation='h',
            x=0.5,
            xanchor='center',
            y=-0.0,
            yanchor='top',
            title=color_column
        )
    )

    # Balkendiagramm
    if selected_metric == 'Count':
        grouped = df['Disaster Subtype'].value_counts().nlargest(7).reset_index()
        grouped.columns = ['Disaster Subtype', 'Number of Disasters']
        x_col = 'Number of Disasters'
    else:
        grouped = df.groupby('Disaster Subtype', as_index=False)[selected_metric].sum()
        grouped = grouped.sort_values(selected_metric, ascending=False).head(7)
        x_col = selected_metric

    bar_fig = px.bar(
        grouped.sort_values(x_col),
        x=x_col,
        y='Disaster Subtype',
        template='simple_white',
        orientation='h',
        title=f'Top 7 Disaster Subtypes by {x_col} ({selected_group})'
    )
    bar_fig.update_traces(marker_color='#a63603')

    # Liniendiagramm
    if selected_metric == 'Count':
        # Zähle die Anzahl der Ereignisse pro Jahr
        line_df = df.groupby('Start Year').size().reset_index(name='Number of Disasters')
        y_col = 'Number of Disasters'
    else:
        # Summiere die gewählte Metrik pro Jahr
        line_df = df.groupby('Start Year', as_index=False)[selected_metric].sum()
        y_col = selected_metric

    line_fig = px.line(
        line_df,
        x='Start Year',
        y=y_col,
        template='simple_white',
        title=f'{y_col} per Year ({selected_group})'
    )
    line_fig.update_traces(line_color='#a63603')
    line_fig.update_layout(xaxis_title='Year', yaxis_title=y_col)

    return map_fig, bar_fig, line_fig

if __name__ == '__main__':
    app.run(debug=True)
