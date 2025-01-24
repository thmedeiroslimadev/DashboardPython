import os
import openai
import pandas as pd



df = pd.read_csv('whatsapp_chamados_detailed.csv')

csv_string = df.to_csv(index=False)

print(csv_string)

# **IMPORTANTE:** Certifique-se de ter revogado a chave anterior e gerado uma nova.
# Defina a nova chave de API como uma variável de ambiente para segurança.

# No código, recupere a chave da variável de ambiente
openai.api_key = os.getenv('OPENAI_API_KEY')

# Verifique se a chave de API está definida
if not openai.api_key:
    raise ValueError("A chave da API da OpenAI não está definida. Defina a variável de ambiente OPENAI_API_KEY.")

# Defina o prompt do sistema em português para orientar o modelo
system_prompt = "Você é um assistente útil que responde sempre em português."

# Defina a mensagem do usuário em português
user_message = csv_string + "Faça uma análise dos chamados e me retorne o resultado."

try:
    # Faça uma chamada para o ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Alterado para gpt-3.5-turbo
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=150,
        temperature=0.7  # Ajuste a criatividade da resposta conforme necessário
    )

    # Exiba a resposta
    resposta = response.choices[0].message['content']
    print(resposta)

except openai.error.InvalidRequestError as e:
    # Erro específico de requisição inválida
    print(f"Erro na requisição: {e}")
except openai.error.AuthenticationError as e:
    # Erro de autenticação
    print(f"Erro de autenticação: {e}")
except openai.error.OpenAIError as e:
    # Outros erros da OpenAI
    print(f"Ocorreu um erro ao chamar a API da OpenAI: {e}")
except Exception as e:
    # Erros gerais
    print(f"Ocorreu um erro inesperado: {e}")
