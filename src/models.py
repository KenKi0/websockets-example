import pydantic


class LoginMessage(pydantic.BaseModel):
    sender: str


class Message(pydantic.BaseModel):
    sender: str
    text: str
