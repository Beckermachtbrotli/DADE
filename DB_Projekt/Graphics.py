import pandas as pd
from datetime import datetime

df = pd.read_excel("Datensatz_public_emdat_incl_hist_20250409_modified_2.xlsx", sheet_name="EM-DAT Data (Original)")

relevant_columns = [
    "DisNo.",
    "Historic",
    "Classification Key",
    "Disaster Group",
    "Disaster Subgroup",
    "Disaster Type",
    "Disaster Subtype",
    "Event Name",
    "Country",
    "Subregion",
    "Region",
    "Location",
    "Associated Types",
    "Start Year",
    "Start Month",
    "Start Day",
    "End Year",
    "End Month",
    "End Day",
    "Total Deaths",
    "No. Injured",
    "No. Affected",
    "No. Homeless",
    "Total Affected"
]

df_filtered = df[relevant_columns].copy()
print(df_filtered.head())

#Jahresverlauf
df_events = df_filtered["Start Year"]
df_events = df_events.dropna()

#Anzahl Ereignisse Pro Jahr zählen
current_year = datetime.now().year
events_per_year = df_events.value_counts().sort_index()
df_events_per_year = events_per_year.reset_index()
df_events_per_year.columns = ["Year", "Event Count"]
df_events_per_year = df_events_per_year[df_events_per_year["Year"] < current_year]
print(df_events_per_year)

#Plotten der Ereignisse pro Jahr
import plotly.express as px

# Plot
fig = px.line(
    df_events_per_year,
    x="Year",
    y="Event Count",
    title="Distribution over Time",
    labels={"Year": "Jahr", "Event Count": "Anzahl Katastrophen"}
)

# Optik
fig.update_traces(line=dict(color="orange", width=3))
fig.update_layout(
    plot_bgcolor="white",
    xaxis=dict(showgrid=False, tickformat=".0f"),
    yaxis=dict(showgrid=False),
    font=dict(family="Comic Sans MS", size=14),
    title_font=dict(size=20, family="Comic Sans MS")
)

# Plot anzeigen
fig.show()

df_deaths = df_filtered[["Country", "Total Deaths"]].dropna()

# Gruppieren: Summe der Todesfälle pro Land
deaths_per_country = df_deaths.groupby("Country", as_index=False)["Total Deaths"].sum()

# Plotly-Choroplethenkarte
fig = px.choropleth(
    deaths_per_country,
    locations="Country",
    locationmode="country names",
    color="Total Deaths",
    color_continuous_scale="Reds",
    title="Todesfälle durch Katastrophen pro Land",
)

fig.update_layout(
    geo=dict(showframe=False, showcoastlines=False),
    font=dict(family="Comic Sans MS", size=14),
    title_font=dict(size=20, family="Comic Sans MS")
)

fig.show()