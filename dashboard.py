import subprocess
import io
import dash
from dash import dash_table, dcc, html, Input, Output, State, ctx
import plotly.express as px
import dash_bootstrap_components as dbc
import json
import pandas as pd
from datetime import datetime
from openAiChatDashBoardIntegration import analisar_chamados


# Carregar usuários do arquivo JSON
def carregar_usuarios():
    with open('usuarios.json', 'r') as f:
        return json.load(f)['usuarios']

usuarios = carregar_usuarios() 


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
            
            .dash-table-container {
                position: relative !important;
                width: 100% !important;
            }

            .previous-next-container {
                display: flex !important;
                justify-content: center !important;  /* Alterado para center */
                align-items: center !important;
                padding: 10px !important;
                background-color: #2d2d2d !important;
                position: absolute !important;
                left: 0 !important;  /* Adicionado */
                right: 0 !important;
                bottom: -50px !important;
                width: 100% !important;
            }

            .previous-next-container button {
                background-color: #1f77b4 !important;
                color: white !important;
                border: none !important;
                padding: 5px 10px !important;
                margin: 0 2px !important;
                border-radius: 4px !important;
                cursor: pointer !important;
                min-width: 40px !important;
            }

            .previous-next-container button:hover {
                background-color: #2ecc71 !important;
            }

            .dash-table-container .dash-spreadsheet-container {
                margin-bottom: 60px !important;
            }

            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner input[type="text"] {
                color: white !important;
                background-color: #374151 !important;
                border: 1px solid #4B5563 !important;
            }

            .dash-table-container .dash-spreadsheet-container input::placeholder {
                color: #9CA3AF !important;
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

# Layout de login
login_layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src="/assets/fast-logo.png", className="logo-img mb-3", style={
                "maxWidth": "120px",  # Tamanho máximo da imagem
                "margin": "0 auto",  # Centraliza horizontalmente
                "display": "block"   # Garante centralização
            }),
            
            html.H2("Dashboard de Atendimento WhatsApp", 
                    className="text-center text-white mb-4",
                    style={"fontSize": "24px", "fontWeight": "bold"}),

            html.P("Dashboard de Atendimento",
                   className="text-center mb-4",
                   style={"color": "#9CA3AF", "fontSize": "14px"}),

            dbc.Input(
                id="input-usuario",
                type="text",
                placeholder="Usuário",
                className="mb-3",
                style={
                    "backgroundColor": "#374151",
                    "border": "1px solid #4B5563",
                    "color": "white",
                    "padding": "10px 15px",
                    "borderRadius": "6px",
                    "width": "100%"
                }
            ),

            dbc.Input(
                id="input-senha",
                type="password",
                placeholder="Senha", 
                className="mb-4",
                style={
                    "backgroundColor": "#374151",
                    "border": "1px solid #4B5563",
                    "color": "white",
                    "padding": "10px 15px",
                    "borderRadius": "6px",
                    "width": "100%"
                }
            ),

            dbc.Button(
                "Entrar",
                id="btn-login",
                n_clicks=0,
                className="w-100",
                style={
                    "backgroundColor": "#3B82F6",
                    "border": "none",
                    "padding": "10px",
                    "borderRadius": "6px",
                    "fontWeight": "bold",
                    "transition": "all 0.2s ease-in-out"
                }
            ),

            html.Div(
                id="login-feedback",
                className="text-danger mt-3 text-center"
            ),

            html.P(
                "© 2025 Sistema de Gestão de Atendimentos WhatsApp. Todos os direitos reservados.",
                className="text-center mt-4",
                style={"color": "#9CA3AF", "fontSize": "12px"}
            )
        ], style={
            "backgroundColor": "#1F2937",
            "padding": "40px",
            "borderRadius": "12px",
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
            "maxWidth": "400px",
            "width": "90%",
            "border": "1px solid #374151"
        })
    ], style={
        "minHeight": "100vh",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "backgroundColor": "#111827",
        "background": "linear-gradient(135deg, #111827 0%, #1F2937 100%)"
    })
])


# Layout do dashboard (após login)
dashboard_layout = html.Div(className="dashboard-container", children=[
    html.Div(className="watermark"),
        html.Div(id="botao-executar-container", className="mt-4"),
        html.Div(id="script-output", className="mt-3 text-white"),    
    html.Div(className="animate__animated animate__fadeIn p-4", children=[
        html.Div([
            html.I(className="fas fa-chart-line mr-2 text-primary", style={"fontSize": "2rem"}),
            html.H1("Dashboard de Atendimento WhatsApp", className="title animate__animated animate__fadeInDown text-center mb-4 d-inline-block ml-2")
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

        # Tabela de chamados
html.Div([
    html.H4("Lista de Chamados", className="text-white mb-3"),
    
    # Botões de exportação estilizados
    html.Div([
        html.Button('⬇ Exportar para CSV', id='btn-exportar-csv', className="btn btn-success mr-2"),
        html.Button('⬇ Exportar para Excel', id='btn-exportar-excel', className="btn btn-primary"),
    ], className="mb-3 d-flex align-items-center"),
    
    dcc.Download(id="download-dataframe-csv"),
    dcc.Download(id="download-dataframe-excel"),

    # Tabela interativa com paginação, ordenação e pesquisa
dash_table.DataTable(
    id='tabela-chamados',
    columns=[
        {"name": "Data e Hora", "id": "Data e Hora"},
        {"name": "Tipo de Chamado", "id": "Tipo de Chamado"},
        {"name": "Chamado", "id": "Chamado"},
        {"name": "Problema", "id": "Problema"}
    ],
    style_filter={
    'backgroundColor': '#2d2d2d',
    'color': 'white',
    'fontWeight': 'bold'
    },
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'fontWeight': 'bold',
        'color': 'white',
        'textAlign': 'center'
    },
    style_cell={
            'textAlign': 'center',
            'padding': '10px',
            'backgroundColor': '#2d2d2d',
            'color': 'white',
            'border': '1px solid #444'
        },
    style_cell_conditional=[{
    'if': {'column_id': 'Problema'},
    'textAlign': 'left',
    'minWidth': '300px', 
    'maxWidth': '500px',
    'whiteSpace': 'normal',
    'height': 'auto'
    }],
    style_table={
        'position': 'relative',
        'width': '100%',
        'marginBottom': '60px',
        'overflowX': 'auto'
    },
    style_data={
        'backgroundColor': '#2d2d2d',
        'color': 'white',
    },
    style_filter_conditional=[{
        'if': {'column_id': column} for column in ['Data e Hora', 'Tipo de Chamado', 'Chamado', 'Problema']
    }],
    css=[{
        'selector': '.dash-table-container input',
        'rule': 'color: white !important; background-color: #374151 !important;'
    }],    
    style_data_conditional=[{
        'if': {'row_index': 'odd'},
        'backgroundColor': '#1f1f1f'
    }],
    page_size=10,
    page_action='native',
    filter_action="native",
    sort_action="native"
)
    ,
], className="mt-4 p-4 bg-dark rounded"),

    ])
])

# Dashboard layout
app.layout = html.Div([
    dcc.Store(id='usuario-logado', storage_type='session'),
    html.Div(id="page-content", children=[login_layout])
])
    


@app.callback(
    Output("script-output", "children"),
    Input("btn-executar-script", "n_clicks"),
    prevent_initial_call=True  # Impede que a callback seja chamada ao carregar a página
)
def executar_script(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise dash.exceptions.PreventUpdate  # Impede a execução se não houve clique

    try:
        resultado = subprocess.run(
            ["python3", "run_all.py"],
            text=True,
            capture_output=True
        )

        if resultado.returncode == 0:
            mensagem = resultado.stdout.strip().split('\n')
            return dbc.Alert([
                html.H5("✅ Script executado com sucesso!", className="text-success mb-3"),
                html.Ul([html.Li(msg, className="text-light") for msg in mensagem if msg.strip()])
            ], color="success", className="mt-3 p-3 shadow")
        else:
            erro_msg = resultado.stderr.strip().split('\n')
            return dbc.Alert([
                html.H5("❌ Erro ao executar o script!", className="text-danger mb-3"),
                html.Ul([html.Li(msg, className="text-light") for msg in erro_msg if msg.strip()])
            ], color="danger", className="mt-3 p-3 shadow")
    except Exception as e:
        return dbc.Alert([
            html.H5("⚠️ Erro inesperado!", className="text-warning mb-3"),
            html.P(f"Detalhes: {str(e)}", className="text-light")
        ], color="warning", className="mt-3 p-3 shadow")





@app.callback(
    Output("botao-executar-container", "children"),
    Input("usuario-logado", "data"),  # Verifica usuário armazenado
    prevent_initial_call=True
)
def mostrar_botao_execucao(usuario):
    usuarios_permitidos = ["admin", "gestor"]  # Lista de usuários autorizados

    if usuario and usuario in usuarios_permitidos:
        return dbc.Button("Rodar Script", id="btn-executar-script", n_clicks=0, className="btn btn-warning")
    else:
        return ""  # Se o usuário não for permitido, não mostra nada



# Callback de autenticação do login
@app.callback(
    [Output("page-content", "children"),
     Output("login-feedback", "children"),
     Output("usuario-logado", "data")],  # Armazena usuário logado
    Input("btn-login", "n_clicks"),
    State("input-usuario", "value"),
    State("input-senha", "value")
)
def verificar_login(n_clicks, usuario, senha):
    if n_clicks > 0:
        for u in usuarios:
            if u["usuario"] == usuario and u["senha"] == senha:
                return dashboard_layout, "", usuario  # Retorna o dashboard e armazena usuário
        return login_layout, "Usuário ou senha incorretos", None
    return dash.no_update, "", dash.no_update


# Callback para logout
@app.callback(
    Output("page-content", "children", allow_duplicate=True),
    Input("btn-logout", "n_clicks"),
    prevent_initial_call=True
)
def realizar_logout(n_clicks):
    if n_clicks > 0:
        return login_layout
    return dash.no_update


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


# Callback para carregar a tabela de chamados
@app.callback(
    Output('tabela-chamados', 'data'),
    [Input('btn-analisar', 'n_clicks')]
)
def atualizar_tabela(n_clicks):
    df_chamados = carregar_chamados()

    if df_chamados.empty:
        return []

    return df_chamados.to_dict('records')


# Callback para exportar CSV
@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("btn-exportar-csv", "n_clicks")],
    prevent_initial_call=True
)
def exportar_para_csv(n_clicks):
    df_chamados = carregar_chamados()
    
    # Salvar o dataframe como CSV para download
    return dcc.send_data_frame(df_chamados.to_csv, "chamados_exportados.csv", index=False)

# Callback para exportar Excel
@app.callback(
    Output("download-dataframe-excel", "data"),
    [Input("btn-exportar-excel", "n_clicks")],
    prevent_initial_call=True
)
def exportar_para_excel(n_clicks):
    df_chamados = carregar_chamados()

    # Criando um buffer de memória para armazenar o arquivo Excel
    output = io.BytesIO()

    # Escrever os dados no buffer usando ExcelWriter
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_chamados.to_excel(writer, index=False, sheet_name='Chamados')
        writer.close()  # Fechar corretamente para garantir a gravação

    output.seek(0)  # Retornar ao início do buffer para leitura

    return dcc.send_bytes(output.getvalue(), "chamados_exportados.xlsx")

# Formatação das datas
def format_week_label(semana):
    try:
        inicio, fim = semana.split('/')
        data_inicio = datetime.strptime(inicio, '%Y-%m-%d')
        data_fim = datetime.strptime(fim, '%Y-%m-%d')
        return f"{data_inicio.strftime('%d/%m')} - {data_fim.strftime('%d/%m')}"
    except:
        return semana
    
# Função para carregar os chamados do CSV
def carregar_chamados():
    try:
        # Carregar o CSV com tratamento de caracteres especiais
        df_chamados = pd.read_csv('uploads/whatsapp_chamados_detailed.csv', encoding='utf-8', dtype=str)

        # Remover quebras de linha nas colunas de problema
        if 'Relato do Problema' in df_chamados.columns and 'Anomalia' in df_chamados.columns:
            df_chamados['Relato do Problema'] = df_chamados['Relato do Problema'].str.replace('\n', ' ', regex=True).str.strip()
            df_chamados['Anomalia'] = df_chamados['Anomalia'].str.replace('\n', ' ', regex=True).str.strip()

            # Unificar as colunas em uma única coluna 'Problema'
            df_chamados['Problema'] = df_chamados['Relato do Problema'].fillna('') + ' ' + df_chamados['Anomalia'].fillna('')
            
            # Remove as colunas originais
            df_chamados.drop(columns=['Relato do Problema', 'Anomalia'], inplace=True)

        # Selecionar apenas as colunas desejadas para exibição
        colunas_exibir = ['Data e Hora', 'Tipo de Chamado', 'Chamado', 'Problema']
        df_chamados = df_chamados[colunas_exibir]

        print(df_chamados.head())  # Verificar se os dados foram processados corretamente

        return df_chamados
    except Exception as e:
        print(f"Erro ao carregar chamados: {e}")
        return pd.DataFrame(columns=["Erro"], data=[[str(e)]])


    


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
    host='127.0.0.1',
    port=5000)