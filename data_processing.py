import pandas as pd
import json
import logging
from datetime import datetime

# Configuração do logging
logging.basicConfig(
    filename='processamento.log',  # Arquivo de log na raiz do projeto
    level=logging.INFO,  # Nível de log INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato do log
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info("Início do processamento de métricas.")

try:
    # Carregar os arquivos CSV
    logging.info("Carregando os arquivos CSV.")
    whatsapp_chamados = pd.read_csv("uploads/whatsapp_chamados_detailed.csv", delimiter=",", encoding="utf-8")
    first_responses = pd.read_csv("uploads/first_responses.csv", delimiter=",", encoding="utf-8")
    latest_responses = pd.read_csv("uploads/latest_responses.csv", delimiter=",", encoding="utf-8")

    # Convertendo colunas de data para datetime com tratamento de erro
    logging.info("Convertendo colunas de data para datetime.")
    whatsapp_chamados['Data e Hora'] = pd.to_datetime(whatsapp_chamados['Data e Hora'], format='%d/%m/%Y %H:%M', errors='coerce')
    first_responses['Data e Hora'] = pd.to_datetime(first_responses['Data e Hora'], format='%d/%m/%Y %H:%M', errors='coerce')
    latest_responses['Data e Hora'] = pd.to_datetime(latest_responses['Data e Hora'], format='%d/%m/%Y %H:%M', errors='coerce')

    # Criando colunas de agrupamento por mês e semana
    whatsapp_chamados['AnoMes'] = whatsapp_chamados['Data e Hora'].dt.to_period('M').astype(str)
    whatsapp_chamados['AnoSemana'] = whatsapp_chamados['Data e Hora'].dt.to_period('W').astype(str)

    logging.info("Gerando métricas de chamados.")
    
    # Chamados abertos por atendente hoje
    chamados_abertos_hoje = whatsapp_chamados[whatsapp_chamados['Data e Hora'].dt.date == pd.Timestamp.today().date()]
    chamados_por_atendente_hoje = chamados_abertos_hoje['Remetente'].value_counts().to_dict()

    # Chamados abertos por atendente no mês
    chamados_abertos_mes = whatsapp_chamados[whatsapp_chamados['Data e Hora'].dt.month == pd.Timestamp.today().month]
    chamados_por_atendente_mes = chamados_abertos_mes['Remetente'].value_counts().to_dict()

    # Chamados semanais por mês
    chamados_semana_mes = whatsapp_chamados.groupby(['AnoMes', 'AnoSemana'])['Chamado'].count().unstack(fill_value=0).to_dict()

    # Tempo médio de atendimento
    merged_responses = pd.merge(
        first_responses[['Chamado', 'Data e Hora']].rename(columns={'Data e Hora': 'Data_Inicial'}),
        latest_responses[['Chamado', 'Data e Hora']].rename(columns={'Data e Hora': 'Data_Final'}),
        on='Chamado'
    )
    merged_responses['Tempo_Atendimento_Minutos'] = (merged_responses['Data_Final'] - merged_responses['Data_Inicial']).dt.total_seconds() / 60
    tempo_medio_atendimento = merged_responses['Tempo_Atendimento_Minutos'].mean()

    # Tempo médio de primeira resposta
    merged_first_response = pd.merge(
        whatsapp_chamados[['Chamado', 'Data e Hora']].rename(columns={'Data e Hora': 'Data_Abertura'}),
        first_responses[['Chamado', 'Data e Hora']].rename(columns={'Data e Hora': 'Data_Resposta'}),
        on='Chamado'
    )
    merged_first_response['Tempo_Resposta_Minutos'] = (merged_first_response['Data_Resposta'] - merged_first_response['Data_Abertura']).dt.total_seconds() / 60
    tempo_medio_resposta = merged_first_response['Tempo_Resposta_Minutos'].mean()

    # Criando o dicionário de métricas
    metricas_dashboard = {
        "Total de Chamados": whatsapp_chamados['Chamado'].nunique(),
        "Chamados Abertos Hoje": chamados_abertos_hoje.shape[0],
        "Chamados Fechados Hoje": latest_responses[latest_responses['Data e Hora'].dt.date == pd.Timestamp.today().date()].shape[0],
        "Chamados Abertos Mês": chamados_abertos_mes.shape[0],
        "Chamados Fechados Mês": latest_responses[latest_responses['Data e Hora'].dt.month == pd.Timestamp.today().month].shape[0],
        "Chamados por Atendente": chamados_abertos_mes['Remetente'].value_counts().to_dict(),
        "Tempo Médio de Atendimento": round(tempo_medio_atendimento, 2),
        "Tempo Médio de Resposta": round(tempo_medio_resposta, 2),
        "Chamados Abertos por Atendente Hoje": chamados_por_atendente_hoje,
        "Chamados Abertos por Atendente Mês": chamados_por_atendente_mes,
        "Chamados Semana Mês": chamados_semana_mes
    }

    # Salvar métricas no arquivo JSON
    with open("metricas.json", "w") as f:
        json.dump(metricas_dashboard, f, indent=4)

    logging.info("Métricas salvas com sucesso no arquivo 'metricas.json'.")
    print("Processamento concluído! Métricas salvas em 'metricas.json'.")

except Exception as e:
    logging.error(f"Erro durante o processamento: {e}", exc_info=True)
    print("Ocorreu um erro durante o processamento. Verifique o arquivo de log para mais detalhes.")
