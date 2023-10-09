"""Utility functions for sending emails to users."""

import argparse
import asyncio
import logging
import textwrap
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from bot.api.token import create_token, load_token
from bot.settings import load_settings

logger = logging.getLogger(__name__)


async def send_email(subject: str, body: str, to: str) -> None:
    settings = load_settings().email

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.name} <{settings.email}>"
    msg["To"] = to

    msg.attach(MIMEText(body, "html"))

    smtp_client = aiosmtplib.SMTP(hostname=settings.host, port=settings.port)

    await smtp_client.connect()
    await smtp_client.login(settings.email, settings.password)
    await smtp_client.sendmail(settings.email, to, msg.as_string())
    await smtp_client.quit()


@dataclass
class OneTimePassPayload:
    email: str

    def encode(self) -> str:
        expire_minutes = load_settings().crypto.expire_otp_minutes
        return create_token({"email": self.email}, expire_minutes=expire_minutes)

    @classmethod
    async def decode(cls, payload: str) -> "OneTimePassPayload":
        _, data = await load_token(payload, only_once=True)
        return cls(email=data["email"])


async def send_otp_email(payload: OneTimePassPayload, login_url: str) -> None:
    url = f"{login_url}?otp={payload.encode()}"

    body = textwrap.dedent(
        f"""
            <h1><code>don't panic</code><br/><code>stay human</code></h1>
            <h2><code><a href="{url}">log in</a></code></h2>
            <p>Or copy-paste this link: {url}</p>
        """
    )

    await send_email(subject="One-Time Password", body=body, to=payload.email)


async def send_delete_email(email: str) -> None:
    body = textwrap.dedent(
        """
            <h1><code>don't panic</code><br/><code>stay human</code></h1>
            <h2><code>your account has been deleted</code></h2>
        """
    )

    await send_email(subject="Account Deleted", body=body, to=email)


def test_email_adhoc() -> None:
    parser = argparse.ArgumentParser(description="Test sending an email.")
    parser.add_argument("subject", help="The subject of the email.")
    parser.add_argument("body", help="The body of the email.")
    parser.add_argument("to", help="The recipient of the email.")
    args = parser.parse_args()

    asyncio.run(send_email(args.subject, args.body, args.to))


if __name__ == "__main__":
    # python -m bot.api.email
    test_email_adhoc()
