"""Google cloud helper functions."""

import json
import logging
import os

from google.oauth2 import service_account


def get_creds_from_env_vars():
    """Get credentials from environmental variables."""
    logging.info("Trying to load credentials from environment variables.")
    creds = service_account.Credentials.from_service_account_info(
        info=json.loads(os.getenv("GCP_KEYFILE"))
    )
    logging.info("Loaded credentials successfully.")
    return creds
