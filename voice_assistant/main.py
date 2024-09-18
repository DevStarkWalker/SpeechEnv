from openai import OpenAI
import speech_recognition as sr
import openai
import pyttsx3
import os
import sys
from dotenv import load_dotenv
import time  # Import time module

# Initialize the speech engine globally
engine = pyttsx3.init()

# Load environment variables from .env file
load_dotenv()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

for voice in voices:
    print(f"ID: {voice.id}, Name: {voice.name}, Lang: {voice.languages}")

# Get API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
print(f"Loaded API Key: {os.getenv('OPENAI_API_KEY')}")  # Add this line
if not os.getenv('OPENAI_API_KEY'):
    print(f"No API Key found")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

assistant = client.beta.assistants.create(
    name="Jarvis",
    instructions="You are a personal assistant. Respond and act like Jarvis from Iron Man.",
    model="gpt-4o",
)

thread = client.beta.threads.create()

listening = False  # Flag to control listening state

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I did not quite understand that.")
    except sr.RequestError:
        print("Sorry, the speech service is unavailable.")
    return None

def get_openai_response(prompt):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        for message in messages.data:
            if message.role == "assistant":
                return message.content[0].text.value

def speak_text(text):
    time.sleep(0.2)  # Add a small delay before speaking
    engine.say("I will " + text)
    engine.runAndWait()

def main():
    global listening
    while True:
        if not listening:
            print("Waiting for 'Start Jarvis' command...")
            command = recognize_speech_from_mic()
            if command and "start jarvis" in command.lower():
                listening = True
                speak_text(" Hello sir, what can I do for you?")
                print("Listening for commands...")
            if command and "exit" in command.lower():
                speak_text(" Goodbye.")
                sys.exit() 
        else:
            command = recognize_speech_from_mic()
            if command:
                if "stop listening" in command.lower():
                    listening = False
                    speak_text(" Goodbye Sir.")
                    print("Stopped listening for commands.")
                else:
                    response = get_openai_response(command)
                    print(f"Assistant: {response}")
                    speak_text(response)

if __name__ == "__main__":
     
    time.sleep(1)
    main()
