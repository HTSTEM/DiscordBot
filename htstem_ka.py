import time
import subprocess

while True:
    subprocess.call(["python3.6", "htstem_bote_wrapper.py"])
    print("[WARNING] Bot crashed at %d! Restarting!" % time.time())
