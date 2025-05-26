import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from scraper import fetch_market_cap_data

# Fetch data from scraper
df = fetch_market_cap_data()

# Create the pie chart
fig = px.pie(
    df,
    names="Asset",
    values="Weight (%)",
    title="Global Asset Allocation by Market Cap",
    hole=0.4
)
fig.update_traces(textinfo='percent+label')

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div(children=[
    html.H1("Global Portfolio Dashboard", style={"textAlign": "center"}),
    dcc.Graph(figure=fig)
])

# Run the app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
