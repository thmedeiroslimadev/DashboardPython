import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import subprocess
import time
import os
from datetime import datetime
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, f'monitor_{datetime.now().strftime("%Y%m%d")}.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_processed = {}
        self.processing_lock = False
        self.process = None

    def run_processing(self):
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = BASE_DIR
            self.process = subprocess.Popen(
                ["python3", os.path.join(BASE_DIR, "run_all.py")],
                env=env,
                cwd=BASE_DIR
            )
            self.process.wait()
        except Exception as e:
            logging.error(f"Error in processing: {e}")
            return False
        return True

    def on_modified(self, event):
        if self.processing_lock:
            logging.info("Skipping due to lock")
            return

        if not isinstance(event, FileModifiedEvent) or event.is_directory:
            return

        filepath = event.src_path
        current_time = time.time()

        if filepath in self.last_processed:
            if current_time - self.last_processed[filepath] < 10:
                return

        try:
            self.processing_lock = True
            self.last_processed[filepath] = current_time
            logging.info(f"Processing modified file: {filepath}")

            if not self.run_processing():
                logging.error("Processing failed")

        except Exception as e:
            logging.error(f"Error handling file modification: {e}")
        finally:
            self.processing_lock = False
            if self.process:
                self.process = None


def signal_handler(signum, frame):
    logging.info("Received shutdown signal")
    raise KeyboardInterrupt


def main():
    signal.signal(signal.SIGTERM, signal_handler)
    path = os.path.join(BASE_DIR, "uploads")
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
        logging.info("Monitor stopped")
    observer.join()


if __name__ == "__main__":
    main()