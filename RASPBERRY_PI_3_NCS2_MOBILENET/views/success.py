# Importacion de Librerias
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import sqlite3
import xlsxwriter
import time
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objs as go  # pie
from dash.dependencies import Input, Output
from server import app
from dash.dependencies import Input, Output, State
import dash_table_experiments as dte
from flask import send_file
import io
import flask
#Warning para manejo de exepciones
import warnings
warnings.filterwarnings("ignore")

################################## 
# Manipulación de datos / Modelo #            
##################################       
# Parametros de Conexion
conn = sqlite3.connect('bd/bd_conteo_clasificacion.db')
#Pandas
df = pd.read_sql_query("select * from tclasificacion", conn)
# Daclaracion de Variables - Arreglos
count1 = []
cHora =[]
# Array para Grafico Barras
l1 = []
l2 = []
l3 = []
# Array para Grafico Barras Fechas
lf1_10 = []
lf2_10 = []
lf3_10 = []
lf1_12 = []
lf2_12 = []
lf3_12 = []
lf1_14 = []
lf2_14 = []
lf3_14 = []

# Array para Grafico de Barras
tiposv = []
times = []
cantidad = []
# Array para Grafico Circular
labels2 = []
values2 = []
# Conexion del Cursos con la consulra sqlite                       
c = conn.cursor()
c.execute(
    "select hora, tipos, count(tipos) from tclasificacion group by hora, tipos")
datas = c.fetchall()
# Consulta para Grafico Circular
c = conn.cursor()
c.execute(
    "select count(hora), tipos from tclasificacion where tipos <> '' group by tipos")
circular = c.fetchall()
# Consulta para Grafico barras                 
cbarras = conn.cursor()
cbarras.execute(
    "select hora, tipos, count(tipos) from tclasificacion where tipos <> '' group by tipos")
barras = cbarras.fetchall()  

# Consulta para Grafico Barras Fechas              
cbarfecha = conn.cursor()
cbarfecha.execute(
    "select fecha, tipos, count(tipos) from tclasificacion where fecha='2020-08-10' group by fecha, tipos")
barras_fecha10 = cbarfecha.fetchall() 
cbarfecha.execute(
    "select fecha, tipos, count(tipos) from tclasificacion where fecha='2020-08-12' group by fecha, tipos")
barras_fecha12 = cbarfecha.fetchall() 
cbarfecha.execute(
    "select fecha, tipos, count(tipos) from tclasificacion where fecha='2020-08-14' group by fecha, tipos")
barras_fecha14 = cbarfecha.fetchall() 

# Consulta para Conteo de Vehiculos por Tipo
c_conteo = conn.cursor()
c_conteo.execute(
    "select count(tipos) from tclasificacion")
counts = c_conteo.fetchall()
c_conteo.execute(
    "select hora from tclasificacion")
contHora = c_conteo.fetchall()

####
c_conteo.execute(
    "select count(tipos) from tclasificacion where tipos = 'MOTO'")
moto_s = c_conteo.fetchall()
c_conteo.execute(
    "select count(tipos) from tclasificacion where tipos = 'AUTO/CAMIONETA'")
auto_s = c_conteo.fetchall()
c_conteo.execute(
    "select count(tipos) from tclasificacion where tipos = 'BUS/FURGONETA'")
bus_s = c_conteo.fetchall()
c_conteo.execute(
    "select count(tipos) from tclasificacion where tipos = 'CAMION/TRAYLER'")
camion_s = c_conteo.fetchall()
# Recorrido de los Arreglos
for row in datas:
    times.append(row[0])
    tiposv.append(row[1])

for row in circular:
    values2.append(row[0])
    labels2.append(row[1])

for row in barras:
    l1.append(row[0])
    l2.append(row[1])
    l3.append(row[2])
    
for row in barras_fecha10:
    lf1_10.append(row[0])
    lf2_10.append(row[1])
    lf3_10.append(row[2])

for row in barras_fecha12:
    lf1_12.append(row[0])
    lf2_12.append(row[1])
    lf3_12.append(row[2])
for row in barras_fecha14:
    lf1_14.append(row[0])
    lf2_14.append(row[1])
    lf3_14.append(row[2])
    
for row in counts:
    count1.append(row[0])
for row in contHora:
    cHora.append(row[0])
for row in moto_s:
    count1.append(row[0])
for row in auto_s:
    count1.append(row[0])
for row in bus_s:
    count1.append(row[0])
for row in camion_s:
    count1.append(row[0])
 
##############################
# Diseño del Tablero / Vista #
##############################
# Estilo CSS Grafico Circular
colors = ['#2373F5', '#F54023', '#F2D800', '#ADFB11']
colorsfondo = {
    'background': '#111111',
    'text': '#7FDBFF'
}
# Estilos de Tabla 
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

# Create success layout
layout = html.Div(children=[html.H3("SISTEMA DE CONTEO VEHICULAR", style={'textAlign': 'center'}),
    dcc.Location(id='url_login_success', refresh=True),
    html.Div([
        html.Div([
            dbc.CardBody([
                html.H5("Total Conteo", className="card-title"),
                html.P("Por Tipo"),
                dbc.Label(str(counts), color="primary"),
            ]),
        ], className="six columns"),

        html.Div([
            dbc.CardBody([
                html.P("Moto: "+str(moto_s)),
                html.P("Auto/Camioneta: "+str(auto_s)),
                html.P("Bus/Furgoneta: "+str(bus_s)),
                html.P("Camion/Trayler: "+str(camion_s)),
            ]),
        ], className="six columns"),
        ], className="row"),
        
    # Titulo
    html.Div(
        className="container",
        children=[
            html.Div(
                  html.Div(
                      className="row",
                      children=[
                          html.Div(
                                className="twelve columns",
                                children=[
                                    html.Br(),
                                    html.H4(
                                        'Estadisticas del Conteo')
                                ], style={'width': '100%', 'margin': 0, 'textAlign': 'center'}
                          )

                      ]
                  )
            )
        ]
    ),
    # Creacion de Tablas
    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        dcc.Tab(label='GRAFICO DE BARRAS', value='tab-1', style=tab_style,
                selected_style=tab_selected_style),
        dcc.Tab(label='GRAFICO CIRCULAR', value='tab-2', style=tab_style,
                selected_style=tab_selected_style),
        dcc.Tab(label='VEHICULOS X HORA', value='tab-3', style=tab_style,
                selected_style=tab_selected_style),
        dcc.Tab(label='BARRAS POR FECHA', value='tab-4', style=tab_style,
                selected_style=tab_selected_style),
    ], style=tabs_styles),
    html.Div(id='tabs-content-inline'),
    # Creacion de Tabla y Boton Exportar
    html.Div(
        className="container",
        children=[
            html.Div(
                dash_table.DataTable(
                id="table",
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict("records"),
                export_format="xlsx",
                )                    

            )
        ]
    ),
    
    html.Div(
        
        )
])






# Crear Llamadas - Callbacks
@app.callback(Output('tabs-content-inline', 'children'),
              [Input('tabs-styled-with-inline', 'value')])
# Cargar datos para elaboracion de graficos estadisticos #
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dcc.Graph(
                id='GraficoBarras',
                figure={
                    'data': [
                        {'x':l2,'y':l3,'type':'bar','name':'Tipos','showlegend': True},
                        #{'x':l1,'y':l3,'type':'bar','name':'Tipos','showlegend': True},
                    ],
                    'layout': {
                        'title': 'GRAFICO DE BARRAS',
                        'barmode' : 'group',
                        'mode':'lines+markers',
                        "autorange": True,
                        'xaxis': dict(
                            title='Tipos',
                            tickangle= 15
                            ),
                        'yaxis': dict(
                            title='Cantidad',
                            )
                    }
                }
            ),
        ])
    elif tab == 'tab-2':
        return html.Div([
            dcc.Graph(id='GraficoCircular',
                      figure={
                          'data': [go.Pie(labels=labels2,
                                          values=values2,
                                          marker=dict(colors=colors, line=dict(
                                              color='#fff', width=1)),
                                          hoverinfo='label+value+percent', textinfo='value+percent',
                                          domain={
                                              'x': [0.30, .55], 'y': [0, 1]}
                                          )
                                   ],
                          'layout': go.Layout(title='GRAFICO CIRCULAR',
                                              autosize=True
                                              )
                      }
                      ),
        ])
    elif tab == 'tab-3':
        return html.Div([
            dcc.Graph(
                figure=dict(
                    data=[
                        dict(
                            x=times,
                            y=tiposv,
                            name='Vehiculos x Hora',
                            marker = dict(color='rgb(13,89,186)',
                            ),
                            
                            
                        ),
                      
                    ],
                    layout=dict(
                        xaxis=dict(
                            size=10,
                            tickangle= 70,
                            tickfont=dict(family='Rockwell', 
                            color='crimson', 
                            size=14)
                            ),
                        showlegend=True,
                        legend=dict(
                            x=1,
                            y=1.2
                        ),
                        margin=dict(l=120, r=0, t=90, b=90)
                    )
                ),
                style={'height': 500},
                id='my-graph'
            )
        ])
    elif tab == 'tab-4':
        return html.Div([
            
            dcc.Graph(
                id='GraficoBarrasFecha',
                figure={
                    'data': [
                        {'x':lf1_10,'y':lf3_10,'type':'bar','name':'2020-08-10','showlegend': True},
                        {'x':lf1_12,'y':lf3_12,'type':'bar','name':'2020-08-12','showlegend': True},
                        {'x':lf1_14,'y':lf3_14,'type':'bar','name':'2020-08-14','showlegend': True},
                        
                    ],
                    'layout': {
                        'title': 'Conteo Por Fecha',
                        'barmode':'stack',
                        'xaxis': dict(
                            title='Fecha',
                            tickangle= -45
                            ),
                        'yaxis': dict(
                            title='Cantidad',
                            )
                    }
                }
            ),
            
            
        ])
        
###############################################
# Interacción entre componentes / controlador #
###############################################

              
@app.callback(Output('url_login_success', 'pathname'),
              [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'
