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

def extract_all_messages(zip_path, output_csv):
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
                print(f"Processing file: {file}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                matches = message_pattern.finditer(content)
                matched = False
                for match in matches:
                    matched = True
                    raw_message = match.group("Mensagem").strip()
                    cleaned_message = remove_whatsapp_formatting(raw_message)

                    # Extracting data for Chamados Regionais
                    if "Chamado Regional" in cleaned_message:
                        tipo_chamado = "Chamado Regional"
                        region_match = re.search(r"Chamado Regional (\S+)", cleaned_message)
                        region = region_match.group(1) if region_match else ""
                        filial_match = re.search(r"Filial:\s*(\S+)", cleaned_message)
                        filial = filial_match.group(1) if filial_match else ""
                        tabela_match = re.search(r"Tabela:\s*(\S+)", cleaned_message)
                        tabela = tabela_match.group(1) if tabela_match else ""
                        relato_match = re.search(r"Relato.*?:\s*(.*)", cleaned_message, re.DOTALL)
                        relato = relato_match.group(1).strip() if relato_match else ""
                        cliente_match = re.search(r"Cliente:\s*(\S+)", cleaned_message)
                        cliente = cliente_match.group(1) if cliente_match else ""
                        cpf_match = re.search(r"CPF:\s*(\d+)", cleaned_message)
                        cpf = cpf_match.group(1) if cpf_match else ""
                        pedido_match = re.search(r"Pedido Vtx:\s*(\S+)", cleaned_message)
                        pedido_vtx = pedido_match.group(1) if pedido_match else ""
                        nf_match = re.search(r"NF:\s*(\S+)", cleaned_message)
                        nf = nf_match.group(1) if nf_match else ""
                        contato_match = re.search(r"Contato:\s*(.*)", cleaned_message)
                        contato = contato_match.group(1).strip() if contato_match else ""

                        # Extract chamado number
                        chamado_match = re.search(r"Chamado:\s*(\S+)", cleaned_message)
                        chamado = chamado_match.group(1) if chamado_match else ""

                        messages.append({
                            "Data e Hora": match.group("DataHora").strip(),
                            "Remetente": match.group("Remetente").strip() if match.group("Remetente") else "Desconhecido",
                            "Tipo de Chamado": tipo_chamado,
                            "Região": region,
                            "Filial": filial,
                            "Tabela": tabela,
                            "Relato do Problema": relato,
                            "Cliente": cliente,
                            "CPF": cpf,
                            "Pedido Vtx": pedido_vtx,
                            "NF": nf,
                            "Contato": contato,
                            "Chamado": chamado
                        })

                    # Extracting data for Chamados Lojas
                    elif "Chamados lojas" in cleaned_message:
                        tipo_chamado = "Chamado Lojas"
                        nome_loja_match = re.search(r"Nome da loja:\s*(.*)", cleaned_message)
                        nome_loja = nome_loja_match.group(1).strip() if nome_loja_match else ""
                        filial_match = re.search(r"Filial:\s*(\S+)", cleaned_message)
                        filial = filial_match.group(1) if filial_match else ""
                        chamado_match = re.search(r"Chamado:\s*(\S+)", cleaned_message)
                        chamado = chamado_match.group(1) if chamado_match else ""
                        anomalia_match = re.search(r"Anomalia:\s*(.*)", cleaned_message, re.DOTALL)
                        anomalia = anomalia_match.group(1).strip() if anomalia_match else ""
                        cliente_match = re.search(r"CLIENTE:\s*(.*)", cleaned_message)
                        cliente = cliente_match.group(1).strip() if cliente_match else ""
                        cpf_match = re.search(r"CPF:\s*(\d+)", cleaned_message)
                        cpf = cpf_match.group(1) if cpf_match else ""
                        telefone_match = re.search(r"Telefone.*?:\s*(.*)", cleaned_message)
                        telefone = telefone_match.group(1).strip() if telefone_match else ""

                        messages.append({
                            "Data e Hora": match.group("DataHora").strip(),
                            "Remetente": match.group("Remetente").strip() if match.group("Remetente") else "Desconhecido",
                            "Tipo de Chamado": tipo_chamado,
                            "Nome da Loja": nome_loja,
                            "Filial": filial,
                            "Chamado": chamado,
                            "Anomalia": anomalia,
                            "Cliente": cliente,
                            "CPF": cpf,
                            "Telefone": telefone
                        })

                    if not matched:
                        unmatched_lines.append(f"No matches in file: {file}\nContent:\n{content}\n")

    # Save messages to a CSV file
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = [
                "Data e Hora", "Remetente", "Tipo de Chamado", "Região", "Filial", "Tabela",
                "Relato do Problema", "Cliente", "CPF", "Pedido Vtx", "NF", "Contato",
                "Nome da Loja", "Chamado", "Anomalia", "Telefone"
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for message in messages:
                writer.writerow(message)
        print(f"Messages saved to: {output_csv}")
    except Exception as e:
        print(f"Failed to save CSV file: {e}")

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
    output_file = "whatsapp_chamados_detailed.csv"
    extract_all_messages(zip_file, output_file)
