import json
from pymongo import MongoClient
from pydantic import BaseModel, EmailStr, model_validator
from bw_secrets import MONGO_CONN_STR

class Participant(BaseModel):
    first_name: str
    last_name: str
    full_name: str | None = None
    primary_email: EmailStr
    all_emails: list[EmailStr] | None = None

    @model_validator(mode="after")
    def set_full_name(self):
        if not self.full_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        return self

    @model_validator(mode="after")
    def set_all_emails(self):
        if not (self.all_emails and self.primary_email in self.all_emails):
            self.all_emails = [self.primary_email]
        return self

    def __str__(self):
        return self.full_name


MONGO_CLIENT: MongoClient = MongoClient(MONGO_CONN_STR)

db = MONGO_CLIENT.get_database("res-req")
participants_collection = db.get_collection("participants")

participants: list[Participant] = []
for doc in participants_collection.find():
    participants.append(Participant.model_validate(doc))

for participant in participants:
    print(participant)