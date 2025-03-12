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

"""# Überblick über Deutschlands Handel

## Gesamtüberblick seit 2008 bis 2024

### Gesamter Export-, Import- und Handelsvolumen-Verlauf Deutschlands
"""

# CSV-Datei einlesen
df_gesamt_deutschland = pd.read_csv('data/1gesamt_deutschland.csv')

# Dash-App erstellen
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Deutschlands Handelsentwicklung"),
    dcc.Graph(id='handel_graph'),
])

@app.callback(
    Output('handel_graph', 'figure'),
    Input('handel_graph', 'id')
)
def update_graph(_):
    fig = go.Figure()

    # Linien für Export, Import und Handelsvolumen
    for col, name, color in zip(
        ['gesamt_export', 'gesamt_import', 'gesamt_handelsvolumen'],
        ['Exportvolumen', 'Importvolumen', 'Gesamthandelsvolumen'],
        ['#1f77b4', '#ff7f0e', '#2ca02c']
    ):
        fig.add_trace(go.Scatter(
            x=df_gesamt_deutschland['Jahr'],
            y=df_gesamt_deutschland[col],
            mode='lines+markers',
            name=name,
            line=dict(width=2, color=color),
            hovertemplate=f'<b>{name}</b><br>Jahr: %{{x}}<br>Wert: %{{y:,.0f}} € €<extra></extra>'
        ))

    # Berechnung der maximalen Y-Achse für Tick-Werte
    max_value = df_gesamt_deutschland[['gesamt_export', 'gesamt_import', 'gesamt_handelsvolumen']].values.max()
    tick_step = 500e9  # 500 Mrd als Schrittgröße
    tickvals = np.arange(0, max_value + tick_step, tick_step)

    # Layout-Anpassungen
    fig.update_layout(
        title='Entwicklung von Export, Import und Handelsvolumen',
        xaxis_title='Jahr',
        yaxis_title='Wert in €',
        yaxis=dict(
            tickformat=',',
            tickvals=tickvals,
            ticktext=[f"{val/1e9:.0f} Mrd" for val in tickvals]
        ),
        legend=dict(title='Kategorie', bgcolor='rgba(255,255,255,0.7)')
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
