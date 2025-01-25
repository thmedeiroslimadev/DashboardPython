#!/bin/bash

# Nome do arquivo de serviço
SERVICE_FILE="/etc/systemd/system/dashboard-monitor.service"

# Caminho do script Python
SCRIPT_PATH="/home/quality/DashboardPython/monitor.py"

# Caminho do ambiente virtual
VENV_PATH="/home/quality/DashboardPython/venv/bin/python"

# Criar o arquivo de serviço
echo "Criando o serviço dashboard-monitor..."
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Dashboard Directory Monitor
After=network.target

[Service]
Type=simple
User=quality
Group=quality
ExecStart=$VENV_PATH $SCRIPT_PATH
Restart=on-failure
UMask=002

[Install]
WantedBy=multi-user.target
EOL

# Ajustar permissões para o diretório de uploads
echo "Ajustando permissões no diretório de uploads..."
UPLOADS_DIR="/home/quality/DashboardPython/uploads"
sudo chmod -R 775 $UPLOADS_DIR
sudo chmod g+s $UPLOADS_DIR
sudo chown -R quality:quality $UPLOADS_DIR

# Recarregar o daemon do systemd e iniciar o serviço
echo "Recarregando daemon do systemd..."
sudo systemctl daemon-reload

echo "Habilitando o serviço para iniciar no boot..."
sudo systemctl enable dashboard-monitor

echo "Iniciando o serviço dashboard-monitor..."
sudo systemctl start dashboard-monitor

echo "Serviço dashboard-monitor instalado e iniciado com sucesso."
