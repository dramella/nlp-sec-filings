########################################################################################################################
# Import necessary packages
########################################################################################################################
import os
import pandas as pd
from datetime import datetime
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
from secnlp.ml_logic import data as d
from dotenv import load_dotenv
load_dotenv('.env')
########################################################################################################################
# Initialize the Dash app
########################################################################################################################
app = Dash(__name__)

########################################################################################################################
# Style components
########################################################################################################################
style_year = {'width': '200px', 'height': '28px', 'marginRight': '20px',
               'display': 'inline-block', 'margin-bottom': -12, 'margin-top': 30}

style_company = {'width': '200px', 'marginRight': '20px', 'display': 'inline-block',
                  'margin-bottom': -12,'margin-top': 30}

style_filing = {'width': '100px', 'marginRight': '20px', 'display': 'inline-block',
                  'margin-bottom': -12,'margin-top': 30}

style_quarter = {'width': '100px', 'marginRight': '20px', 'display': 'inline-block',
                  'margin-bottom': -12,'margin-top': 30}

########################################################################################################################
#Companies dropdown list
########################################################################################################################
companies_list = d.current_edgar_companies_list(agent=os.environ.get('AGENT'))
companies_list_dic = dict(zip(companies_list.index, companies_list['name']))
########################################################################################################################
# App Layout
########################################################################################################################
app.layout = html.Div([
    # Header
    html.H1("SEC Filing Retriever", style={'textAlign': 'center', 'marginBottom': 10, 'color': '#0099FF'}),

    # Input form section
    html.Div([
        # Company input field
        html.Label("Company:"),
        dcc.Dropdown(companies_list_dic,
            id='company-input',
            placeholder='Enter company name',
            style=style_company
        ),

        # Year input field
        html.Label("Year:"),
        dcc.Input(
            id='year-input',
            type='text',
            placeholder='Enter reference year',
            style=style_year
        ),
        # Filing type dropdown
        html.Label("Filing type:"),
        dcc.Dropdown(
            id='filing-input',
            options=[{'label': '10-K', 'value': '10-K'}, {'label': '10-Q', 'value': '10-Q'}],
            value='10-K',
            style=style_filing
        ),

        # Quarter dropdown
        html.Label("Quarter:"),
        dcc.Dropdown(
            id='quarter-input',
            options=[{'label': f'Q{i}', 'value': f'Q{i}'} for i in range(1, 5)],
            value='Q4',
            style=style_quarter
        )
    ]),

    # Submit button
    html.Button('Submit', id='submit-button', style={'backgroundColor': '#0099FF', 'color': 'white', 'padding': '10px 15px',
                                                     'border': 'none', 'display': 'block',
                                                     'margin': 'auto', 'marginTop': '20px'}),

    # Output container
    html.Div(id='output-container', style={'marginTop': 50, 'fontWeight': 'bold', 'fontSize': 16}),
],style={'maxWidth': '950px', 'margin': 'auto'})


@app.callback(
    Output('output-container', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('company-input', 'value'),
     State('year-input', 'value'),
     State('filing-input', 'value'),
     State('quarter-input', 'value')]
)
def update_output(n_clicks, company, year, filing_type, quarter):
    if n_clicks:
        raw_data = d.basic_info_company(cik = company, agent = os.environ.get('AGENT'))
        data_df = pd.DataFrame(data = {k: raw_data[k] for k in ['sicDescription','name','tickers','exchanges','fiscalYearEnd']})
        data_df = data_df.rename({'sicDescription': 'Standard Industrial Classification', 'fiscalYearEnd': 'Fiscal Year End'},axis=1)
        data_df.columns = data_df.columns.str.capitalize()
        data_df['Fiscal year end'] = data_df['Fiscal year end'].apply(lambda x: datetime.strptime(x, '%m%d').strftime('%d %B'))
        return dash_table.DataTable(data_df.to_dict('records'), [{"name": i, "id": i} for i in data_df.columns])

# Run the app if the script is executed
if __name__ == '__main__':
    app.run_server(debug=True)
