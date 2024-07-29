def handle_file_commands(server, command):
    if command.startswith('sendfile'):
        return send_file(server, command)
    elif command == 'download':
        return download_file(server)
    elif command == 'upload':
        return upload_file(server)
    return "Command not recognized"

def send_file(server, command):
    try:
        filename = command.split(' ')[1]
        with open(filename, 'rb') as f:
            l = f.read(1024)
            while l:
                server.current_client_socket.send(l)
                l = f.read(1024)
        return 'File Sent'
    except Exception as e:
        return str(e)

def download_file(server):
    try:
        file = server.current_client_socket.recv(1024)
        if file:
            with open('new_file', 'wb') as f:
                f.write(file)
        return "File is downloaded"
    except Exception as e:
        return str(e)

def upload_file(server, command):
    server.clients[server.current_client_ip].send(command.encode())
    file = input("Enter the filepath to the file: ")
    filename = input("Enter the filepath to outgoing file (with filename and extension): ")
    with open(file, 'rb') as data:
        filedata = data.read(2147483647)
    server.clients[server.current_client_ip].send(filename.encode())
    server.clients[server.current_client_ip].send(filedata)
    return "File has been sent"
