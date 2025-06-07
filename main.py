import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import vlc
import time
import os
from yt_dlp import YoutubeDL

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import re
import pyautogui
# Setup for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# ✅ Correct path to ffmpeg
FFMPEG_PATH = "C:/ffmpeg/bin"

VLC_PATH = "C:/Program Files/VideoLAN/VLC"
os.add_dll_directory(VLC_PATH)
vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

listenr = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)

def talk(text):
    engine.say(text)
    engine.runAndWait()



def set_volume_level(level):  # 0.0 to 1.0
    volume.SetMasterVolumeLevelScalar(level, None)

def increase_volume():
    current = volume.GetMasterVolumeLevelScalar()
    set_volume_level(min(current + 0.1, 1.0))
    talk("Volume increased")

def decrease_volume():
    current = volume.GetMasterVolumeLevelScalar()
    set_volume_level(max(current - 0.1, 0.0))
    talk("Volume decreased")

def mute_volume():
    try:
        volume.SetMute(1, None)
        print("🔇 Muted via API")
        talk("Volume muted")
    except:
        pyautogui.press('volumemute')
        talk("Muted using system key")

def unmute_volume():
    try:
        volume.SetMute(0, None)
        set_volume_level(0.3)  # set volume to 30%
        print("🔊 Unmuted via API")
        talk("Volume unmuted")
    except:
        pyautogui.press('volumeup')  # simulate system unmute
        talk("Unmuted using system key")

def take_commad():
    command = ""
    try:
        with sr.Microphone() as source:
            talk("Hey I am your alexa.Please speake your command")
            print("🎤 Listening...")
            voice = listenr.listen(source, timeout=5, phrase_time_limit=5)
            command = listenr.recognize_google(voice).lower()
            if "alexa" in command:
                command = command.replace('alexa', '').strip()
                print(command)
            print("🗣️ Heard:", command)
    except Exception as e:
        print("⚠️ Error recognizing speech:", e)
        pass
    return command
    

def search_and_download_audio(song_name):
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': False,  # Show logs for debugging
            'default_search': 'ytsearch1',
            'outtmpl': 'temp_song.%(ext)s',
            'ignoreerrors': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # Optionally add FFMPEG path if required
        if 'FFMPEG_PATH' in globals():
            ydl_opts['ffmpeg_location'] = FFMPEG_PATH

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=True)
            if 'entries' in info:
                info = info['entries'][0]  # for ytsearch1
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + '.mp3'
            file_path = os.path.abspath(filename)
            print(f"✅ Downloaded: {file_path}")
            return file_path, info.get('title')

    except Exception as e:
        print("❌ Download error:", e)
        return None, None
    
def get_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        print("🗣️ Heard:", command)
        return command
    except sr.UnknownValueError:
        print("Sorry, I didn't understand.")
        return ""
    except sr.RequestError:
        print("Speech service error.")
        return ""

def handle_command(command):
    if 'play' in command or 'start' in command:
        # media = vlc_instance.media_new("temp_song.mp3")
        # player.set_media(media)
        player.play()
        print("Playing music.")
        return False
    elif 'pause' in command or 'stop' in command:
        player.pause()
        print("Paused.")
        return False
    elif 'resume' in command:
        player.play()
        print("Resumed.")
        return False
    elif 'next' in command:
        player.next()
        print("Next song.")
        return False
    elif 'previous' in command or 'back' in command:
        player.previous()
        print("Previous song.")
        return False
    elif 'increase volume' in command:
        increase_volume()
        return False
    elif 'decrease volume' in command:
        decrease_volume()
        return False
    elif 'unmute' in command:
        unmute_volume()
        return False
    elif 'mute' in command:
        mute_volume()
        return False
    elif 'exit' in command:
        player.stop()
        talk("Exiting playback.")
        return True
    else:
        print("Command not recognized.")
        return False


def play_song(filepath, title):
    talk(f"Now playing {title}")
    media = vlc_instance.media_new(filepath)
    player.set_media(media)
    player.play()
    while True:
        command = get_command()
        action = handle_command(command)
        if action == True:
            break
        time.sleep(5)
    # input("🎵 Press Enter to stop the music...\n")
    # player.stop()

def run_alexa():
    command = take_commad()
    print(command)
    if 'start' in command:
         song = command.lower().replace('start', '').strip()
         talk('playing '+ song)
         print('playing '+ song)
         pywhatkit.playonyt(song)
    elif "time" in command:
         time = datetime.datetime.now().strftime('%I:%M %p')
         talk('Current time is' + time)
    elif "who is" in command:
         person = command.replace('who is','')
         try:
            info = wikipedia.summary(person, 1)
            print("🤖", info)
            talk(info)
         except wikipedia.exceptions.PageError:
            print(f"❌ No page found for '{person}' on Wikipedia.")
            talk(f"Sorry, I couldn't find anything about {person}. Try a different name.")
         except wikipedia.exceptions.DisambiguationError as e:
            print(f"⚠️ '{person}' is too ambiguous. Options: {e.options}")
         talk(f"{person} has many results. Please be more specific.")

    elif 'play' in command:
        song = command.lower().replace('start', '').strip()
        file_path, song_title = search_and_download_audio(song)
        if file_path and os.path.exists(file_path):
            play_song(file_path, song_title)
            os.remove(file_path)
        else:
            talk("Sorry, I couldn't find or play that song.")
    else:
         talk("I can not undertstand yout command .Please say the command again!")

while True:            
    run_alexa()
    