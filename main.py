import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia

listenr = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def talk(text):
    engine.say(text)
    engine.runAndWait()

def take_commad():
        try:
            with sr.Microphone() as source:
                talk('Hey! I am your alexa.How can i help you? ')
                print("listening....")
                voice = listenr.listen(source,timeout=8)
                command = listenr.recognize_google(voice)
                if "alexa" in command.lower():
                    command = command.lower().replace('alexa', '').strip()
                    print(command)
                
        except:
            pass
        return command


def run_alexa():
    command = take_commad()
    print(command)
    if 'play' in command:
         song = command.lower().replace('play', '').strip()
         talk('playing '+ song)
         print('playing '+ song)
         pywhatkit.playonyt(song)
    elif "time" in command:
         time = datetime.datetime.now().strftime('%I:%M %p')
         talk('Current time is' + time)
    elif "who hack the person":
         person = command.replace('who hack the person','')
         info = wikipedia.summary(person,1)
         print(info)
         talk(info)
              
run_alexa()