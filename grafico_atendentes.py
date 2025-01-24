import pandas as pd
import plotly.express as px
import json

# Carregar métricas salvas
with open("metricas.json", "r") as f:
    metricas_dashboard = json.load(f)

# Ordenar atendentes pelo número de chamados e selecionar os Top 10
sorted_atendentes = sorted(metricas_dashboard["Chamados por Atendente"].items(), key=lambda x: x[1], reverse=True)

# Selecionar os 10 atendentes com mais chamados
top_n = 10
top_atendentes = dict(sorted_atendentes[:top_n])

# Criando gráfico atualizado de chamados por atendente (Top 10) com rótulos
fig_atendentes = px.bar(
    x=list(top_atendentes.keys()),
    y=list(top_atendentes.values()),
    labels={'x': 'Atendente', 'y': 'Número de Chamados'},
    title="Top 10 Atendentes com Mais Chamados",
    color=list(top_atendentes.values()),
    color_continuous_scale="Blues",
    text_auto=True,  # Adiciona rótulos nos valores das barras
    template="plotly_dark"
)

# Ajustando layout para melhorar a visibilidade dos rótulos
fig_atendentes.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)




# Mostrar gráfico no navegador
fig_atendentes.show()
