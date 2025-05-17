from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Load data and process revenue
df = pd.read_csv("FIEP Data set(Sheet1).csv")  # Adjust path if needed
df['Revenue'] = pd.to_numeric(df['Revenue'].astype(str).str.replace(',', ''), errors='coerce')
df.dropna(subset=['Revenue', 'Sector', 'Symbol', 'Company'], inplace=True)

def categorize_revenue(value):
    if value < 1_000_000:
        return "0 - 1M"
    elif value < 10_000_000:
        return "1M - 10M"
    elif value < 100_000_000:
        return "10M - 100M"
    else:
        return "100M+"

df['Revenue Category'] = df['Revenue'].apply(categorize_revenue)

# Categories for filtering chart
filter_categories = ['Sector', 'Revenue Category']

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create dropdowns for Sector and Revenue Category (multi-select)
filter_dropdowns = []
for cat in filter_categories:
    options = [{'label': v, 'value': v} for v in sorted(df[cat].unique())]
    filter_dropdowns.append(
        html.Div([
            html.H6(cat, style={'fontWeight': 'bold', 'marginTop': '20px'}),
            dcc.Dropdown(
                id=f'dropdown-{cat.replace(" ", "-")}',
                options=options,
                multi=True,
                placeholder=f"Select {cat}..."
            )
        ])
    )

# Separate dropdown for Company Name (using Symbol column data)
company_name_options = [{'label': v, 'value': v} for v in sorted(df['Symbol'].unique())]

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                *filter_dropdowns,
                html.Hr(),
                html.Div([
                    html.H6("Company Name", style={'fontWeight': 'bold', 'marginTop': '30px'}),
                    dcc.Dropdown(
                        id='dropdown-Company-Name',
                        options=company_name_options,
                        multi=True,
                        placeholder="Select Company Name(s)..."
                    )
                ])
            ],
            width=3,
            style={
                "borderRight": "2px solid #007BFF",
                "height": "90vh",
                "overflowY": "auto",
                "padding": "20px",
                "backgroundColor": "#E6F0FF",
                "fontWeight": "600"
            }
        ),
        dbc.Col([
            html.H3("Visualization & Details", style={'marginBottom': '20px', 'fontWeight': '700', 'color': '#004085'}),
            dcc.Graph(id='main-chart'),
            html.Div(id='company-details', style={
                'marginTop': '20px',
                'fontWeight': '600',
                'color': '#004085',
                'backgroundColor': '#D0E4FF',
                'padding': '10px',
                'borderRadius': '5px'
            }),
        ], width=9, style={"padding": "20px"})
    ])
], fluid=True, style={"fontFamily": "'Montserrat', sans-serif"})


@app.callback(
    [Output('main-chart', 'figure'),
     Output('company-details', 'children')],
    [Input(f'dropdown-{cat.replace(" ", "-")}', 'value') for cat in filter_categories] +
    [Input('dropdown-Company-Name', 'value')]
)
def update_visual(*inputs):
    selected_sector = inputs[0]
    selected_revenue_cat = inputs[1]
    selected_company_names = inputs[2]

    # Filter dataframe for chart (Sector and Revenue Category)
    filtered_df = df.copy()
    if selected_sector:
        filtered_df = filtered_df[filtered_df['Sector'].isin(selected_sector)]
    if selected_revenue_cat:
        filtered_df = filtered_df[filtered_df['Revenue Category'].isin(selected_revenue_cat)]

    if filtered_df.empty:
        fig = {}
    else:
        fig = px.bar(filtered_df, x='Company', y='Revenue',
                     title="Revenue by Company for selected filters",
                     labels={"Revenue": "Revenue", "Company": "Company"})
        fig.update_layout(transition_duration=500)

    # Prepare company details based on selected Company Names (Symbol)
    if selected_company_names and len(selected_company_names) > 0:
        selected_companies = df[df['Symbol'].isin(selected_company_names)]

        if selected_companies.empty:
            details = html.Div("No data found for selected company names.", style={'color': 'red', 'fontWeight': '600'})
        else:
            table_header = [
                html.Thead(html.Tr([html.Th(col, style={'backgroundColor': '#cce5ff', 'padding': '6px', 'border': '1px solid #ccc'}) for col in selected_companies.columns]))
            ]
            table_body = [
                html.Tbody([
                    html.Tr([html.Td(selected_companies.iloc[i][col], style={'padding': '6px', 'border': '1px solid #ccc'}) for col in selected_companies.columns])
                    for i in range(len(selected_companies))
                ])
            ]

            details = html.Table(table_header + table_body, style={"width": "100%", "borderCollapse": "collapse", 'backgroundColor': 'white'})
    else:
        details = ""

    return fig, details


if __name__ == '__main__':
    app.run(debug=True)
