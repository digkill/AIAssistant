import base64
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
import pygame
import speech_recognition as sr
import cv2

load_dotenv()

api_key_openai = os.getenv("API_KEY_OPENAI")
client = OpenAI(api_key=api_key_openai)

# 🔹 Initialization voice engine
pygame.mixer.init()

# 🔹 Initialization recognizer voice
recognizer = sr.Recognizer()

# 🔹 Voice acting function
def speak(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )

    response.stream_to_file("output.mp3")
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()


def listen():
    with sr.Microphone() as source:
        print("🎤 Слушаю...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        with open('speech.wav', 'wb') as file:
            wav_data = audio.get_wav_data()
            file.write(wav_data)
            file.close()
    try:
        audio_file = open("./speech.wav", "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file= audio_file
        )


        print(f"🎙️ You said: {transcription.text}")
        audio_file.close()
        return transcription.text.lower()
    except sr.UnknownValueError:
        return "Ошибка распознавания."
    except sr.RequestError:
        return "Ошибка сервера."


def analyze_image(user_input_message):
    video = cv2.VideoCapture(0)
    record_time = 2
    start_time = time.time()

    message =  "Это кадры из видео, опиши что изображено на видео. " + user_input_message

    if not video.isOpened():
        print("[Error] Opening camera failed.!")
        exit()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break

        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        out.write(frame)

        cv2.imshow('frame', frame)

        if time.time() - start_time > record_time:
            print("Record finished.")
            break

    video.release()
    print(len(base64Frames), "frames read.")
    cv2.destroyAllWindows()
    out.release()

    prompt_messages = [
        {
            "role": "user",
            "content": [
                message,
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[2::48]),
            ],
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": prompt_messages,
        "max_tokens": 200,
    }

    result = client.chat.completions.create(**params)
    print(result.choices[0].message.content)

    return result.choices[0].message.content

while True:
    user_input = listen()

    if "goodbye" in user_input or "stop" in user_input or "exit" in user_input:
        speak("Switch off, goodbye!")
        break

    elif "что ты видишь" in user_input or "describe the scene" in user_input:
        vision_response = analyze_image(user_input)
        print(f"👀 {vision_response}")
        speak(vision_response)

    elif "лапуля" in user_input:
        response = client.chat.completions.create(model="gpt-4o",
        messages=[{"role": "user", "content": user_input}])
        bot_reply = response.choices[0].message.content
        print(f"🤖 ChatGPT: {bot_reply}")
        speak(bot_reply)
