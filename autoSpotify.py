#!/usr/bin/env python

# pip install dbus-python pulsectl

import signal
import sys
import pulsectl
import dbus

def sig_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)

session_bus = dbus.SessionBus()
spotify = session_bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
player_iface = dbus.Interface(spotify, 'org.mpris.MediaPlayer2.Player')
props_iface = dbus.Interface(spotify, 'org.freedesktop.DBus.Properties')

with pulsectl.Pulse('my-client') as pulse:
    spotify_sink_input = next(filter(lambda si: 'Spotify' in si.name, pulse.sink_input_list()))
    spotify_status = props_iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')

    def event_handler(ev):
        event_handler.ev = ev
        event_handler.index = ev.index
        event_handler.t = ev.t
        raise pulsectl.PulseLoopStop

    pulse.event_mask_set('sink_input')
    pulse.event_callback_set(event_handler)

    while True:
        pulse.event_listen(timeout = 0)

        #print(event_handler.ev)

        if spotify_sink_input.index == event_handler.index:
            continue
        if event_handler.t == 'new':
            player_iface.Pause()

        sink_inputs = pulse.sink_input_list()
        uncorked = filter(lambda si: not 'Spotify' in si.name and not si.corked, sink_inputs)

        uncorkedAmount = int(len(list(uncorked)))
        if uncorkedAmount > 0:
            spotify_status = props_iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
            player_iface.Pause()
        elif spotify_status == 'Playing':
            player_iface.Play()
