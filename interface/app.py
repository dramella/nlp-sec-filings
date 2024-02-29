
# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd


# Initialize the app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Simple Dash Form"),

    # Form with two input fields
    html.Label("Company:"),
    dcc.Input(id='company-input', type='text', placeholder='Enter company name'),

    html.Label("Filing type:"),
    dcc.Dropdown(id='filing-input',options = ['Q1', 'Q2', 'Q3', 'Q4'], value = 'Q4', style = {'width': '30%'} ),

    html.Label("Quarter"),
    dcc.Input(id='quarter-input', type='text', placeholder='Enter reference quarter'),

    html.Label("Year"),
    dcc.Input(id='year-input', type='text', placeholder='Enter reference year'),

    html.Button('Submit', id='submit-button'),

    # Output to display the result
    html.Div(id='output-container')
])

if __name__ == '__main__':
    app.run_server(debug=True)
