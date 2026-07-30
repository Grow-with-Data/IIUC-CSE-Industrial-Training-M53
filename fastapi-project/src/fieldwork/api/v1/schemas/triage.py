from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TriageInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    thread_id: str
    user_input: str

class TriageOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    response: str