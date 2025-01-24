#!/bin/bash

# Exibir status do serviço
echo "Exibindo status do serviço dashboard-monitor..."
sudo systemctl status dashboard-monitor

# Perguntar se deseja monitorar logs em tempo real
read -p "Deseja monitorar os logs em tempo real? (s/n): " MONITOR_LOGS

if [[ "$MONITOR_LOGS" =~ ^[Ss]$ ]]; then
  echo "Monitorando logs em tempo real. Pressione Ctrl+C para sair."
  sudo journalctl -u dashboard-monitor.service -f
else
  echo "Logs em tempo real não foram exibidos."
fi
