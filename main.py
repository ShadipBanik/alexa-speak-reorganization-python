import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import vlc
import time
import os
from yt_dlp import YoutubeDL

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


def take_commad():
        try:
            with sr.Microphone() as source:
                talk('Hey! I am your alexa.How can i help you? ')
                print("listening....")
                voice = listenr.listen(source)
                command = listenr.recognize_google(voice)
                if "alexa" in command.lower():
                    command = command.lower().replace('alexa', '').strip()
                    print(command)
                
        except:
            pass
        return command

def search_and_download_audio(song_name):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': False,  # 👈 Enable output to see errors
            'default_search': 'ytsearch1',
            'outtmpl': 'temp_song.%(ext)s',
            'ffmpeg_location': FFMPEG_PATH,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=True)
            filename = ydl.prepare_filename(info)
            # Replace extension with .mp3
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
        talk("Sorry, I didn't understand.")
        return ""
    except sr.RequestError:
        talk("Speech service error.")
        return ""

def handle_command(command):
    if 'play' in command or 'start' in command:
        player.play()
        talk("Playing music.")
    elif 'pause' in command or 'stop' in command:
        player.pause()
        talk("Paused.")
    elif 'resume' in command:
        player.play()
        talk("Resumed.")
    elif 'next' in command:
        player.next()
        talk("Next song.")
    elif 'previous' in command or 'back' in command:
        player.previous()
        talk("Previous song.")
    else:
        talk("Command not recognized.")


def play_song(filepath, title):
    talk(f"Now playing {title}")
    media = vlc_instance.media_new(filepath)
    player.set_media(media)
    player.play()
    input("🎵 Press Enter to stop the music...\n")
    player.stop()

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
    elif "who hack the person" in command:
         person = command.replace('who hack the person','')
         info = wikipedia.summary(person,1)
         print(info)
         talk(info)

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