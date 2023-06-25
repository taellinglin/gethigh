import sounddevice as sd
import numpy as np
import time
import sys

# Define the brainwave frequencies and their corresponding ranges
brainwave_frequencies = {
    'Delta': 1,
    'Theta': 4,
    'Alpha': 8,
    'Beta': 12,
    'Gamma': 30
}

# Define the duration (in seconds) for each brainwave frequency
duration_per_frequency = 30

# Define the fade-in and fade-out durations (in seconds)
fade_duration = 1.0

# Define the total duration (in seconds) for the program to run
total_duration = 180

# Define the sample rate and duration for each tone
sample_rate = 192000

# Define the transpose factor to adjust the frequencies
transpose_factor = 100

# Define the modulation frequency and depth
modulation_frequency = 0.1
modulation_depth = 2

# ANSI escape sequences for colored output
COLOR_GREEN = '\033[92m'
COLOR_CYAN = '\033[96m'
COLOR_YELLOW = '\033[93m'
COLOR_MAGENTA = '\033[95m'
COLOR_BLUE = '\033[94m'
COLOR_RESET = '\033[0m'

# Define the rainbow colors
RAINBOW_COLORS = [COLOR_GREEN, COLOR_CYAN, COLOR_YELLOW, COLOR_MAGENTA, COLOR_BLUE]

def generate_binaural_beat(frequency, next_frequency, duration):
    # Calculate the number of samples needed
    num_samples = int(duration * sample_rate)

    # Generate the time array
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # Calculate the modulation factor
    modulation_factor = np.sin(2 * np.pi * modulation_frequency * t) * modulation_depth

    # Calculate the left and right channel frequencies with modulation
    left_frequency = ((frequency - 1) * transpose_factor) + modulation_factor
    right_frequency = ((frequency + 1) * transpose_factor) + modulation_factor

    # Calculate the next left and right channel frequencies with modulation
    next_left_frequency = ((next_frequency - 1) * transpose_factor) + modulation_factor
    next_right_frequency = ((next_frequency + 1) * transpose_factor) + modulation_factor

    # Generate the left and right channel signals
    left_channel = np.sin(2 * np.pi * left_frequency * t, dtype='float32')
    right_channel = np.sin(2 * np.pi * right_frequency * t, dtype='float32')

    # Generate the next left and right channel signals
    next_left_channel = np.sin(2 * np.pi * next_left_frequency * t, dtype='float32')
    next_right_channel = np.sin(2 * np.pi * next_right_frequency * t, dtype='float32')

    # Apply fade-in and fade-out to the signals
    fade_samples = int(fade_duration * sample_rate)
    fade = np.linspace(0, 1, fade_samples, dtype='float32')

    left_channel[:fade_samples] *= fade
    left_channel[-fade_samples:] *= fade[::-1]

    right_channel[:fade_samples] *= fade
    right_channel[-fade_samples:] *= fade[::-1]

    next_left_channel[:fade_samples] *= fade[::-1]
    next_left_channel[-fade_samples:] *= fade

    next_right_channel[:fade_samples] *= fade[::-1]
    next_right_channel[-fade_samples:] *= fade

    # Crossfade between the current and next frequencies
    crossfade = np.linspace(1, 0, fade_samples, dtype='float32')

    left_channel[-fade_samples:] = (left_channel[-fade_samples:] * crossfade) + (next_left_channel[:fade_samples] * (1 - crossfade))
    right_channel[-fade_samples:] = (right_channel[-fade_samples:] * crossfade) + (next_right_channel[:fade_samples] * (1 - crossfade))

    # Combine the channels
    stereo_signal = np.column_stack((left_channel, right_channel))

    # Play the binaural beat
    stream = sd.OutputStream(samplerate=sample_rate, channels=2, dtype='float32')
    stream.start()
    stream.write(stereo_signal)
    stream.stop()
    stream.close()

def print_colored_text(text, color):
    sys.stdout.write(color + text + COLOR_RESET)
    sys.stdout.flush()

# Main program loop
start_time = time.time()
current_frequency = None
while time.time() - start_time < total_duration:
    frequencies = list(brainwave_frequencies.values())
    for i in range(len(frequencies)):
        frequency = frequencies[i]
        next_frequency = frequencies[(i + 1) % len(frequencies)]
        if current_frequency is None:
            print_colored_text(f"Stimulating {frequency} brainwaves...", RAINBOW_COLORS[i % len(RAINBOW_COLORS)])
            current_frequency = frequency
        else:
            print_colored_text(f"Transitioning from {current_frequency} to {next_frequency} brainwaves...", RAINBOW_COLORS[i % len(RAINBOW_COLORS)])
            generate_binaural_beat(current_frequency, next_frequency, duration_per_frequency - fade_duration)
            current_frequency = next_frequency

print("Program completed.")
