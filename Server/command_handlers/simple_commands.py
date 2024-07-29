def handle_simple_commands(server, command):
    server.clients[server.current_client_ip].send(command.encode())
    if command == 'sendmessage':
        text = input("Enter the text: ")
        server.clients[server.current_client_ip].send(text.encode())
        title = input("Enter the title: ")
        server.clients[server.current_client_ip].send(title.encode())
    result_output = server.clients[server.current_client_ip].recv(1024).decode()
    return result_output
