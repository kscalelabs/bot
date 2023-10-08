"""Entrypoint for FastAPI through AWS Lambda."""

from mangum import Mangum

from bot.api.app.main import app

# This is required for AWS Lambda.
handler = Mangum(app)
