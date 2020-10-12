#!/usr/bin/env python2
#
# volatile: ALSA status icon and volume control
# https://github.com/gavinhungry/volatile
#

import alsaaudio
import getopt
import gobject
import gtk
import pygtk
import signal
import sys

pygtk.require("2.0")

class Volatile:
  def __init__(self, reverse, card):
    self.REVERSE_SCROLL  = reverse
    self.CARD            = int(card)
    self.MASTER          = alsaaudio.mixers(self.CARD)[0]

    self.PANEL_HEIGHT    = 34    # in pixels, negative if panel is on bottom
    self.WINDOW_OPACITY  = 0.95  #
    self.VOLUME_WIDTH    = 200   # in pixels
    self.VOLUME_HEIGHT   = 25    # in pixels, adjust if the widget doesn't fit
    self.SCROLL_BY       = 3     # increase to scroll "faster"
    self.MAX_VOLUME      = 90    # limit volume percentage

    self.VOLUME_MULTIPLIER = float(100) / self.MAX_VOLUME

    if self.REVERSE_SCROLL:
      self.SCROLL_BY *= -1

    self.init_gtk()
    self.init_alsa()

    self.update()
    self.icon.set_visible(True)

    signal.signal(signal.SIGINT, gtk.main_quit)
    gtk.main()

  # create the icon, slider and containing window
  def init_gtk(self):
    self.icon = gtk.StatusIcon()
    self.icon.connect('activate', self.toggle_window)
    self.icon.connect('popup-menu', self.toggle_mute)
    self.icon.connect('scroll-event', self.on_scroll)

    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_skip_taskbar_hint(True)
    self.window.set_skip_pager_hint(True)
    self.window.set_decorated(False)
    self.window.set_resizable(False)
    self.window.set_keep_above(True)
    self.window.set_wmclass('volatile', 'volatile')
    self.window.set_opacity(self.WINDOW_OPACITY)
    self.window.connect('focus-out-event', self.on_focus_out)

    self.slider = gtk.HScale()
    self.slider.set_can_focus(False)
    self.slider.set_size_request(self.VOLUME_WIDTH, self.VOLUME_HEIGHT)
    self.slider.set_range(0, 100)
    self.slider.set_increments(-self.SCROLL_BY, -self.SCROLL_BY * 2)
    self.slider.set_draw_value(0)
    self.slider.connect('value-changed', self.on_slide)

    self.frame = gtk.Frame()
    self.frame.set_shadow_type(gtk.SHADOW_OUT)
    self.frame.add(self.slider)

    self.window.add(self.frame)

  # define mixer and start watch
  def init_alsa(self):
    try:
      self.mixer = alsaaudio.Mixer(self.MASTER, 0, self.CARD)
    except alsaaudio.ALSAAudioError:
      print >> sys.stderr, 'Could not initialize mixer'
      sys.exit(2)

    try:
      self.headphone = alsaaudio.Mixer('Headphone', 0, self.CARD)
      self.speaker = alsaaudio.Mixer('Speaker', 0, self.CARD)
    except alsaaudio.ALSAAudioError:
      pass

    fd, eventmask = self.mixer.polldescriptors()[0];
    gobject.io_add_watch(fd, eventmask, self.watch)

  def show_window(self):
    self.window.set_position(gtk.WIN_POS_MOUSE)
    self.window.move(self.window.get_position()[0], self.PANEL_HEIGHT)
    self.window.show_all()
    self.window.present()

  def hide_window(self):
    self.window.hide()

  def toggle_window(self, widget):
    if self.window.get_property('visible'):
      self.hide_window()
    else:
      self.show_window()

  # toggle current mute state
  def toggle_mute(self, widget, button, time):
    mute = not self.mixer.getmute()[0]

    self.mixer.setmute(mute)

    if hasattr(self, 'headphone'):
      self.headphone.setmute(mute)

    if hasattr(self, 'speaker'):
      self.speaker.setmute(mute)

  def clamp(self, value, min = 0, max = 100):
    if value > max:
      return max
    if value < min:
      return min

    return int(round(value))

  def level_to_volume(self, level):
    volume = level / self.VOLUME_MULTIPLIER
    return self.clamp(volume, 0, self.MAX_VOLUME)

  def volume_to_level(self, volume):
    level = volume * self.VOLUME_MULTIPLIER
    return self.clamp(level, 0, 100)

  def get_level(self):
    volume = self.mixer.getvolume()[0]
    return self.volume_to_level(volume)

  def set_level(self, level):
    volume = self.level_to_volume(level)
    self.mixer.setvolume(volume)

  # event handler for the HScale being dragged
  def on_slide(self, widget):
    level = widget.get_value()
    self.set_level(level)

  # event handler for scrolling while hovering the icon
  def on_scroll(self, widget, event):
    level = self.get_level()

    if event.direction == gtk.gdk.SCROLL_DOWN:
      self.set_level(level - (self.SCROLL_BY))
    elif event.direction == gtk.gdk.SCROLL_UP:
      self.set_level(level + (self.SCROLL_BY))

  def on_focus_out(self, widget, event):
    self.hide_window()

  def watch(self, fd, cond):
    self.mixer.handleevents()
    self.update()
    return True

  # updates the global mixer, moves slider and updates icon
  def update(self):
    level = self.get_level()
    muted = self.mixer.getmute()[0]

    self.slider.set_value(level)

    if level <= 0 or muted:
      self.icon.set_from_icon_name('audio-volume-muted')
    elif level <= 20:
      self.icon.set_from_icon_name('audio-volume-off')
    elif level <= 55:
      self.icon.set_from_icon_name('audio-volume-low')
    elif level <= 90:
      self.icon.set_from_icon_name('audio-volume-medium')
    else:
      self.icon.set_from_icon_name('audio-volume-high')

    tooltip_text = "Volume: {0}%".format(level)

    if muted:
      tooltip_text += ' (muted)'

    self.icon.set_tooltip_text(tooltip_text)

if __name__ == '__main__':
  try:
    args, _ = getopt.getopt(sys.argv[1:], 'rc:', ['reverse-scroll', 'card='])
  except getopt.GetoptError as err:
    print >> sys.stderr, err
    sys.exit(1)

  reverse = False
  card = 0

  for arg, val in args:
    if arg in ('-r', '--reverse-scroll'):
      reverse = True

    if arg in ('-c', '--card'):
      card = val

  volatile = Volatile(reverse, card)
