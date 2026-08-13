import os
import datetime
import subprocess
import webbrowser
import pyautogui
import psutil
from urllib.parse import quote
from config import BROWSER_PATH
from audio_engine import speak

def open_browser_url(url=""):
    try:
        if os.path.exists(BROWSER_PATH):
            if url:
                subprocess.Popen([BROWSER_PATH, url])
            else:
                subprocess.Popen([BROWSER_PATH])
        else:
            if url:
                webbrowser.open(url)
            else:
                webbrowser.open("https://www.google.com")
    except Exception as e:
        print(f"Error opening browser: {e}")
        if url:
            webbrowser.open(url)

def check_battery():
    battery = psutil.sensors_battery()
    if battery:
        plugged = "plugged in" if battery.power_plugged else "not plugged in"
        speak(f"Battery is at {battery.percent}% and {plugged}.")
    else:
        speak("Battery info is currently unavailable.")

def check_cpu():
    cpu = psutil.cpu_percent(interval=1)
    cores = psutil.cpu_count()
    speak(f"CPU usage is at {cpu}% across {cores} cores.")

def check_memory():
    mem = psutil.virtual_memory()
    used = mem.used / (1024**3)
    total = mem.total / (1024**3)
    speak(f"Memory is at {mem.percent}%, using {used:.1f} GB of {total:.1f} GB.")

def check_disk():
    disk = psutil.disk_usage("/")
    free = disk.free / (1024**3)
    speak(f"Disk is {disk.percent}% full with {free:.1f} GB free.")

def analyze_system():
    speak("Running system analysis. One moment.")
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    battery = psutil.sensors_battery()
    bat_str = f"{battery.percent}%" if battery else "unavailable"
    report = f"CPU at {cpu}%, memory at {mem.percent}%, disk at {disk.percent}%, battery at {bat_str}."
    
    recommendations = []
    if cpu > 80:
        recommendations.append("CPU load is high.")
    if mem.percent > 85:
        recommendations.append("RAM usage is high.")
    if disk.percent > 90:
        recommendations.append("Storage is running low.")
        
    full_report = report + (" " + " ".join(recommendations) if recommendations else " All systems running smoothly.")
    speak(full_report)

def take_screenshot():
    try:
        path = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots", f"jay_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        speak("Screenshot saved to your Pictures folder.")
    except Exception as e:
        speak(f"Could not take screenshot: {e}")

def volume_up():
    pyautogui.press("volumeup")
    speak("Volume up.")

def volume_down():
    pyautogui.press("volumedown")
    speak("Volume down.")

def mute_volume():
    pyautogui.press("volumemute")
    speak("Muted.")

def shutdown_pc():
    speak("Shutting down the system. Catch you later!")
    subprocess.run(["shutdown", "/s", "/t", "10"])

def restart_pc():
    speak("Restarting the system.")
    subprocess.run(["shutdown", "/r", "/t", "10"])

def sleep_pc():
    speak("Putting the system to sleep.")
    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])

def open_application(app_name):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "file explorer": "explorer.exe",
        "word": "WINWORD.EXE",
        "excel": "EXCEL.EXE",
        "powerpoint": "POWERPNT.EXE",
        "paint": "mspaint.exe",
        "task manager": "taskmgr.exe",
    }
    app_lower = app_name.lower().strip()
    if app_lower in apps:
        try:
            subprocess.Popen(apps[app_lower])
            speak(f"Opening {app_name}.")
        except Exception:
            speak(f"Could not open {app_name}.")
    else:
        try:
            subprocess.run(["cmd", "/c", "start", "", app_name], check=True)
            speak(f"Opening {app_name}.")
        except Exception:
            speak(f"Could not find application {app_name}.")

def close_application(app_name):
    try:
        subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], check=True)
        speak(f"Closing {app_name}.")
    except Exception:
        speak(f"Could not close {app_name}.")

def mouse_click(click_type="left"):
    if "double" in click_type:
        pyautogui.doubleClick()
        speak("Double clicked.")
    elif "right" in click_type:
        pyautogui.rightClick()
        speak("Right clicked.")
    else:
        pyautogui.click()
        speak("Clicked.")

def scroll_screen(direction="up"):
    if "down" in direction:
        pyautogui.scroll(-300)
        speak("Scrolled down.")
    else:
        pyautogui.scroll(300)
        speak("Scrolled up.")

def search_website(command):
    if " in " in command:
        parts = command.split(" in ")
        query = parts[0].replace("search", "").strip()
        app = parts[1].strip().lower()
        website_searches = {
            "amazon": f"https://www.amazon.in/s?k={quote(query)}",
            "youtube": f"https://www.youtube.com/results?search_query={quote(query)}",
            "flipkart": f"https://www.flipkart.com/search?q={quote(query)}",
            "email": f"https://mail.google.com/mail/u/1/#inbox/search?q={quote(query)}",
            "spotify": f"https://open.spotify.com/search/{quote(query)}",
            "twitter": f"https://twitter.com/search?q={quote(query)}",
            "github": f"https://github.com/search?q={quote(query)}",
            "wikipedia": f"https://en.wikipedia.org/wiki/{quote(query)}",
            "chatgpt": f"https://chatgpt.com/search?q={quote(query)}",
        }
        if app in website_searches:
            speak(f"Searching for {query} in {app}.")
            open_browser_url(website_searches[app])
        else:
            speak(f"Searching for {query}.")
            open_browser_url(f"https://www.google.com/search?q={quote(query)}")
    else:
        query = command.replace("search", "").strip()
        speak(f"Searching for {query}.")
        open_browser_url(f"https://www.google.com/search?q={quote(query)}")
