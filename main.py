import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, html, Output, Input, dcc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

server = app.server 

def load_data():
    emissions_df = pd.read_csv("assets/Dataset/apple_emissions/greenhouse_gas_emissions.csv")
    emissions_df = emissions_df.sort_values(by="Fiscal Year")

    normalized_df = pd.read_csv("assets/Dataset/apple_emissions/normalizing_factors.csv")
    normalized_df = normalized_df.sort_values(by="Fiscal Year")

    return emissions_df, normalized_df

emissions_df, normalized_df = load_data()


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


def create_intensity_chart(emissions_df, normalized_df, selected_scope="All"):
    gross_emissions = emissions_df[emissions_df["Type"] == "Gross emissions"]

    if selected_scope != "All":
        gross_emissions = gross_emissions[gross_emissions["Scope"] == selected_scope]
        title = f"{selected_scope}"
    else:
        title = f"All Scopes"

    total_emissions = gross_emissions.groupby("Fiscal Year", as_index=False)["Emissions"].sum()
    # merged = total_emissions.merge(normalized_df, on="Fiscal Year")
    merged = pd.merge(total_emissions, normalized_df, on="Fiscal Year")

    merged["Emissions Intensity"] = merged["Emissions"] / merged["Revenue"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged["Fiscal Year"], y=merged["Emissions Intensity"],
                             mode="lines+markers", name="Emissions per $ Revenue",
                             line=dict(color='#007aff', width=3)))
    fig.update_layout(title=f'Carbon Intensity {title}',
                      yaxis_title='Metric Tons CO2e / $M Revenue',
                      xaxis_title='Fiscal Year')
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
        ],
        width=6),
    dbc.Col(
            dcc.Graph(
                id="intensity-chart",
                figure=create_intensity_chart(emissions_df, normalized_df),
                style={'height': '400px'},
                config={'responsive': True}
            ),
            width=6
        )
    ])
])

@callback(
    [Output('emissions-chart', 'figure'),
     Output('intensity-chart', 'figure')],
    Input('dropdown-toggle', 'value')
)
def update_emissions(selected_toggle):
    fig_total = create_emissions_chart(emissions_df, selected_toggle)
    fig_intensity = create_intensity_chart(emissions_df, normalized_df, selected_toggle)
    return fig_total, fig_intensity

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)