from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# CSV-Datei einlesen
csv_path = os.path.join("data", "aggregated_df.csv")
aggregated_df = pd.read_csv(csv_path)

# Funktion zum Formatieren der x-Achse
def formatter(value):
    if value >= 1e9:
        return f'{int(value * 1e-9)} Mrd'
    elif value >= 1e6:
        return f'{int(value * 1e-6)} Mio'
    elif value >= 1e3:
        return f'{int(value * 1e-3)} K'
    else:
        return f'{int(value)}'

# Layout-Funktion für das Modul
def create_layout():
    return html.Div([
        html.H1("Top 10 Export- und Importprodukte nach Jahr"),

        # Dropdown-Menü für Jahr
        dcc.Dropdown(
            id='jahr_dropdown',
            options=[{'label': str(j), 'value': j} for j in sorted(aggregated_df['Jahr'].unique())],
            value=2024,
            clearable=False,
            style={'width': '50%'}
        ),

        # Graphen für Export und Import
        dcc.Graph(id='export_graph'),
        dcc.Graph(id='import_graph'),
    ])

# Callback-Registrierung für die Haupt-App
def register_callbacks(app):
    @app.callback(
        [Output('export_graph', 'figure'),
         Output('import_graph', 'figure')],
        Input('jahr_dropdown', 'value')
    )
    def update_graphs(selected_year):
        filtered_df = aggregated_df[aggregated_df['Jahr'] == selected_year]

        aggregated_year_df = filtered_df.groupby(['Jahr', 'Code', 'Label'], as_index=False).agg(
            {'Ausfuhr: Wert': 'sum', 'Einfuhr: Wert': 'sum'}
        )

        aggregated_year_df['Handelsvolumen'] = aggregated_year_df['Ausfuhr: Wert'] + aggregated_year_df['Einfuhr: Wert']

        # Top 10 Export- und Importprodukte
        top_10_exports = aggregated_year_df.sort_values(by='Ausfuhr: Wert', ascending=False).head(10)
        top_10_imports = aggregated_year_df.sort_values(by='Einfuhr: Wert', ascending=False).head(10)

        max_value = max(top_10_exports['Ausfuhr: Wert'].max(), top_10_imports['Einfuhr: Wert'].max())
        tick_max = np.ceil(max_value / 2e10) * 2e10
        tick_vals = np.arange(0, tick_max + 1, 2e10)

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
