from django.shortcuts import render, redirect
from django.http import JsonResponse
from gtts import gTTS
import os
from django.conf import settings
from datetime import datetime
import random
import requests
import pyttsx3
import speech_recognition as sr
import time
import json
from django.views.decorators.csrf import csrf_exempt
import smtplib
import wikipedia
import pyjokes
import urllib.parse
import subprocess




# Initialize text-to-speech engine
engine = pyttsx3.init()

# Your API key for OpenWeatherMap (replace with your actual key)
API_KEY = '67d618ba5070fb877ead132332a6475a'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather?'


def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def get_weather_forecast(city_name):
    """Fetch and return weather forecast for a given city."""
    # Clean the city_name string
    city_name = city_name.replace("weather", "").replace("forecast", "").replace("in", "").replace("current", "").strip()
    
    # Remove any trailing punctuation
    city_name = city_name.rstrip('.')
    
    # Ensure city_name is not empty
    if not city_name:
        return "Sorry, city name is missing."

    request_url = f"{BASE_URL}q={city_name}&appid={API_KEY}&units=metric"
    
    print(f"Request URL: {request_url}")  # Debugging: Log the request URL
    
    try:
        response = requests.get(request_url)
        response.raise_for_status()  # This will raise an error for HTTP error codes
        data = response.json()
        
        if 'main' not in data or 'weather' not in data:
            return "Sorry, I couldn't retrieve the weather data."
        
        city = data.get('name', city_name)
        country = data['sys'].get('country', '')
        temp = data['main']['temp']
        weather_description = data['weather'][0]['description']
        weather_info = f"Current weather in {city}, {country}: Temperature: {temp}°C, Condition: {weather_description}."
        return weather_info
        
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"

def listen_for_command():
    """Listen for a voice command and return the text."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio)
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Sorry, there was an issue with the speech recognition service.")
        return None

def index(request):
    greeting_message = "Hey User, I am Laika. I am here to assist you. Do you want to explore? Say 'next'."
    
    # Convert the text to speech using gTTS
    tts = gTTS(text=greeting_message, lang='en')
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'speech.mp3')
    tts.save(audio_file_path)
    
    return render(request, 'laikaai/index.html', {
        'audio_url': settings.MEDIA_URL + 'speech.mp3'
    })

def explore(request):
    return render(request, 'laikaai/explore.html')

def object_detection_view(request):
    return render(request, 'laikaai/object.html')

def email_view(request):
    return render(request, 'laikaai/email.html')

def navigation_view(request):
    return render(request, 'laikaai/navigation.html')

def chat_view(request):
    return render(request, 'laikaai/chat.html')




def weather_view(request):
    if request.method == 'POST':
        # Load JSON data from the request body
        try:
            data = json.loads(request.body)
            command = data.get('command')
        except json.JSONDecodeError:
            print("Error decoding JSON.")  # Debugging: Log JSON decoding error
            return JsonResponse({'weather_info': "Invalid JSON data."})
        
        print(f"Received command: {command}")  # Debugging: Log the command

        if command:
            city_name = command.replace("weather", "").strip()
            print(f"City Name: {city_name}")  # Debugging: Log the cleaned city name
            
            weather_info = get_weather_forecast(city_name)
            print(f"Weather Info: {weather_info}")  # Debugging: Log the weather info
            
            # You can use speak here if needed, but it's already handled in JavaScript
            return JsonResponse({'weather_info': weather_info})
        else:
            print("No command received or command empty.")  # Debugging: Log empty command
            return JsonResponse({'weather_info': "No command received."})
    
    return render(request, 'laikaai/weather.html')





def get_current_time_view(request):
    """Return the current time in a JSON response."""
    current_time = datetime.now().strftime("%I:%M %p")
    return JsonResponse({'time': f"{current_time}"})




@csrf_exempt
def process_command(request):
    """Process commands for various actions including telling a joke."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get('command', '').lower()
        except json.JSONDecodeError:
            return JsonResponse({'response': "Invalid JSON data."})
        
        if 'current time' in command:
            return JsonResponse({'response': get_current_time_view(request).content.decode()})
        elif 'object detection' in command:
            return redirect('/object/')
        elif 'weather' in command:
            city_name = command.replace("weather", "").strip()
            weather_info = get_weather_forecast(city_name)
            return JsonResponse({'response': weather_info})
        elif 'email' in command or 'email assistant' in command or 'mail' in command:
            return redirect('/email/')
        # elif 'play' in command:
        #     song_name = command.replace('play', '').strip()
        #     if song_name:
        #         # URL encode the song name
        #         youtube_search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_name)}"
        #         return JsonResponse({'response': youtube_search_url})
        
        elif 'who is' in command or 'about' in command:
            person_name = command.replace('who is', '').replace('about', '').strip()
            person_info = get_person_info(person_name)
            return JsonResponse({'response': person_info})

        elif 'go back' in command:
            return redirect('/explore/')
        
        

    return JsonResponse({'response': "Invalid request method."})

    


def tell_joke():
    """Fetch and return a joke using pyjokes."""
    return pyjokes.get_joke()

def get_joke(request):
    """Return a joke as JSON."""
    joke = tell_joke()
    return JsonResponse({'joke': joke})

def get_person_info(person_name):
    """Fetch and return a summary of a person from Wikipedia."""
    try:
        summary = wikipedia.summary(person_name, sentences=2)  # Fetch a brief summary
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation error. Possible options: {', '.join(e.options)}"
    except wikipedia.exceptions.PageError:
        return "Page not found."
    except Exception as e:
        return f"An error occurred: {e}"
  
  

    
@csrf_exempt
def place_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        command = data.get('command', '')
        if 'navigate to' in command:
            place_name = command.replace('navigate to', '').strip()
            try:
                summary = wikipedia.summary(place_name, sentences=1)
                url = f'https://www.google.com/maps/dir/?api=1&destination={place_name.replace(" ", "+")}'
                return JsonResponse({'info': summary, 'url': url})
            except wikipedia.exceptions.PageError:
                return JsonResponse({'info': f'I couldn\'t find information about {place_name} on Wikipedia.'})
            except wikipedia.exceptions.DisambiguationError as e:
                return JsonResponse({'info': f'There are multiple results for {place_name}. Please be more specific.'})
    return JsonResponse({'info': 'Invalid command.'})


def recognize_speech_from_mic(retry_count=3, timeout=15, phrase_time_limit=15):
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.energy_threshold = 300
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        for attempt in range(retry_count):
            print(f"Listening... (attempt {attempt + 1})")
            try:
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = r.recognize_google(audio).lower().strip()
                return text
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that. Please try again.")
            except sr.RequestError as e:
                speak("Speech recognition service is unavailable.")
                return ""
    return ""

@csrf_exempt
def compose_email(request):
    if request.method == 'POST':
        try:
            process = subprocess.Popen(
                ["python", r"C:\Users\swath\OneDrive\Desktop\InteliBiz-main\AI LKA\laika_ai\laika\laikaai\voice_based_email_for_blind.py", "compose"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                return JsonResponse({"status": "success", "output": stdout.decode()}, status=200)
            else:
                return JsonResponse({"status": "failure", "error": stderr.decode()}, status=500)
        except Exception as e:
            return JsonResponse({"status": "failure", "error": str(e)}, status=500)
    return JsonResponse({"status": "failure"}, status=400)

@csrf_exempt
def read_email(request):
    if request.method == 'POST':
        try:
            process = subprocess.Popen(
                ["python", r"C:\Users\Adithya\Desktop\Vision__Speak\laika_ai\laika\laikaai\voice_based_email_for_blind.py", "read"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                return JsonResponse({"status": "success", "output": stdout.decode()}, status=200)
            else:
                return JsonResponse({"status": "failure", "error": stderr.decode()}, status=500)
        except Exception as e:
            return JsonResponse({"status": "failure", "error": str(e)}, status=500)
    return JsonResponse({"status": "failure"}, status=400)

@csrf_exempt
def delete_email(request):
    if request.method == 'POST':
        try:
            process = subprocess.Popen(
                ["python", r"C:\Users\Adithya\Desktop\Vision__Speak\laika_ai\laika\laikaai\voice_based_email_for_blind.py", "delete"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                return JsonResponse({"status": "success", "output": stdout.decode()}, status=200)
            else:
                return JsonResponse({"status": "failure", "error": stderr.decode()}, status=500)
        except Exception as e:
            return JsonResponse({"status": "failure", "error": str(e)}, status=500)
    return JsonResponse({"status": "failure"}, status=400)