from pydantic import BaseModel
from typing import Optional, Dict, Union


class UserCreate(BaseModel):
    email: str
    password: str
    