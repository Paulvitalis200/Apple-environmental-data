import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import callback, html, Output, Input, dcc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

def load_data():
    df = pd.read_csv("assets/Dataset/apple_emissions/greenhouse_gas_emissions.csv")

    df = df.sort_values(by="Fiscal Year")
    return df

emissions_df = load_data()


def create_emissions_chart(data, selected_scope):
    emissions_data = data[data["Type"] == "Gross emissions"]


    if selected_scope != "All":
        emissions_data = emissions_data[emissions_data["Scope"] == selected_scope]
        title = f"Gross Emissions ({selected_scope})"
    else:
        title = f"Gross Emissions {selected_scope}"


    total_data = emissions_data.groupby("Fiscal Year", as_index=False)["Emissions"].sum()

    fig = px.area(
       total_data,
        x="Fiscal Year",
        y="Emissions",
        labels={'Emissions': 'Metric Tons CO2e'},
        title=title
    )

    fig.add_shape(type="line",
        x0=2015, y0=0, x1=2030, y1=0,
        line=dict(color="green", width=2, dash="dash"),
    )
    fig.add_annotation(x=2030, y=0, text="2030 Goal: Net Zero", showarrow=True, arrowhead=1)
    

    return fig

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Apple Environmental Dashboard", className="text-center my-4"), width=12),
        dbc.Col(html.P("Tracking progress towards 2030 Net Zero Goal", className="text-center text-muted"), width=12),
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="dropdown-toggle",
                options=[
                    {"label": "All Scopes", "value": "All"},
                    {"label": "Scope 1", "value": "Scope 1"},
                    {"label": "Scope 2", "value": "Scope 2 (market-based)"},
                    {"label": "Scope 3", "value": "Scope 3"}
                ],
                className="mb-5",
                value="All"
            ),
            dcc.Graph(
                id="emissions-chart",
                style={"height": "400px"}
            )
        ])
    ])
])

@callback(
    Output('emissions-chart', 'figure'),
    Input('dropdown-toggle', 'value')
)
def update_emissions(selected_toggle):
    fig = create_emissions_chart(emissions_df, selected_toggle)
    return fig

if __name__ == "__main__":
    app.run()