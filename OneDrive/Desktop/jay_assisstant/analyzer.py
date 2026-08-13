import datetime
import actions
from audio_engine import speak

def analyze_and_route_request(command):
    cmd = command.lower().strip()

    # 1. Direct System Commands (Tool Router)
    if any(w in cmd for w in ["volume up", "increase volume", "louder"]):
        actions.volume_up()
        return True, "EXECUTED_SIMPLE"

    elif any(w in cmd for w in ["volume down", "decrease volume", "quieter"]):
        actions.volume_down()
        return True, "EXECUTED_SIMPLE"

    elif any(w in cmd for w in ["mute", "silence"]):
        actions.mute_volume()
        return True, "EXECUTED_SIMPLE"

    elif "screenshot" in cmd or "capture screen" in cmd:
        actions.take_screenshot()
        return True, "EXECUTED_SIMPLE"

    elif any(w in cmd for w in ["check battery", "battery level", "battery status"]):
        actions.check_battery()
        return True, "EXECUTED_SIMPLE"

    elif any(w in cmd for w in ["check cpu", "cpu usage", "processor"]):
        actions.check_cpu()
        return True, "EXECUTED_SIMPLE"

    elif any(w in cmd for w in ["check memory", "ram usage", "memory status"]):
        actions.check_memory()
        return True, "EXECUTED_SIMPLE"

    elif any(w in cmd for w in ["check disk", "disk space", "storage"]):
        actions.check_disk()
        return True, "EXECUTED_SIMPLE"

    elif any(w in cmd for w in ["analyze system", "system analysis", "system status"]):
        actions.analyze_system()
        return True, "EXECUTED_SIMPLE"

    elif "shutdown pc" in cmd or "shut down pc" in cmd:
        actions.shutdown_pc()
        return True, "EXECUTED_SIMPLE"

    elif "restart pc" in cmd or "reboot pc" in cmd:
        actions.restart_pc()
        return True, "EXECUTED_SIMPLE"

    elif "sleep pc" in cmd or "hibernate" in cmd:
        actions.sleep_pc()
        return True, "EXECUTED_SIMPLE"

    elif "double click" in cmd:
        actions.mouse_click("double")
        return True, "EXECUTED_SIMPLE"

    elif "right click" in cmd:
        actions.mouse_click("right")
        return True, "EXECUTED_SIMPLE"

    elif "click" in cmd:
        actions.mouse_click("left")
        return True, "EXECUTED_SIMPLE"

    elif "scroll down" in cmd:
        actions.scroll_screen("down")
        return True, "EXECUTED_SIMPLE"

    elif "scroll up" in cmd:
        actions.scroll_screen("up")
        return True, "EXECUTED_SIMPLE"

    elif "what time" in cmd or "current time" in cmd:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time} IST Sir.")
        return True, "EXECUTED_SIMPLE"

    elif "what day" in cmd or "what date" in cmd or "today's date" in cmd:
        current_date = datetime.datetime.now().strftime("%A, %B %d %Y")
        speak(f"Today is {current_date} Sir.")
        return True, "EXECUTED_SIMPLE"

    elif "search" in cmd:
        actions.search_website(cmd)
        return True, "EXECUTED_SIMPLE"

    elif "open browser" in cmd or "open comet" in cmd:
        speak("Opening browser Sir.")
        actions.open_browser_url()
        return True, "EXECUTED_SIMPLE"

    elif "open youtube" in cmd:
        speak("Opening YouTube Sir.")
        actions.open_browser_url("https://www.youtube.com")
        return True, "EXECUTED_SIMPLE"

    elif "open google" in cmd:
        speak("Opening Google Sir.")
        actions.open_browser_url("https://www.google.com")
        return True, "EXECUTED_SIMPLE"

    elif "open amazon" in cmd:
        speak("Opening Amazon Sir.")
        actions.open_browser_url("https://www.amazon.in")
        return True, "EXECUTED_SIMPLE"

    elif "open" in cmd and len(cmd.split()) <= 3:
        app = cmd.replace("open", "").strip()
        actions.open_application(app)
        return True, "EXECUTED_SIMPLE"

    elif "close" in cmd and len(cmd.split()) <= 3:
        app = cmd.replace("close", "").strip()
        actions.close_application(app)
        return True, "EXECUTED_SIMPLE"

    elif any(w in cmd for w in ["sleep", "goodbye", "bye"]):
        return True, "SLEEP"

    elif any(w in cmd for w in ["exit", "shutdown jay", "turn off"]):
        return True, "EXIT"

    # 2. Goal-Based Request (Requires LLM Planner & Execution Manager)
    return False, "GOAL_BASED_REQUEST"
