import dash
from dash import dcc, html, Input, Output, State, ctx
import plotly.express as px
import dash_bootstrap_components as dbc
import json
import pandas as pd
from datetime import datetime
from openAiChatDashBoardIntegration import analisar_chamados


# Load data
with open("metricas.json", "r") as f:
    metricas_dashboard = json.load(f)

total_chamados = metricas_dashboard.get("Total de Chamados", 0)
chamados_abertos_hoje = metricas_dashboard.get("Chamados Abertos Hoje", 0)
chamados_fechados_hoje = metricas_dashboard.get("Chamados Fechados Hoje", 0)
tempo_medio_atendimento = metricas_dashboard.get("Tempo Médio de Atendimento", 0.0)
chamados_abertos_mes = metricas_dashboard.get("Chamados Abertos Mês", 0)
chamados_fechados_mes = metricas_dashboard.get("Chamados Fechados Mês", 0)

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.SLATE,
        "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True  # Suprime erros de componentes não encontrados
)

# Custom styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%css%}
        <style>
            :root {
                --primary-color: #1f77b4;
                --secondary-color: #2ecc71;
                --warning-color: #f1c40f;
                --bg-dark: #343a40;
            }
            
            .dashboard-container {
                position: relative;
                min-height: 100vh;
                z-index: 1;
            }
            
            .watermark {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 400px;
                height: 200px;
                opacity: 0.1;
                pointer-events: none;
                z-index: 0;
                background-image: url('/assets/fast-logo.png');
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
            }
            
            .metric-card {
                height: 100%;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
                background: linear-gradient(145deg, var(--bg-dark), #2b2f33);
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                transform: translateX(-100%);
                transition: transform 0.6s;
            }
            
            .metric-card:hover::before {
                transform: translateX(100%);
            }
            
            .metric-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 12px 20px rgba(0, 0, 0, 0.4);
            }
            
            .metric-card .icon {
                font-size: 1.5rem;
                margin-right: 0.5rem;
                opacity: 0.8;
            }
            
            .metric-card .tooltip {
                position: absolute;
                bottom: -30px;
                left: 50%;
                transform: translateX(-50%);
                padding: 5px 10px;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                border-radius: 4px;
                font-size: 0.8rem;
                opacity: 0;
                transition: all 0.3s ease;
                pointer-events: none;
                white-space: nowrap;
            }
            
            .metric-card:hover .tooltip {
                bottom: 10px;
                opacity: 1;
            }
            
            .graph-container {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                padding: 15px;
                border-radius: 12px;
                background: var(--bg-dark);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 1;
            }
            
            .graph-container:hover {
                transform: translateY(-5px) scale(1.01);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2),
                           0 0 30px rgba(31, 119, 180, 0.15);
                border-color: var(--primary-color);
            }
            
            .dropdown-container {
                transition: all 0.3s ease;
                padding: 10px;
                border-radius: 8px;
                background: var(--bg-dark);
                margin-bottom: 2rem;
            }
            
            .dropdown-container:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
            
            .filter-label {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: white;
                font-size: 1.1rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Cards with icons and tooltips
metricas_cards = dbc.Row([
    dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-ticket-alt icon"),
                    html.H5("Total de Chamados", className="card-title text-white d-inline")
                ], className="d-flex align-items-center"),
                html.H3(f"{total_chamados}", className="card-text text-center font-weight-bold mt-3"),
                html.Span("Total de chamados registrados no sistema", className="tooltip")
            ])
        ], className="metric-card text-white shadow-lg animate__animated animate__fadeInLeft h-100"), 
        width=3, className="d-flex"
    ),
    dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-clock icon text-warning"),
                    html.H5("Chamados Abertos Hoje", className="card-title text-warning d-inline")
                ], className="d-flex align-items-center"),
                html.H3(f"{chamados_abertos_hoje}", className="card-text text-center font-weight-bold mt-3"),
                html.Span("Chamados abertos nas últimas 24 horas", className="tooltip")
            ])
        ], className="metric-card text-white shadow-lg animate__animated animate__fadeInRight h-100"), 
        width=3, className="d-flex"
    ),
    dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-check-circle icon text-success"),
                    html.H5("Chamados Fechados Hoje", className="card-title text-success d-inline")
                ], className="d-flex align-items-center"),
                html.H3(f"{chamados_fechados_hoje}", className="card-text text-center font-weight-bold mt-3"),
                html.Span("Chamados fechados nas últimas 24 horas", className="tooltip")
            ])
        ], className="metric-card text-white shadow-lg animate__animated animate__fadeInUp h-100"), 
        width=3, className="d-flex"
    ),
    dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-hourglass-half icon text-info"),
                    html.H5("Tempo Médio de Atendimento", className="card-title text-info d-inline")
                ], className="d-flex align-items-center"),
                html.H3(f"{tempo_medio_atendimento:.2f} min", className="card-text text-center font-weight-bold mt-3"),
                html.Span("Tempo médio para resolução dos chamados", className="tooltip")
            ])
        ], className="metric-card text-white shadow-lg animate__animated animate__fadeInDown h-100"), 
        width=3, className="d-flex"
    ),
], className="mb-4 g-3")

def format_month_label(mes):
    try:
        date = datetime.strptime(mes, "%Y-%m")
        meses = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
            'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
            'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
            'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }
        mes_nome = date.strftime("%B")
        return f"{meses[mes_nome]}/{date.year}"
    except:
        return mes

# Process data
chamados_semana_mes = metricas_dashboard.get("Chamados Semana Mês", {})
dados_processados = []

for semana, meses in chamados_semana_mes.items():
    for mes, chamados in meses.items():
        dados_processados.append({
            "Semana": semana,
            "Mês": mes,
            "Chamados": chamados
        })

df_semana_mes = pd.DataFrame(dados_processados)
meses_disponiveis = df_semana_mes["Mês"].unique().tolist()
mes_inicial = meses_disponiveis[-1] if meses_disponiveis else None
df_filtrado = df_semana_mes[df_semana_mes["Mês"] == mes_inicial] if mes_inicial else pd.DataFrame()

# Create figures with custom theme
fig_chamados_dia = px.bar(
    x=["Abertos", "Fechados"],
    y=[chamados_abertos_hoje, chamados_fechados_hoje],
    title="Chamados Abertos x Fechados - Hoje",
    labels={'x': 'Status', 'y': 'Quantidade'},
    color=["Abertos", "Fechados"],
    color_discrete_map={"Abertos": "#1f77b4", "Fechados": "#2ecc71"},
    text_auto=True,
    template="plotly_dark"
)

fig_chamados_dia.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    transition_duration=500
)

fig_chamados_mes = px.bar(
    x=["Abertos", "Fechados"],
    y=[chamados_abertos_mes, chamados_fechados_mes],
    title="Chamados Abertos x Fechados - Mês",
    labels={'x': 'Status', 'y': 'Quantidade'},
    color=["Abertos", "Fechados"],
    color_discrete_map={"Abertos": "#1f77b4", "Fechados": "#2ecc71"},
    text_auto=True,
    template="plotly_dark"
)

fig_chamados_mes.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    transition_duration=500
)

# Dashboard layout
# Dashboard layout atualizado
app.layout = html.Div(className="dashboard-container", children=[
    html.Div(className="watermark"),
    html.Div(className="animate__animated animate__fadeIn p-4", children=[
        html.Div([
            html.I(className="fas fa-chart-line mr-2 text-primary", style={"fontSize": "2rem"}),
            html.H1("Dashboard de Atendimento", className="title animate__animated animate__fadeInDown text-center mb-4 d-inline-block ml-2")
        ], className="d-flex justify-content-center align-items-center"),
        html.Div([
            html.P("Na Versão 1.0 este Dashboard é atualizado às: 12:00 hrs e às 22:00 hrs",
                className="text-center mb-4",
                style={"color": "orange"})
        ]),
        metricas_cards,
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(id='grafico-chamados-dia', figure=fig_chamados_dia),
                className="graph-container animate__animated animate__fadeInLeft"), width=6),
            dbc.Col(html.Div(dcc.Graph(id='grafico-chamados-mes', figure=fig_chamados_mes),
                className="graph-container animate__animated animate__fadeInRight"), width=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                html.Label([
                    html.I(className="fas fa-filter text-primary"),
                    html.Span("Filtrar por Mês", className="ml-2")
                ], className="filter-label mb-2"),
                dcc.Dropdown(
                    id='dropdown-mes',
                    options=[{"label": format_month_label(mes), "value": mes} for mes in meses_disponiveis],
                    value=mes_inicial,
                    clearable=False,
                    className="mb-4"
                ),
                dcc.Graph(id='grafico-chamados-semana'),
            ], width=12)
        ]),
        html.Div([
            html.H4("Análise de Chamados com IA", className="text-white mb-3"),
            html.Button('Analisar Chamados', id='btn-analisar', n_clicks=0, className="btn btn-primary mb-3"),
            html.Div(id='resultado-analise', className="mt-3")
        ], className="mt-4"),
    ])
])
@app.callback(
    Output('resultado-analise', 'children'),
    [Input('btn-analisar', 'n_clicks')],
    prevent_initial_call=True
)
def handle_analise(n_clicks):
    if not n_clicks:
        return html.Div()
    if n_clicks > 0:
        try:
            resultado = analisar_chamados('uploads/whatsapp_chamados_detailed.csv')
            return html.Pre(resultado)
        except Exception as e:
            return html.Div(f"Erro na análise: {str(e)}", className="text-danger")
    return dash.no_update


# Formatação das datas
def format_week_label(semana):
    try:
        inicio, fim = semana.split('/')
        data_inicio = datetime.strptime(inicio, '%Y-%m-%d')
        data_fim = datetime.strptime(fim, '%Y-%m-%d')
        return f"{data_inicio.strftime('%d/%m')} - {data_fim.strftime('%d/%m')}"
    except:
        return semana

# Callback para interatividade entre gráficos
@app.callback(
    [Output('grafico-chamados-semana', 'figure'),
     Output('grafico-chamados-dia', 'figure'),
     Output('grafico-chamados-mes', 'figure')],
    [Input('dropdown-mes', 'value')]
)
def update_all_graphs(mes_selecionado):
    if mes_selecionado is None:
        return [px.bar(title="Sem dados") for _ in range(3)]

    # Gráfico semanal
    df_filtrado = df_semana_mes[df_semana_mes["Mês"] == mes_selecionado]
    df_filtrado = df_filtrado.sort_values(by=['Semana'])
    df_filtrado['Semana_Formatada'] = df_filtrado['Semana'].apply(format_week_label)
    
    fig_semana = px.bar(
        df_filtrado,
        x="Semana_Formatada",
        y="Chamados",
        title=f"Chamados por Semana - {format_month_label(mes_selecionado)}",
        labels={"Semana_Formatada": "Período", "Chamados": "Quantidade"},
        text_auto=True,
        template="plotly_dark",
        color_discrete_sequence=["#1f77b4"]
    )
    
    fig_semana.update_layout(
        transition_duration=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        showlegend=False,
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=12,
            font_family="Arial"
        ),
        xaxis_title="Período",
        yaxis_title="Quantidade de Chamados"
    )

    # Gráfico diário atualizado
    fig_dia = px.bar(
        x=["Abertos", "Fechados"],
        y=[chamados_abertos_hoje, chamados_fechados_hoje],
        title=f"Chamados Abertos x Fechados - Hoje ({datetime.now().strftime('%d/%m/%Y')})",
        labels={'x': 'Status', 'y': 'Quantidade'},
        color=["Abertos", "Fechados"],
        color_discrete_map={"Abertos": "#1f77b4", "Fechados": "#2ecc71"},
        text_auto=True,
        template="plotly_dark"
    )
    fig_dia.update_layout(
        transition_duration=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Gráfico mensal atualizado
    fig_mes = px.bar(
        x=["Abertos", "Fechados"],
        y=[chamados_abertos_mes, chamados_fechados_mes],
        title=f"Chamados Abertos x Fechados - {format_month_label(mes_selecionado)}",
        labels={'x': 'Status', 'y': 'Quantidade'},
        color=["Abertos", "Fechados"],
        color_discrete_map={"Abertos": "#1f77b4", "Fechados": "#2ecc71"},
        text_auto=True,
        template="plotly_dark"
    )
    fig_mes.update_layout(
        transition_duration=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig_semana, fig_dia, fig_mes

if __name__ == '__main__':
    app.run_server(debug=True,
    host='0.0.0.0')