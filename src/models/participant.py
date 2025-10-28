from __future__ import annotations
from pydantic import BaseModel, EmailStr, model_validator, Field


class Participant(BaseModel):
    first_name: str
    last_name: str
    full_name: str | None = None
    primary_email: EmailStr
    all_emails: list[EmailStr] | None = None
    next_participant: Participant | None = Field(default=None, repr=False)

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
