import zipfile
import os
import re
import csv

def remove_whatsapp_formatting(message):
    """Remove formatting such as bold, italic, and strikethrough from WhatsApp messages."""
    message = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', message)
    message = re.sub(r'\_{1,2}([^_]+)\_{1,2}', r'\1', message)
    message = re.sub(r'\~{1,2}([^~]+)\~{1,2}', r'\1', message)
    message = re.sub(r'\`{1,3}([^`]+)\`{1,3}', r'\1', message)
    message = message.replace('**', '')
    return message

def extract_unanswered_calls(zip_path, unanswered_csv):
    """Extract chamados without a response and save to CSV."""
    extract_dir = "extracted_files"

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"ZIP content extracted to {extract_dir}")
    except Exception as e:
        print(f"Failed to extract ZIP file: {e}")
        return

    all_chamados = {}
    answered_chamados = set()

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
                for match in matches:
                    raw_message = match.group("Mensagem").strip()
                    cleaned_message = remove_whatsapp_formatting(raw_message)

                    chamado_match = re.search(r"Chamado\s+(INC\d+)", cleaned_message)
                    chamado = chamado_match.group(1) if chamado_match else None

                    if chamado:
                        # Store all chamados
                        if chamado not in all_chamados:
                            all_chamados[chamado] = {
                                "Data de Abertura": match.group("DataHora").strip(),
                                "Chamado": chamado,
                                "Mensagem Inicial": cleaned_message
                            }
                        # Check for response indicators
                        if "sendo tratado pela" in cleaned_message or "Resolvido" in cleaned_message or "Quality" in cleaned_message:
                            answered_chamados.add(chamado)

    # Filter chamados without response
    unanswered_chamados = [v for k, v in all_chamados.items() if k not in answered_chamados]

    with open(unanswered_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["Data de Abertura", "Chamado", "Mensagem Inicial"])
        writer.writeheader()
        for chamado in unanswered_chamados:
            writer.writerow(chamado)
    print(f"Unanswered chamados saved to: {unanswered_csv}")

    # Clean up extracted files
    for root, _, files in os.walk(extract_dir):
        for file in files:
            os.remove(os.path.join(root, file))
        os.rmdir(root)
    print(f"Temporary files cleaned up from {extract_dir}")

if __name__ == "__main__":
    zip_file = "Conversa do WhatsApp com TI escalada.zip"
    unanswered_file = "unanswered_chamados.csv"
    extract_unanswered_calls(zip_file, unanswered_file)
