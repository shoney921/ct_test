from pydantic import BaseModel
from typing import List
from app.schemas.common import PackingInfo, Document

class SearchRequest(BaseModel):
    packages: List[PackingInfo]
    lab_id: str
    lab_info: str
    optimum_capacity: str
    special_note: str

class SearchResponse(BaseModel):
    results: List[Document]
    total: int
