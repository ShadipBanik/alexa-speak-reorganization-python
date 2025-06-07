import os
import json
import pyttsx3
import requests
from vosk import Model, KaldiRecognizer
import pyaudio

# Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    print("🤖 GPT:", text)
    engine.say(text)
    engine.runAndWait()

# Load Vosk model
model_path = "model"
if not os.path.exists(model_path):
    raise FileNotFoundError("Vosk model not found!")

model = Model(model_path)
rec = KaldiRecognizer(model, 16000)

# Audio Input Stream
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

# Get response from OpenRouter using DeepSeek
def ask_gpt(question):
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",  # You can try "meta-llama/llama-3-8b-instruct" too
        "messages": [
            {"role": "system", "content": "You are a helpful voice assistant."},
            {"role": "user", "content": question}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        reply = response.json()['choices'][0]['message']['content']
        return reply
    else:
        print("⚠️ API Error:", response.text)
        return "Sorry, I couldn't get a response."

# Main Loop
print("🛑 Say something...")
while True:
    data = stream.read(4000, exception_on_overflow=False)
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        command = result.get("text", "")
        if command:
            print("🗣️ You said:", command)
            if "stop" in command.lower():
                speak("Goodbye!")
                break
            response = ask_gpt(command)
            speak(response)
