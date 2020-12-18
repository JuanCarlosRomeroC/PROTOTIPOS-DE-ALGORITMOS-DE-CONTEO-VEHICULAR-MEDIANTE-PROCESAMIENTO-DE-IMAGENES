# index page
import os
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from server import app, server
from flask_login import logout_user, current_user
from views import success, login, login_fd, logout


header = html.Div(
    className='header',
    children=html.Div(
        className='container-width',
        style={'height': '100%','text-align': 'left'},
        children=[
            html.Img(
                src='assets/logo.png',
                className='logo'
            ),
                html.Div(className='links', children=[
                html.Div(id='user-name', className='link'),
                html.Div(id='logout', className='link')
            ])
        ]
    )
)

app.layout = html.Div(
    [
        header,
        html.Div([
            html.Div(
                html.Div(id='page-content', className='content'),
                className='content-container'
            ),
        ], className='container-width'),
        dcc.Location(id='url', refresh=False),
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return login.layout
    elif pathname == '/login':
        return login.layout
    elif pathname == '/success':
        if current_user.is_authenticated:
            return success.layout
        else:
            return login_fd.layout
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout.layout
        else:
            return logout.layout
    else:
        return '404'


@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated:
        return html.Div('Usuario Actual: ' + current_user.username)
        # 'User authenticated' return username in get_id()
    else:
        return ''


@app.callback(
    Output('logout', 'children'),
    [Input('page-content', 'children')])
def user_logout(input1):
    if current_user.is_authenticated:
        return html.A('Salir', href='/logout')
    else:
        return ''


if __name__ == '__main__':
    ##servidor local
    #app.run_server(debug=True)
    ##servidor redlan
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('PRODUCTION') is None
    app.run_server(debug=debug, host='192.168.43.137', port=port)
