from time import time
from threading import Timer
from os import popen
import curses
import platform
import subprocess

host = "google.com"
param = "-n" if platform.system().lower() == "windows" else "-c"
command = [ "ping", param, "1", host ]
current_time = lambda: round( time() * 1000 )
console_height, cosnole_width = [ int(i) for i in popen('stty size', 'r').read().split() ]

stdscr = curses.initscr()

def draw():
  crossX = 6
  crossY = console_height - 3

  for h in range( 0, console_height - 3 ):
    stdscr.addstr( h, crossX, "║" )

  for w in range( 0, cosnole_width - 1 ):
    stdscr.addstr( crossY, w, "═" )

  stdscr.addstr( crossY, crossX, "╩" )
  curses.curs_set( 0 )
  stdscr.refresh()


def ping():
  start = current_time()
  retcode = subprocess.call( command, stdout=subprocess.PIPE )

  stdscr.addstr( 1, 10, f"ping: {current_time() - start}, code: {retcode}   " )

  draw()

  Timer( 1, ping ).start()


ping()