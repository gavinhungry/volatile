volatile
========
volatile is a status icon which controls audio volume via ALSA.

Usage
-----
Clicking the icon brings up a volume slider. Context-clicking the icon toggles
mute.

Scrolling while hovering the icon (whether the slider is visible or not) also
adjusts the volume.

### Arguments

`-c/--card`: sound card ID to use

`-r/--reverse-scroll`: scroll volume in reverse ("natural scrolling")

Requirements
------------
volatile requires `pyalsaaudio`:
http://pyalsaaudio.sourceforge.net/

License
-------
This software is released under the terms of the **MIT license**. See `LICENSE`.
