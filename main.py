from time import time, sleep
from threading import Timer
from os import popen
import sys
import threading
import pygcurse
import platform
import subprocess
import math

class ColorPair:
  def __init__( self, lower_limit, chart_color ):
    self.color = chart_color
    self.limit = lower_limit

win = pygcurse.PygcurseWindow( 100, 50 )
win.autoupdate = False

color_default = pygcurse.Color( 175, 175, 175 )
color_distinction = pygcurse.Color( 255, 255, 255 )
color_frame_fg = pygcurse.Color( 100, 100, 100 )
color_frame_bg = pygcurse.Color( 50, 50, 50 )

colors_pairs = [
  ColorPair( 0,   pygcurse.Color( 0,   255, 0 ) ),
  ColorPair( 30,  pygcurse.Color( 0,   175, 0 ) ),
  ColorPair( 120, pygcurse.Color( 255, 255, 0 ) ),
  ColorPair( 180, pygcurse.Color( 255, 0,   0 ) ),
  ColorPair( 400, pygcurse.Color( 175, 0,   0 ) ),
]

current_time = lambda: int( round( time() * 1000 ) )
console_height = win.height
cosnole_width = win.width

host = ""
command = [ "ping", "-n" if platform.system().lower() == "windows" else "-c", "1", host ]

pings = []
running = True
setup_mode = True
biggest_ping = 0
interval_in_seconds = .5
average_from_minutes = 10
max_pings_count = int( average_from_minutes * 60 / interval_in_seconds )

info_new_address = '1'

frame_cross = "+" # "╩"
frame_colums = "|" # "║"
frame_row = "-" # "═"


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
  global setup_mode, biggest_ping

  crossX = 6
  crossY = console_height - 5
  pingsLen = len( pings )
  biggestOnChart = 0 if pingsLen == 0 else max( pings[ slice( 0, cosnole_width - crossX ) ] )
  labels = [ math.floor( biggestOnChart / crossY * i ) for i in reversed( range( 1, crossY + 1 ) ) ]

  for y in range( 0, crossY ):
    win.write( frame_colums, crossX, y, color_frame_fg, color_frame_bg )

  for x in range( 0, cosnole_width ):
    win.write( frame_row, x, crossY, color_frame_fg, color_frame_bg )

  win.write( frame_cross, crossX, crossY, color_frame_fg, color_frame_bg )

  for y in range( 0, len( pings ) - max_pings_count ):
    if pings.pop() == biggest_ping:
      biggest_ping = max( pings )

  for x in range( 0, cosnole_width - crossX - 1 ):
    ping = pings[ x ] if x < pingsLen else 0

    for y in range( 0, crossY ):
      color = 0
      char = ' '

      if ping == -1:
        color = pygcurse.Color( 255, 255, 255 )
        char = 'X' if y == int( crossY / 2 ) else ' '
      else:
        height = math.floor( mapInt( ping, 0, biggestOnChart, 0, crossY ) )
        color = color_on_chart( labels[ crossY - y - 1 ] )
        char = '#' if height > y else ' '

      win.putchars( char, x + crossX + 1, crossY - y - 1, color )

  for y in range( 0, crossY, 5 ):
    win.write( f"{labels[ y ]}".rjust( crossX - 1, ' ' ), 0, y )

  only_good_pings = [ ping for ping in filter( lambda ping: ping != -1, pings ) ]

  win.write( "Adres: ", 1, crossY + 2 )
  win.write( host, fgcolor=color_distinction )
  win.write( "   Ping: " + f"{pings[ 0 ]}    " )
  win.write( f"   Aby wprowadzić nowy adres wciśnij {info_new_address} " )
  win.write( f"Dane na przestrzeni ", 1, crossY + 3 )
  win.write( f"{len( only_good_pings )}".center( len( str( max_pings_count ) ) , ' ' ) + f" zliczeń ({1 / interval_in_seconds}/s)", fgcolor=color_distinction )
  win.write( "   ->   " )
  win.write( "Największy: " + f"{biggest_ping}".ljust( 6, ' ' ) )
  win.write( "Średni: " + f"{round( sum( only_good_pings ) / pingsLen )}".ljust( 6, ' ' ) )

  if not setup_mode:
    win.update()


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

  setup_mode = True

  clear()

  win.write( "Wprowadź nowy adres: ", 2, 2, color_distinction )

  change_host( win.input() )

  setup_mode = False

  clear()


def clear():
  win.setscreencolors( clear=True )


def keys_detector():
  global setup_mode, running

  while running:
    for event in pygcurse.pygame.event.get():
      if event.type == pygcurse.QUIT or (event.type == pygcurse.KEYDOWN and event.key == pygcurse.K_ESCAPE):
        pygcurse.pygame.quit()
        running = False
        break
      elif event.type == pygcurse.KEYDOWN:
        if event.unicode == info_new_address:
          new_address()


def run():
  global setup_mode, running

  setup_mode = False
  threading.Thread( target=keys_detector ).start()

  while running:
    if not setup_mode:
      do_ping()
      draw()

    sleep( interval_in_seconds )


run()