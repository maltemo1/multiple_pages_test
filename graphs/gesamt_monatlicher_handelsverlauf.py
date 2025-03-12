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


# CSV-Datei einlesen
gesamt_deutschland_monthly = pd.read_csv('data/gesamt_deutschland_monthly.csv')


# Funktion zur Formatierung der Y-Achse
def formatter(value):
    if value >= 1e9:
        return f'{value / 1e9:.0f} Mrd'
    elif value >= 1e6:
        return f'{value / 1e6:.0f} Mio'
    elif value >= 1e3:
        return f'{value / 1e3:.0f} K'
    else:
        return str(value)



# Dash-App erstellen
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Monatlicher Handelsverlauf Deutschlands"),

    dcc.Dropdown(
        id='jahr_dropdown',
        options=[{'label': str(j), 'value': j} for j in sorted(gesamt_deutschland_monthly['Jahr'].unique())],
        value=2024,  # Standardwert
        clearable=False,
        style={'width': '50%'}
    ),

    dcc.Graph(id='monatlicher_handel_graph'),
])

@app.callback(
    Output('monatlicher_handel_graph', 'figure'),
    Input('jahr_dropdown', 'value')
)
def update_graph(year_selected):
    df_year_monthly = gesamt_deutschland_monthly[gesamt_deutschland_monthly['Jahr'] == year_selected]

    fig = go.Figure()

    for col, name, color in zip(
        ['export_wert', 'import_wert', 'handelsvolumen_wert'],
        ['Exportvolumen', 'Importvolumen', 'Gesamthandelsvolumen'],
        ['#1f77b4', '#ff7f0e', '#2ca02c']
    ):
        fig.add_trace(go.Scatter(
            x=df_year_monthly['Monat'],
            y=df_year_monthly[col],
            mode='lines+markers',
            name=name,
            line=dict(width=2, color=color),
            hovertemplate=f'<b>{name}</b><br>Monat: %{{x}}<br>Wert: %{{y:,.0f}} € €<extra></extra>'
        ))

    # Maximale Werte bestimmen
    max_value = df_year_monthly[['export_wert', 'import_wert', 'handelsvolumen_wert']].values.max()

    # Auf nächste 50 Mrd aufrunden
    rounded_max = math.ceil(max_value / 50e9) * 50e9

    # Y-Achse in 25-Mrd-Schritten skalieren
    tickvals = np.arange(0, rounded_max + 1, 25e9)
    ticktext = [formatter(val) for val in tickvals]

    # Achsen und Layout
    fig.update_layout(
        title=f'Monatlicher Export-, Import- und Handelsverlauf Deutschlands im Jahr {year_selected}',
        xaxis_title='Monat',
        yaxis_title='Wert in €',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        ),
        yaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext
        ),
        legend=dict(title='Kategorie', bgcolor='rgba(255,255,255,0.7)')
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
