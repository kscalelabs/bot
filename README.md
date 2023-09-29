# Discord Bot

Discord bot code

## Infrastructure

Under the hood, there is a single endpoint which serves the core voice changing model. This takes:

1. The audio file
2. The JST token

There is also wrapper bot code which interfaces between Discord and the endpoint. The server can also just serve requests directly, for example, through a web app.

The voice changer service logs:

1. The user ID
2. The source (e.g., web verses Discord)
3. The uploaded audio ID
4. The generated audio ID
