import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import datetime
import numpy as np

# === Asset Classes with ETF Tickers and Weights (market cap-based) ===
asset_classes = {
    'Global Equities': {'weight': 0.55, 'ticker': 'VT'},
    'Global Bonds': {'weight': 0.25, 'ticker': 'AGG'},
    'Global Real Estate': {'weight': 0.10, 'ticker': 'VNQ'},
    'Commodities': {'weight': 0.05, 'ticker': 'DBC'},
    'Gold': {'weight': 0.03, 'ticker': 'GLD'},
    'Cash': {'weight': 0.02, 'ticker': 'BIL'}
}

start_date = datetime.datetime.now() - datetime.timedelta(days=365 * 5)
end_date = datetime.datetime.now()

price_data = pd.DataFrame()
etf_info = {}

for label, info in asset_classes.items():
    data = yf.download(info['ticker'], start=start_date, end=end_date, auto_adjust=True, progress=False)
    if not data.empty and 'Close' in data.columns:
        price_data[label] = data['Close']
        etf_info[label] = {
            'ticker': info['ticker'],
            'price': round(data['Close'].iloc[-1], 2),
            'return_5y': round((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1, 4),
            'data': data['Close']
        }

price_data.dropna(inplace=True)
returns = price_data.pct_change().dropna()
weights = np.array([info['weight'] for info in asset_classes.values()])
returns['Global Portfolio'] = returns.dot(weights)
cumulative_returns = (1 + returns).cumprod()

annualized_return = (cumulative_returns.iloc[-1]) ** (1 / 5) - 1
annualized_volatility = returns.std() * np.sqrt(252)
sharpe_ratio = annualized_return / annualized_volatility
correlation_matrix = returns.corr()
rolling_volatility = returns.rolling(window=90).std() * np.sqrt(252)

cumulative_max = cumulative_returns.cummax()
drawdowns = (cumulative_returns - cumulative_max) / cumulative_max
max_drawdowns = drawdowns.min()

app = dash.Dash(__name__)
app.title = "Global Portfolio Dashboard"

app.layout = html.Div(id='main-div', children=[
    html.H1("🌍 Global Market Portfolio Dashboard", id="title", style={"textAlign": "center", "fontSize": "32px"}),

    dcc.RadioItems(
        id='theme-toggle',
        options=[
            {'label': 'Light Mode', 'value': 'light'},
            {'label': 'Dark Mode', 'value': 'dark'}
        ],
        value='light',
        labelStyle={'display': 'inline-block', 'marginRight': '20px'},
        style={'textAlign': 'center', 'marginBottom': '20px'}
    ),

    html.Div(id='date-range', style={'textAlign': 'center', 'marginBottom': '20px'},
             children=[html.P(f"Data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")]),

    dcc.Tabs(id="tabs", value='overview', children=[
        dcc.Tab(label="📊 Overview", value='overview', children=[
            html.Div([
                html.H3("Actual Global Portfolio Allocation (Market Cap-Based)", style={"textAlign": "center"}),
                dcc.Graph(id='pie-chart'),

                html.H3("Performance Summary", style={"textAlign": "center", "marginTop": "30px"}),
                html.Div(id='performance-table'),

                dcc.Graph(id='cumulative-return-chart')
            ])
        ]),

        dcc.Tab(label="📈 Risk & Correlation", value='risk', children=[
            dcc.Graph(id='rolling-vol-chart'),

            dcc.Graph(id='corr-matrix'),

            html.Div([
                html.H4("Drawdown Analysis"),
                html.P("Select an asset class to view its historical drawdown."),
                dcc.Dropdown(
                    id='drawdown-asset-selector',
                    options=[{'label': col, 'value': col} for col in drawdowns.columns],
                    value='Global Portfolio'
                ),
                dcc.Graph(id='drawdown-chart')
            ], style={"padding": "0 10%"})
        ]),

        dcc.Tab(label="💡 ETF Implementation", value='etf', children=[
            html.Div([
                html.H3("How to Invest in the Global Portfolio", style={"textAlign": "center"}),
                html.P("The ETFs below are recommended for replicating the current global asset class exposure."),

                html.Label("💰 Investment Amount ($):"),
                dcc.Slider(id='amount-slider', min=1000, max=100000, step=1000, value=10000,
                           marks={i: f"${i:,}" for i in range(1000, 100001, 25000)},
                           tooltip={"placement": "bottom", "always_visible": True}),
                html.Br(),

                html.Div(id='etf-breakdown')
            ], style={"padding": "0 10%"})
        ])
    ])
])

@app.callback(
    Output('main-div', 'style'),
    Input('theme-toggle', 'value')
)
def update_background(theme):
    return {
        'backgroundColor': '#1e1e1e' if theme == 'dark' else '#ffffff',
        'color': '#f0f0f0' if theme == 'dark' else '#000000',
        'fontFamily': 'Segoe UI, sans-serif',
        'padding': '20px'
    }

@app.callback(
    Output('pie-chart', 'figure'),
    Input('theme-toggle', 'value')
)
def update_pie_chart(theme):
    fig = px.pie(
        names=list(asset_classes.keys()),
        values=[info['weight'] for info in asset_classes.values()],
        hole=0.45,
        title="Global Asset Class Allocation",
        color_discrete_sequence=px.colors.sequential.Teal
    )
    fig.update_layout(title_x=0.5, template='plotly_dark' if theme == 'dark' else 'plotly_white')
    return fig

@app.callback(
    Output('cumulative-return-chart', 'figure'),
    Input('theme-toggle', 'value')
)
def update_cumulative_return(theme):
    fig = px.line(
        cumulative_returns,
        x=cumulative_returns.index,
        y=cumulative_returns.columns,
        title="Cumulative Return Over Time"
    )
    fig.update_layout(title_x=0.5, legend_title_text="ETF", template='plotly_dark' if theme == 'dark' else 'plotly_white')
    return fig

@app.callback(
    Output('performance-table', 'children'),
    Input('theme-toggle', 'value')
)
def update_performance_table(theme):
    style = {
        "width": "80%",
        "margin": "0 auto",
        "marginTop": "20px",
        "borderCollapse": "collapse",
        "textAlign": "center",
        "border": "1px solid gray",
        "backgroundColor": "#1e1e1e" if theme == 'dark' else '#ffffff',
        "color": "#f0f0f0" if theme == 'dark' else '#000000'
    }
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Asset Class"),
            html.Th("Annualized Return"),
            html.Th("Annualized Volatility"),
            html.Th("Sharpe Ratio"),
            html.Th("Max Drawdown")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(col),
                html.Td(f"{annualized_return[col]:.2%}"),
                html.Td(f"{annualized_volatility[col]:.2%}"),
                html.Td(f"{sharpe_ratio[col]:.2f}"),
                html.Td(f"{max_drawdowns[col]:.2%}")
            ]) for col in cumulative_returns.columns
        ])
    ], style=style)

@app.callback(
    Output('rolling-vol-chart', 'figure'),
    Input('theme-toggle', 'value')
)
def update_rolling_vol(theme):
    fig = go.Figure([
        go.Scatter(x=rolling_volatility.index, y=rolling_volatility[col], mode='lines', name=col)
        for col in rolling_volatility.columns
    ])
    fig.update_layout(title="90-Day Rolling Volatility (Annualized)", yaxis_title="Volatility",
                      template='plotly_dark' if theme == 'dark' else 'plotly_white', title_x=0.5)
    return fig

@app.callback(
    Output('corr-matrix', 'figure'),
    Input('theme-toggle', 'value')
)
def update_corr_matrix(theme):
    fig = px.imshow(correlation_matrix, text_auto=True, color_continuous_scale='Teal',
                    title="Correlation Matrix", aspect="auto")
    fig.update_layout(title_x=0.5, template='plotly_dark' if theme == 'dark' else 'plotly_white')
    return fig

@app.callback(
    Output('drawdown-chart', 'figure'),
    Input('drawdown-asset-selector', 'value'),
    State('theme-toggle', 'value')
)
def update_drawdown_chart(asset, theme):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=drawdowns.index, y=drawdowns[asset], mode='lines', name=asset))
    fig.update_layout(title=f"Drawdown Over Time: {asset}", yaxis_title="Drawdown",
                      template='plotly_dark' if theme == 'dark' else 'plotly_white', title_x=0.5)
    return fig

@app.callback(
    Output('etf-breakdown', 'children'),
    Input('amount-slider', 'value'),
    State('theme-toggle', 'value')
)
def update_etf_allocation(amount, theme):
    rows = []
    for asset, info in asset_classes.items():
        etf = etf_info.get(asset, {'ticker': '-', 'price': 1, 'return_5y': 0})
        alloc = amount * info['weight']
        shares = int(alloc // etf['price'])
        rows.append(html.Tr([
            html.Td(asset),
            html.Td(etf['ticker']),
            html.Td(f"${etf['price']:.2f}"),
            html.Td(f"{etf['return_5y']*100:.2f}%"),
            html.Td(f"${alloc:,.0f}"),
            html.Td(f"{shares} shares")
        ]))

    return html.Table([
        html.Thead(html.Tr([
            html.Th("Asset Class"),
            html.Th("ETF Ticker"),
            html.Th("Current Price"),
            html.Th("5Y Return"),
            html.Th("Allocation ($)"),
            html.Th("Estimated Shares")
        ])),
        html.Tbody(rows)
    ], style={
        "width": "100%",
        "marginTop": "20px",
        "borderCollapse": "collapse",
        "textAlign": "center",
        "border": "1px solid gray"
    })

if __name__ == '__main__':
    app.run(debug=True)
