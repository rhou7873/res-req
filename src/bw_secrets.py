"""Secrets management"""
from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
import logging
import os

API_URL = os.getenv("BW_API_URL")
IDENTITY_URL = os.getenv("BW_ID_URL")
ACCESS_TOKEN = os.getenv("BW_ACCESS_TOKEN")

if (API_URL is None or
    IDENTITY_URL is None or
        ACCESS_TOKEN is None):
    raise Exception(
        "Environment variables aren't set: "
        f"API_URL={API_URL}, "
        f"IDENTITY_URL={IDENTITY_URL}, "
        f"ACCESS_TOKEN={ACCESS_TOKEN}")

client = BitwardenClient(
    client_settings_from_dict(
        {
            "apiUrl": API_URL,
            "deviceType": DeviceType.SDK,
            "identityUrl": IDENTITY_URL,
            "userAgent": "Python",
        }
    )
)

client.access_token_login(ACCESS_TOKEN)

################## GLOBAL CONSTANTS ###################

MONGO_CONN_STR = client.secrets().get(
    "32d23546-9159-491a-88dd-b3770028fbef").data.value

#######################################################

# Global logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s, %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)