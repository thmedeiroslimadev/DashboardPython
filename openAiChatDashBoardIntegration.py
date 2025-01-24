import os
from dotenv import load_dotenv
import openai
import pandas as pd

# Load environment variables at startup
load_dotenv()


def analisar_chamados(csv_file_path):
    try:
        df = pd.read_csv(csv_file_path)
        csv_string = df.to_csv(index=False)

        # Get API key from environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        openai.api_key = api_key

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil que responde sempre em português."},
                {"role": "user",
                 "content": csv_string + "\nFaça uma análise dos chamados e me retorne o resultado, resuma os tipos de chamado!"}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message['content']

    except Exception as e:
        return f"Error: {str(e)}"