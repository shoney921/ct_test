from pydantic import BaseModel
from typing import List, Dict

# 1. /api/search
class PackingInfo(BaseModel):
    type: str
    material: str
    spec: str
    company: str

class ExperimentInfo(BaseModel):
    code: str
    item: str
    period: str
    check: str
    standard: str
    result: str

class SearchRequest(BaseModel):
    packages: List[PackingInfo]
    lab_id: str
    special_note: str

class Document(BaseModel):
    document_id: str
    summary: str
    file_name: str
    test_no: str
    product_name: str
    customer: str
    developer: str
    requester: str
    test_count: str
    test_quantity: str
    test_date: str
    expected_date: str
    writer: str
    reviewer: str
    approver: str
    packing_info: List[PackingInfo]
    lab_id: str
    lab_info: str
    experiment_info: List[ExperimentInfo]
    special_notes: Dict[str, str]
    download_url: str

class SearchResponse(BaseModel):
    results: List[Document]
    total: int


# 2. /api/generate
class GenerateRequest(BaseModel):
    document_ids: List[str]
    additional_prompt: str

class GenerateResponse(BaseModel):
    status: str
    file_name: str
    special_notes: Dict[str, str]
