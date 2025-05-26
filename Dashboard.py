import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from scraper import fetch_market_cap_data

# Fetch live market cap data
df = fetch_market_cap_data()

# Load ETF mapping
etf_df = pd.read_csv("etf_data.csv")

# Build pie chart
fig = px.pie(
    df,
    names="Asset",
    values="Weight (%)",
    title="Global Asset Allocation by Market Cap",
    hole=0.4
)
fig.update_traces(textinfo='percent+label')

# Build Dash app
app = dash.Dash(__name__)
app.title = "Global Market Portfolio Dashboard"

app.layout = html.Div([
    html.H1("🌍 Global Market Portfolio Dashboard"),

    dcc.Graph(figure=fig),

    html.H2("💼 ETF Implementation Suggestions"),
    html.P("These low-cost ETFs are mapped to global asset classes."),

    html.Table([
        html.Thead(html.Tr([html.Th(col) for col in etf_df.columns])),
        html.Tbody([
            html.Tr([html.Td(etf_df.iloc[i][col]) for col in etf_df.columns])
            for i in range(len(etf_df))
        ])
    ], style={"width": "100%", "border": "1px solid gray", "margin-top": "20px"})
])

if __name__ == "__main__":
    app.run(debug=True)
