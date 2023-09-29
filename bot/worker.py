"""Defines the worker that handles queries from the AWS queue."""

import json
import logging
import os
import random
from pathlib import Path

import boto3
import numpy as np
import requests
from codec.models.hubert import HubertModel

logger = logging.getLogger(__name__)

REGION = os.environ["REGION"]
ssm = boto3.client("ssm", region_name=REGION)
USER_HG = ssm.get_parameter(Name="/USER_HG")["Parameter"]["Value"]
PASSWORD_HG = ssm.get_parameter(Name="/PASSWORD_HG", WithDecryption=True)["Parameter"]["Value"]

SQS = boto3.client("sqs", region_name=REGION)

QUEUE_URL = os.environ["SQSQUEUEURL"]
WAIT_TIME_SECONDS = 20


def get_sqs_message(queue_url: str, time_wait: float) -> tuple[dict, str]:
    response = SQS.receive_message(
        QueueUrl=queue_url,
        AttributeNames=["SentTimestamp"],
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        WaitTimeSeconds=time_wait,
    )

    try:
        message = response["Messages"][0]
    except KeyError:
        return None, None

    receipt_handle = message["ReceiptHandle"]
    return message, receipt_handle


def delete_sqs_message(queue_url: str, receipt_handle: str, prompt: str) -> None:
    SQS.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    logger.info("Received and deleted message: %s", prompt)


def convert_message_to_dict(message: dict) -> dict:
    cleaned_message = {}
    body = json.loads(message["Body"])
    for item in body:
        cleaned_message[item] = body[item]["StringValue"]
    return cleaned_message


def validate_request(r: requests.Response) -> None:
    if not r.ok:
        logger.error("Failure: %s", r.text)
    else:
        logger.info("Success")


def update_discord_picture(application_id: str, interaction_token: str, file_path: str | Path) -> None:
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}/messages/@original"
    files = {"stable-diffusion.png": open(file_path, "rb")}
    r = requests.patch(url, files=files)
    validate_request(r)


def pictures_to_discord(file_path: str | Path, message_dict: dict, message_response: str) -> None:
    # Posts a follow up picture back to user on Discord.
    url = f"https://discord.com/api/v10/webhooks/{message_dict['applicationId']}/{message_dict['interactionToken']}/messages/@original"
    json_payload = {
        "content": f"*Completed your Sparkle!*```{message_response}```",
        "embeds": [],
        "attachments": [],
        "allowed_mentions": {"parse": []},
    }
    r = requests.patch(url, json=json_payload)
    validate_request(r)

    # Upload a picture.
    files = {"stable-diffusion.png": open(file_path, "rb")}
    r = requests.patch(url, json=json_payload, files=files)
    validate_request(r)


def message_response(customer_data: dict) -> str:
    message_response = f"\nPrompt: {customer_data['prompt']}"
    if "negative_prompt" in customer_data:
        message_response += f"\nNegative Prompt: {customer_data['negative_prompt']}"
    if "seed" in customer_data:
        message_response += f"\nSeed: {customer_data['seed']}"
    if "steps" in customer_data:
        message_response += f"\nSteps: {customer_data['steps']}"
    if "sampler" in customer_data:
        message_response += f"\nSampler: {customer_data['sampler']}"
    return message_response


def submit_initial_response(application_id: str, interaction_token: str, message_response: str) -> None:
    # Posts a follow up picture back to user on Discord
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}/messages/@original"
    json_payload = {
        "content": f"Processing your Sparkle```{message_response}```",
        "embeds": [],
        "attachments": [],
        "allowed_mentions": {"parse": []},
    }
    r = requests.patch(
        url,
        json=json_payload,
    )
    validate_request(r)


def cleanup_pictures(path_to_file: str | Path) -> None:
    # Clean up file(s) created during creation.
    os.remove(path_to_file)


def run_speech_translation(model: HubertModel, source_audio: np.ndarray, ref_audio: np.ndarray) -> list[np.ndarray]:
    raise NotImplementedError


def decide_inputs(user_dict: dict) -> dict:
    if "seed" not in user_dict:
        user_dict["seed"] = random.randint(0, 99999)

    if "steps" not in user_dict:
        user_dict["steps"] = 16

    if "sampler" not in user_dict:
        user_dict["sampler"] = "k_euler_a"
    return user_dict


def run_main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    run_main()
