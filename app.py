# Create emissions graph. Emissions (y-axis), year (x-axis)
# Loading data
#   - Read data
#   - Get emissions by type e.g Gross
#   - Since we are trying to get the emissions, sum the emissions for each year.
#   - 
# Components: Dropdown of scopes, area chart
# The graph should have interactivity where if a scope is selected in the dropdown, the graph is updated
# Initialize a dash app. Set external stylesheets to LUX

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, dcc, Output, Input


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

def load_data():
    emissions_df = pd.read_csv("assets/Dataset/apple_emissions/greenhouse_gas_emissions.csv")
    emissions_df = emissions_df.sort_values('Fiscal Year')

    return emissions_df


gross_emissions = load_data()


def create_total_emissions_graph(df, selected_scope="All"):
    gross_emissions = df[df["Type"] == "Gross emissions"]

    if selected_scope != "All":
        print(f"Selected scope: {selected_scope}")
        gross_emissions = gross_emissions[gross_emissions["Scope"] == selected_scope]
        title = f"Gross emissions {selected_scope}"
    else:
        title = f"Gross emissions (All)"


    total_emissions = gross_emissions.groupby("Fiscal Year", as_index=False)['Emissions'].sum()

    fig = px.area(
        total_emissions,
        title=title,
        x="Fiscal Year",
        y="Emissions",
        labels={"Emissions": "CO2 emissions (Tonnes)"},
        color_discrete_sequence=["#ff5722"]
    )

    return fig

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Total Emissions', className="text-center my-5"),
            html.P("Emissions to get to 2030", className="text-center")
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="emissions-dropdown",
                options=[
                    {"label": "All Scopes", "value": "All"},
                    {"label": "Scope 1", "value": "Scope 1"},
                    {"label": "Scope 2", "value": "Scope 2 (market-based)"},
                    {"label": "Scope 3", "value": "Scope 3"}
                ],
                value="All",
                clearable=False
            ),
           dcc.Graph(
            id='gross-emissions',
            style={'height': '400px'}
           )
        ])
    ])
])

@app.callback(
    Output('gross-emissions','figure'),
    Input('emissions-dropdown', 'value')
)
def update_emissions(selected_scope):
    fig_total = create_total_emissions_graph(gross_emissions, selected_scope)

    return fig_total

if __name__ == '__main__':
    app.run()