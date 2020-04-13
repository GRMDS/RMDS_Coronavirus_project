from dataclasses import dataclass, field
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
import ssl
import smtplib
from typing import List


@dataclass
class Addressee:

    """A user sending or receiving email."""

    name: str
    email: str


@dataclass
class AttachedImage:

    """An image embedded in an email."""

    content: bytes
    image_format: str
    cid: str = field(default_factory=lambda: make_msgid())


@dataclass
class AlertEmail:

    """An email alerting a user to COVID19 data."""

    sender: Addressee
    recipient: Addressee
    subject: str
    plain_text: str
    html: str
    images: List[AttachedImage]


def send_emails(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    emails: List[AlertEmail],
):
    formatted_emails = [create_formatted_email(email) for email in emails]

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()

        server.login(smtp_username, smtp_password)

        for formatted_email in formatted_emails:
            server.send_message(formatted_email)


def create_formatted_email(email: AlertEmail) -> EmailMessage:
    msg = EmailMessage()

    sender_username, sender_domain = email.sender.email.split('@')
    recipient_username, recipient_domain = email.recipient.email.split('@')

    msg['From'] = Address(email.sender.name, sender_username, sender_domain)
    msg['To'] = Address(
        email.recipient.name,
        recipient_username,
        recipient_domain,
    )
    msg['Subject'] = email.subject

    msg.set_content(email.plain_text)

    msg.add_alternative(email.html, subtype='html')

    for img in email.images:
        msg.get_payload()[1].add_related(
            img.content,
            'image',
            img.image_format,
            cid=img.cid,
        )

    return msg
