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


class Volatile:

  def __init__(self):
    self.PANEL_HEIGHT    = 24    # in pixels, negative if panel is on bottom
    self.WINDOW_OPACITY  = 0.95  # 
    self.UPDATE_INTERVAL = 250   # in ms
    self.VOLUME_WIDTH    = 200   # in pixels
    self.VOLUME_HEIGHT   = 25    # in pixels, adjust if the widget doesn't fit
    self.SCROLL_BY       = 2     # increase to scroll "faster"

    self.init_volume()

    self.icon = gtk.StatusIcon()
    self.icon.connect('activate', self.show_window)
    self.icon.connect('popup-menu', self.toggle_mute)
    self.icon.connect('scroll-event', self.on_scroll)
    self.icon.timeout = gobject.timeout_add(self.UPDATE_INTERVAL, self.update)

    self.update()
    self.icon.set_visible(True)

    signal.signal(signal.SIGINT, gtk.main_quit)
    gtk.main()


  #
  # create the slider and containing window
  #
  def init_volume(self):
    self.window = gtk.Window(gtk.WINDOW_POPUP)
    self.window.set_opacity(self.WINDOW_OPACITY)

    self.slider = gtk.HScale()
    self.slider.set_can_focus(False)
    self.slider.set_size_request(self.VOLUME_WIDTH, self.VOLUME_HEIGHT)
    self.slider.set_range(0, 100)
    self.slider.set_increments(-self.SCROLL_BY, 12)
    self.slider.set_draw_value(0)
    self.slider.connect('value-changed', self.on_slide)

    self.frame = gtk.Frame()
    self.frame.set_shadow_type(gtk.SHADOW_OUT)
    self.frame.add(self.slider)
    self.window.add(self.frame)


  #
  # icon was clicked, show the window or re-hide it if already visible
  #
  def show_window(self, widget):
    if self.window.get_property('visible'):
      self.window.hide()
    else:
      self.update()
      self.window.set_position(gtk.WIN_POS_MOUSE)
      self.window.move(self.window.get_position()[0], self.PANEL_HEIGHT)
      self.window.show_all()
      self.window.present()


  #
  # set the volume to some level bound by [0,100]
  #
  def set_volume(self, level):
    volume = int(level)

    if volume > 100:
      volume = 100
    if volume < 0:
      volume = 0

    self.mixer.setvolume(volume)
    self.update()


  def toggle_mute(self, widget, button, time):
    self.mixer.setmute(not self.mixer.getmute()[0])
    self.update()


  #
  # event handler for the HScale being dragged
  #
  def on_slide(self, widget):
    volume = widget.get_value()
    self.set_volume(volume)


  #
  # event handler for scrolling while hovering the icon
  #
  def on_scroll(self, widget, event):
    volume = self.mixer.getvolume()[0]

    if event.direction == gtk.gdk.SCROLL_UP:
      self.set_volume(volume + (self.SCROLL_BY * 2))
    elif event.direction == gtk.gdk.SCROLL_DOWN:
      self.set_volume(volume - (self.SCROLL_BY * 2))


  #
  # updates the global mixer, moves slider and updates icon
  #
  def update(self):
    self.mixer = alsaaudio.Mixer('Master', 0, 0)

    volume = self.mixer.getvolume()[0]
    muted  = self.mixer.getmute()[0]

    self.slider.set_value(volume)

    if volume <= 0 or muted:
      self.icon.set_from_icon_name('audio-volume-muted')
    elif volume <= 20:
      self.icon.set_from_icon_name('audio-volume-off')
    elif volume <= 55:
      self.icon.set_from_icon_name('audio-volume-low')
    elif volume <= 90:
      self.icon.set_from_icon_name('audio-volume-medium')
    else:
      self.icon.set_from_icon_name('audio-volume-high')
    return True


if __name__ == '__main__':
  vol = Volatile();
