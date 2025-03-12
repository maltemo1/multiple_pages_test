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
df_reduced = pd.read_csv('data/df_reduced.csv')

# Funktion zum Formatieren der x-Achse (Mrd, Mio, Tsd)
def formatter(value):
    if abs(value) >= 1e9:
        return f'{int(value * 1e-9)} Mrd'
    elif abs(value) >= 1e6:
        return f'{int(value * 1e-6)} Mio'
    elif abs(value) >= 1e3:
        return f'{int(value * 1e-3)} Tsd'
    else:
        return f'{int(value)}'

# Dash-App erstellen
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Handelsdifferenzen nach Warengruppe"),

    # Dropdown für Jahresauswahl
    dcc.Dropdown(
        id='jahr_dropdown',
        options=[{'label': str(j), 'value': j} for j in sorted(df_reduced['Jahr'].unique())],
        value=2024,  # Standardjahr
        clearable=False,
        style={'width': '50%'}
    ),

    # Balkendiagramme für Export- und Importdifferenzen
    dcc.Graph(id='export_diff_graph'),
    dcc.Graph(id='import_diff_graph'),
])

@app.callback(
    [Output('export_diff_graph', 'figure'),
     Output('import_diff_graph', 'figure')],
    Input('jahr_dropdown', 'value')
)
def update_graphs(selected_year):
    # Daten für das ausgewählte Jahr filtern
    df_current = df_reduced[df_reduced['Jahr'] == selected_year]
    df_previous = df_reduced[df_reduced['Jahr'] == selected_year - 1]

    df_diff = pd.merge(df_current, df_previous, on="Label", suffixes=('_current', '_previous'))
    df_diff['export_differenz'] = df_diff['Ausfuhr: Wert_current'] - df_diff['Ausfuhr: Wert_previous']
    df_diff['import_differenz'] = df_diff['Einfuhr: Wert_current'] - df_diff['Einfuhr: Wert_previous']

    # Top & Bottom 4 Export-Differenzen
    top_4_export_diff = df_diff.nlargest(4, 'export_differenz')
    bottom_4_export_diff = df_diff.nsmallest(4, 'export_differenz')
    export_diff_min = min(bottom_4_export_diff['export_differenz'].min(), 0)
    export_diff_max = max(top_4_export_diff['export_differenz'].max(), 0)

    # Top & Bottom 4 Import-Differenzen
    top_4_import_diff = df_diff.nlargest(4, 'import_differenz')
    bottom_4_import_diff = df_diff.nsmallest(4, 'import_differenz')
    import_diff_min = min(bottom_4_import_diff['import_differenz'].min(), 0)
    import_diff_max = max(top_4_import_diff['import_differenz'].max(), 0)

    # Generiere die X-Achsen-Ticks (Schrittgröße: 1 Mrd)
    step_size = 2e9
    export_ticks = np.arange(math.floor(export_diff_min / step_size) * step_size,
                             math.ceil(export_diff_max / step_size) * step_size + step_size, step_size)

    import_ticks = np.arange(math.floor(import_diff_min / step_size) * step_size,
                             math.ceil(import_diff_max / step_size) * step_size + step_size, step_size)

    # Graph für Exportdifferenzen
    export_fig = go.Figure()

    export_fig.add_trace(go.Bar(
        y=top_4_export_diff['Label'],
        x=top_4_export_diff['export_differenz'],
        orientation='h',
        name='Top 4 Zuwächse',
        marker_color='green',
        hovertemplate='Exportzuwachs: %{x:,.0f} €<extra></extra>'
    ))

    export_fig.add_trace(go.Bar(
        y=bottom_4_export_diff['Label'],
        x=bottom_4_export_diff['export_differenz'],
        orientation='h',
        name='Top 4 Rückgänge',
        marker_color='red',
        hovertemplate='Exportrückgang: %{x:,.0f} €<extra></extra>'
    ))

    export_fig.update_layout(
        title=f'Exportdifferenzen nach Warengruppe ({selected_year} vs. {selected_year - 1})',
        xaxis_title='Exportdifferenz (EUR)',
        xaxis=dict(tickmode='array', tickvals=export_ticks, ticktext=[formatter(val) for val in export_ticks]),
        yaxis_title='Warengruppe',
        xaxis_range=[export_diff_min * 1.1, export_diff_max * 1.3],
    )

    # Graph für Importdifferenzen
    import_fig = go.Figure()

    import_fig.add_trace(go.Bar(
        y=top_4_import_diff['Label'],
        x=top_4_import_diff['import_differenz'],
        orientation='h',
        name='Top 4 Zuwächse',
        marker_color='green',
        hovertemplate='Importzuwachs: %{x:,.0f} €<extra></extra>'
    ))

    import_fig.add_trace(go.Bar(
        y=bottom_4_import_diff['Label'],
        x=bottom_4_import_diff['import_differenz'],
        orientation='h',
        name='Top 4 Rückgänge',
        marker_color='red',
        hovertemplate='Importrückgang: %{x:,.0f} €<extra></extra>'
    ))

    import_fig.update_layout(
        title=f'Importdifferenzen nach Warengruppe ({selected_year} vs. {selected_year - 1})',
        xaxis_title='Importdifferenz (EUR)',
        xaxis=dict(tickmode='array', tickvals=import_ticks, ticktext=[formatter(val) for val in import_ticks]),
        yaxis_title='Warengruppe',
        xaxis_range=[import_diff_min * 1.1, import_diff_max * 1.3],
    )

    return export_fig, import_fig

if __name__ == '__main__':
    app.run_server(debug=True)
