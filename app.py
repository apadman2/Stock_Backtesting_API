import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas_datareader as pdr
import dash_table
import pandas as pd
from rsi import RSI
from rwb import RWB
from kvo import KVO
from sharpe import Sharpe
import datetime

## Testing GITHUB LINK TO VSCODE

# Activating Yahoo finance
yf.pdr_override()

# Default Analysis
x = RWB('SPY', '2020-01-01', datetime.datetime.now().date())
x1, x2 = x.analysis()
y = RSI('SPY', '2020-01-01', datetime.datetime.now().date())
y1, y2, y3 = y.calculator()
z = KVO('SPY', '2020-01-01', datetime.datetime.now().date())
z1, z2 = z.kvo()
ent = ['Number of Trades', 'Gain to Loss ratio',
       'Average Gain (%)', 'Average Loss (%)',
       'Maximum Return (%)', 'Maximum Loss (%)',
       'Total Return (%)']

dataframe = pd.DataFrame({'Entity': ent,
                          'Red, White and Blue Strategy': x1,
                          'RSI and WMA': y1,
                          'KVO': z1})

# Risk Analysis
sharpe = Sharpe('SPY', '2018-01-01')
sr = sharpe.sharpe_ratio()
alpha, beta = sharpe.risk_factor()
ent2 = ['Sharpe Ratio', 'Alpha', 'Beta']
value = [sr, alpha, beta]
dataframe2 = pd.DataFrame({'Entity': ent2,
                           'Value': value})

# Empty
fig = {}
fig2 = {}

# Stylesheet
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {
    'background': '#000000',
    'text': '#FFFFFF'
}

# Layout
app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1(
                            children="Input:"
                        ),
                        html.Div(children=["Ticker: ",
                                           dcc.Input(id='ticker',
                                                     value='SPY',
                                                     type='text')],
                                 style={'fontSize': 20,
                                        }),
                        html.Br(),
                        html.Div(children=["Investment: ",
                                           dcc.Input(id='investment',
                                                     value='100000',
                                                     type='number')],
                                 style={'fontSize': 20,
                                        }),
                        html.Br(),
                        html.Div(children=["Date: ",
                                           html.Br(),
                                           dcc.DatePickerSingle(id='date',
                                                                date='2018-01-01')],
                                 style={'fontSize': 20,
                                        }),
                        html.Br(),
                        html.Div(
                            html.Button(id='submit-button-state', n_clicks=0, children='Submit'
                                        )),
                    ]
                ), style={"width": "18rem"}, color="primary", inverse=True
            ), width=2
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H3(
                            children="Candlestick graph: ",
                            style={'fontSize': 30,
                                   }
                        ),
                        dcc.Graph(id='candlestick', figure=fig),
                        html.H3(
                            children="Trade Results: ",
                            style={'fontSize': 30,
                                   }
                        ),
                        dash_table.DataTable(
                            id='table',
                            columns=[{'name': i, 'id': i, 'type': 'numeric'} for i in dataframe.columns],
                            data=dataframe.to_dict('records'),
                            style_cell_conditional=[
                                {'if': {'column_id': 'Entity'},
                                 'width': '19%'},
                                {'if': {'column_id': 'Red, White and Blue Strategy'},
                                 'width': '17%'},
                                {'if': {'column_id': 'RSI and WMA'},
                                 'width': '17%'},
                                {'if': {'column_id': 'KVO'},
                                 'width': '17%'},
                            ],
                            style_data_conditional=(
                                    [
                                        {
                                            'if': {
                                                'filter_query': '{{{}}} > 0'.format(col),
                                                'column_id': col
                                            },
                                            'backgroundColor': 'Green',
                                            'color': 'white'
                                        } for col in dataframe.columns
                                    ] +
                                    [
                                        {
                                            'if': {
                                                'filter_query': '{{{}}} < 0'.format(col),
                                                'column_id': col
                                            },
                                            'backgroundColor': 'Red',
                                            'color': 'white'
                                        } for col in dataframe.columns
                                    ]
                            ),
                            style_cell={
                                'text_align': 'center',
                                'fontSize': 20,
                                'backgroundColor': '#828282',
                                'border': '5px solid black',
                            },
                            style_header={
                                'backgroundColor': '#111111',
                                'fontWeight': 'bold'
                            }
                        ),
                        html.Br(),
                        html.H3(
                            children="Other Statistics: ",
                            style={'fontSize': 30,
                                   }
                        ),
                        dash_table.DataTable(
                            id='table2',
                            columns=[{'name': i, 'id': i, 'type': 'numeric'} for i in dataframe2.columns],
                            data=dataframe2.to_dict('records'),
                            style_cell_conditional=[
                                {'if': {'column_id': 'Entity'},
                                 'width': '19%'},
                                {'if': {'column_id': 'Value'},
                                 'width': '19%'}
                            ],
                            style_cell={
                                'text_align': 'center',
                                'fontSize': 20,
                                'backgroundColor': '#828282',
                                'border': '5px solid black',
                            },
                            style_header={
                                'backgroundColor': '#111111',
                                'fontWeight': 'bold'
                            }
                        ),
                        html.Br(),
                        html.H3(
                            children="Profit and Loss: ",
                            style={'fontSize': 30,
                                   }
                        ),
                        dcc.Graph(id='pnl', figure=fig2),
                        html.Br(),
                    ]
                ), color="dark", inverse=True
            ), width=10
        )
    ], no_gutters=True)

], style={'padding': '0px',
          'font-family': 'Trebuchet MS, sans-serif',
          'color': 'Black',
          'background': '#227efa'})


@app.callback(
    Output('candlestick', 'figure'),
    Input('submit-button-state', 'n_clicks'),
    State('ticker', 'value'),
    State('date', 'date')
)
def update_figure(n_clicks, ticker, date):
    # Creating data frame with ticker data
    df = pdr.get_data_yahoo(str(ticker), str(date), str(datetime.datetime.today()))
    df2 = pdr.get_data_yahoo('SPY', str(date), str(datetime.datetime.today()))

    # Plotting
    figure = go.Figure(data=[go.Candlestick(x=df.index,
                                            open=df['Open'],
                                            high=df['High'],
                                            low=df['Low'],
                                            close=df['Close'])])
    figure.update_layout(plot_bgcolor='#353a40',
                         paper_bgcolor='#353a40',
                         font_color="white", )
    figure.update_xaxes(gridcolor='Black')
    figure.update_yaxes(gridcolor='Black')
    figure.update_layout(xaxis_rangeslider_visible=False)
    figure.add_trace(go.Scatter(x=df.index, y=df2['Adj Close'],
                                mode='lines',
                                name='SPY'))
    print(n_clicks)
    return figure


@app.callback(
    Output('pnl', 'figure'),
    Input('submit-button-state', 'n_clicks'),
    State('ticker', 'value'),
    State('date', 'date'),
    State('investment', 'value')
)
def update_figure(n_clicks, ticker, date, investment):
    e = RWB(str(ticker), str(date), datetime.datetime.now().date())
    x11, x21 = e.analysis()
    f = RSI(str(ticker), str(date), datetime.datetime.now().date())
    y11, y21, y31 = f.calculator()
    g = KVO(str(ticker), str(date), datetime.datetime.now().date())
    z11, z21 = g.kvo()
    x_21 = [i * int(investment) for i in x21]
    y_21 = [i * int(investment) for i in y21]
    z_21 = [i * int(investment) for i in z21]

    # Final plot
    figure1 = px.line()
    figure1.add_trace(go.Scatter(x=y31, y=x_21,
                                 mode='lines',
                                 name='RWB'))
    figure1.add_trace(go.Scatter(x=y31, y=y_21,
                                 mode='lines',
                                 name='RSI + WMA'))
    figure1.add_trace(go.Scatter(x=y31, y=z_21,
                                 mode='lines',
                                 name='KVO'))
    figure1.update_layout(plot_bgcolor='#353a40',
                          paper_bgcolor='#353a40',
                          font_color="white", )
    figure1.update_xaxes(gridcolor='Black')
    figure1.update_yaxes(gridcolor='Black')
    print(n_clicks)
    return figure1


@app.callback(
    Output('table', 'data'),
    Input('submit-button-state', 'n_clicks'),
    State('ticker', 'value'),
    State('date', 'date')
)
def update_table1(n_clicks, ticker, date):
    # updated table
    # Default Analysis
    e = RWB(str(ticker), str(date), datetime.datetime.now().date())
    x11, x21 = e.analysis()
    f = RSI(str(ticker), str(date), datetime.datetime.now().date())
    y11, y21, y31 = f.calculator()
    g = KVO(str(ticker), str(date), str(datetime.datetime.now().date()))
    z11, z21 = g.kvo()
    ent1 = ['Number of Trades', 'Gain to Loss ratio',
            'Average Gain (%)', 'Average Loss (%)',
            'Maximum Return (%)', 'Maximum Loss (%)',
            'Total Return (%)']
    dataframe_u1 = pd.DataFrame({'Entity': ent1,
                                 'Red, White and Blue Strategy': x11,
                                 'RSI and WMA': y11,
                                 'KVO': z11})
    print(n_clicks)
    return dataframe_u1.to_dict('records')


@app.callback(
    Output('table2', 'data'),
    Input('submit-button-state', 'n_clicks'),
    State('ticker', 'value'),
    State('date', 'date')
)
def update_table(n_clicks, ticker, date):
    # Risk Analysis
    sharpe = Sharpe(ticker, date)
    sr = sharpe.sharpe_ratio()
    alpha, beta = sharpe.risk_factor()
    ent2 = ['Sharpe Ratio', 'Alpha', 'Beta']
    value = [sr, alpha, beta]
    dataframe2 = pd.DataFrame({'Entity': ent2,
                               'Value': value})
    print(n_clicks)
    return dataframe2.to_dict('records')


if __name__ == '__main__':
    app.run_server()
