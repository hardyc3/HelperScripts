import sys
import time
import getpass
import os
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy
from paramiko import SFTPClient
from scp import SCPClient
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyEventHandler(FileSystemEventHandler):

    def __init__(self, username, ip_address, local_dir, remote_dir):
        '''
            Initializes local variables and captures a password for the ssh key
        '''
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        self.ip_address = ip_address
        self.username = username
        print("Enter your ssh key password (or enter if blank): ")
        self.password = getpass.getpass()
        print("Ready for monitoring")

    def dispatch(self, event):
        self.sync_folders(event)

    def on_any_event(self, event):
        self.sync_folders(event)

    def on_created(self, event):
        self.sync_folders(event)

    def on_deleted(self, event):
        self.sync_folders(event)

    def on_modified(self, event):
        self.sync_folders(event)

    def on_moved(self, event):
        self.sync_folders(event)
    
    def sync_folders(self, event):
        '''
            Connects to the remote server and uploads all the files in the 
            local_dir to the remote_dir
        '''
        try:
            print("detected change on: " + event.src_path)
            print("syching " + self.local_dir + " with remote " + self.remote_dir)
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.load_system_host_keys()
            if self.password == "":
                self.password = None
            ssh.connect(self.ip_address, username=self.username, password=self.password, timeout=2)
            
            pathArray = event.src_path.split('\\')
            fileName = pathArray[len(pathArray)-1]
            print("file: " + fileName)
            print("remote: " + self.remote_dir)
           
            scp = ssh.open_sftp()
            scp.put(event.src_path, self.remote_dir+"/"+fileName)
            scp.close()

        except Exception as e:
            print("Something failed: " + str(e))

if __name__ == "__main__":
    local_folder = sys.argv[1]
    remote_folder = sys.argv[2]
    username = sys.argv[3]
    ip_address = sys.argv[4]
    
    print("watching local folder: " + local_folder)
    print("remote folder: " + remote_folder + " on ip: " + username + "@" + ip_address)
    #watch files in folder for changes
    event_handler = MyEventHandler(username, ip_address, local_folder, remote_folder)
    observer = Observer()
    observer.schedule(event_handler, local_folder, recursive=True)
    observer.start()

    #Make sure we are available to capture a ctrl+c to close the program
    try: 
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    #make sure everything shuts down before ending
    observer.join()