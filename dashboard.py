import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import plotly.express as px
import matplotlib.dates as mdates

try:
    with open('ChopoApp/_chat.txt', 'r', encoding='utf-8') as txt:
        chat = txt.read()
except Exception:
    with open('_chat.txt', 'r', encoding='utf-8') as txt:
        chat = txt.read()



chat = chat.strip().split('\n')
reg_ex = r'\[(\d+/\d+/\d+), (\d+:\d+:\d+)\] (.+): (.)'

nueva_lista = []
for cadena in chat:
    partes = cadena.split('] ')
    fecha_hora = partes[0] + ']'
    nombre_mensaje = partes[1]

    if "\u200e" not in nombre_mensaje:
        nueva_lista.append(cadena)

chat_df = pd.DataFrame([list(re.search(reg_ex, msg).groups()) for msg in nueva_lista if re.search(reg_ex, msg)], columns=['Dia', 'Hora', 'Integrante', 'Deposito'])
chat_df['Instante'] = pd.to_datetime(chat_df['Dia']+' '+chat_df['Hora'])
chat_df['Dia'] = pd.to_datetime(chat_df['Dia'], format='%d/%m/%y')
chat_df['Hora'] = chat_df.Hora.str.split(':').str[0].astype(int)
semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
chat_df['DiaSemana'] = chat_df['Dia'].dt.dayofweek.map(dict(enumerate(semana)))
chat_df['DiaSemana'] = pd.Categorical(chat_df['DiaSemana'], categories=semana, ordered=True)

app = dash.Dash(__name__)
server = app.server

card_style = {
        'border-radius': '8px',  # bordes redondeados
        'box-shadow': '0 2px 20px rgba(0, 0, 0, 0.1)',  # sombra difuminada
        'background-color': '#ffffff',  # fondo blanco para la "tarjeta"
        # 'padding': '10px',  # espacio alrededor del gráfico dentro de la tarjeta
        'margin': '10px',  # espacio entre las tarjetas
        'flex': '1 1 0',
        'min-width': '30vw',
        'height': '50vh',
    }

sidebar_style = {
        'border-radius': '8px',  # bordes redondeados en el lado derecho
        'box-shadow': '4px 0 8px -2px rgba(0, 0, 0, 0.1)',  # sombra solo en el lado derecho
        'background-color': '#ffffff',  # fondo blanco para el "sidebar"
        'padding': '10px',  # espacio alrededor del dropdown dentro del sidebar
        'margin': '10px 10px 10px 0',  # espacio alrededor del sidebar, sin margen a la izquierda
        'width': '20%',  # o cualquier otra medida que prefieras
        'min-height': '100vh',  # para que el sidebar tenga la altura completa de la ventana
    }

app.layout = html.Div([
    # Sidebar
    html.Div([
        html.Img(src='/assets/shit.png', style={'width': '50%', 'display':'block', 'margin-left':'auto', 'margin-right':'auto', 'margin-bottom': '10px'}),
        html.H2("Chopo App", style={'color':'rgb(0,26,72)'}),
        html.H4("Integrantes", style={'color':'rgb(0,26,72)'}),
        dcc.Dropdown(
            id='dropdown',
            options=[
                {'label': 'Datos generales', 'value': 'All'},
                {'label': 'Alvaputo', 'value': 'Alvaputo'},
                {'label': 'Miguel', 'value': 'Michael'},
                {'label': 'Jaime', 'value': 'Jimmy'},
                {'label': 'El Dandy', 'value': 'The Dandy'},
                {'label': 'Ruix', 'value': 'Ruix'},
                {'label': 'Zurdo', 'value': 'Afro-Flash'},
                {'label': 'Cristobal', 'value': 'Colon'}
            ],
            value='All', style={'width':'95%'}  # Valor por defecto
        )
    ], style={'width': '15%', 'float': 'left', 'display': 'flex', 'flexDirection': 'column', **sidebar_style}),

    html.Div([
    # Primera fila de gráficos
    html.Div([
        dcc.Graph(id='grafico1', style=card_style),
        dcc.Graph(id='grafico2', style=card_style)
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'flex-wrap': 'wrap'}),

    # Segunda fila de gráficos
    html.Div([
        dcc.Graph(id='grafico3', style=card_style),
        dcc.Graph(id='grafico4', style=card_style)
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'flex-wrap': 'wrap'})
], style={'flex-grow': 5, 'flex-basis': '85%', 'flex-wrap': 'wrap', 'max-width': '100%'})
], style={'display': 'flex', 'flexDirection': 'row'})

# Callbacks para actualizar gráficos
@app.callback(
    [Output('grafico1', 'figure'),
     Output('grafico2', 'figure'),
     Output('grafico3', 'figure'),
     Output('grafico4', 'figure')],
    [Input('dropdown', 'value')]
)
def update_graphs(elemento):
    
    if elemento == 'All':

        fig1 = px.histogram(chat_df, x='Hora', nbins=24, text_auto=True)
        fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        )

        data = chat_df.groupby('Dia').size().reset_index(name='Cacas')
        fig2 = px.line(data, x='Dia', y='Cacas', line_shape='spline')
        fig2.add_scatter(x=data['Dia'], y=data['Cacas'], mode='markers', name='valores')
        fig2.add_hline(y=chat_df.groupby('Dia').size().mean(), line=dict(color='rgb(255, 105, 105)', width=2, dash='dash'))
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            transition=dict(duration=1000, ordering='traces first')
        )

        fig3 = px.bar(chat_df.groupby('Integrante').size().reset_index(name='Cacas'), y='Integrante', x='Cacas', color='Integrante')
        fig3.add_shape(type='line',
                        x0=chat_df.groupby('Integrante').size().mean(), y0=0, x1=chat_df.groupby('Integrante').size().mean(), y1=1, xref='x', yref='paper',
                        line=dict(color='rgb(255, 105, 105)', width=2, dash='dash'))
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            transition=dict(duration=1000, ordering='traces first')
        )

        fig4 = px.scatter(pd.merge(chat_df, chat_df.groupby('Integrante').size().reset_index(name='Cacas acumuladas'), on='Integrante'), x='Dia', y='Hora', title='Scatter Plot de Horas vs. Días', color='Integrante', size='Cacas acumuladas', opacity=0.5)
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            transition=dict(duration=1000, ordering='traces first')
        )
                
    else:
        integrante = elemento
        data = chat_df[chat_df.Integrante == integrante].groupby('Dia').size().reset_index(name='Cacas')
        fig3 = px.line(data, x='Dia', y='Cacas', line_shape='spline')
        fig3.add_scatter(x=data['Dia'], y=data['Cacas'], mode='markers', name='valores')
        fig3.add_hline(y=chat_df[chat_df.Integrante == integrante].groupby('Dia').size().mean(), line=dict(color='rgb(255, 105, 105)', width=2, dash='dash'))
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            transition=dict(duration=1000, ordering='traces first')
        )

        fig2 = px.bar(chat_df[chat_df.Integrante==integrante].groupby('DiaSemana').size().reset_index(name='Cacas'), x='DiaSemana', y='Cacas', color='DiaSemana')
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            transition=dict(duration=1000, ordering='traces first')
        )

        fig1 = px.histogram(chat_df[chat_df.Integrante == integrante], x='Hora', nbins=24, text_auto=True)
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            transition=dict(duration=1000, ordering='traces first')
        )

        fig4 = px.scatter(pd.merge(chat_df, chat_df.groupby('Integrante').size().reset_index(name='Cacas acumuladas'), on='Integrante'), x='Dia', y='Hora', title='Scatter Plot de Horas vs. Días', color='Integrante', size='Cacas acumuladas', opacity=0.5)
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            transition=dict(duration=1000, ordering='traces first')
        )
        
    
    return fig1, fig2, fig3, fig4

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)
