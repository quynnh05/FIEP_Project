# === Step 1: Install Required Packages ===
# pip install dash pandas

# === Step 2: Create a file: app.py ===
import dash
from dash import dcc, html, Input, Output, State
import pandas as pd

# === Step 3: Sample ETF Dataset (replace this with real data or database connection) ===
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

# === Step 4: Build Dash App ===
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
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

if __name__ == '__main__':
    app.run(debug=True, port=8050)


