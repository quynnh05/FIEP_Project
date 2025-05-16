import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import base64
import webbrowser
import threading

app = dash.Dash("Chart")

# Dữ liệu mẫu nhiều công ty, nhiều category
data = pd.DataFrame({
    'Company': ['IPO1']*5 + ['IPO2']*5,
    'Date': pd.date_range('2023-01-01', periods=5).tolist()*2,
    'Revenue': [10, 15, 14, 20, 25, 8, 12, 11, 15, 18],
    'Cost': [5, 7, 6, 8, 9, 4, 5, 6, 7, 8],
    'Stock Price': [100, 102, 101, 105, 110, 50, 52, 51, 55, 60]
})

companies = data['Company'].unique()
categories = ['Revenue', 'Cost', 'Stock Price']

app.layout = html.Div([
    html.H2("Dashboard IPO NASDAQ"),

    html.Label("Chọn công ty:"),
    dcc.Dropdown(
        id='company-dropdown',
        options=[{'label': c, 'value': c} for c in companies],
        value=[companies[0]],
        multi=True
    ),

    html.Label("Chọn category:"),
    dcc.Checklist(
        id='category-checklist',
        options=[{'label': cat, 'value': cat} for cat in categories],
        value=[categories[0]]
    ),

    html.Button("Download Data & Chart Excel", id='download-btn'),

    html.A("Tải file", id="download-link", download="data_chart.xlsx", href="", target="_blank", style={"display": "none"}),

    dcc.Graph(id='dashboard-chart')
])

@app.callback(
    Output('dashboard-chart', 'figure'),
    Input('company-dropdown', 'value'),
    Input('category-checklist', 'value')
)
def update_chart(selected_companies, selected_categories):
    if not selected_companies or not selected_categories:
        return go.Figure()

    if isinstance(selected_companies, str):
        selected_companies = [selected_companies]

    filtered_data = data[data['Company'].isin(selected_companies)]

    fig = go.Figure()

    right_y_cats = [cat for cat in selected_categories if 'Price' in cat or 'price' in cat]
    left_y_cats = [cat for cat in selected_categories if cat not in right_y_cats]

    for cat in left_y_cats:
        for company in selected_companies:
            df = filtered_data[filtered_data['Company'] == company]
            fig.add_trace(go.Bar(
                x=df['Date'], y=df[cat], name=f"{company} - {cat}",
                yaxis='y1'
            ))

    for cat in right_y_cats:
        for company in selected_companies:
            df = filtered_data[filtered_data['Company'] == company]
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df[cat], mode='lines+markers', name=f"{company} - {cat}",
                yaxis='y2'
            ))

    fig.update_layout(
        yaxis=dict(title='Financial Data'),
        yaxis2=dict(title='Stock Price', overlaying='y', side='right'),
        barmode='group',
        title="Financial Dashboard",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

@app.callback(
    Output("download-link", "href"),
    Output("download-link", "style"),
    Input("download-btn", "n_clicks"),
    State('company-dropdown', 'value'),
    State('category-checklist', 'value'),
    prevent_initial_call=True
)
def generate_excel(n_clicks, selected_companies, selected_categories):
    if not n_clicks:
        return "", {"display": "none"}

    if isinstance(selected_companies, str):
        selected_companies = [selected_companies]

    filtered_data = data[data['Company'].isin(selected_companies)]
    filtered_data = filtered_data[['Company', 'Date'] + selected_categories]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        filtered_data.to_excel(writer, index=False, sheet_name='Data')
    excel_data = output.getvalue()

    b64 = base64.b64encode(excel_data).decode()
    href = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"

    return href, {"display": "inline"}

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run(debug=True)

