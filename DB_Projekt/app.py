import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np

# Daten laden
df = pd.read_excel("Datensatz_public_emdat_incl_hist_20250409_modified_2.xlsx", sheet_name="EM-DAT Data (Original)")
df.rename(columns={"Total Damage ('000 US$)": "Total Damages"}, inplace=True)

# Relevante Spalten extrahieren
relevant_columns = [
    "DisNo.", "Historic", "Classification Key", "Disaster Group",
    "Disaster Subgroup", "Disaster Type", "Disaster Subtype", "Event Name",
    "Country", "Subregion", "Region", "Location", "Associated Types",
    "Start Year", "Start Month", "Start Day", "End Year", "End Month",
    "End Day", "Total Deaths", "No. Injured", "No. Affected",
    "No. Homeless", "Total Affected", "Total Damages"
]
df_filtered = df[relevant_columns].copy()

# Visualisierungen vorbereiten
def generate_figures(filtered_df, metric):
    if filtered_df.empty:
        return {}, {}, {}

    # Zeitverlauf
    df_events = filtered_df["Start Year"].dropna()
    events_per_year = df_events.value_counts().sort_index()
    df_events_per_year = events_per_year.reset_index()
    df_events_per_year.columns = ["Year", "Event Count"]

    fig_time = px.line(
        df_events_per_year,
        x="Year",
        y="Event Count",
        title="Distribution over Time",
        labels={"Year": "Jahr", "Event Count": "Anzahl Katastrophen"}
    )
    fig_time.update_traces(line=dict(color="orange", width=3))
    fig_time.update_layout(
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, showline=True, linecolor='black', linewidth=2, tickformat=".0f"),
        yaxis=dict(showgrid=False, showline=True, linecolor='black', linewidth=2),
        font=dict(family="Comic Sans MS", size=14),
        title_font=dict(size=20, family="Comic Sans MS")
    )

    # Karte
    df_deaths = filtered_df[["Country", "Total Deaths"]].dropna()
    deaths_per_country = df_deaths.groupby("Country", as_index=False)["Total Deaths"].sum()
    fig_map = px.choropleth(
        deaths_per_country,
        locations="Country",
        locationmode="country names",
        color="Total Deaths",
        color_continuous_scale="Reds",
        title="Todesfälle durch Katastrophen pro Land",
    )
    fig_map.update_layout(
        geo=dict(showframe=False, showcoastlines=False),
        font=dict(family="Comic Sans MS", size=14),
        title_font=dict(size=20, family="Comic Sans MS"),
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        coloraxis_colorbar=dict(
            title="Tote",
            thickness=12,
            len=0.5,
            x=1.02
        )
    )
    # Balkendiagramm
    if metric == "Count":
        df_types = filtered_df["Disaster Type"].value_counts().nlargest(4).reset_index()
        df_types.columns = ["Disaster Type", "Count"]
    else:
        df_types = filtered_df[["Disaster Type", metric]].dropna()
        df_types = df_types.groupby("Disaster Type", as_index=False)[metric].sum()
        df_types = df_types.sort_values(by=metric, ascending=False).head(4)

    fig_bar = px.bar(
        df_types,
        x=metric if metric != "Count" else "Count",
        y="Disaster Type",
        orientation="h",
        title=f"Greatest Disaster Groups ({filtered_df['Start Year'].min()}–{filtered_df['Start Year'].max()})",
        text_auto=True
    )
    fig_bar.update_traces(marker_color="orange")
    fig_bar.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        font=dict(family="Comic Sans MS", size=14),
        title_font=dict(size=20, family="Comic Sans MS"),
        plot_bgcolor="white"
    )

    return fig_map, fig_time, fig_bar

# Dash App
app = dash.Dash(__name__)
app.title = "Disaster Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Impact of Disasters Worldwide", style={"color": "#fbbf24", "fontFamily": "Comic Sans MS"}),

    html.Div([
        dcc.Dropdown(
            id="disaster-group-dropdown",
            options=[{"label": i, "value": i} for i in sorted(df_filtered["Disaster Group"].dropna().unique())],
            placeholder="Disaster Group",
            clearable=True,
            style={"minWidth": "150px", "width": "100%"}
        ),
        dcc.Dropdown(
            id="metric-dropdown",
            options=[
                {"label": "Deaths", "value": "Total Deaths"},
                {"label": "Number Disaster", "value": "Count"},
                {"label": "Total Damages", "value": "Total Damages"}
            ],
            placeholder="Group",
            value="Total Deaths",
            style={"minWidth": "150px", "width": "100%"}
        ),
        html.Div([
            dcc.RangeSlider(
                id="year-slider",
                min=int(df_filtered["Start Year"].min()),
                max=int(df_filtered["Start Year"].max()),
                step=1,
                value=[1990, 2023],
                marks={year: {'label': str(year), 'style': {'fontSize': '10px'}} for year in range(1960, 2026, 20)},
                tooltip={"placement": "bottom", "always_visible": False},
                allowCross=False
            ),
            html.Div(id="year-range-text", style={"marginTop": "10px", "fontWeight": "bold", "fontFamily": "Comic Sans MS"})
        ], style={"flex": "1"})
    ], style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"}),

    html.Div([
        dcc.Graph(id="map", style={"width": "65%"}),
        html.Div([
            dcc.Graph(id="bar"),
            dcc.Graph(id="time"),
        ], style={"width": "35%"})
    ], style={"display": "flex", "gap": "20px"})
])

# Haupt-Callback für die Visualisierungen
@app.callback(
    Output("map", "figure"),
    Output("time", "figure"),
    Output("bar", "figure"),
    Input("disaster-group-dropdown", "value"),
    Input("metric-dropdown", "value"),
    Input("year-slider", "value")
)
def update_graphs(selected_group, selected_metric, selected_years):
    dff = df_filtered.copy()
    if selected_group:
        dff = dff[dff["Disaster Group"] == selected_group]
    if selected_years:
        dff = dff[(dff["Start Year"] >= selected_years[0]) & (dff["Start Year"] <= selected_years[1])]
    return generate_figures(dff, selected_metric)

# Callback für Textanzeige des Zeitraums
@app.callback(
    Output("year-range-text", "children"),
    Input("year-slider", "value")
)
def update_year_text(year_range):
    return f"Zeitraum: {year_range[0]}–{year_range[1]}"

# Run
if __name__ == '__main__':
    app.run(debug=True)

