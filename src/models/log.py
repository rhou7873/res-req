from pydantic import BaseModel
from models import Participant
from datetime import datetime


class Log(BaseModel):
    participant: Participant
    timestamp: datetime
    email_sent: str
