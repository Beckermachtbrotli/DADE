import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import ctx

# Daten einlesen
df_original = pd.read_excel('Datensatz_public_emdat_incl_hist_20250409_modified_2.xlsx',
                            sheet_name='EM-DAT Data (Original)')

# Dash App with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
])

app.layout = html.Div([
        # Linke Spalte
        html.Div([
            # Titelzeile mit Info-Icon
            html.Div([
                html.H1("Impact of disasters worldwide", style={
                    'display': 'inline-block',
                    'marginBottom': '0',
                    'marginRight': '6px'
                }),
                dbc.Button(
                    html.I(className="bi bi-info-circle"),
                    id="info-icon",
                    color="link",
                    size="sm",
                    className="info-button",
                    title="Information about data quality & source",
                    style={
                        "padding": "0",
                        "fontSize": "18px",
                        "color": "#6c757d",
                        "transform": "translateY(2px)"
                    }
                )
            ], style={"marginBottom": "10px", "display": "flex", "alignItems": "flex-end"}),
            # Info-Modal
            dbc.Modal(
                [
                    dbc.ModalHeader("Datenqualität & Quelle"),
                    dbc.ModalBody([
                        html.P("Die Daten vor dem Jahr 2000 sind unvollständig oder weniger zuverlässig."),
                        html.P("Quelle: EM-DAT – The International Disaster Database (www.emdat.be)")
                    ]),
                    dbc.ModalFooter(
                        dbc.Button("Schliessen", id="close-modal", color="secondary", className="ms-auto", n_clicks=0)
                    )
                ],
                id="info-modal",
                is_open=False,
                centered=True
            ),

            # Dropdown-Box
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
                ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '4%'}),

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
                ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '4%'}),

                html.Div(
                    dbc.Button(
                        [html.I(className="bi bi-arrow-counterclockwise me-2"), "Reset Country Selection"],
                        id='reset-country-button',
                        color='secondary',
                        outline=True,
                        className="mt-4"
                    ),
                    style={'width': '30%', 'display': 'inline-block'}
                )
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

        ], style={'width': '60%', 'display': 'inline-block', 'paddingRight': '2%', "bottom": "0"}),

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

], className='app-background', style = {"with":"100%"})



# Callback zur Aktualisierung der Diagramme
@app.callback(
    Output('map-fig', 'figure'),
    Output('bar-fig', 'figure'),
    Output('line-fig', 'figure'),
    Input('disaster-group-dropdown', 'value'),
    Input('year-slider', 'value'),
    Input('metric-dropdown', 'value'),
    Input('map-fig', 'clickData'),
    Input('reset-country-button', 'n_clicks'),

)

def update_graphs(selected_group, selected_year, selected_metric, map_click, reset_clicks):
    # Reset-Funktion
    triggered_id = ctx.triggered_id if ctx.triggered_id else None
    if triggered_id == 'reset-country-button':
        map_click = None

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

    elif selected_metric == 'Total Damages':
        map_df = df_map.groupby('Country', as_index=False)[selected_metric].sum()
        map_df[selected_metric] = map_df[selected_metric] / 1000
        color_column = selected_metric

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
    try:
        selected_country = map_click["points"][0]["location"] if map_click else None
        if selected_country in df_map["Country"].values:
            df_bar = df_map[df_map["Country"] == selected_country]
        else:
            selected_country = None
            df_bar = df_map
    except (TypeError, IndexError, KeyError):
        selected_country = None
        df_bar = df_map

    if selected_metric == 'Count':
        grouped = df[df['Start Year'] == selected_year]
        if selected_country:
            grouped = grouped[grouped["Country"] == selected_country]
        grouped = grouped['Disaster Subtype'].value_counts().nlargest(7).reset_index()
        grouped.columns = ['Disaster Subtype', 'Number of Disasters']
        x_col = 'Number of Disasters'
    else:
        grouped = df[df['Start Year'] == selected_year]
        if selected_country:
            grouped = grouped[grouped["Country"] == selected_country]
        grouped = grouped.groupby('Disaster Subtype', as_index=False)[selected_metric].sum()
        grouped = grouped.sort_values(selected_metric, ascending=False).head(7)
        if selected_metric == 'Total Damages':
            grouped[selected_metric] = grouped[selected_metric] / 1000

        x_col = selected_metric

    bar_title = f"Disaster subtypes with the most severe impact {selected_year}"
    if selected_country:
        bar_title += f" – {selected_country}"

    bar_fig = px.bar(
        grouped.sort_values(x_col),
        x=x_col,
        y='Disaster Subtype',
        template='simple_white',
        orientation='h',
        title=bar_title
    )
    if selected_metric == 'Total Damages':
        bar_fig.update_layout(xaxis_title="Total Damages (in million US$)")
        bar_fig.update_traces(hovertemplate='%{x:,.2f} million US$')
    else:
        bar_fig.update_layout(xaxis_title=selected_metric)

    bar_fig.update_traces(marker_color='#a63603')

    # Liniendiagramm

    max_year = 2024 #Fehlende Werte für 2025 rausfiltern
    df_filtered_years = df[df['Start Year'] <= max_year].copy()
    if selected_country:
        df_filtered_years = df_filtered_years[df_filtered_years['Country'] == selected_country]
    year_cutoff = 2000 # unverlässliche Daten bis

    if selected_metric == 'Count':
        # Zähle die Anzahl der Ereignisse pro Jahr
        line_df = df_filtered_years.groupby('Start Year').size().reset_index(name='Number of Disasters')
        y_col = 'Number of Disasters'
    else:
        # Summiere die gewählte Metrik pro Jahr
        line_df = df_filtered_years.groupby('Start Year', as_index=False)[selected_metric].sum()
        if selected_metric == 'Total Damages':
            line_df[selected_metric] = line_df[selected_metric] / 1000
        y_col = selected_metric

    line_df_pre_2000 = line_df[line_df['Start Year'] < year_cutoff]
    line_df_post_2000 = line_df[line_df['Start Year'] >= year_cutoff]

    line_fig = go.Figure()

    line_fig.add_trace(go.Scatter(
        x=line_df_pre_2000['Start Year'],
        y=line_df_pre_2000[y_col],
        mode='lines',
        name=f'{y_col} before {year_cutoff}',
        line=dict(color='gray', dash='dot')
    ))

    line_fig.add_trace(go.Scatter(
        x=line_df_post_2000['Start Year'],
        y=line_df_post_2000[y_col],
        mode='lines',
        name=f'{y_col} from {year_cutoff}',
        line=dict(color='#a63603')
    ))

    line_title = f'{y_col} per Year ({selected_group})'
    if selected_country:
        line_title += f" – {selected_country}"

    line_fig.update_layout(
        template='simple_white',
        title=line_title,
        xaxis_title='Year'
    )

    if selected_metric == 'Total Damages':
        line_fig.update_yaxes(title="Total Damages (in million US$)", tickformat=",.2f")
        line_fig.update_traces(hovertemplate='%{y:,.2f} million US$')
    else:
        line_fig.update_yaxes(title=y_col)

    line_fig.update_traces(line_color='#a63603')

    return map_fig, bar_fig, line_fig

#Callback für Infobox
@app.callback(
    Output("info-modal", "is_open"),
    [Input("info-icon", "n_clicks"), Input("close-modal", "n_clicks")],
    prevent_initial_call=True
)
def toggle_modal(n_info, n_close):
    return ctx.triggered_id == "info-icon"

if __name__ == '__main__':
    app.run(debug=True)
