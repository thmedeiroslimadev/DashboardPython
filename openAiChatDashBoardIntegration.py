import os
import openai
import pandas as pd


def analisar_chamados(csv_file_path):
    try:
        # Carregar dados do CSV
        df = pd.read_csv(csv_file_path)
        csv_string = df.to_csv(index=False)

        # Configurar a chave da API
        openai.api_key = os.getenv('OPENAI_API_KEY')

        if not openai.api_key:
            raise ValueError(
                "A chave da API da OpenAI não está definida. Defina a variável de ambiente OPENAI_API_KEY.")

        # Definir prompt
        system_prompt = "Você é um assistente útil que responde sempre em português."
        user_message = csv_string + "\nFaça uma análise dos chamados e me retorne o resultado, resuma os tipos de chamado!"

        # Chamada à API da OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # Retorna a resposta da API
        return response.choices[0].message['content']

    except openai.error.InvalidRequestError as e:
        return f"Erro na requisição: {e}"
    except openai.error.AuthenticationError as e:
        return f"Erro de autenticação: {e}"
    except openai.error.OpenAIError as e:
        return f"Ocorreu um erro ao chamar a API da OpenAI: {e}"
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"
