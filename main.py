import asyncio
import base64
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
import pygame
import speech_recognition as sr
import cv2
from concurrent.futures import ThreadPoolExecutor
from miio import DreameVacuum
import uuid

# Xiaomi Vacuum settings
bot = DreameVacuum('192.168.0.42', '364a424b66794465373655614b57616a')

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("API_KEY_OPENAI"))

# Initialize pygame mixer
pygame.mixer.init()

# Recognizer
recognizer = sr.Recognizer()

# Conversation history
conversation_history = []

executor = ThreadPoolExecutor(max_workers=4)

async def speak(text):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor, lambda: _sync_speak(text))

def _sync_speak(text):
    filename = f"output_{uuid.uuid4().hex}.mp3"
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    response.stream_to_file(filename)

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

async def listen():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, _sync_listen)

def _sync_listen():
    filename = f"speech_{uuid.uuid4().hex}.mp3"
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    with open(filename, 'wb') as file:
        file.write(audio.get_wav_data())
    with open(filename, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    print(f"🎙️ You said: {transcription.text}")
    return transcription.text.lower()

async def analyze_image(prompt):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, lambda: _sync_analyze_image(prompt))

def _sync_analyze_image(prompt):
    video = cv2.VideoCapture(0)
    base64Frames = []
    start_time = time.time()
    while video.isOpened() and (time.time() - start_time < 2):
        success, frame = video.read()
        if success:
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
    video.release()

    prompt_messages = [{
        "role": "user",
        "content": [prompt, *map(lambda x: {"image": x, "resize": 768}, base64Frames[::48])],
    }]

    result = client.chat.completions.create(model="gpt-4o", messages=prompt_messages)
    print(result.choices[0].message.content)
    return result.choices[0].message.content

async def handle_command(text):
    if "что ты видишь" in text or "describe the scene" in text:
        vision_response = await analyze_image(text)
        print(f"👀 {vision_response}")
        await speak(vision_response)
    else:
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": text}]
        ).choices[0].message.content
        print(f"🤖 {response}")
        await speak(response)

async def stop_speak():
    pygame.mixer.music.stop()

async def main():
    await speak("Ассистент готов к работе.")
    while True:
        user_input = await listen()
        if any(word in user_input for word in ["стоп", "stop"]):
            await stop_speak()
        if any(word in user_input for word in ["goodbye", "exit"]):
            await speak("Выключаюсь, пока!")
            break
        if "лапуля" in user_input or "lapula" in user_input:
            asyncio.create_task(handle_command(user_input))

asyncio.run(main())
