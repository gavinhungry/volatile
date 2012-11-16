#!/usr/bin/python2
#
# Name: volatile
# Auth: Gavin Lloyd <gavinhungry@gmail.com>
# Date: 21 Apr 2011 (last modified: 15 Nov 2012)
# Desc: Simple ALSA status icon and volume control
#

import pygtk
import gtk
import alsaaudio
import gobject
import signal
pygtk.require("2.0")

PANEL_HEIGHT    = 24    # in pixels, negative if panel is on the bottom
WINDOW_OPACITY  = 0.95  # 
UPDATE_INTERVAL = 250   # in ms
VOLUME_WIDTH    = 200   # in pixels
VOLUME_HEIGHT   = 25    # in pixels, adjust if the widget doesn't fit
SCROLL_BY       = 2     # increase to scroll "faster"


def volatile():
  init_volume()

  global icon
  icon = gtk.StatusIcon()
  icon.connect('activate',   show_window)
  icon.connect('popup-menu', toggle_mute)
  icon.connect('scroll-event', on_scroll)
  icon.timeout = gobject.timeout_add(UPDATE_INTERVAL, update_all)

  update_all()
  icon.set_visible(1)

  gtk.main()


#
# create the slider and containing window
#
def init_volume():
  global window
  window = gtk.Window(gtk.WINDOW_POPUP)
  window.set_opacity(WINDOW_OPACITY)

  global slider
  slider = gtk.HScale()
  slider.set_size_request(VOLUME_WIDTH, VOLUME_HEIGHT)
  slider.set_range(0, 100)
  slider.set_increments(-SCROLL_BY, 12)
  slider.set_draw_value(0)
  slider.connect('value-changed', on_slide)

  frame = gtk.Frame()
  frame.set_shadow_type(gtk.SHADOW_OUT)
  frame.add(slider)
  window.add(frame)


#
# icon was clicked, show the window or re-hide it if already visible
#
def show_window(widget):
  if window.get_property('visible'):
    window.hide()
  else:
    update_all()
    window.set_position(gtk.WIN_POS_MOUSE)
    window.move(window.get_position()[0], PANEL_HEIGHT)
    window.show_all()
    window.present()


#
# set the volume to some level bound by [0,100]
#
def set_volume(level):
  volume = int(level)

  if volume > 100:
    volume = 100
  if volume < 0:
    volume = 0

  mixer.setvolume(volume)
  update_all()


def toggle_mute(widget, button, time):
  mixer.setmute(not mixer.getmute()[0])
  update_all()


#
# event handler for the HScale being dragged
#
def on_slide(widget):
  volume = widget.get_value()
  set_volume(volume)


#
# event handler for scrolling while hovering the icon
#
def on_scroll(widget, event):
  volume = mixer.getvolume()[0]

  if event.direction == gtk.gdk.SCROLL_UP:
    set_volume(volume + (SCROLL_BY*2))
  elif event.direction == gtk.gdk.SCROLL_DOWN:
    set_volume(volume - (SCROLL_BY*2))


#
# updates the global mixer, moves slider and updates icon
#
def update_all():
  global mixer
  mixer = alsaaudio.Mixer('Master', 0, 0)

  volume = mixer.getvolume()[0]
  muted  = mixer.getmute()[0]

  slider.set_value(volume)

  if volume <= 0 or muted:
    icon.set_from_icon_name('audio-volume-muted')
  elif volume <= 20:
    icon.set_from_icon_name('audio-volume-off')
  elif volume <= 55:
    icon.set_from_icon_name('audio-volume-low')
  elif volume <= 90:
    icon.set_from_icon_name('audio-volume-medium')
  else:
    icon.set_from_icon_name('audio-volume-high')
  return True


if __name__ == '__main__':
  signal.signal(signal.SIGINT, gtk.main_quit)
  volatile()
