import os
import smtplib
import ssl
from email.message import EmailMessage


def send_email(recipient: str, subject: str, body: str) -> None:
    host = os.environ.get("SMTP_HOST", "").strip()
    username = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM", username).strip()
    port = int(os.environ.get("SMTP_PORT", "465"))
    timeout = int(os.environ.get("SMTP_TIMEOUT_SECONDS", "20"))

    if not host or not username or not password or not sender:
        raise RuntimeError("La configuració SMTP és incompleta")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    use_ssl = os.environ.get("SMTP_USE_SSL", "true").lower() in {"1", "true", "yes"}
    if use_ssl:
        with smtplib.SMTP_SSL(
            host, port, timeout=timeout, context=ssl.create_default_context()
        ) as server:
            server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=timeout) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(username, password)
            server.send_message(message)
