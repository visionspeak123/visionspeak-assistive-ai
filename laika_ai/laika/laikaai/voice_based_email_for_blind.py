import re
import speech_recognition as sr
import smtplib
import email
import imaplib
import pyttsx3
import os
import time
from fuzzywuzzy import process

predefined_emails = [
    {"name": "adithya lekshmi", "email": "adithyalekshmi98@gmail.com"},
    {"name": "ammalu", "email": "ammalu0202@gmail.com"},
    {"name": "anakha suresh", "email": "anakhasuresh888@gmail.com"},
    {"name": "anu lekshmi", "email": "anulekshmi2701@gmail.com"},
    {"name": "aparna appu", "email": "aparnaappuappu09@gmail.com"},
    {"name": "athira sb", "email": "athirasb735@gmail.com"},
    {"name": "devika", "email": "devika3388devu@gmail.com"},
    {"name": "devuvi", "email": "devuvi3388@gmail.com"},
    {"name": "dhanya meenakshi", "email": "dhanyameenakshi979@gmail.com"},
    {"name": "ganga ghosh", "email": "gangaghosh423@gmail.com"},
    {"name": "kajal kichu", "email": "kajalkichu@gmail.com"},
    {"name": "lisy jayakumar", "email": "lisyjayakumar@gmail.com"},
    {"name": "mahima", "email": "mahimamahi8518@gmail.com"},
    {"name": "nandana ss", "email": "ssnandana200@gmail.com"},
    {"name": "rahitha nair", "email": "rahithatnair@gmail.com"},
    {"name": "remya ks", "email": "ksremya718@gmail.com"},
    {"name": "sarjitha vipin", "email": "sarjithavipin1998@gmail.com"},
    {"name": "soorya", "email": "sooryaa013@gmail.com"},
    {"name": "sooryasearah", "email": "sooryasairah@gmail.com"},
    {"name": "sreethu mohan", "email": "sreethumohan7034@gmail.com"},
    {"name": "surya suresh", "email": "suryasuresh29012000@gmail.com"},
    {"name": "swathy chandran", "email": "swathychandran76@gmail.com"},
    {"name": "vidhya vijayan", "email": "vidhyavijayan412@gmail.com"},
    {"name": "adithya", "email": "adithyalekshmi54@gmail.com"},
    {"name": "neethu ms", "email": "neethums40@gmail.com"},
    {"name": "neethu", "email": "neethu@edunetfoundation.org"}
]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_speech_from_mic(retry_count=3, timeout=15, phrase_time_limit=15):
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.energy_threshold = 400  # Adjusted for better noise handling
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        for attempt in range(retry_count):
            print(f"Listening... (attempt {attempt + 1})")
            try:
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                print("Processing...")
                text = r.recognize_google(audio, show_all=True)  # Get detailed results
                if text and 'alternative' in text:  # Check for recognition alternatives
                    recognized_text = text['alternative'][0]['transcript'].lower().strip()
                    confidence = text['alternative'][0]['confidence'] if 'confidence' in text['alternative'][0] else 1.0
                    if confidence < 0.7:  # If confidence is low, ask to repeat
                        speak("I heard you say: " + recognized_text + ". Is that correct?")
                        confirmation = recognize_speech_from_mic()
                        if confirmation == "yes":
                            return recognized_text
                        else:
                            continue  # Go to the next attempt
                    return recognized_text
                else:
                    print("Could not recognize the speech.")
                    speak("Sorry, I did not catch that. Could you please repeat?")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio.")
                speak("Sorry, I did not catch that. Could you please repeat?")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                speak("Sorry, there was an issue with the speech recognition service.")
                break
    return ""


def get_predefined_email(name):
    normalized_name = name.lower().strip()
    names = [item["name"].lower().strip() for item in predefined_emails]
    best_match = process.extractOne(normalized_name, names, score_cutoff=80)
    if best_match:
        for item in predefined_emails:
            if item["name"].lower().strip() == best_match[0]:
                return item["email"]
    return None

def send_email(recipient, subject, msg):
    try:
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login('adithyalekshmi54@gmail.com', 'xfcc fubn kfhy oquw')
        message = f"Subject: {subject}\n\nDear {recipient.split('@')[0]},\n\n{msg}\n\nBest regards,\nAdithya Lekshmi"
        mail.sendmail('adithyalekshmi54@gmail.com', recipient, message)
        print("Congrats! Your mail has been sent.")
        speak("Congrats! Your mail has been sent.")
        mail.close()
    except Exception as e:
        print(f"Failed to send email: {e}")
        speak("Failed to send email.")

def chunk_text(text, chunk_size=150):
    """Splits text into smaller chunks."""
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def check_inbox():
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login('adithyalekshmi54@gmail.com', 'xfcc fubn kfhy oquw')
        mail.select('inbox')

        status, messages = mail.search(None, 'ALL')
        mail_ids = messages[0].split()

        if not mail_ids:
            speak("Your inbox is empty.")
            return

        latest_email_id = mail_ids[-1]

        status, data = mail.fetch(latest_email_id, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject = msg['subject']
                email_from = msg['from']

                speak(f"From: {email_from}")
                speak(f"Subject: {email_subject}")

                email_body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain' and not part.get('Content-Disposition'):
                            email_body = part.get_payload(decode=True).decode()
                            break
                else:
                    email_body = msg.get_payload(decode=True).decode()

                if email_body:
                    speak("Email body: ")
                    for chunk in chunk_text(email_body):
                        speak(chunk)
                        text = recognize_speech_from_mic(retry_count=1, timeout=1, phrase_time_limit=1)
                        if text == "exit":
                            speak("Exiting the operation.")
                            return
                else:
                    speak("The email body is empty or could not be read.")
        
        mail.logout()
    except Exception as e:
        print(f"Failed to check inbox: {e}")
        speak("Failed to check inbox.")

def delete_recent_email():
    speak("This function will delete the most recent email. Feature under construction.")

def email_composition_with_timer():
    start_time = time.time() 
    
    while True:
        speak("Who is the recipient?")
        recipient_name = recognize_speech_from_mic()
        if recipient_name == "exit":
            return
        if time.time() - start_time > 600:
            speak("Time limit exceeded. Exiting email composition.")
            return
        
        recipient = get_predefined_email(recipient_name)
        if recipient:
            break
        else:
            speak("The email address is invalid or not recognized. Please try again.")

    while True:
        speak("What is the subject?")
        subject = recognize_speech_from_mic()
        if subject == "exit":
            return
        if time.time() - start_time > 600:
            speak("Time limit exceeded. Exiting email composition.")
            return
        
        if subject:
            break
        else:
            speak("Please provide a subject for the email.")

    while True:
        speak("Tell me the message.")
        message = recognize_speech_from_mic(timeout=600, phrase_time_limit=600)
        if message == "exit":
            return
        if time.time() - start_time > 1200:
            speak("Time limit exceeded. Exiting email composition.")
            return
        
        if message:
            break
        else:
            speak("Please provide the message content.")

    send_email(recipient, subject, message)

def main():
    speak("Project: Voice based Email for blind")
    login = os.getlogin()
    print("You are logging from: " + login)

    print("1. Compose a mail.")
    speak("1. Compose a mail.")
    print("2. Check inbox.")
    speak("2. Check inbox.")
    print("3. Delete recent email.")
    speak("3. Delete recent email.")

    option_keywords = {
        "compose": ["option one", "option 1", "1", "one", "option run", "compose"],
        "check": ["option two", "option 2", "2", "two", "check", "inbox"],
        "delete": ["option three", "option","option 3", "three", "3", "delete tree"]
    }

    while True:
        speak("Please say the option number or command.")
        option = recognize_speech_from_mic()
        if option == "exit":
            speak("Exiting the application.")
            return
        if option in option_keywords["compose"]:
            email_composition_with_timer()
            break
        elif option in option_keywords["check"]:
            check_inbox()
            break
        elif option in option_keywords["delete"]:
            delete_recent_email()
            break
        else:
            speak("Invalid option. Please try again.")

if __name__ == "__main__":
    main()


import re
import speech_recognition as sr
import smtplib
import email
import imaplib
import pyttsx3
import os
import time
from fuzzywuzzy import process

predefined_emails = [
    {"name": "adithya lekshmi", "email": "adithyalekshmi98@gmail.com"},
    {"name": "ammalu", "email": "ammalu0202@gmail.com"},
    {"name": "anakha suresh", "email": "anakhasuresh888@gmail.com"},
    {"name": "anu lekshmi", "email": "anulekshmi2701@gmail.com"},
    {"name": "aparna appu", "email": "aparnaappuappu09@gmail.com"},
    {"name": "athira sb", "email": "athirasb735@gmail.com"},
    {"name": "devika", "email": "devika3388devu@gmail.com"},
    {"name": "devuvi", "email": "devuvi3388@gmail.com"},
    {"name": "dhanya meenakshi", "email": "dhanyameenakshi979@gmail.com"},
    {"name": "ganga ghosh", "email": "gangaghosh423@gmail.com"},
    {"name": "kajal kichu", "email": "kajalkichu@gmail.com"},
    {"name": "lisy jayakumar", "email": "lisyjayakumar@gmail.com"},
    {"name": "mahima", "email": "mahimamahi8518@gmail.com"},
    {"name": "nandana ss", "email": "ssnandana200@gmail.com"},
    {"name": "rahitha nair", "email": "rahithatnair@gmail.com"},
    {"name": "remya ks", "email": "ksremya718@gmail.com"},
    {"name": "sarjitha vipin", "email": "sarjithavipin1998@gmail.com"},
    {"name": "soorya", "email": "sooryaa013@gmail.com"},
    {"name": "sooryasearah", "email": "sooryasairah@gmail.com"},
    {"name": "sreethu mohan", "email": "sreethumohan7034@gmail.com"},
    {"name": "surya suresh", "email": "suryasuresh29012000@gmail.com"},
    {"name": "swathy chandran", "email": "swathychandran76@gmail.com"},
    {"name": "vidhya vijayan", "email": "vidhyavijayan412@gmail.com"},
    {"name": "adithya", "email": "adithyalekshmi54@gmail.com"},
    {"name": "neethu ms", "email": "neethums40@gmail.com"},
    {"name": "neethu", "email": "neethu@edunetfoundation.org"}
]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_speech_from_mic(retry_count=3, timeout=15, phrase_time_limit=15):
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.energy_threshold = 400  # Adjusted for better noise handling
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        for attempt in range(retry_count):
            print(f"Listening... (attempt {attempt + 1})")
            try:
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                print("Processing...")
                text = r.recognize_google(audio, show_all=True)  # Get detailed results
                if text and 'alternative' in text:  # Check for recognition alternatives
                    recognized_text = text['alternative'][0]['transcript'].lower().strip()
                    confidence = text['alternative'][0]['confidence'] if 'confidence' in text['alternative'][0] else 1.0
                    if confidence < 0.7:  # If confidence is low, ask to repeat
                        speak("I heard you say: " + recognized_text + ". Is that correct?")
                        confirmation = recognize_speech_from_mic()
                        if confirmation == "yes":
                            return recognized_text
                        else:
                            continue  # Go to the next attempt
                    return recognized_text
                else:
                    print("Could not recognize the speech.")
                    speak("Sorry, I did not catch that. Could you please repeat?")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio.")
                speak("Sorry, I did not catch that. Could you please repeat?")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                speak("Sorry, there was an issue with the speech recognition service.")
                break
    return ""


def get_predefined_email(name):
    normalized_name = name.lower().strip()
    names = [item["name"].lower().strip() for item in predefined_emails]
    best_match = process.extractOne(normalized_name, names, score_cutoff=80)
    if best_match:
        for item in predefined_emails:
            if item["name"].lower().strip() == best_match[0]:
                return item["email"]
    return None

def send_email(recipient, subject, msg):
    try:
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login('adithyalekshmi54@gmail.com', 'xfcc fubn kfhy oquw')
        message = f"Subject: {subject}\n\nDear {recipient.split('@')[0]},\n\n{msg}\n\nBest regards,\nAdithya Lekshmi"
        mail.sendmail('adithyalekshmi54@gmail.com', recipient, message)
        print("Congrats! Your mail has been sent.")
        speak("Congrats! Your mail has been sent.")
        mail.close()
    except Exception as e:
        print(f"Failed to send email: {e}")
        speak("Failed to send email.")

def chunk_text(text, chunk_size=150):
    """Splits text into smaller chunks."""
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def check_inbox():
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login('adithyalekshmi54@gmail.com', 'xfcc fubn kfhy oquw')
        mail.select('inbox')

        status, messages = mail.search(None, 'ALL')
        mail_ids = messages[0].split()

        if not mail_ids:
            speak("Your inbox is empty.")
            return

        latest_email_id = mail_ids[-1]

        status, data = mail.fetch(latest_email_id, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject = msg['subject']
                email_from = msg['from']

                speak(f"From: {email_from}")
                speak(f"Subject: {email_subject}")

                email_body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain' and not part.get('Content-Disposition'):
                            email_body = part.get_payload(decode=True).decode()
                            break
                else:
                    email_body = msg.get_payload(decode=True).decode()

                if email_body:
                    speak("Email body: ")
                    for chunk in chunk_text(email_body):
                        speak(chunk)
                        text = recognize_speech_from_mic(retry_count=1, timeout=1, phrase_time_limit=1)
                        if text == "exit":
                            speak("Exiting the operation.")
                            return
                else:
                    speak("The email body is empty or could not be read.")
        
        mail.logout()
    except Exception as e:
        print(f"Failed to check inbox: {e}")
        speak("Failed to check inbox.")

def delete_recent_email():
    speak("This function will delete the most recent email. Feature under construction.")

def email_composition_with_timer():
    start_time = time.time() 
    
    while True:
        speak("Who is the recipient?")
        recipient_name = recognize_speech_from_mic()
        if recipient_name == "exit":
            return
        if time.time() - start_time > 600:
            speak("Time limit exceeded. Exiting email composition.")
            return
        
        recipient = get_predefined_email(recipient_name)
        if recipient:
            break
        else:
            speak("The email address is invalid or not recognized. Please try again.")

    while True:
        speak("What is the subject?")
        subject = recognize_speech_from_mic()
        if subject == "exit":
            return
        if time.time() - start_time > 600:
            speak("Time limit exceeded. Exiting email composition.")
            return
        
        if subject:
            break
        else:
            speak("Please provide a subject for the email.")

    while True:
        speak("Tell me the message.")
        message = recognize_speech_from_mic(timeout=600, phrase_time_limit=600)
        if message == "exit":
            return
        if time.time() - start_time > 1200:
            speak("Time limit exceeded. Exiting email composition.")
            return
        
        if message:
            break
        else:
            speak("Please provide the message content.")

    send_email(recipient, subject, message)

def main():
    speak("Project: Voice based Email for blind")
    login = os.getlogin()
    print("You are logging from: " + login)

    print("1. Compose a mail.")
    speak("1. Compose a mail.")
    print("2. Check inbox.")
    speak("2. Check inbox.")
    print("3. Delete recent email.")
    speak("3. Delete recent email.")

    option_keywords = {
        "compose": ["option one", "option 1", "1", "one", "option run", "compose"],
        "check": ["option two", "option 2", "2", "two", "check", "inbox"],
        "delete": ["option three", "option","option 3", "three", "3", "delete tree"]
    }

    while True:
        speak("Please say the option number or command.")
        option = recognize_speech_from_mic()
        if option == "exit":
            speak("Exiting the application.")
            return
        if option in option_keywords["compose"]:
            email_composition_with_timer()
            break
        elif option in option_keywords["check"]:
            check_inbox()
            break
        elif option in option_keywords["delete"]:
            delete_recent_email()
            break
        else:
            speak("Invalid option. Please try again.")

if __name__ == "__main__":
    main()