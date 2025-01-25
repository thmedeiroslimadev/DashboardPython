import zipfile
import os
import re
import csv
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, f'processCalled_{datetime.now().strftime("%Y%m%d")}.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def remove_whatsapp_formatting(message):
    # Remove WhatsApp-specific formatting like *bold*, _italic_, ~strikethrough~, and others
    message = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', message)  # Remove *bold* or **bold**
    message = re.sub(r'\_{1,2}([^_]+)\_{1,2}', r'\1', message)  # Remove _italic_ or __italic__
    message = re.sub(r'\~{1,2}([^~]+)\~{1,2}', r'\1', message)  # Remove ~strikethrough~
    message = re.sub(r'\`{1,3}([^`]+)\`{1,3}', r'\1', message)  # Remove `code` or ```code```

    # Explicitly remove any remaining ** format markers
    message = message.replace('**', '')  # Remove leftover **

    return message


def extract_all_messages(zip_path, output_csv):
    # Directory to extract the files
    extract_dir = "extracted_files"

    # Ensure the output directory exists
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # Extract ZIP content
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logging.info(f"ZIP content extracted to {extract_dir}")
    except Exception as e:
        logging.info(f"Failed to extract ZIP file: {e}")
        return

    messages = []
    unmatched_lines = []

    # Define pattern to capture all WhatsApp message details
    message_pattern = re.compile(
        r"(?P<DataHora>\d{2}/\d{2}/\d{4} \d{2}:\d{2}) - (?P<Remetente>([^:]+?):)? (?P<Mensagem>[\s\S]*?)(?=\n\d{2}/\d{2}/\d{4} \d{2}:\d{2} -|\Z)"
    )

    # Process each file in the extracted directory
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.txt'):  # Assuming conversations are in .txt files
                logging.info(f"Processing file: {file}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find all matches for WhatsApp messages
                matches = message_pattern.finditer(content)
                matched = False
                for match in matches:
                    matched = True
                    raw_message = match.group("Mensagem").strip()
                    cleaned_message = remove_whatsapp_formatting(raw_message)
                    contains_anomalia = "X" if "Anomalia" in cleaned_message else ""

                    # Extract "Chamado:" value if present
                    chamado_match = re.search(r"Chamado:\s*(\S+)", cleaned_message)
                    chamado = chamado_match.group(1) if chamado_match else ""

                    messages.append({
                        "Data e Hora": match.group("DataHora").strip(),
                        "Remetente": match.group("Remetente").strip() if match.group("Remetente") else "Desconhecido",
                        "Mensagem": cleaned_message,
                        "Tipo de Conteúdo": "Mídia" if "<Mídia oculta>" in raw_message else "Texto",
                        "Contém Anomalia": contains_anomalia,
                        "Chamado": chamado
                    })
                if not matched:
                    unmatched_lines.append(f"No matches in file: {file}\nContent:\n{content}\n")

    # Save messages to a CSV file
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=[
                "Data e Hora", "Remetente", "Mensagem", "Tipo de Conteúdo", "Contém Anomalia", "Chamado"
            ])
            writer.writeheader()
            for message in messages:
                writer.writerow(message)
        logging.info(f"Messages saved to: {output_csv}")
    except Exception as e:
        logging.info(f"Failed to save CSV file: {e}")

    # Save unmatched content to a log file for debugging
    unmatched_log = "logs/unmatched_lines.log"
    try:
        with open(unmatched_log, 'w', encoding='utf-8') as log_file:
            log_file.write("Unmatched Lines:\n")
            for line in unmatched_lines:
                log_file.write(line + "\n")
        logging.info(f"Unmatched lines saved to: {unmatched_log}")
    except Exception as e:
        logging.info(f"Failed to save log file: {e}")

    # Clean up extracted files
    try:
        for root, _, files in os.walk(extract_dir):
            for file in files:
                os.remove(os.path.join(root, file))
            os.rmdir(root)
        logging.info(f"Temporary files cleaned up from {extract_dir}")
    except Exception as e:
        logging.info(f"Failed to clean up extracted files: {e}")


# Main execution
if __name__ == "__main__":
    zip_file = "Conversa do WhatsApp com TI escalada.zip"  # ZIP file in the root of the project
    output_file = "whatsapp_messages.csv"  # Output CSV file
    extract_all_messages(zip_file, output_file)
