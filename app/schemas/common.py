from pydantic import BaseModel
from typing import List, Optional

class PackingInfo(BaseModel):
    type: str
    material: Optional[str] = None
    spec: Optional[str] = None
    company: Optional[str] = None

class ExperimentInfo(BaseModel):
    code: Optional[str] = None
    item: Optional[str] = None
    period: Optional[str] = None
    check: Optional[str] = None
    standard: Optional[str] = None
    result: Optional[str] = None

class SpecialNote(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None

class Document(BaseModel):
    document_id: str
    summary: str
    file_name: str
    test_no: Optional[str] = None
    product_name: Optional[str] = None
    customer: Optional[str] = None
    developer: Optional[str] = None
    requester: Optional[str] = None
    test_count: Optional[str] = None
    test_quantity: Optional[str] = None
    test_date: Optional[str] = None
    expected_date: Optional[str] = None
    writer: Optional[str] = None
    reviewer: Optional[str] = None
    approver: Optional[str] = None
    packing_info: List[PackingInfo]
    lab_id: Optional[str] = None
    lab_info: Optional[str] = None
    optimum_capacity : Optional[str] = None
    experiment_info: List[ExperimentInfo]
    special_notes: List[SpecialNote]
    download_url: str

