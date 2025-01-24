# /home/quality/DashboardPython/monitor.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time


class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        subprocess.run(["python3", "/home/quality/DashboardPython/run_all.py"])


def main():
    path = "/home/quality/DashboardPython/uploads"
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