import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Initialisiere Dash mit Unterstützung für Multi-Pages
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Removed use_pages

server = app.server

# Kategorien mit URLs
categories = {
    "Overview of Germany's trade": {
        "Total overview since 2008 to 2024": {
            "Germany's total export, import and trade volume history": "/gesamt_export_import_volumen"
        }
    }
}

# Sidebar-Funktion
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

# Layout mit Sidebar und dynamischem Seiteninhalt
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(render_sidebar(categories), width=3),
            dbc.Col(dash.page_container, width=9)  # Hier wird die jeweilige Seite geladen
        ])
    ])
])

# Nach App-Initialisierung: Import der Seiten (um Reihenfolge sicherzustellen)
import graphs.gesamt_export_import_volumen  # <-- Jetzt erst importieren

if __name__ == "__main__":
    app.run_server(debug=True)
