volatile
========
volatile is a GTK status icon which controls audio volume via ALSA and
PulseAudio.

Usage
-----
Clicking the icon brings up a volume slider. Scrolling while hovering the icon
(whether the slider is visible or not) also adjusts the volume.

Right-clicking the icon opens a context menu to toggle mute and select the
default PulseAudio sink.

### Arguments

`-r/--reverse-scroll`: scroll volume in reverse ("natural scrolling")

`-m/--max-volume`: maximum volume level (0-100, default 100)

`-v/--volatile-icons`: use volatile-prefixed icon names

### Sink name mapping

Sink descriptions can be mapped to custom names by creating a
`~/.volatile.json` file:

```json
{
  "Built-in Audio Analog Stereo": "Speakers",
  "USB Headset": "Headphones"
}
```

Requirements
------------
- [PyAlsaAudio](https://larsimmisch.github.io/pyalsaaudio/)
- [pulsectl](https://pypi.org/project/pulsectl)
- GTK 3 (via PyGObject)

License
-------
This software is released under the terms of the **MIT license**. See `LICENSE`.
