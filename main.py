from time import time, sleep
from threading import Timer
from os import popen
import threading
import curses
import platform
import subprocess
import math

class ColorPair:
  def __init__( self, curses_color, lower_limit ):
    self.color = curses_color
    self.limit = lower_limit

stdscr = curses.initscr()

curses.echo( False )
curses.start_color()
curses.init_pair( 1, 47,  curses.COLOR_BLACK ) # light green
curses.init_pair( 2, 71,  curses.COLOR_BLACK ) # green
curses.init_pair( 3, 221, curses.COLOR_BLACK ) # yellow
curses.init_pair( 4, 203, curses.COLOR_BLACK ) # light red
curses.init_pair( 5, 1,   curses.COLOR_BLACK ) # red
curses.init_pair( 6, 15,  curses.COLOR_BLACK ) # skull
colors_pairs = [
  ColorPair( 1, 0 ),
  ColorPair( 2, 30 ),
  ColorPair( 3, 120 ),
  ColorPair( 4, 180 ),
  ColorPair( 5, 400 )
]

current_time = lambda: int( round( time() * 1000 ) )
console_height, cosnole_width = [ int( i ) for i in popen( 'stty size', 'r' ).read().split() ]

host = ""
command = [ "ping", "-n" if platform.system().lower() == "windows" else "-c", "1", host ]

pings = []
setup_mode = True
biggest_ping = 0
interval_in_seconds = .5
average_from_minutes = 10
max_pings_count = int( average_from_minutes * 60 / interval_in_seconds )

info_new_address = '1'

def change_host( new_host:str ):
  global host

  host = new_host
  command[ 3 ] = host


def mapInt( num, range1A, range1B, range2A, range2B ):
  return (num - range1A) / (range1B - range1A) * (range2B - range2A) + range2A


def color_on_chart( ping ):
  for color_pair in colors_pairs:
    if color_pair.limit > ping:
      index = colors_pairs.index( color_pair )

      if index == 0:
        return color_pair.color
      return colors_pairs[ index - 1 ].color

  return colors_pairs[ - 1 ].color


def draw():
  global biggest_ping

  crossX = 6
  crossY = console_height - 3
  pingsLen = len( pings )
  biggestOnChart = 0 if pingsLen == 0 else max( pings[ slice( 0, cosnole_width - crossX ) ] )
  labels = [ math.floor( biggestOnChart / crossY * i ) for i in reversed( range( 1, crossY + 1 ) ) ]

  for h in range( 0, crossY ):
    stdscr.addstr( h, crossX, "║" )

  for w in range( 0, cosnole_width ):
    stdscr.addstr( crossY, w, "═" )

  stdscr.addstr( crossY, crossX, "╩" )

  for i in range( 0, len( pings ) - max_pings_count ):
    if pings.pop() == biggest_ping:
      biggest_ping = max( pings )

  for w in range( 0, cosnole_width - crossX - 1 ):
    ping = pings[ w ] if w < pingsLen else 0

    for h in range( 0, crossY ):
      color = 0
      char = ' '

      if ping == -1:
        color = 6
        char = '☠' if h == int( crossY / 2 ) else ' '
      else:
        height = math.floor( mapInt( ping, 0, biggestOnChart, 0, crossY ) )
        color = color_on_chart( labels[ crossY - h - 1 ] )
        char = '#' if height > h else ' '

      stdscr.addstr( crossY - h - 1, w + crossX + 1, char, curses.color_pair( color ) )

  for i in range( 0, crossY, 5 ):
    stdscr.addstr( i, 0, f"{labels[ i ]}".rjust( crossX - 1, ' ' ) )

  only_good_pings = [ ping for ping in filter( lambda ping: ping != -1, pings ) ]

  stdscr.addstr( crossY + 1, 0, "Adres: " )
  stdscr.addstr( host, curses.A_BOLD )
  stdscr.addstr( "   Ping: " + f"{pings[ 0 ]}    " )
  stdscr.addstr( f"   Aby wprowadzić nowy adres wciśnij {info_new_address} " )
  stdscr.addstr( crossY + 2, 0, f"Dane na przestrzeni " )
  stdscr.addstr( f"{len( only_good_pings )}".center( len( str( max_pings_count ) ) , ' ' ) + f" zliczeń ({1 / interval_in_seconds}/s)", curses.A_BOLD )
  stdscr.addstr( "   ->   " )
  stdscr.addstr( "Największy: " + f"{biggest_ping}".ljust( 6, ' ' ) )
  stdscr.addstr( "Średni: " + f"{round( sum( only_good_pings ) / pingsLen )}".ljust( 6, ' ' ) )

  curses.curs_set( 0 )
  stdscr.refresh()


def do_ping():
  global biggest_ping

  start = current_time()
  retcode = subprocess.call( command, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

  ping = -1 if retcode != 0 else current_time() - start

  if ping > biggest_ping:
    biggest_ping = ping

  pings.insert( 0, ping )


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

      if char == ord( info_new_address ):
        new_address()


def run():
  global setup_mode

  setup_mode = False
  threading.Thread( target=keys_detector ).start()

  while True:
    if not setup_mode:
      do_ping()
      draw()

    sleep( interval_in_seconds )


run()


##
##  CURSES COLORS VIEWER
##
#
# import curses
#
# max_height = 17
#
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
#
# curses.wrapper(main)