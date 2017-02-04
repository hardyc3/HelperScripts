import sys
import time
from paramiko import SSHClient
from scp import SCPClient
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import LoggingEventHandler

class MyEventHandler(FileSystemEventHandler):

    def __init__(self, local_dir, remote_dir):
        self.local_dir = local_dir
        self.remote_dir = remote_dir

    def dispatch(self, event):
        print("dispatch: " + str(event))
        self.sync_folders()

    def on_any_event(self, event):
        print("on_any_event: " + str(event))
        self.sync_folders()

    def on_created(self, event):
        print("on_created: " + str(event))
        self.sync_folders()

    def on_deleted(self, event):
        print("on_deleted: " + str(event))
        self.sync_folders()

    def on_modified(self, event):
        print("on_modified: " + str(event))
        self.sync_folders()

    def on_moved(self, event):
        print("on_moved: " + str(event))
        self.sync_folders()
    
    def sync_folders(self):
        print("syching " + self.local_dir + " with remote " + self.remote_dir)


if __name__ == "__main__":
    local_folder = sys.argv[1]
    remote_folder = sys.argv[2]
    ip_address = sys.argv[3]
    
    print("watching local folder: " + local_folder)
    print("remote folder: " + remote_folder + " on ip: " + ip_address)
    #watch files in folder for changes
    event_handler = MyEventHandler(local_folder, remote_folder)
    observer = Observer()
    observer.schedule(event_handler, local_folder, recursive=True)
    observer.start()

    try: 
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    #when changes happen scp changed files to remote folder