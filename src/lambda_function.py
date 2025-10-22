import json
import logging
from typing import Any, Dict

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Use a higher retry count because Payment Cryptography APIs can throttle quickly.
_boto_config = Config(retries={"max_attempts": 6, "mode": "standard"})
_client = boto3.client("payment-cryptography", config=_boto_config)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for the Payment Cryptography key listing Lambda.

    Returns:
        dict: API Gateway compatible response listing key metadata found.
    """
    try:
        paginator = _client.get_paginator("list_keys")
        keys = []
        for page in paginator.paginate():
            keys.extend(page.get("Keys", []))
        logger.info("Discovered %d AWS payment cryptography keys.", len(keys))
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"keys": keys}),
        }
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to list payment cryptography keys.")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Failed to list keys", "error": str(exc)}),
        }
