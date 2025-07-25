from pydantic import BaseModel
from typing import List, Optional

class PackingInfo(BaseModel):
    type: str
    material: str
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
    optimum_capacity : str
    experiment_info: List[ExperimentInfo]
    special_notes: List[SpecialNote]
    download_url: str

