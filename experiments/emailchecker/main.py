import imaplib
import email
from email.header import decode_header
import time

# Set up email credentials and server details
username = "ralph.brecheisen@gmail.com"
password = "nrkl rozg nncm kwvo"
imap_server = "imap.gmail.com"


def get_command(subject):
    pass


def check_mail():
    try:
        # Connect to the Gmail IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select("inbox")

        # Search for unread messages
        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK":
            print("No new messages.")
            return

        # Process each unread message
        for num in messages[0].split():
            status, msg_data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            # Decode email subject and sender
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            from_ = msg.get("From")
            print(f"Processing email from {from_} with subject: {subject}")

            # Check for specific command in subject
            if subject.startswith('EmailChecker'):
                command = get_command(subject)
                cpu_info = get_cpu_status()
                send_response(cpu_info)

            # Mark as seen or delete as needed
        mail.close()
        mail.logout()

    except Exception as e:
        print(f"Error: {e}")

def get_cpu_status():
    # cpu_percent = psutil.cpu_percent(interval=1)
    # memory_info = psutil.virtual_memory()
    return f"CPU Usage: 100%\nMemory Usage: 100%"


def send_response(body):
    import smtplib
    from email.mime.text import MIMEText

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = username
    receiver_email = "r.brecheisen@maastrichtuniversity.nl"
    password = "nrkl rozg nncm kwvo"

    # Compose the message
    msg = MIMEText(body)
    msg["Subject"] = "EmailChecker: "
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


# Schedule check every 5 minutes
while True:
    check_mail()
    time.sleep(5)