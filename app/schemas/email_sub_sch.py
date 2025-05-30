# app/schemas/email_sub_sch.py
from pydantic import BaseModel, EmailStr

class EmailSubscriptionCreate(BaseModel):
    email: EmailStr
