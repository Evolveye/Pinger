from time import time
from threading import Timer
from os import popen
import curses
import platform
import subprocess
import math

host = ""
pings = []
param = "-n" if platform.system().lower() == "windows" else "-c"
command = [ "ping", param, "1", host ]
biggestPing = 0
intervalInSeconds = .5
averageFromMinutes = 10
countOfPings = int( averageFromMinutes * 60 / intervalInSeconds )
current_time = lambda: (int) (round( time() * 1000 ))
console_height, cosnole_width = [ int(i) for i in popen('stty size', 'r').read().split() ]

stdscr = curses.initscr()
curses.start_color()
curses.init_pair( 1, 47,  curses.COLOR_BLACK ) # light green
curses.init_pair( 2, 71,  curses.COLOR_BLACK ) # green
curses.init_pair( 3, 221, curses.COLOR_BLACK ) # yellow
curses.init_pair( 4, 203, curses.COLOR_BLACK ) # light red
curses.init_pair( 5, 1, curses.COLOR_BLACK ) # red


def mapInt( num, range1A, range1B, range2A, range2B ):
  return (num - range1A) / (range1B - range1A) * (range2B - range2A) + range2A


def draw():
  global biggestPing

  crossX = 6
  crossY = console_height - 3
  pingsLen = len( pings )
  biggestOnChart = 0 if pingsLen == 0 else max( pings[ slice( 0, cosnole_width - crossX ) ] )
  labels = range( 0, int( (crossY - 1) / 5 ) + 1 )

  for h in range( 0, crossY ):
    stdscr.addstr( h, crossX, "║" )

  for w in range( 0, cosnole_width - 1 ):
    stdscr.addstr( crossY, w, "═" )

  stdscr.addstr( crossY, crossX, "╩" )

  for i in range( 0, len( pings ) - countOfPings ):
    if pings.pop() == biggestPing:
      biggestPing = max( pings )

  for w in range( 0, cosnole_width - crossX - 1 ):
    if w < pingsLen:
      for h in range( 0, crossY ):
        height = math.floor( mapInt( pings[ w ], 0, biggestOnChart, 0, crossY ) )

        char = '#' if height >= h else ' '
        color = math.floor( mapInt( h, 0, crossY, 1, 6 ) )
        stdscr.addstr( crossY - h - 1, w + crossX + 1, char, curses.color_pair( color ) )

  for i in labels:
    stdscr.addstr( i * 5, 0, f"{round( biggestOnChart / (i + 1) )}".rjust( crossX - 1, ' ' ) )

  stdscr.addstr( crossY + 1, 0, "Adres: " )
  stdscr.addstr( host, curses.A_BOLD )
  stdscr.addstr( "   Ping: " + f"{pings[ 0 ]}    " )
  stdscr.addstr( crossY + 2, 0, f"Dane na przestrzeni " )
  stdscr.addstr( f"{pingsLen}".center( len( str( countOfPings ) ) , ' ' ) + f" zliczeń ({intervalInSeconds}/s)", curses.A_BOLD )
  stdscr.addstr( "   ->   " )
  stdscr.addstr( "Największy: " + f"{biggestPing}".ljust( 6, ' ' ) )
  stdscr.addstr( "Średni: " + f"{round( sum( pings ) / pingsLen )}".ljust( 6, ' ' ) )

  curses.curs_set( 0 )
  stdscr.refresh()


def doPing():
  global biggestPing

  start = current_time()
  retcode = subprocess.call( command, stdout=subprocess.PIPE )

  ping = current_time() - start

  if ping > biggestPing:
    biggestPing = ping

  pings.insert( 0, ping )

  draw()

  # Timer( 1, doPing ).start()
  Timer( intervalInSeconds, doPing ).start()


host = "google.com"
command = [ "ping", param, "1", host ]
doPing()

# import curses

# max_height = 17

# def main(stdscr):
#     curses.start_color()
#     curses.use_default_colors()
#     for i in range(0, curses.COLORS):
#         curses.init_pair(i + 1, i, -1)
#     try:
#         for i in range(0, 255):
#             stdscr.addstr( i % max_height, (int)(i / max_height) * 7, f"▉▉#{i}", curses.color_pair(i))
#     except curses.ERR:
#         # End of screen reached
#         pass
#     stdscr.getch()

# curses.wrapper(main)