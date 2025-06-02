import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import yfinance as yf
import datetime

# === ETF Data (for ETF Recommendation Tool) ===
etf_data = pd.DataFrame([
    {"Sector": "Technology", "ETF": "EXV3.DE", "Name": "iShares STOXX Europe 600 Technology", "Price": 340.50},
    {"Sector": "Healthcare", "ETF": "HEAL.L", "Name": "iShares Healthcare Innovation UCITS", "Price": 65.30},
    {"Sector": "Financials", "ETF": "BNKE.PA", "Name": "Lyxor Euro Stoxx Banks", "Price": 23.10},
    {"Sector": "Consumer Goods", "ETF": "XCGD.DE", "Name": "Xtrackers Consumer Discretionary", "Price": 89.90},
    {"Sector": "Energy", "ETF": "IESU.L", "Name": "iShares MSCI Europe Energy", "Price": 34.60},
    {"Sector": "Utilities", "ETF": "UTIL.DE", "Name": "SPDR MSCI Europe Utilities", "Price": 77.20},
    {"Sector": "Real Estate", "ETF": "IPRP.L", "Name": "iShares European Property Yield", "Price": 42.75},
    {"Sector": "Industrials", "ETF": "XIND.DE", "Name": "Xtrackers MSCI Europe Industrials", "Price": 51.30},
    {"Sector": "Materials", "ETF": "XMAT.DE", "Name": "iShares MSCI Europe Materials", "Price": 68.90},
    {"Sector": "Telecommunications", "ETF": "TELE.PA", "Name": "Lyxor STOXX Europe 600 Telecom", "Price": 27.45},
])

# === Global Market Portfolio Data ===
asset_classes = {
    'Equities': {'weight': 0.55, 'ticker': 'VT'},
    'Bonds': {'weight': 0.25, 'ticker': 'AGG'},
    'Real Estate': {'weight': 0.10, 'ticker': 'VNQ'},
    'Commodities': {'weight': 0.05, 'ticker': 'DBC'},
    'Gold': {'weight': 0.03, 'ticker': 'GLD'},
    'Cash': {'weight': 0.02, 'ticker': 'BIL'}
}

start_date = datetime.datetime.now() - datetime.timedelta(days=365 * 5)
end_date = datetime.datetime.now()
price_data = pd.DataFrame()

for asset, info in asset_classes.items():
    data = yf.download(info['ticker'], start=start_date, end=end_date, auto_adjust=False, progress=False)
    if 'Close' in data.columns:
        price_data[asset] = data['Close']

price_data.dropna(inplace=True)
returns = price_data.pct_change().dropna()
weights = [info['weight'] for info in asset_classes.values()]
returns['Portfolio'] = returns.dot(weights)
cumulative_returns = (1 + returns).cumprod()
volatility = returns.std() * (252 ** 0.5)
volatility_text = [f"{asset}: {volatility[asset]:.2%}" for asset in asset_classes.keys()]
volatility_text.append(f"Portfolio: {volatility['Portfolio']:.2%}")

# === App Initialization ===
app = dash.Dash(__name__)
server = app.server

# === ETF Tab Layout ===
etf_tab = html.Div([
    html.H2("💼 ETF Recommendation Tool (EUR-based Investors)"),
    html.Label("Step 1: Select sectors you're interested in:"),
    dcc.Dropdown(
        id='sector-dropdown',
        options=[{'label': s, 'value': s} for s in etf_data['Sector'].unique()],
        multi=True,
        placeholder="Select sectors...",
    ),
    html.Br(),
    html.Label("Step 2: Enter your investment budget (EUR):"),
    dcc.Input(
        id='budget-input',
        type='number',
        placeholder="e.g. 1000",
        min=0,
        step=50
    ),
    html.Br(), html.Br(),
    html.Button('🎯 Get ETF Suggestions', id='suggest-button', n_clicks=0),
    html.Hr(),
    html.Div(id='etf-suggestion-output', style={'whiteSpace': 'pre-line'})
])

# === Portfolio Tab Layout ===
portfolio_tab = html.Div([
    html.H1("Global Market Portfolio Dashboard", style={"textAlign": "center"}),

    html.Div([
        dcc.Graph(
            figure=px.pie(
                names=list(asset_classes.keys()),
                values=[v['weight'] for v in asset_classes.values()],
                title="Global Market Portfolio Allocation",
                hole=0.3
            )
        )
    ], style={"width": "50%", "display": "inline-block"}),

    html.Div([
        dcc.Graph(
            figure=px.line(
                cumulative_returns,
                x=cumulative_returns.index,
                y=cumulative_returns.columns,
                title="Cumulative Returns Over 5 Years"
            )
        )
    ], style={"width": "50%", "display": "inline-block"}),

    html.H3("Annualized Volatility (5Y)", style={"textAlign": "center", "marginTop": "30px"}),
    html.Ul([html.Li(v) for v in volatility_text], style={"textAlign": "center", "fontSize": "18px"})
])

# === Combined Layout with Tabs ===
app.layout = html.Div([
    dcc.Tabs(id="tabs", value='tab-etf', children=[
        dcc.Tab(label='ETF Recommendation Tool', value='tab-etf'),
        dcc.Tab(label='Global Market Portfolio', value='tab-portfolio'),
    ]),
    html.Div(id='tab-content')
])

# === Callbacks ===

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def render_tab(tab_name):
    if tab_name == 'tab-etf':
        return etf_tab
    elif tab_name == 'tab-portfolio':
        return portfolio_tab

@app.callback(
    Output('etf-suggestion-output', 'children'),
    Input('suggest-button', 'n_clicks'),
    State('sector-dropdown', 'value'),
    State('budget-input', 'value')
)
def suggest_etfs(n_clicks, selected_sectors, budget):
    if not n_clicks or not selected_sectors or budget is None:
        return "⚠️ Please select sectors and enter your budget."

    filtered = etf_data[(etf_data['Sector'].isin(selected_sectors)) & (etf_data['Price'] <= budget)]

    if filtered.empty:
        return "🚫 No ETFs found matching your budget and selected sectors."

    result = f"🔍 ETFs matching your preferences (<= €{budget:.2f}):\n\n"
    for _, row in filtered.iterrows():
        result += f"- {row['Name']} ({row['ETF']}) — €{row['Price']:.2f}\n"
    return result

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True, port=8050)
