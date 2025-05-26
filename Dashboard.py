import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import yfinance as yf
import datetime

# Asset class definitions
asset_classes = {
    'Equities': {'weight': 0.55, 'ticker': 'VT'},
    'Bonds': {'weight': 0.25, 'ticker': 'AGG'},
    'Real Estate': {'weight': 0.10, 'ticker': 'VNQ'},
    'Commodities': {'weight': 0.05, 'ticker': 'DBC'},
    'Gold': {'weight': 0.03, 'ticker': 'GLD'},
    'Cash': {'weight': 0.02, 'ticker': 'BIL'}
}

# Download price data
start_date = datetime.datetime.now() - datetime.timedelta(days=365 * 5)
end_date = datetime.datetime.now()
price_data = pd.DataFrame()

for asset, info in asset_classes.items():
    data = yf.download(info['ticker'], start=start_date, end=end_date, auto_adjust=False, progress=False)
    if 'Close' in data.columns:
        price_data[asset] = data['Close']

price_data.dropna(inplace=True)

# If no data, raise error
if price_data.empty:
    raise Exception("No valid price data was loaded.")

# Calculate returns and cumulative returns
returns = price_data.pct_change().dropna()
weights = [info['weight'] for info in asset_classes.values()]
returns['Portfolio'] = returns.dot(weights)
cumulative_returns = (1 + returns).cumprod()

# Annualized volatility
volatility = returns.std() * (252 ** 0.5)
volatility_text = [f"{asset}: {volatility[asset]:.2%}" for asset in asset_classes.keys()]
volatility_text.append(f"Portfolio: {volatility['Portfolio']:.2%}")

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Global Market Portfolio Dashboard"

# Pie chart for asset allocation
pie_fig = px.pie(
    names=list(asset_classes.keys()),
    values=[v['weight'] for v in asset_classes.values()],
    title="Global Market Portfolio Allocation",
    hole=0.3
)

# Line chart for cumulative returns
line_fig = px.line(
    cumulative_returns,
    x=cumulative_returns.index,
    y=cumulative_returns.columns,
    title="Cumulative Returns Over 5 Years"
)

# Dash layout
app.layout = html.Div([
    html.H1("Global Market Portfolio Dashboard", style={"textAlign": "center"}),

    html.Div([
        dcc.Graph(figure=pie_fig)
    ], style={"width": "50%", "display": "inline-block"}),

    html.Div([
        dcc.Graph(figure=line_fig)
    ], style={"width": "50%", "display": "inline-block"}),

    html.H3("Annualized Volatility (5Y)", style={"textAlign": "center", "marginTop": "30px"}),
    html.Ul([html.Li(v) for v in volatility_text], style={"textAlign": "center", "fontSize": "18px"})
])

if __name__ == '__main__':
    app.run(debug=True)
