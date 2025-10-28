from bw_secrets import MONGO_CONN_STR
import json
import logging
from models import Participant, Log
from pymongo import MongoClient

LOGGER = logging.getLogger(__name__)

DB_NAME = "res-req"
PARTICIPANTS_COLLECTION_NAME = "participants"
LOGS_COLLECTION_NAME = "logs"
ORDER_FILE = "order.json"

MONGO_CLIENT: MongoClient = MongoClient(MONGO_CONN_STR)
DB = MONGO_CLIENT.get_database(DB_NAME)
PARTICIPANTS_COLLECTION = DB.get_collection(PARTICIPANTS_COLLECTION_NAME)
LOGS_COLLECTION = DB.get_collection(LOGS_COLLECTION_NAME)


def get_order_from_file(order_file: str) -> list[str]:
    with open(order_file) as f:
        return json.load(f)


def get_participants(order: list[str]) -> list[Participant]:
    participants: list[Participant] = []

    # Insert participants in order
    for name in order:
        first_name, last_name = name.split(" ")
        doc = (PARTICIPANTS_COLLECTION
               .find_one({"first_name": first_name, "last_name": last_name}))
        if doc:
            participants.append(Participant.model_validate(doc))

    # Link next_participant references
    for participant in participants:
        current_index = order.index(participant.full_name)
        next_index = (current_index + 1) % len(order)
        next_name = order[next_index]
        participant.next_participant = next(
            p for p in participants if p.full_name == next_name)

    return participants


# Read in order.json, which is the single source-of-truth
# that dictates the overall participant order
participant_order: list[str] = get_order_from_file(ORDER_FILE)
LOGGER.info(f"Got participant order: {participant_order}")
participants: list[Participant] = get_participants(participant_order)
LOGGER.info(f"Got participants: {participants}")
