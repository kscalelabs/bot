"""Utility functions for sending emails to users."""

import argparse
import asyncio
import logging
import textwrap

import aiosmtplib
import jwt

from bot.api.model import User
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


async def send_verification_email(email: str) -> None:
    payload = jwt.encode({"email": email}, load_settings().crypto.jwt_secret, algorithm="HS256")

    body = textwrap.dedent(
        f"""
            Please verify your email by clicking the link below:

            https://api.dpsh.dev/users/verify/{payload}
        """
    )

    await send_email(subject="Verify your email", body=body, to=email)


async def verify_email(payload: str) -> str:
    try:
        email = jwt.decode(payload, load_settings().crypto.jwt_secret, algorithms=["HS256"])["email"]
        user_obj = await User.get_or_none(email=email)
        assert user_obj is not None
    except Exception:
        logger.exception("Invalid payload")
        raise ValueError("Invalid payload")

    user_obj.email_verified = True
    await user_obj.save()
    return email


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
