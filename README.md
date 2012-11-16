volatile
========
volatile is a status icon which controls audio volume via ALSA.


Usage
-----
Clicking the icon brings up a volume slider. Context-clicking the icon toggles
mute.

Scrolling while hovering the icon (whether the slider is visible or not) also
adjusts the volume.

The ALSA mixer is polled in order to relect changes made externally.


Requirements
------------
volatile requires `pyalsaaudio`:
http://pyalsaaudio.sourceforge.net/
