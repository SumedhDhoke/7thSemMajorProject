# INMP441 Microphone Recording Test Script
# Prerequisite: Install PyAudio first using 'pip install pyaudio'
# Note: Ensure you have configured /boot/firmware/config.txt with:
# dtoverlay=googlevoicehat-soundcard

import os
import wave
import sys
import time

try:
    import pyaudio
except ImportError:
    print("Error: PyAudio module is not installed.")
    print("Please install it by running: pip install pyaudio")
    print("If you encounter installation errors, run: sudo apt-get install python3-pyaudio")
    sys.exit(1)

# Audio Recording Configuration Parameters
FORMAT = pyaudio.paInt32      # INMP441 outputs 24-bit audio inside a 32-bit slot
CHANNELS = 2                 # Stereo mode (required by the Raspberry Pi I2S driver overlay)
RATE = 44100                 # Sampling rate in Hz (44.1 kHz)
CHUNK = 1024                 # Size of each data buffer block
RECORD_SECONDS = 5           # Length of time to record
OUTPUT_FILENAME = "mic_test_recording.wav"

def test_microphone():
    audio = pyaudio.PyAudio()
    
    # Inform user about available input devices
    print("\n=== Scanning Audio Input Devices ===")
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    input_device_index = None
    for i in range(0, numdevices):
        device_info = audio.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            print(f"Device ID {i}: {device_info.get('name')}")
            # Automatically try to pick up the I2S/Google Voice HAT driver
            if "snd_rpi" in device_info.get('name').lower() or "voicehat" in device_info.get('name').lower():
                input_device_index = i

    print("\n=== Initializing Audio Stream ===")
    try:
        if input_device_index is not None:
            print(f"Using auto-detected I2S Device ID: {input_device_index}")
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                input_device_index=input_device_index,
                                frames_per_buffer=CHUNK)
        else:
            print("Using system default audio input device...")
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"Initialization Failed: {e}")
        print("Verify your hardware connections and that your I2S overlay is enabled.")
        audio.terminate()
        return

    print(f"\n* Recording audio for {RECORD_SECONDS} seconds... Speak into the mic now!")
    frames = []

    # Read data streams from the micro-architecture interface buffer
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except IOError as e:
            # Prevent minor buffer overflow gaps from crashing the script execution
            if e.errno == pyaudio.paInputOverflowed:
                continue
            else:
                raise e

    print("* Finished recording phase.")

    # Safely disconnect hardware register streams
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Pack raw byte frames straight into standard WAV container syntax
    print(f"* Saving audio stream frames to container: {OUTPUT_FILENAME}")
    wave_file = wave.open(OUTPUT_FILENAME, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()
    
    print(f"=== Success! Test file successfully saved to: {os.path.abspath(OUTPUT_FILENAME)} ===")

if __name__ == "__main__":
    test_microphone()
