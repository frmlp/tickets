import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json


def send_email(play_name):
    print("Preparing to send email notification...")
    # Email configuration
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('EMAIL_PASSWORD')  # Get password from environment variable
    receiver_email = os.getenv('RECEIVER_EMAIL')

    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Tickets Available!"
    
    print("Creating email content...")
    body = "Tickets are now available for " + play_name + "!"
    message.attach(MIMEText(body, "plain"))
    
    print("Email content created. Setting up email server...")
    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.wp.pl", 465) as server:
            print("Logging in to email server...")
            server.login(sender_email, sender_password)
            print("Sending email...")
            server.send_message(message)
        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def check_tickets(name):
    try:
        # Download the webpage
        url = os.getenv('BASE_URL') + "/" + name
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all div elements with class 'repertuare-shows'
        repertoire_divs = soup.find_all('div', class_='repertuare-shows')
        
        # Check if there are any 'a' elements within these divs
        for div in repertoire_divs:
            if div.find('a'):
                return True
        return False

    except requests.RequestException as e:
        print(f"Error downloading the page: {e}")
        return False
    except Exception as e:
        print(f"Error processing the page: {e}")
        return False
    

# Load plays from environment variable
plays_json = os.getenv('PLAYS').strip()
plays = json.loads(plays_json)

for play in plays:
    print(f"Checking tickets for: {play}")
    if check_tickets(play):
        print(f"Tickets available for {play}")
        send_email(play)
    else:
        print(f"No tickets found for {play}")

