import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from statistics import mean
import glob
from statsmodels.tsa.seasonal import seasonal_decompose
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.ticker import FuncFormatter
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import math
import gdown
import os


# Dash-App erstellen
app = dash.Dash(__name__)

# CSV-Datei einlesen
aggregated_df = pd.read_csv('data/aggregated_df.csv')


        # Funktion zum Formatieren der x-Achse (Euro-Werte) ohne Komma
def formatter(value):
    if value >= 1e9:
        return f'{int(value * 1e-9)} Mrd'  # Ganze Zahl für Milliarden
    elif value >= 1e6:
        return f'{int(value * 1e-6)} Mio'  # Ganze Zahl für Millionen
    elif value >= 1e3:
        return f'{int(value * 1e-3)} K'  # Ganze Zahl für Tausend
    else:
        return f'{int(value)}'


# Layout der Dash-App
app.layout = html.Div([
    html.H1("Top 10 Export- und Importprodukte nach Jahr"),

    # Dropdown-Menü für Jahr
    dcc.Dropdown(
        id='jahr_dropdown',
        options=[{'label': str(j), 'value': j} for j in sorted(aggregated_df['Jahr'].unique())],
        value=2024,  # Standardwert
        clearable=False,
        style={'width': '50%'}
    ),

    # Graphen für Export und Import
    dcc.Graph(id='export_graph'),
    dcc.Graph(id='import_graph'),
])

# Callback für die Aktualisierung der Diagramme
@app.callback(
    [Output('export_graph', 'figure'),
     Output('import_graph', 'figure')],
    Input('jahr_dropdown', 'value')
)
def update_graphs(selected_year):
    # Filterung des DataFrames für das ausgewählte Jahr
    filtered_df = aggregated_df[aggregated_df['Jahr'] == selected_year]

    # Gruppieren nach Jahr, Warencode und Warenkategorie
    aggregated_year_df = filtered_df.groupby(['Jahr', 'Code', 'Label'], as_index=False).agg(
        {'Ausfuhr: Wert': 'sum', 'Einfuhr: Wert': 'sum'}
    )

    # Handelsvolumen berechnen (Exportwert + Importwert)
    aggregated_year_df['Handelsvolumen'] = aggregated_year_df['Ausfuhr: Wert'] + aggregated_year_df['Einfuhr: Wert']

    # Top 10 Exportprodukte nach Exportwert
    top_10_exports = aggregated_year_df.sort_values(by='Ausfuhr: Wert', ascending=False).head(10)

    # Top 10 Importprodukte nach Importwert
    top_10_imports = aggregated_year_df.sort_values(by='Einfuhr: Wert', ascending=False).head(10)

    # Maximaler Wert für die Achse bestimmen
    max_export = top_10_exports['Ausfuhr: Wert'].max()
    max_import = top_10_imports['Einfuhr: Wert'].max()
    max_value = max(max_export, max_import)

    # Tick-Werte in 20-Mrd-Schritten
    tick_max = np.ceil(max_value / 2e10) * 2e10  # Aufrunden auf nächsthöhere 20 Mrd
    tick_vals = np.arange(0, tick_max + 1, 2e10)  # Schrittweite 20 Mrd

    # Export-Plot
    export_fig = go.Figure()
    export_fig.add_trace(go.Bar(
        x=top_10_exports['Ausfuhr: Wert'],
        y=top_10_exports['Label'],
        orientation='h',
        marker_color='blue',
        hovertemplate='Exportwert: %{x:,.0f} €<extra></extra>'
    ))
    export_fig.update_layout(
        title=f"Top 10 Exportprodukte im Jahr {selected_year}",
        xaxis_title="Exportwert (Euro)",
        yaxis_title="Warenkategorie",
        xaxis=dict(tickmode='array', tickvals=tick_vals, ticktext=[formatter(val) for val in tick_vals]),
    )

    # Import-Plot
    import_fig = go.Figure()
    import_fig.add_trace(go.Bar(
        x=top_10_imports['Einfuhr: Wert'],
        y=top_10_imports['Label'],
        orientation='h',
        marker_color='red',
        hovertemplate='Importwert: %{x:,.0f} €<extra></extra>'
    ))
    import_fig.update_layout(
        title=f"Top 10 Importprodukte im Jahr {selected_year}",
        xaxis_title="Importwert (Euro)",
        yaxis_title="Warenkategorie",
        xaxis=dict(tickmode='array', tickvals=tick_vals, ticktext=[formatter(val) for val in tick_vals]),
    )

    return export_fig, import_fig

# App starten
if __name__ == '__main__':
    app.run_server(debug=True)
