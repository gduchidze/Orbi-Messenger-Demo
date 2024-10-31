from typing import List, Optional, Dict
from pydantic import BaseModel

class User(BaseModel):
    id: str

    class Config:
        extra = "allow"

class Postback(BaseModel):
    payload: str
    title: Optional[str] = None

class Message(BaseModel):
    mid: str
    text: Optional[str] = None
    attachments: Optional[List[Dict]] = None

    class Config:
        extra = "allow"

class Conversation(BaseModel):
    sender: User
    recipient: User
    message: Optional[Message] = None
    postback: Optional[Postback] = None

    class Config:
        arbitrary_types_allowed = True

class ConversationEntry(BaseModel):
    messaging: List[Conversation]

    class Config:
        extra = "allow"

class MessengerWebhookPayload(BaseModel):
    entry: List[ConversationEntry]
    object: Optional[str] = ""

    class Config:
        extra = "allow"