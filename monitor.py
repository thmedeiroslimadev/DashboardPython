import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import subprocess
import time
import os
from datetime import datetime

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'monitor_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_processed = {}

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent) or event.is_directory:
            return

        filepath = event.src_path
        current_time = time.time()

        if filepath in self.last_processed:
            # Ignore if less than 5 seconds since last process
            if current_time - self.last_processed[filepath] < 5:
                return

        self.last_processed[filepath] = current_time
        logging.info(f"Processing modified file: {filepath}")
        subprocess.run(["python3", "/home/quality/DashboardPython/run_all.py"])


def main():
    path = "/home/quality/DashboardPython/uploads"
    logging.info(f"Starting monitor for directory: {path}")

    handler = ChangeHandler()
    observer = Observer()
    observer.schedule(handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Monitor stopped by user")
    observer.join()


if __name__ == "__main__":
    main()