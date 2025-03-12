from dash import dcc, html
import dash
import pandas as pd
import plotly.graph_objects as go
import os

# Define path to the data file
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "1gesamt_deutschland.csv")

# Read CSV file
df_gesamt_deutschland = pd.read_csv(data_path)

# Create the layout for this page
layout = html.Div([
    html.H1("Deutschlands Handelsentwicklung"),
    dcc.Graph(id='handel_graph')
])

# Callback to update the graph
@dash.callback(
    dash.Output('handel_graph', 'figure'),
    dash.Input('handel_graph', 'id')
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
            hovertemplate=f'<b>{name}</b><br>Jahr: %{{x}}<br>Wert: %{{y:,.0f}} €<extra></extra>'
        ))

    # Berechnung der maximalen Y-Achse für Tick-Werte
    max_value = df_gesamt_deutschland[['gesamt_export', 'gesamt_import', 'gesamt_handelsvolumen']].values.max()
    tick_step = 500e9  # 500 Mrd als Schrittgröße
    tickvals = list(range(0, int(max_value) + int(tick_step), int(tick_step)))

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
