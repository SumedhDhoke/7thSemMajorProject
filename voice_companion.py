import speech_recognition as sr
import datetime
import subprocess
import os
import time

# ============================================================
# Text-to-Speech Configuration
# ============================================================

SPEAKER_DEVICE = "plughw:2,0"

def speak(text):
    print("Companion:", text)

    try:
        # Generate speech using eSpeak-NG
        subprocess.run(
            [
                "espeak-ng",
                "-w",
                "/tmp/companion.wav",
                "-s",
                "155",
                text
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Play generated speech through Raspberry Pi 3.5mm output
        subprocess.run(
            [
                "aplay",
                "-D",
                SPEAKER_DEVICE,
                "/tmp/companion.wav"
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except FileNotFoundError:
        print("ERROR: espeak-ng or aplay is not installed.")

    except subprocess.CalledProcessError:
        print("ERROR: Unable to play audio through speaker.")


# ============================================================
# Speech Recognition
# ============================================================

recognizer = sr.Recognizer()

# Microphone sensitivity
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8


def listen():

    with sr.Microphone() as source:

        print("\nListening...")

        # Adjust for background noise
        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        try:

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

            print("Processing...")

            # Google Speech Recognition
            text = recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            print("You:", text)

            return text.lower()

        except sr.WaitTimeoutError:

            print("No speech detected.")
            return ""

        except sr.UnknownValueError:

            print("Sorry, I couldn't understand that.")

            speak(
                "Sorry, I couldn't understand that."
            )

            return ""

        except sr.RequestError:

            print(
                "Speech recognition service unavailable."
            )

            speak(
                "I am unable to connect to the speech recognition service."
            )

            return ""


# ============================================================
# Command Processing
# ============================================================

def process_command(command):

    if not command:
        return True

    # --------------------------------------------------------
    # Greeting
    # --------------------------------------------------------

    if "hello" in command or "hi" in command:

        speak(
            "Hello! How can I help you?"
        )

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    elif "who are you" in command:

        speak(
            "I am your desktop companion. "
            "I can listen to your voice and respond "
            "to your commands."
        )

    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------

    elif "time" in command:

        current_time = datetime.datetime.now().strftime(
            "%I:%M %p"
        )

        speak(
            f"The current time is {current_time}"
        )

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    elif "date" in command:

        current_date = datetime.datetime.now().strftime(
            "%d %B %Y"
        )

        speak(
            f"Today is {current_date}"
        )

    # --------------------------------------------------------
    # Open Browser
    # --------------------------------------------------------

    elif (
        "open browser" in command
        or "open chrome" in command
    ):

        speak(
            "Opening the browser."
        )

        try:

            subprocess.Popen(
                ["chromium"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except FileNotFoundError:

            speak(
                "I could not find the Chromium browser."
            )

    # --------------------------------------------------------
    # Open Terminal
    # --------------------------------------------------------

    elif "open terminal" in command:

        speak(
            "Opening the terminal."
        )

        try:

            subprocess.Popen(
                ["lxterminal"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except FileNotFoundError:

            speak(
                "I could not open the terminal."
            )

    # --------------------------------------------------------
    # System Information
    # --------------------------------------------------------

    elif "system information" in command:

        speak(
            "I will show you the system information."
        )

        subprocess.Popen(
            [
                "lxterminal",
                "-e",
                "bash",
                "-c",
                "uname -a; echo; hostnamectl; read"
            ]
        )

    # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------

    elif "shutdown" in command:

        speak(
            "Shutdown command received. Goodbye."
        )

        os.system(
            "sudo shutdown now"
        )

        return False

    # --------------------------------------------------------
    # Exit Companion
    # --------------------------------------------------------

    elif (
        "exit" in command
        or "quit" in command
        or "goodbye" in command
    ):

        speak(
            "Goodbye! See you later."
        )

        return False

    # --------------------------------------------------------
    # Unknown Command
    # --------------------------------------------------------

    else:

        speak(
            "I heard you, but I don't have "
            "a command for that yet."
        )

    return True


# ============================================================
# Main Program
# ============================================================

def main():

    print("=" * 50)
    print("        VOICE DESKTOP COMPANION")
    print("=" * 50)

    speak(
        "Hello. I am ready. You can talk to me."
    )

    running = True

    while running:

        command = listen()

        if command:

            running = process_command(
                command
            )

        time.sleep(0.5)


# ============================================================
# Program Entry Point
# ============================================================

if __name__ == "__main__":

    main()
