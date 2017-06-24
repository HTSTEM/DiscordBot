import time
import subprocess

while True:
    subprocess.call(["python3.6", "joinbot.py"])
    print("[WARNING] Bot crashed at %d! Restarting!" % time.time())
