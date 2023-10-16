# Bot

The main `dpsh` bot.

## Infrastructure

- Frontend
  - Web: React
  - Mobile: React Native
- Backend: FastAPI
  - Database: PostgreSQL (Aurora Serverless on AWS)
  - Model inference: The FastAPI endpoint queues samples through SQS, which are then processed by ECS tasks.
