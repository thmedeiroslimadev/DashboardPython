from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import logging
import os
from datetime import datetime

# Configuração do logger
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'monitor_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        subprocess.run(["python3", "/home/quality/DashboardPython/run_all.py"])
        logging.info(f"Running script: {event.src_path}")
        logging.info(f"Event type: {event.event_type}")



def main():
    path = "/home/quality/DashboardPython/uploads"
    logging.info(f"Monitoring directory: {path}")
    handler = ChangeHandler()
    observer = Observer()
    observer.schedule(handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
