from pydantic import BaseModel
from typing import List, Dict

# 1. /api/search
class PackageInfo(BaseModel):
    type: str
    material: str
    detail: str
    manufacturer: str

class SearchRequest(BaseModel):
    packages: List[PackageInfo]
    labId: str
    specialNote: str

class SearchResult(BaseModel):
    documentId: str
    id: str
    fileName: str
    packageInfo: List[PackageInfo]
    summary: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int

# 2. /api/generate
class GenerateRequest(BaseModel):
    documentIds: List[str]
    additionalPrompt: str

class GenerateResponse(BaseModel):
    status: str
    fileName: str
    special_notes: Dict[str, str]

# 3. /api/document
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

class DocumentRequest(BaseModel):
    documentId: str

class DocumentResponse(BaseModel):
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

# 4. /api/download
class DownloadRequest(BaseModel):
    documentId: str

class DownloadResponse(BaseModel):
    downloadUrl: str
    fileName: str
    status: str 