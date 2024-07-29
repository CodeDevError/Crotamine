import logging
from command_handlers import execute_command

def setup_event_handlers(server):
    @server.sio.event
    def connect():
        logging.debug('Connected to server')

    @server.sio.event
    def connect_error(data):
        logging.debug(f'Connection failed: {data}')

    @server.sio.event
    def disconnect():
        logging.debug('Disconnected from server')

    @server.sio.on('server-message')
    def on_server_message(message):
        logging.debug(f'Server message: {message}')

    @server.sio.on('client-update')
    def on_client_update(data):
        logging.debug(f'Client update: {data}')

    @server.sio.on('client-command')
    def on_client_command(data):
        command = data['command']
        logging.debug(f'Received command: {command}')
        result = execute_command(server, command)
        server.sio.emit('client-command-response', {'status': 'success', 'message': result})

    @server.sio.on('connect')
    def on_connect():
        client_ip = server.sio.sid
        server.set_current_client(client_ip, server.sio)
        logging.debug(f'Client connected: {client_ip}')
