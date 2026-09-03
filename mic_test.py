import pyaudio
import wave
import sys

# Audio processing constants
FORMAT = pyaudio.paInt32      # INMP441 outputs 24-bit audio inside a 32-bit slot
CHANNELS = 2                 # ALSA I2S voice overlays default to stereo allocation
RATE = 44100                 # Standard sample rate (Hz)
CHUNK = 1024                 # Audio data buffer frame size
RECORD_SECONDS = 5           # Duration of the capture test
OUTPUT_FILENAME = "mic_test_recording.wav"

p = pyaudio.PyAudio()

# Step 1: Scan for the correct hardware input index matching the I2S microphone
input_device_index = None
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

print("--- Scanning for Audio Input Devices ---")
for i in range(0, numdevices):
    device_info = p.get_device_info_by_host_api_device_index(0, i)
    if device_info.get('maxInputChannels') > 0:
        print(f"Index {i}: {device_info.get('name')}")
        # Match against common ALSA I2S sound card overlay driver keywords
        if "snd_rpi" in device_info.get('name').lower() or "voicehat" in device_info.get('name').lower() or "default" in device_info.get('name').lower():
            input_device_index = i

# Fallback: if no keyword matches but input devices exist, use the first available input
if input_device_index == None and numdevices > 0:
    for i in range(0, numdevices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            input_device_index = i
            break

if input_device_index is None:
    print("\n[ERROR] No working input device found. Ensure you executed 'sudo reboot' after updating config.txt.")
    p.terminate()
    sys.exit(1)

print(f"\nTargeting Input Device Index: {input_device_index}")

# Step 2: Open the stream explicitly targeting the input index while leaving output settings blank
try:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=input_device_index, # Critical parameter bypasses default check
                    frames_per_buffer=CHUNK)
except Exception as e:
    print(f"\n[ERROR] Failed to initialize stream: {e}")
    p.terminate()
    sys.exit(1)

print("* Recording audio sample...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    except IOError as e:
        print(f"Warning: dropped frame buffer: {e}")

print("* Finished recording test.")

# Clean up audio capture interfaces
stream.stop_stream()
stream.close()
p.terminate()

# Step 3: Write out buffer to disk file
wf = wave.open(OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"Success! Data written directly to: {OUTPUT_FILENAME}")
