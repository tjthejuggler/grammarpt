import subprocess
import time
import requests

def is_anki_running():
    try:
        response = requests.post('http://localhost:8765', json={"action": "version", "version": 6}, timeout=1)
        return response.status_code == 200
    except Exception:
        return False

def launch_anki():
    subprocess.Popen(["anki"])
    time.sleep(4)  # Wait for Anki to start (increase if needed)

def ensure_anki_running():
    if not is_anki_running():
        launch_anki()
        # Wait and check again
        for _ in range(10):
            if is_anki_running():
                return True
            time.sleep(1)
        return False
    return True