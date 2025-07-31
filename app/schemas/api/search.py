from pydantic import BaseModel
from typing import List
from app.schemas.common import PackingInfo, Document

class SearchRequest(BaseModel):
    packages: List[PackingInfo]
    lab_id: str
    lab_info: str
    optimum_capacity: str
    special_note: str
    test_date_start: str | None = None  # 테스트 날짜 시작 범위 (YYYY-MM-DD)
    test_date_end: str | None = None    # 테스트 날짜 종료 범위 (YYYY-MM-DD)

class SearchResponse(BaseModel):
    results: List[Document]
    total: int
