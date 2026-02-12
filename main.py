import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, ctx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Initialize App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])


# --- Data Loading & Processing ---
def load_all_data():
   try:
       # Load datasets
       emissions = pd.read_csv('assets/Dataset/apple_emissions/greenhouse_gas_emissions.csv')
       normalizing = pd.read_csv('assets/Dataset/apple_emissions/normalizing_factors.csv')
       products = pd.read_csv('assets/Dataset/apple_emissions/carbon_footprint_by_product.csv')


       # Clean Emissions Data
       emissions = emissions.sort_values('Fiscal Year')
      
       # Clean Normalizing Data
       normalizing = normalizing.sort_values('Fiscal Year')


       # Clean Product Data
       products = products.sort_values('Release Year')


       return emissions, normalizing, products
   except FileNotFoundError as e:
       print(f"Error loading data: {e}")
       return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


df_emissions, df_normalizing, df_products = load_all_data()


# --- Helper Functions for Figures ---


def create_total_emissions_chart(df, selected_scope='All'):
   # Filter for total gross emissions
   gross = df[df['Type'] == 'Gross emissions']
  
   if selected_scope != 'All':
       gross = gross[gross['Scope'] == selected_scope]
       title = f'Total Gross Emissions ({selected_scope})'
   else:
       title = 'Total Gross Emissions (All Scopes)'


   # Group by Year
   grouped = gross.groupby('Fiscal Year')['Emissions'].sum().reset_index()
  
   fig = px.area(
       grouped, x='Fiscal Year', y='Emissions',
       title=title,
       labels={'Emissions': 'Metric Tons CO2e'},
       color_discrete_sequence=['#ff5722']
   )
  
   # Add 2030 Net Zero Goal Line (Target: 0)
   fig.add_shape(type="line",
       x0=2015, y0=0, x1=2030, y1=0,
       line=dict(color="green", width=2, dash="dash"),
   )
   fig.add_annotation(x=2030, y=0, text="2030 Goal: Net Zero", showarrow=True, arrowhead=1)
  
   return fig


def create_intensity_chart(df_em, df_norm, selected_scope='All'):
   # Filter for emissions
   gross = df_em[df_em['Type'] == 'Gross emissions']
  
   if selected_scope != 'All':
       gross = gross[gross['Scope'] == selected_scope]
       title_suffix = f'({selected_scope})'
   else:
       title_suffix = '(All Scopes)'


   # Group by Year
   total_emissions = gross.groupby('Fiscal Year')['Emissions'].sum().reset_index()
   merged = pd.merge(total_emissions, df_norm, on='Fiscal Year')

   print(merged)
   print(merged.info())
  
   # Calculate Intensity (Emissions / Revenue in Millions)
   merged['Emission Intensity'] = merged['Emissions'] / merged['Revenue']
  
   fig = go.Figure()
   fig.add_trace(go.Scatter(x=merged['Fiscal Year'], y=merged['Emission Intensity'],
                            mode='lines+markers', name='Emissions per $ Revenue',
                            line=dict(color='#007aff', width=3)))
  
   fig.update_layout(title=f'Carbon Intensity {title_suffix}',
                     yaxis_title='Metric Tons CO2e / $M Revenue')
   return fig


def create_scope_breakdown_chart(df):
   gross = df[df['Type'] == 'Gross emissions']
   # Group by Year and Scope
   fig = px.bar(gross, x='Fiscal Year', y='Emissions', color='Scope',
                title='Emissions Breakdown by Scope (Click to Sync)',
                color_discrete_map={
                    'Scope 1': '#ffcc00',
                    'Scope 2 (market-based)': '#4cd964',
                    'Scope 3': '#5ac8fa'
                })
   # Make bars clickable
   fig.update_layout(clickmode='event+select')
   return fig


def create_scope3_sunburst(df, year):
   # Filter for Scope 3 and Specific Year
   scope3 = df[(df['Scope'] == 'Scope 3') & (df['Fiscal Year'] == year) & (df['Type'] == 'Gross emissions')]
  
   fig = px.sunburst(scope3, path=['Description'], values='Emissions',
                     title=f'Scope 3 Details ({year})',
                     color='Emissions', color_continuous_scale='RdBu_r')
   return fig


def create_product_chart(df):
   fig = px.bar(df, x='Product', y='Carbon Footprint',
                color='Carbon Footprint', # Color by footprint for visual impact
                title='iPhone Carbon Footprint Evolution',
                labels={'Carbon Footprint': 'kg CO2e'},
                color_continuous_scale='Viridis')
   # Add trendline
   fig.add_trace(go.Scatter(x=df['Product'], y=df['Carbon Footprint'], mode='lines', line=dict(color='red', dash='dot'), name='Trend'))
   return fig


# --- KPI Calculations ---
def calculate_kpis(df):
   if df.empty:
       return "N/A", "N/A", "N/A"
  
   gross = df[df['Type'] == 'Gross emissions']
  
   # 1. Total Emissions (Latest Year)
   latest_year = gross['Fiscal Year'].max()
   latest_emissions = gross[gross['Fiscal Year'] == latest_year]['Emissions'].sum()
  
   # 2. Reduction Since 2015
   base_year_emissions = gross[gross['Fiscal Year'] == 2015]['Emissions'].sum()
   reduction = ((latest_emissions - base_year_emissions) / base_year_emissions) * 100
  
   # 3. Largest Contributor (Latest Year)
   largest_scope = gross[gross['Fiscal Year'] == latest_year].groupby('Scope')['Emissions'].sum().idxmax()
  
   return f"{latest_emissions/1e6:.1f} M", f"{reduction:.1f}%", largest_scope


kpi_total, kpi_reduction, kpi_scope = calculate_kpis(df_emissions)


def calculate_scorecard_items(df):
    if df.empty:
        return []
    
    gross = df[df['Type'] == 'Gross emissions']
    
    categories = {
        "Transport": "Product transportation (upstream and downstream)",
        "Manufacturing": "Manufacturing (purchased goods and services)",
        "Business Travel": "Business travel"
    }
    
    items = []
    
    for label, desc in categories.items():
        v2015 = gross[(gross['Fiscal Year'] == 2015) & (gross['Description'] == desc)]['Emissions'].sum()
        v2022 = gross[(gross['Fiscal Year'] == 2022) & (gross['Description'] == desc)]['Emissions'].sum()
        
        if v2015 != 0:
            change = ((v2022 - v2015) / v2015) * 100
        else:
            change = 0 
            
        # Determine color
        if change < 0:
            color = "success" # Reduction is good
        elif change > 0:
            color = "danger" # Increase is bad
        else:
            color = "warning" # No change
            
        items.append(dbc.ListGroupItem(f"{label}: {change:+.1f}%", color=color))
        
    return items


# --- Layout ---


app.layout = dbc.Container([
   # Header
   dbc.Row([
       dbc.Col(html.H1("Corporate Climate Emissions Tracker", className="text-center my-4"), width=12),
       dbc.Col(html.P("Tracking progress towards 2030 Net Zero Goal", className="text-center text-muted"), width=12),
   ]),
  
   # KPI Row
   dbc.Row([
       dbc.Col(dbc.Card(dbc.CardBody([html.H4(kpi_reduction, className="text-danger" if "-" not in kpi_reduction else "text-success"), html.P("Change Since 2015", className="text-muted")]), className="text-center"), width=4),
       dbc.Col(dbc.Card(dbc.CardBody([html.H4(kpi_total), html.P(f"Total Emissions ({df_emissions['Fiscal Year'].max()})", className="text-muted")]), className="text-center"), width=4),
       dbc.Col(dbc.Card(dbc.CardBody([html.H4(kpi_scope), html.P("Largest Contributor", className="text-muted")]), className="text-center"), width=4),
   ], className="mb-4"),


   # Row 1: Trends
   dbc.Row([
       dbc.Col([
           dcc.Dropdown(
               id='scope-filter',
               options=[
                   {'label': 'All Scopes', 'value': 'All'},
                   {'label': 'Scope 1 (Direct)', 'value': 'Scope 1'},
                   {'label': 'Scope 2 (Energy)', 'value': 'Scope 2 (market-based)'},
                   {'label': 'Scope 3 (Value Chain)', 'value': 'Scope 3'}
               ],
               value='All',
               clearable=False,
               className="mb-2"
           ),
           dcc.Graph(id='total-emissions-chart', style={'height': '400px'}, config={'responsive': True})
       ], width=6),
       dbc.Col(dcc.Graph(id='intensity-chart', figure=create_intensity_chart(df_emissions, df_normalizing), style={'height': '400px'}, config={'responsive': True}), width=6),
   ]),


   # Row 2: Scope Analysis
   dbc.Row([
       dbc.Col(dcc.Graph(id='scope-breakdown-chart', figure=create_scope_breakdown_chart(df_emissions), style={'height': '400px'}, config={'responsive': True}), width=6),
       dbc.Col([
           html.Br(),
           html.Label("Select Year for Scope 3 Detail:"),
           dcc.Slider(
               id='year-slider',
               min=df_emissions['Fiscal Year'].min(),
               max=df_emissions['Fiscal Year'].max(),
               value=df_emissions['Fiscal Year'].max(),
               marks={str(year): str(year) for year in df_emissions['Fiscal Year'].unique()},
               step=None
           ),
           dcc.Graph(id='scope3-sunburst', style={'height': '400px'}, config={'responsive': True})
       ], width=6),
   ], className="mt-4"),


   # Row 3: Product & Scorecard
   dbc.Row([
       dbc.Col(dcc.Graph(figure=create_product_chart(df_products), style={'height': '400px'}, config={'responsive': True}), width=8), 
       dbc.Col(dbc.Card([
            dbc.CardHeader("Performance Scorecard (2015 vs 2022)"),
            dbc.ListGroup(
                calculate_scorecard_items(df_emissions),
                flush=True
            )
       ]), width=4),
   ], className="mt-4 mb-5"),


], fluid=True)


# --- Callbacks ---


# Callback 1: Update Total Emissions AND Intensity Chart based on Dropdown
@app.callback(
   [Output('total-emissions-chart', 'figure'),
    Output('intensity-chart', 'figure')],
   Input('scope-filter', 'value')
)
def update_charts(selected_scope):
   fig_total = create_total_emissions_chart(df_emissions, selected_scope)
   fig_intensity = create_intensity_chart(df_emissions, df_normalizing, selected_scope)
   return fig_total, fig_intensity


# Callback 2: Update Slider based on click in Bar Chart
@app.callback(
   Output('year-slider', 'value'),
   Input('scope-breakdown-chart', 'clickData'),
   prevent_initial_call=False
)
def sync_slider_with_click(click_data):
   if click_data:
       # Extract year from the clicked point
       year = click_data['points'][0]['x']
       return year
   return df_emissions['Fiscal Year'].max() # Default to latest year


# Update Sunburst based on Slider (which might have been updated by click)
@app.callback(
   Output('scope3-sunburst', 'figure'),
   Input('year-slider', 'value')
)
def update_sunburst(selected_year):
   return create_scope3_sunburst(df_emissions, selected_year)


if __name__ == '__main__':
   app.run(debug=False, host='0.0.0.0')

