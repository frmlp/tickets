import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from dotenv import load_dotenv

load_dotenv()


def send_email(play_name, success):
    print("Preparing to send email notification...")
    # Email configuration
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('EMAIL_PASSWORD')  # Get password from environment variable
    receiver_email = os.getenv('RECEIVER_EMAIL')

    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email

    print("Creating email content...")
    if(success):
        message["Subject"] = "Tickets Available!"
        body = f"Tickets are now available for {play_name} !"
    else:
        message["Subject"] = "Error Checking Tickets"
        body = f"An error occurred while checking tickets for {play_name}"
    
    message.attach(MIMEText(body, "plain"))
    
    print("Email content created. Setting up email server...")
    # Send email
    try:
        SMTP_SERVER = os.getenv('SMTP_SERVER')
        SMTP_PORT = int(os.getenv('SMTP_PORT'))
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            print("Logging in to email server...")
            server.login(sender_email, sender_password)
            print("Sending email...")
            server.send_message(message)
        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def check_tickets(name):
    print(f"Checking tickets for {name} on {os.getenv('DATE')}...")
    try:
        # Download the webpage
        url = os.getenv('BASE_URL') + "/" + name
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        repertuare_grid_divs = soup.find_all('div', class_='repertuare-grid')
        if not repertuare_grid_divs:
            raise Exception("No repertuare grid found on the page. Please check the URL or the page structure.")
        for div in repertuare_grid_divs:
            time_element = div.find('time', datetime=os.getenv('DATE'))
            if time_element:
                print(f"Found time element for date {os.getenv('DATE')}")
                if div.find('a'):
                    return True
        return False

    except requests.RequestException as e:
        print(f"Error downloading the page: {e}")
        raise  # Re-raise the exception
    except Exception as e:
        print(f"Error processing the page: {e}")
        raise  # Re-raise the exception
    
if __name__ == "__main__":
    # Load plays from environment variable
    plays_json = os.getenv('PLAYS').strip()
    plays = json.loads(plays_json)

    for play in plays:
        try:
            if check_tickets(play):
                print(f"Tickets available for {play}")
                send_email(play, True)
            else:
                print(f"No tickets found for {play}")
        except Exception as e:
            send_email(play, False)
