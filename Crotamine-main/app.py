from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    ip = request.remote_addr  # Get client IP address
    logging.debug(f'Client connected: {sid} from IP: {ip}')
    clients[sid] = ip
    emit('server-message', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    logging.debug(f'Client disconnected: {sid}')
    if sid in clients:
        del clients[sid]

@socketio.on('client-command')
def handle_client_command(data):
    command = data.get('command')
    if command:
        logging.debug(f'Received command from client: {command}')
        # Send the command to the server
        socketio.emit('server-command', {'command': command})
    else:
        logging.debug('Received invalid command')
        emit('server-message', {'message': 'Received invalid command'}, broadcast=True)

@socketio.on('server-response')
def handle_server_response(response):
    logging.debug(f'Received response from server: {response}')
    # Emit the response back to the client
    emit('server-message', response, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
