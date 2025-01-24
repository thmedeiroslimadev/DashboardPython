import zipfile
import os
import re
import csv

def remove_whatsapp_formatting(message):
    # Remove WhatsApp-specific formatting like *bold*, _italic_, etc.
    message = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', message)
    message = re.sub(r'\_{1,2}([^_]+)\_{1,2}', r'\1', message)
    message = re.sub(r'\~{1,2}([^~]+)\~{1,2}', r'\1', message)
    message = re.sub(r'\`{1,3}([^`]+)\`{1,3}', r'\1', message)
    message = message.replace('**', '')
    return message

def extract_all_messages(zip_path, output_csv, responses_csv):
    extract_dir = "extracted_files"

    # Ensure the extraction directory exists
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # Extract ZIP content
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"ZIP content extracted to {extract_dir}")
    except Exception as e:
        print(f"Failed to extract ZIP file: {e}")
        return

    messages = []
    responses = []
    unmatched_lines = []

    # Define pattern to capture WhatsApp messages
    message_pattern = re.compile(
        r"(?P<DataHora>\d{2}/\d{2}/\d{4} \d{2}:\d{2}) - (?P<Remetente>([^:]+?):)? (?P<Mensagem>[\s\S]*?)(?=\n\d{2}/\d{2}/\d{4} \d{2}:\d{2} -|\Z)"
    )

    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.txt'):
                print(f"Processing file: {file}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                matches = message_pattern.finditer(content)
                matched = False
                for match in matches:
                    matched = True
                    raw_message = match.group("Mensagem").strip()
                    cleaned_message = remove_whatsapp_formatting(raw_message)

                    # Extract chamado number if present
                    chamado_match = re.search(r"Chamado\s+(INC\d+)", cleaned_message)
                    chamado = chamado_match.group(1) if chamado_match else ""

                    tipo_resposta = ""

                    # Para os tipos específicos:
                    if "sendo tratado pela" in cleaned_message:
                        tipo_resposta = "Pendente"
                        chamado_match = re.search(r"Chamado\s+(INC\d+)\s+sendo", cleaned_message)
                        chamado = chamado_match.group(1) if chamado_match else chamado
                    elif "Resolvido" in cleaned_message:
                        tipo_resposta = "Resolvido"
                        chamado_match = re.search(r"Chamado\s+(INC\d+)\s+Resolvido", cleaned_message)
                        chamado = chamado_match.group(1) if chamado_match else chamado
                    elif "sendo tratado pelo time Quality." in cleaned_message:
                        tipo_resposta = "Andamento"
                        chamado_match = re.search(r"Chamado\s+(INC\d+)", cleaned_message)
                        chamado = chamado_match.group(1) if chamado_match else chamado

                    if tipo_resposta:
                        responses.append({
                            "Data e Hora": match.group("DataHora").strip(),
                            "Remetente": match.group("Remetente").strip() if match.group("Remetente") else "Desconhecido",
                            "Mensagem": cleaned_message,
                            "Chamado": chamado,
                            "Tipo de Resposta": tipo_resposta
                        })

                    messages.append({
                        "Data e Hora": match.group("DataHora").strip(),
                        "Remetente": match.group("Remetente").strip() if match.group("Remetente") else "Desconhecido",
                        "Mensagem": cleaned_message
                    })

                if not matched:
                    unmatched_lines.append(f"No matches in file: {file}\nContent:\n{content}\n")

    # Save all messages to a CSV file
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["Data e Hora", "Remetente", "Mensagem"])
            writer.writeheader()
            for message in messages:
                writer.writerow(message)
        print(f"Messages saved to: {output_csv}")
    except Exception as e:
        print(f"Failed to save CSV file: {e}")

    # Save responses to a separate CSV file
    try:
        with open(responses_csv, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["Data e Hora", "Remetente", "Mensagem", "Chamado", "Tipo de Resposta"])
            writer.writeheader()
            for response in responses:
                writer.writerow(response)
        print(f"Responses saved to: {responses_csv}")
    except Exception as e:
        print(f"Failed to save responses CSV file: {e}")

    # Save unmatched lines to a log file
    unmatched_log = "unmatched_lines.log"
    try:
        with open(unmatched_log, 'w', encoding='utf-8') as log_file:
            log_file.write("Unmatched Lines:\n")
            for line in unmatched_lines:
                log_file.write(line + "\n")
        print(f"Unmatched lines saved to: {unmatched_log}")
    except Exception as e:
        print(f"Failed to save log file: {e}")

    # Clean up extracted files
    try:
        for root, _, files in os.walk(extract_dir):
            for file in files:
                os.remove(os.path.join(root, file))
            os.rmdir(root)
        print(f"Temporary files cleaned up from {extract_dir}")
    except Exception as e:
        print(f"Failed to clean up extracted files: {e}")

if __name__ == "__main__":
    zip_file = "Conversa do WhatsApp com TI escalada.zip"
    output_file = "whatsapp_messages.csv"
    responses_file = "responses_to_chamados.csv"
    extract_all_messages(zip_file, output_file, responses_file)
