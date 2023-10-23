from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "audio" DROP COLUMN "url";
        ALTER TABLE "audio" DROP COLUMN "url_expires";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "audio" ADD "url" VARCHAR(255);
        ALTER TABLE "audio" ADD "url_expires" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP;"""
