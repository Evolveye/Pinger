from time import time
from threading import Timer
import platform
import subprocess

current_time = lambda: round( time() * 1000 )

host = "google.com"
param = "-n" if platform.system().lower() == "windows" else "-c"
command = [ "ping", param, "1", host ]

def ping():
  start = current_time()
  retcode = subprocess.call( command, stdout=subprocess.PIPE )

  print( f"ping: {current_time() - start}, code: {retcode}" )

  Timer( 1, ping ).start()

ping()