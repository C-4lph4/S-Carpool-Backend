import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

sender = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


def generateCode():
    code = ""
    while len(code) < 6:
        code = f"{random.randint(0, 9)}{code}"
    return code


def send_code(receiver):
    code = generateCode()
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = "Account Activation"
    body = f"Here is your activation code: \n <h2>{code}</h2>"
    message.attach(MIMEText(body, "html"))

    def send_mail(sender, receiver, message):
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, receiver, message.as_string())
            print("Email sent successfully")
        except Exception as e:
            print(e)
            print("Failed to send email")

    email_thread = threading.Thread(target=send_mail, args=(sender, receiver, message))
    email_thread.start()

    return code
