"""
A utility for dynamically building an email message
"""

import smtplib
from email.message import EmailMessage


class IncrementalEmailBuilder:
    """
    Helper class for building an email message incrementally.
    Allows appending to the subject and body, and then constructing the final EmailMessage.
    """

    def __init__(self, sender: str, recipient: str, subject: str = "") -> None:
        self.sender = sender
        self.recipient = recipient
        self._subject_parts = []
        if subject:
            self._subject_parts.append(subject)

        self._body_parts = []

    def append_subject(self, text: str) -> None:
        """Append additional text to the email subject"""
        self._subject_parts.append(text)

    def append_body(self, text: str) -> None:
        """Append text to the email body"""
        self._body_parts.append(text)

    def replace_body(self, text: str) -> None:
        """Replace entire body content"""
        self._body_parts = [text]

    def build(self) -> EmailMessage:
        """Construct and return the final EmailMessage object"""
        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = self.recipient
        msg["Subject"] = " ".join(self._subject_parts)

        body = "\n".join(self._body_parts)
        msg.set_content(body)

        return msg


def send_email(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    message: EmailMessage,
) -> None:
    """
    Send an EmailMessage via SMTP using TLS.

    Args:
        smtp_host: SMTP server hostname (e.g. smtp.gmail.com)
        smtp_port: SMTP port (e.g. 587 for TLS)
        username: SMTP login username
        password: SMTP login password or app password
        message: Fully constructed EmailMessage
    """
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        # Remember to comment out starttls and login to test locally
        # Since MailHog doesn't require authentication
        server.starttls()
        server.login(username, password)
        server.send_message(message)
