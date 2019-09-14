from time import time, sleep
from threading import Timer
from os import popen
import threading
import curses
import platform
import subprocess
import math

stdscr = curses.initscr()

curses.echo( False )
curses.start_color()
curses.init_pair( 1, 47,  curses.COLOR_BLACK ) # light green
curses.init_pair( 2, 71,  curses.COLOR_BLACK ) # green
curses.init_pair( 3, 221, curses.COLOR_BLACK ) # yellow
curses.init_pair( 4, 203, curses.COLOR_BLACK ) # light red
curses.init_pair( 5, 1,   curses.COLOR_BLACK ) # red
curses.init_pair( 6, 15,  curses.COLOR_BLACK ) # skull

current_time = lambda: int( round( time() * 1000 ) )
console_height, cosnole_width = [ int( i ) for i in popen( 'stty size', 'r' ).read().split() ]

host = ""
command = [ "ping", "-n" if platform.system().lower() == "windows" else "-c", "1", host ]

pings = []
setup_mode = True
biggest_ping = 0
interval_in_seconds = .5
average_from_minutes = 10
count_of_pings = int( average_from_minutes * 60 / interval_in_seconds )

def change_host( new_host:str ):
  global host

  host = new_host
  command[ 3 ] = host


def mapInt( num, range1A, range1B, range2A, range2B ):
  return (num - range1A) / (range1B - range1A) * (range2B - range2A) + range2A


def draw():
  global biggest_ping

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

  for i in range( 0, len( pings ) - count_of_pings ):
    if pings.pop() == biggest_ping:
      biggest_ping = max( pings )

  for w in range( 0, cosnole_width - crossX - 1 ):
    if w < pingsLen:
      for h in range( 0, crossY ):
        ping = pings[ w ]

        if ping == -1:
          stdscr.addstr( int( crossY / 2 ), w + crossX + 1, '☠', curses.color_pair( 6 ) )
        else:
          height = math.floor( mapInt( ping, 0, biggestOnChart, 0, crossY ) )

          char = '#' if height >= h else ' '
          color = math.floor( mapInt( h, 0, crossY, 1, 6 ) )
          stdscr.addstr( crossY - h - 1, w + crossX + 1, char, curses.color_pair( color ) )

  for i in labels:
    stdscr.addstr( i * 5, 0, f"{round( biggestOnChart / (i + 1) )}".rjust( crossX - 1, ' ' ) )

  stdscr.addstr( crossY + 1, 0, "Adres: " )
  stdscr.addstr( host, curses.A_BOLD )
  stdscr.addstr( "   Ping: " + f"{pings[ 0 ]}    " )
  stdscr.addstr( crossY + 2, 0, f"Dane na przestrzeni " )
  stdscr.addstr( f"{pingsLen}".center( len( str( count_of_pings ) ) , ' ' ) + f" zliczeń ({interval_in_seconds}/s)", curses.A_BOLD )
  stdscr.addstr( "   ->   " )
  stdscr.addstr( "Największy: " + f"{biggest_ping}".ljust( 6, ' ' ) )
  stdscr.addstr( "Średni: " + f"{round( sum( pings ) / pingsLen )}".ljust( 6, ' ' ) )
  stdscr.addstr( "Setup: " + f"{setup_mode}".ljust( 6, ' ' ) )

  curses.curs_set( 0 )
  stdscr.refresh()


def doPing():
  global biggest_ping

  start = current_time()
  retcode = subprocess.call( command, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

  ping = -1 if retcode != 0 else current_time() - start

  if ping > biggest_ping:
    biggest_ping = ping

  pings.insert( 0, ping )

  # draw()

  # Timer( 1, doPing ).start()
  # Timer( interval_in_seconds, doPing ).start()


def new_address():
  global setup_mode

  clear()

  stdscr.addstr( 2, 2, "Wprowadź nowy adres: ", curses.A_BOLD )

  setup_mode = True
  curses.echo( True )
  string = stdscr.getstr().decode( encoding="utf-8" )
  curses.echo( False )
  setup_mode = False

  change_host( string )

  clear()


def clear():
  for w in range( 0, cosnole_width - 1 ):
    for h in range( 0, console_height ):
      stdscr.addstr( h, w, ' ' )


def keys_detector():
  global setup_mode

  while True:
    if not setup_mode:
      char = stdscr.getch()

      if char == ord( '[' ):
        new_address()


def run():
  global setup_mode

  setup_mode = False
  threading.Thread( target=keys_detector ).start()

  while True:
    if not setup_mode:
      doPing()
      draw()

    sleep( interval_in_seconds )


run()
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