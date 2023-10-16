# Bot

The main `dpsh` bot.

## Getting Started

Install the package:

```bash
pip install -e '.[dev]'
```

Build a local config file:

```bash
python configs/build.py local ~/.config/dpsh.yaml
```

Start the frontend, backend and worker processes:

```bash
make start-frontend
make start-backend
make start-worker
```

## Infrastructure

- Frontend
  - Web: React
  - Mobile: React Native
- Backend: FastAPI
  - Database: PostgreSQL (Aurora Serverless on AWS)
  - Model inference: The FastAPI endpoint queues samples through SQS, which are then processed by ECS tasks.
