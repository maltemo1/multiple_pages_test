import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math
import os

# Daten laden
df_grouped = pd.read_csv('data/df_grouped.csv')

# Funktion zum Formatieren der x-Achse
def formatter(x, pos):
    if abs(x) >= 1e9:
        return f'{int(x * 1e-9)} Mrd'  
    else:
        return f'{int(x)}'  

# Funktion zum Berechnen der Achsen-Ticks
def generate_ticks(min_value, max_value, step_size):
    min_tick = math.floor(min_value / step_size) * step_size
    max_tick = math.ceil(max_value / step_size) * step_size
    return np.arange(min_tick, max_tick + step_size, step_size)

# Layout-Funktion für das Dashboard
def create_layout():
    return html.Div([
        html.H1("Länder mit größten Export- und Importzuwächsen (absolut)"),
        dcc.Dropdown(
            id='jahr_dropdown_2',
            options=[{'label': str(j), 'value': j} for j in sorted(df_grouped['Jahr'].unique())],
            value=2024,  
            clearable=False,
            style={'width': '50%'}
        ),
        dcc.Graph(id='export_diff_graph'),
        dcc.Graph(id='import_diff_graph'),
        dcc.Graph(id='handelsvolumen_diff_graph'),
    ])

# Callback-Funktion zur Aktualisierung der Graphen
def register_callbacks(app):
    @app.callback(
        [Output('export_diff_graph', 'figure'),
         Output('import_diff_graph', 'figure'),
         Output('handelsvolumen_diff_graph', 'figure')],
        Input('jahr_dropdown_2', 'value')
    )
    def update_graphs(year_selected):
        df_filtered = df_grouped[(df_grouped['Jahr'] == year_selected)]
        df_filtered = df_filtered[~df_filtered['Land'].isin(['Nicht ermittelte Länder und Gebiete', 'Schiffs- und Luftfahrzeugbedarf'])]

        top_4_export_diff = df_filtered.nlargest(4, 'export_differenz')
        bottom_4_export_diff = df_filtered.nsmallest(4, 'export_differenz')
        export_diff_min = min(bottom_4_export_diff['export_differenz'].min(), 0)
        export_diff_max = max(top_4_export_diff['export_differenz'].max(), 0)

        top_4_import_diff = df_filtered.nlargest(4, 'import_differenz')
        bottom_4_import_diff = df_filtered.nsmallest(4, 'import_differenz')
        import_diff_min = min(bottom_4_import_diff['import_differenz'].min(), 0)
        import_diff_max = max(top_4_import_diff['import_differenz'].max(), 0)

        top_4_handelsvolumen_diff = df_filtered.nlargest(4, 'handelsvolumen_differenz')
        bottom_4_handelsvolumen_diff = df_filtered.nsmallest(4, 'handelsvolumen_differenz')
        handelsvolumen_diff_min = min(bottom_4_handelsvolumen_diff['handelsvolumen_differenz'].min(), 0)
        handelsvolumen_diff_max = max(top_4_handelsvolumen_diff['handelsvolumen_differenz'].max(), 0)

        export_ticks = generate_ticks(export_diff_min, export_diff_max, 1e9)
        import_ticks = generate_ticks(import_diff_min, import_diff_max, 1e9)
        handelsvolumen_ticks = generate_ticks(handelsvolumen_diff_min, handelsvolumen_diff_max, 1e9)

        # Graph für Exportdifferenzen
        export_fig = go.Figure()
        export_fig.add_trace(go.Bar(y=top_4_export_diff['Land'], x=top_4_export_diff['export_differenz'],
                                    orientation='h', name='Top 4 Zuwächse', marker_color='green'))
        export_fig.add_trace(go.Bar(y=bottom_4_export_diff['Land'], x=bottom_4_export_diff['export_differenz'],
                                    orientation='h', name='Top 4 Rückgänge', marker_color='red'))
        export_fig.update_layout(title=f'Exportdifferenzen für {year_selected}', xaxis=dict(tickvals=export_ticks))

        # Graph für Importdifferenzen
        import_fig = go.Figure()
        import_fig.add_trace(go.Bar(y=top_4_import_diff['Land'], x=top_4_import_diff['import_differenz'],
                                    orientation='h', name='Top 4 Zuwächse', marker_color='green'))
        import_fig.add_trace(go.Bar(y=bottom_4_import_diff['Land'], x=bottom_4_import_diff['import_differenz'],
                                    orientation='h', name='Top 4 Rückgänge', marker_color='red'))
        import_fig.update_layout(title=f'Importdifferenzen für {year_selected}', xaxis=dict(tickvals=import_ticks))

        # Graph für Handelsvolumendifferenzen
        handelsvolumen_fig = go.Figure()
        handelsvolumen_fig.add_trace(go.Bar(y=top_4_handelsvolumen_diff['Land'], x=top_4_handelsvolumen_diff['handelsvolumen_differenz'],
                                            orientation='h', name='Top 4 Zuwächse', marker_color='green'))
        handelsvolumen_fig.add_trace(go.Bar(y=bottom_4_handelsvolumen_diff['Land'], x=bottom_4_handelsvolumen_diff['handelsvolumen_differenz'],
                                            orientation='h', name='Top 4 Rückgänge', marker_color='red'))
        handelsvolumen_fig.update_layout(title=f'Handelsvolumendifferenzen für {year_selected}',
                                         xaxis=dict(tickvals=handelsvolumen_ticks))

        return export_fig, import_fig, handelsvolumen_fig
