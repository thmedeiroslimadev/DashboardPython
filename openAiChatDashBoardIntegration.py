import os
from dotenv import load_dotenv
import openai
import pandas as pd

# Load environment variables
load_dotenv()

def analisar_chamados(csv_file_path):
    try:
        # Load data from CSV
        df = pd.read_csv(csv_file_path)
        csv_string = df.to_csv(index=False)

        # Get API key from environment variable
        openai.api_key = os.getenv('OPENAI_API_KEY')

        if not openai.api_key:
            raise ValueError("OpenAI API key not found in environment variables")

        # Define prompts
        system_prompt = "Você é um assistente útil que responde sempre em português."
        user_message = csv_string + "\nFaça uma análise dos chamados e me retorne o resultado, resuma os tipos de chamado!"

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message['content']

    except openai.error.InvalidRequestError as e:
        return f"Error in request: {e}"
    except openai.error.AuthenticationError as e:
        return f"Authentication error: {e}"
    except openai.error.OpenAIError as e:
        return f"OpenAI API error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"