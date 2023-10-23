from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "audiodeletetask" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "key" UUID NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS "idx_audiodelete_key_606aec" ON "audiodeletetask" ("key");
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "banned" BOOL NOT NULL  DEFAULT False,
    "deleted" BOOL NOT NULL  DEFAULT False
);
CREATE INDEX IF NOT EXISTS "idx_user_email_1b4f1c" ON "user" ("email");
CREATE TABLE IF NOT EXISTS "audio" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "key" UUID NOT NULL UNIQUE,
    "name" VARCHAR(255) NOT NULL,
    "source" VARCHAR(9) NOT NULL,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "num_frames" INT NOT NULL,
    "num_channels" INT NOT NULL,
    "sample_rate" INT NOT NULL,
    "duration" DOUBLE PRECISION NOT NULL,
    "url" VARCHAR(255),
    "url_expires" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "public" BOOL NOT NULL  DEFAULT False,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_audio_key_1adca4" ON "audio" ("key");
CREATE INDEX IF NOT EXISTS "idx_audio_name_cb39a3" ON "audio" ("name");
CREATE INDEX IF NOT EXISTS "idx_audio_source_ce1ad2" ON "audio" ("source");
CREATE INDEX IF NOT EXISTS "idx_audio_user_id_414a9b" ON "audio" ("user_id");
COMMENT ON COLUMN "audio"."source" IS 'uploaded: uploaded\nrecorded: recorded\ngenerated: generated';
CREATE TABLE IF NOT EXISTS "generation" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "model" VARCHAR(255) NOT NULL,
    "elapsed_time" DOUBLE PRECISION NOT NULL,
    "task_finished" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "public" BOOL NOT NULL  DEFAULT False,
    "output_id" INT NOT NULL REFERENCES "audio" ("id") ON DELETE CASCADE,
    "reference_id" INT NOT NULL REFERENCES "audio" ("id") ON DELETE CASCADE,
    "source_id" INT NOT NULL REFERENCES "audio" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_generation_model_8daf5a" ON "generation" ("model");
CREATE INDEX IF NOT EXISTS "idx_generation_output__3faccc" ON "generation" ("output_id");
CREATE INDEX IF NOT EXISTS "idx_generation_referen_f76e59" ON "generation" ("reference_id");
CREATE INDEX IF NOT EXISTS "idx_generation_source__c9231b" ON "generation" ("source_id");
CREATE INDEX IF NOT EXISTS "idx_generation_user_id_93593e" ON "generation" ("user_id");
CREATE TABLE IF NOT EXISTS "task" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "model" VARCHAR(255) NOT NULL,
    "elapsed_time" DOUBLE PRECISION NOT NULL,
    "task_finished" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "generation_id" INT REFERENCES "generation" ("id") ON DELETE SET NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_task_model_e7084d" ON "task" ("model");
CREATE INDEX IF NOT EXISTS "idx_task_generat_56b61d" ON "task" ("generation_id");
CREATE INDEX IF NOT EXISTS "idx_task_user_id_1a29a7" ON "task" ("user_id");
CREATE TABLE IF NOT EXISTS "token" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "issued" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "disabled" BOOL NOT NULL  DEFAULT False,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_token_user_id_55c1a3" ON "token" ("user_id");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
