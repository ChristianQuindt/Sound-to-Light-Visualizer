import time
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import config
import microphone
import dsp
import led

p = np.tile(1.0, (3, config.N_PIXELS // 2))
gain = dsp.ExpFilter(np.tile(0.01, config.N_FFT_BINS),
                     alpha_decay=0.001, alpha_rise=0.99)
exp_filter = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                         alpha_decay=0.01, alpha_rise=0.99)
mel_smoothing = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                         alpha_decay=0.5, alpha_rise=0.99)
# Hamming Window to remove maxima on the intervall ends of a fft
fft_window = np.hamming(int(config.MIC_RATE / config.FPS) * config.N_ROLLING_HISTORY)
# Number of audio samples to read every time frame
samples_per_frame = int(config.MIC_RATE / config.FPS)
# Array containing the rolling audio sample window
samples_roll = np.random.rand(config.N_ROLLING_HISTORY, samples_per_frame) / 1e16

def visualize_scroll(y):
    """Effect that originates in the center and scrolls outwards"""
    global p
    y = y**2.0
    gain.update(y)
    y /= gain.value
    y *= 255.0
    r = int(np.max(y[:len(y) // 3]))
    g = int(np.max(y[len(y) // 3: 2 * len(y) // 3]))
    b = int(np.max(y[2 * len(y) // 3:]))
    # Scrolling effect window
    p[:, 1:] = p[:, :-1]
    p *= 0.98
    p = gaussian_filter1d(p, sigma=0.2)
    # Create new color originating at the center
    p[0, 0] = r
    p[1, 0] = g
    p[2, 0] = b
    # Update the LED strip
    return np.concatenate((p[:, ::-1], p), axis=1)

def microphone_update(audio_samples):
    global samples_roll
    # Normalize samples between 0 and 1
    normalised_samples = audio_samples / 2.0**15
    # Construct a rolling window of audio samples
    samples_roll[:-1] = samples_roll[1:]
    samples_roll[-1, :] = np.copy(normalised_samples)
    sample_data = np.concatenate(samples_roll, axis=0).astype(np.float32)
    
    # Normalise Brightness from Amplitude
    vol = np.max(np.abs(sample_data))
    # Cancel noise when no sound is played
    if vol < 0.0001:
        vol = 0
        print('No audio input. Volume below threshold. Volume:', vol)
        led.pixels = np.tile(0, (3, config.N_PIXELS))
        led.update()
    else:
        # Transform audio input into the frequency domain
        N = len(sample_data)
        N_zeros = 2**int(np.ceil(np.log2(N))) - N # 2^11 - 1470
        # Pad with zeros until the next power of two
        sample_data *= fft_window
        sample_padded = np.pad(sample_data, (0, N_zeros), mode='constant')
        YS = np.abs(np.fft.rfft(sample_padded)[:N // 2])
        # Construct a Mel filterbank from the FFT data
        mel = np.atleast_2d(YS).T * dsp.mel_y.T
        # Scale data to values more suitable for visualization
        mel = np.sum(mel, axis=0)
        mel = mel**2.0
        # Gain normalization
        exp_filter.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
        mel /= exp_filter.value
        mel = mel_smoothing.update(mel)
        # Map filterbank output onto LED strip
        output = visualize_scroll(mel) 
        led.pixels = output
        led.update()
        
if __name__ == '__main__':
    # Initialise LED's
    led.update()
    # Start listening to live audio stream
    microphone.start_stream(microphone_update)