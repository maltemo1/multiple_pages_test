import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import os

# Initialize Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Importing page layouts (this will include your different graph pages)
from graphs import gesamt_export_import_volumen

# Kategorien und Subkategorien mit Links für zukünftige Navigation
def create_nav_structure():
    return {
        "Überblick über Deutschlands Handel": {
            "Gesamtüberblick seit 2008 bis 2024": {
                "Gesamter Export-, Import- und Handelsvolumen-Verlauf Deutschlands": "/gesamt_export_import_volumen"
            }
        }
    }

categories = create_nav_structure()

def render_sidebar(categories):
    def create_items(subcategories):
        items = []
        for name, value in subcategories.items():
            if isinstance(value, dict):
                items.append(
                    dbc.AccordionItem(
                        dbc.Accordion(create_items(value), start_collapsed=True),
                        title=name
                    )
                )
            else:
                items.append(
                    html.Div(
                        html.A(name, href=value, style={"textDecoration": "none", "color": "black", "padding": "5px", "display": "block"})
                    )
                )
        return items
    
    return dbc.Accordion([
        dbc.AccordionItem(
            dbc.Accordion(create_items(subcategories), start_collapsed=True),
            title=category
        )
        for category, subcategories in categories.items()
    ], start_collapsed=True)

sidebar = html.Div([
    html.H2("Navigation", className="display-4"),
    html.Hr(),
    render_sidebar(categories)
], className="sidebar")

# Define the main layout
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(sidebar, width=3),
            dbc.Col(
                html.Div(id='page-content'), 
                width=9
            )
        ])
    ])
])

# Callback to switch between pages
@app.callback(
    dash.Output('page-content', 'children'),
    [dash.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == "/gesamt_export_import_volumen":
        return gesamt_export_import_volumen.layout
    else:
        return html.H3("Bitte wählen Sie eine Kategorie aus der Sidebar.")

if __name__ == "__main__":
    app.run_server(debug=True)
