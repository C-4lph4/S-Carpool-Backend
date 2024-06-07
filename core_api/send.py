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

    timeout = 40

    email_sent_event = threading.Event()
    email_status = {"success": None}

    def send_mail_and_set_event(
        sender, receiver, message, email_status, email_sent_event
    ):
        email_status["success"] = send_mail(sender, receiver, message)
        email_sent_event.set()

    timer = threading.Timer(
        timeout,
        send_mail_and_set_event,
        args=[sender, receiver, message, email_status, email_sent_event],
    )
    timer.start()

    email_sent_event.wait(timeout)

    if email_status["success"]:
        return code
    else:
        return


def send_mail(sender, receiver, message):
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, message.as_string())
        return True
    except Exception as e:
        print(e)
        return False
