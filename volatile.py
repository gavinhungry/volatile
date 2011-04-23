#!/usr/bin/python2
#
# Name: volatile
# Auth: Gavin Lloyd <gavinhungry@gmail.com>
# Date: 21 Apr 2011
# Desc: Simple ALSA status icon and volume control
#

import alsaaudio
import gobject
import gtk
import pygtk
pygtk.require('2.0')

PANEL_HEIGHT    = 22
WINDOW_OPACITY  = 0.95
UPDATE_INTERVAL = 250 # ms
VOLUME_WIDTH    = 200
VOLUME_HEIGHT   = 25


def init_volume():
  global window
  window = gtk.Window(gtk.WINDOW_POPUP)
  window.set_opacity(WINDOW_OPACITY)

  global slider
  slider = gtk.HScale()
  slider.set_size_request(VOLUME_WIDTH, VOLUME_HEIGHT)
  slider.set_range(0, 100)
  slider.set_increments(-1, 12)
  slider.set_draw_value(0)
  slider.connect('value-changed', on_slide)

  frame = gtk.Frame()
  frame.set_shadow_type(gtk.SHADOW_OUT)
  frame.add(slider)
  window.add(frame)



def show_window(a):
  if window.get_property('visible'):
    window.hide()
  else:
    update_all()
    window.set_position(gtk.WIN_POS_MOUSE)
    window.move(window.get_position()[0], PANEL_HEIGHT)
    window.show_all()
    window.present()



def on_slide(widget):
  value = widget.get_value()
  set_volume(value)


def set_volume(level):
  mixer.setvolume(int(level))
  update_all()


def toggle_mute(a, b, c):
  mixer.setmute(not mixer.getmute()[0])
  update_all()



def hide_volume():
  window.hide()



def update_all():
  global mixer
  mixer = alsaaudio.Mixer('Master', 0, 0)

  volume = mixer.getvolume()[0]
  muted  = mixer.getmute()[0]

  slider.set_value(volume)

  if volume <= 0 or muted:
    icon.set_from_icon_name('audio-volume-muted')
  elif volume <= 35:
    icon.set_from_icon_name('audio-volume-low')
  elif volume <= 80:
    icon.set_from_icon_name('audio-volume-medium')
  else:
    icon.set_from_icon_name('audio-volume-high')

  return True


def volatile():
  init_volume()

  global icon
  icon = gtk.StatusIcon()
  icon.connect('activate',   show_window)
  icon.connect('popup-menu', toggle_mute)

  update_all()
  icon.set_visible(1)


  icon._timeout = gobject.timeout_add(UPDATE_INTERVAL, update_all)
  gtk.main()

if __name__ == '__main__':
  volatile()

