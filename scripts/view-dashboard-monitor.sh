#!/bin/bash

# Default action is view if no parameter provided
ACTION=${1:-view}

case "$ACTION" in
   start)
       echo "Starting dashboard-monitor service..."
       sudo systemctl start dashboard-monitor
       ;;
   stop)
       echo "Stopping dashboard-monitor service..."
       sudo systemctl stop dashboard-monitor
       ;;
   restart)
       echo "Restarting dashboard-monitor service..."
       sudo systemctl restart dashboard-monitor
       ;;
   view|status)
       echo "Dashboard monitor status:"
       sudo systemctl status dashboard-monitor

       read -p "Monitor logs in real-time? (y/n): " VIEW_LOGS
       if [[ "$VIEW_LOGS" =~ ^[Yy]$ ]]; then
           echo "Showing real-time logs. Press Ctrl+C to exit."
           sudo journalctl -u dashboard-monitor.service -f
       fi
       ;;
   *)
       echo "Usage: $0 {start|stop|restart|view}"
       exit 1
       ;;
esac

exit 0