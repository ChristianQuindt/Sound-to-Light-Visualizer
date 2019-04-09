"""Settings for audio reactive LED strip"""
import os

UDP_IP = '192.168.0.150'
"""IP address of the ESP8266. Must match IP in ws2812_controller.ino"""
UDP_PORT = 7777
"""Port number used for socket communication between Python and ESP8266"""
USE_GUI = True
"""Whether or not to display a PyQtGraph GUI plot of visualization"""

DISPLAY_FPS = True
"""Whether to display the FPS when running (can reduce performance)"""

N_PIXELS = 256
"""Number of pixels in the LED strip (must match ESP8266 firmware)"""

MIC_RATE = 44100
"""Sampling frequency of the microphone in Hz"""

FPS = 60
"""Desired refresh rate of the visualization (frames per second)

FPS indicates the desired refresh rate, or frames-per-second, of the audio
visualization. The actual refresh rate may be lower if the computer cannot keep
up with desired FPS value.
"""
_max_led_FPS = int(((N_PIXELS * 30e-6) + 50e-6)**-1.0)
assert FPS <= _max_led_FPS, 'FPS must be <= {}'.format(_max_led_FPS)

MIN_FREQUENCY = 200
"""Frequencies below this value will be removed during audio processing"""

MAX_FREQUENCY = 12000
"""Frequencies above this value will be removed during audio processing"""

N_FFT_BINS = 24
"""Number of frequency bins to use when transforming audio to frequency domain

Fast Fourier transforms are used to transform time-domain audio data to the
frequency domain. The frequencies present in the audio signal are assigned
to their respective frequency bins. This value indicates the number of
frequency bins to use.

A small number of bins reduces the frequency resolution of the visualization
but improves amplitude resolution. The opposite is true when using a large
number of bins. More bins is not always better!

There is no point using more bins than there are pixels on the LED strip.
"""

N_ROLLING_HISTORY = 2
"""Number of past audio frames to include in the rolling window"""

MIN_VOLUME_THRESHOLD = 1e-7
"""No music visualization displayed if recorded audio volume below threshold"""
