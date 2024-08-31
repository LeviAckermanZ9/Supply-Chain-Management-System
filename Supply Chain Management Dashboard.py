import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from datetime import datetime, timedelta
import requests
from sklearn.ensemble import IsolationForest
import dash_leaflet as dl
import dash_cytoscape as cyto
import base64
import io

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Global variables
global_df = pd.DataFrame()

# Simulated data for initial view
def generate_supply_chain_data(n=1000):
    date_today = datetime.now()
    dates = [date_today - timedelta(days=x) for x in range(n)]
    
    df = pd.DataFrame({
        'date': dates,
        'order_volume': np.random.normal(1000, 100, n),
        'shipping_delays': np.random.normal(2, 0.5, n),
        'inventory_levels': np.random.normal(5000, 500, n),
        'supplier_reliability': np.random.normal(0.9, 0.05, n),
        'customer_satisfaction': np.random.normal(4, 0.3, n),
    })
    
    # Add some anomalies
    df.loc[n//2, 'order_volume'] *= 3
    df.loc[n//4, 'shipping_delays'] *= 5
    df.loc[3*n//4, 'inventory_levels'] *= 0.2
    
    return df

# AI-Driven Insights
def predict_disruptions(data):
    X = data[['order_volume', 'shipping_delays', 'inventory_levels']]
    clf = IsolationForest(contamination=0.1, random_state=42)
    predictions = clf.fit_predict(X)
    return predictions

# Chatbot Assistant
def chatbot_response(query):
    responses = {
        'help': 'How can I assist you with supply chain management?',
        'data': 'You can upload your own data using the "Upload Data" tab.',
        'features': 'Our dashboard offers predictive analytics, real-time tracking, and more!',
        'disruptions': 'I can help predict potential supply chain disruptions based on our data.',
        'performance': 'You can view key performance indicators in the Main Dashboard tab.'
    }
    return responses.get(query.lower(), "I'm not sure about that. Can you please ask about help, data, features, disruptions, or performance?")

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Advanced Supply Chain Management Dashboard", className="text-center mt-4 mb-4"), width=12)
    ]),
    dbc.Tabs([
        dbc.Tab(label="Upload Data", children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
            html.Div(id='output-data-upload'),
            html.Div(id='data-upload-status')
        ]),
        dbc.Tab(label="Main Dashboard", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id='order-volume-graph'), width=6),
                dbc.Col(dcc.Graph(id='inventory-levels-graph'), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='shipping-delays-graph'), width=6),
                dbc.Col(dcc.Graph(id='customer-satisfaction-graph'), width=6),
            ]),
        ]),
        dbc.Tab(label="AI Insights", children=[
            dbc.Row([
                dbc.Col([
                    html.H5("Supply Chain Disruption Prediction", className="text-center"),
                    dcc.Graph(id='disruption-prediction-graph')
                ], width=12),
            ])
        ]),
        dbc.Tab(label="Real-time Tracking", children=[
            dbc.Row([
                dbc.Col([
                    html.H5("Global Supply Chain Activity", className="text-center"),
                    dl.Map(id="supply-chain-map", style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}, center=[20, 0], zoom=2)
                ], width=12),
            ])
        ]),
        dbc.Tab(label="Supplier Network", children=[
            dbc.Row([
                dbc.Col([
                    html.H5("Supplier Network Visualization", className="text-center"),
                    cyto.Cytoscape(
                        id='supplier-network',
                        layout={'name': 'circle'},
                        style={'width': '100%', 'height': '50vh'},
                        elements=[]
                    )
                ], width=12)
            ])
        ]),
        dbc.Tab(label="Chatbot Assistant", children=[
            html.H5("Supply Chain Assistant", className="text-center"),
            dcc.Input(id="chatbot-input", type="text", placeholder="Ask me anything about supply chain", className="mb-3 form-control"),
            dbc.Button("Send", id="chatbot-send-btn", color="primary", className="mb-3 btn-block"),
            html.Div(id="chatbot-output", className="text-center mt-2")
        ]),
    ]),
], fluid=True)

# Callbacks
@app.callback(
    Output('output-data-upload', 'children'),
    Output('data-upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    global global_df
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return html.Div(['Please upload a CSV or Excel file.']), 'Upload failed'

            global_df = df

            return html.Div([
                html.H5(f'File "{filename}" has been successfully uploaded.'),
                dash_table.DataTable(
                    data=df.head().to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left'},
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    }
                )
            ]), 'Data uploaded successfully'
        except Exception as e:
            print(e)
            return html.Div(['There was an error processing this file.']), 'Upload failed'
    
    if global_df.empty:
        global_df = generate_supply_chain_data()
        return html.Div(['No file uploaded. Using simulated data.']), 'Using simulated data'
    
    return html.Div(), ''

@app.callback(
    [Output('order-volume-graph', 'figure'),
     Output('inventory-levels-graph', 'figure'),
     Output('shipping-delays-graph', 'figure'),
     Output('customer-satisfaction-graph', 'figure')],
    Input('data-upload-status', 'children')
)
def update_main_graphs(upload_status):
    if global_df.empty:
        return [go.Figure()] * 4

    order_volume_fig = px.line(global_df, x='date', y='order_volume', title='Order Volume Over Time')
    inventory_levels_fig = px.line(global_df, x='date', y='inventory_levels', title='Inventory Levels Over Time')
    shipping_delays_fig = px.line(global_df, x='date', y='shipping_delays', title='Shipping Delays Over Time')
    customer_satisfaction_fig = px.line(global_df, x='date', y='customer_satisfaction', title='Customer Satisfaction Over Time')
    
    return order_volume_fig, inventory_levels_fig, shipping_delays_fig, customer_satisfaction_fig

@app.callback(
    Output('disruption-prediction-graph', 'figure'),
    Input('data-upload-status', 'children')
)
def update_disruption_prediction(upload_status):
    if global_df.empty:
        return go.Figure()

    predictions = predict_disruptions(global_df)
    global_df['disruption'] = predictions
    
    fig = px.scatter(global_df, x='order_volume', y='shipping_delays', color='disruption',
                     title='Supply Chain Disruption Prediction',
                     labels={'disruption': 'Predicted Disruption'},
                     color_discrete_map={1: 'blue', -1: 'red'})
    
    return fig

@app.callback(
    Output('supply-chain-map', 'children'),
    Input('supply-chain-map', 'id')  # This is a dummy input to trigger the callback on page load
)
def update_supply_chain_map(dummy):
    # Simulated supply chain locations
    locations = [
        {"name": "Supplier A", "location": [40.7128, -74.0060]},
        {"name": "Supplier B", "location": [34.0522, -118.2437]},
        {"name": "Warehouse 1", "location": [51.5074, -0.1278]},
        {"name": "Warehouse 2", "location": [48.8566, 2.3522]},
        {"name": "Distribution Center", "location": [35.6762, 139.6503]},
    ]
    
    markers = [dl.Marker(position=loc["location"], children=dl.Tooltip(loc["name"])) for loc in locations]
    
    return [dl.TileLayer()] + markers

@app.callback(
    Output('supplier-network', 'elements'),
    Input('supplier-network', 'id')  # This is a dummy input to trigger the callback on page load
)
def update_supplier_network(dummy):
    nodes = [
        {'data': {'id': 'A', 'label': 'Supplier A'}},
        {'data': {'id': 'B', 'label': 'Supplier B'}},
        {'data': {'id': 'C', 'label': 'Manufacturer'}},
        {'data': {'id': 'D', 'label': 'Distributor'}},
        {'data': {'id': 'E', 'label': 'Retailer'}}
    ]
    edges = [
        {'data': {'source': 'A', 'target': 'C'}},
        {'data': {'source': 'B', 'target': 'C'}},
        {'data': {'source': 'C', 'target': 'D'}},
        {'data': {'source': 'D', 'target': 'E'}}
    ]
    return nodes + edges

@app.callback(
    Output('chatbot-output', 'children'),
    Input('chatbot-send-btn', 'n_clicks'),
    State('chatbot-input', 'value')
)
def chatbot_response_callback(n_clicks, query):
    if n_clicks is None or not query:
        return ""
    
    response = chatbot_response(query)
    return f"Chatbot: {response}"

if __name__ == '__main__':
    app.run_server(debug=True)
