from pydantic import BaseModel
from typing import List
from app.schemas.common import SpecialNote

class GenerateRequest(BaseModel):
    document_ids: List[str]
    additional_prompt: str

class GenerateResponse(BaseModel):
    special_notes: List[SpecialNote]
