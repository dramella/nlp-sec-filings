# Import necessary packages
from dash import Dash, html, dcc


# Initialize the Dash app
app = Dash(__name__)

style_input = {'width': '200px', 'height': '28px', 'marginRight': '20px',
               'display': 'inline-block', 'margin-bottom': -12, 'margin-top': 30}

style_dropdown = {'width': '100px', 'marginRight': '20px', 'display': 'inline-block',
                  'margin-bottom': -12,'margin-top': 30}

# Define the layout of the app
app.layout = html.Div([
    # Header
    html.H1("Simple Dash Form", style={'textAlign': 'center', 'marginBottom': 10}),

    # Input form section
    html.Div([
        # Company input field
        html.Label("Company:"),
        dcc.Input(
            id='company-input',
            type='text',
            placeholder='Enter company name',
            style=style_input
        ),

        # Year input field
        html.Label("Year:"),
        dcc.Input(
            id='year-input',
            type='text',
            placeholder='Enter reference year',
            style=style_input
        ),
        # Filing type dropdown
        html.Label("Filing type:"),
        dcc.Dropdown(
            id='filing-input',
            options=[{'label': '10-K', 'value': '10-K'}, {'label': '10-Q', 'value': '10-Q'}],
            value='10-K',
            style=style_dropdown
        ),

        # Quarter dropdown
        html.Label("Quarter:"),
        dcc.Dropdown(
            id='quarter-input',
            options=[{'label': f'Q{i}', 'value': f'Q{i}'} for i in range(1, 5)],
            value='Q4',
            style=style_dropdown
        )
    ]),

    # Submit button
    html.Button('Submit', id='submit-button', style={'backgroundColor': '#4CAF50', 'color': 'white', 'padding': '10px 15px',
                                                     'border': 'none', 'display': 'block',
                                                     'margin': 'auto', 'marginTop': '20px'}),

    # Output container
    html.Div(id='output-container', style={'marginTop': 20, 'fontWeight': 'bold', 'fontSize': 16, 'margin': 'auto'}),
],style={'maxWidth': '950px', 'margin': 'auto'})

# Run the app if the script is executed
if __name__ == '__main__':
    app.run_server(debug=True)
