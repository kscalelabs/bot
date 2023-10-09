"""Utility functions for sending emails to users."""

import argparse
import asyncio
import logging
import textwrap
from dataclasses import dataclass

import aiosmtplib

from bot.api.token import create_access_token, load_access_token
from bot.settings import load_settings

logger = logging.getLogger(__name__)


async def send_email(subject: str, body: str, to: str) -> None:
    settings = load_settings().email

    header = textwrap.dedent(
        f"""
            To: {to}
            From: {settings.name}<{settings.email}>
            Subject: {subject}
        """
    ).strip()

    message = header + "\n\n" + body

    smtp_client = aiosmtplib.SMTP(hostname=settings.host, port=settings.port)

    await smtp_client.connect()
    await smtp_client.login(settings.email, settings.password)
    await smtp_client.sendmail(settings.email, to, message)
    await smtp_client.quit()


@dataclass
class OneTimePassPayload:
    email: str

    def encode(self) -> str:
        expire_minutes = load_settings().crypto.expire_otp_minutes
        return create_access_token({"email": self.email}, expire_minutes=expire_minutes)

    @classmethod
    def decode(cls, payload: str) -> "OneTimePassPayload":
        data = load_access_token(payload)
        return cls(email=data["email"])


async def send_otp_email(payload: OneTimePassPayload, login_url: str) -> None:
    body = textwrap.dedent(
        f"""
            Here is a one-time password (OTP) for you to log in:

            {login_url}?otp={payload.encode()}
        """
    )

    await send_email(subject="One-Time Password", body=body, to=payload.email)


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
