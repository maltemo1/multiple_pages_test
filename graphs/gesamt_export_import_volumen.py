# -*- coding: utf-8 -*-
import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# `register_page` erst nach der Haupt-App-Instanz aufrufen!
dash.register_page(__name__, path="/gesamt_export_import_volumen")

# CSV-Datei einlesen
df_gesamt_deutschland = pd.read_csv('data/1gesamt_deutschland.csv')

# Layout für die Seite
layout = html.Div([
    html.H1("Germany's Trade Development"),
    dcc.Graph(id='handel_graph'),
])

# Callback-Funktion zur Aktualisierung des Diagramms
def update_graph():
    fig = go.Figure()

    # Linien für Export, Import und Handelsvolumen
    for col, name, color in zip(
        ['gesamt_export', 'gesamt_import', 'gesamt_handelsvolumen'],
        ['Export Volume', 'Import Volume', 'Total Trade Volume'],
        ['#1f77b4', '#ff7f0e', '#2ca02c']
    ):
        fig.add_trace(go.Scatter(
            x=df_gesamt_deutschland['Jahr'],
            y=df_gesamt_deutschland[col],
            mode='lines+markers',
            name=name,
            line=dict(width=2, color=color),
            hovertemplate=f'<b>{name}</b><br>Year: %{{x}}<br>Value: %{{y:,.0f}} €<extra></extra>'
        ))

    # Berechnung der maximalen Y-Achse für Tick-Werte
    max_value = df_gesamt_deutschland[['gesamt_export', 'gesamt_import', 'gesamt_handelsvolumen']].values.max()
    tick_step = 500e9  # 500 Mrd als Schrittgröße
    tickvals = np.arange(0, max_value + tick_step, tick_step)

    # Layout-Anpassungen
    fig.update_layout(
        title='Development of Export, Import, and Trade Volume',
        xaxis_title='Year',
        yaxis_title='Value in €',
        yaxis=dict(
            tickformat=',',
            tickvals=tickvals,
            ticktext=[f"{val/1e9:.0f} Bn" for val in tickvals]
        ),
        legend=dict(title='Category', bgcolor='rgba(255,255,255,0.7)')
    )

    return fig

# Graph direkt initialisieren
layout.children.append(dcc.Graph(figure=update_graph()))
