from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.schemas import (
    SearchRequest, SearchResponse, SearchResult, PackageInfo,
    GenerateRequest, GenerateResponse,
    DocumentRequest, DocumentResponse, PackingInfo, ExperimentInfo,
    DownloadRequest, DownloadResponse
)

app = FastAPI()

@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    # 요청 바디(request)는 SearchRequest 타입으로 자동 검증됨
    return SearchResponse(
        results=[
            SearchResult(
                documentId="DOC20250723001",
                id="CT20240001",
                fileName="ㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇ_테스트.pdf",
                packageInfo=[
                    PackageInfo(type="용기", material="PET", detail="직관", manufacturer="ㅇㅇ업체"),
                    PackageInfo(type="펌프", material="OTHER", detail="기본형", manufacturer="ㅇㅇ업체")
                ],
                summary="용기별 타입의 특성상 크랙 발생에 대한 안전성 관리가 중요하며..."
            ),
            SearchResult(
                documentId="DOC20250723002",
                id="CT20240002",
                fileName="ㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇ_테스트.pdf",
                packageInfo=[
                    PackageInfo(type="용기", material="PET", detail="직관", manufacturer="ㅇㅇ업체"),
                    PackageInfo(type="펌프", material="OTHER", detail="스프링형", manufacturer="ㅇㅇ업체")
                ],
                summary="낙하 테... (중략) 조회된 성적서의 특이사항 요약입니다."
            )
        ],
        total=2
    )

@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    return GenerateResponse(
        status="success",
        fileName="CT20240001_성적서_20250723.pdf",
        special_notes={
            "포장재 특이사항": "1. 기밀 관련 \n=>물로 진공감압테스트 시 기밀 양호하나, 용기 네크 및 캡 나사선 규격 관리 철저 요망.\n=>횡도누액테스트 결과 확인 후 진행 요망.\n\n2. 포장재 규격 관리 철저 요망.\n 1) 용기 바닥 및 배두께 규격 관리 철저 요망.\n 2) 용기 네크 늘어짐 관리 철저 요망.\n   → 미관리 시 적정용량 충전 불가.\n 3) 용기, 캡 체결 시 미세 공차 및 편심, 기울어짐 현상 발생.\n\n3. 불투명 용기사용\n=>투명 용기 사용 시 공기층 및 기포 보일 수 있으며, 일광,형광에 노출되어 내용물 변색, 변취 등 장기 안정성에 취약할 수 있음.\n=>충전 후 발생되는 상단 빈공간(헤드 스페이스) 마스킹 필요.\n=>포장재 생산 시 정전기로 인하여 이물이 용기안쪽에 흡착되어 내용물 충전 후 미세하게 보일 수 있음.\n=>투명 용기 사용 시 발생할 수 있는 특이사항에 대해 자사 품질 개런티 불가.\n\n4. 낙하 등의 외부 충격 발생 시 제품 파손 발생될 수 있으므로 제품 운송(택배) 및 소비자 보관 시 주의 필요.\n\n5. 내용물과 직접적으로 닿는 부분의 부자재에서는 형광증백제 사용불가 (*자재 입고검사에서 형광증백제 검출 시 반출사유)\n=>유통화장품 안전관리 기준에 근거하여 ,형광증백제는 화장품에 사용할 수 없는 원료이며 보관과정 중 포장재로부터 이염되면 안됨.",
            "상용성 특이사항": "1. 토출 관련 \n=>박킹 토출구 내경 2.4파이로 토출감 양호.\n=>버진씰 개봉 시 내압으로 인해 내용물이 소량 튈 수 있음.\n=>내용물 제조 로트 편차, 보관 조건, 소비자 사용 방법에 따라 토출량, 토출감도, 발림성 차이 발생할 수 있음.\n\n2. 기밀 유지를 위해 정립 상태로 제품 이동 및 보관 요망.",
            "생산관련": "1. 토크 관련\n   잠금 토크 약 23.14kgf / 풀림 토크 약 21.19kgf",
            "기타": "특이사항 없음."
        }
    )

@app.post("/api/document", response_model=DocumentResponse)
async def document(request: DocumentRequest):
    return DocumentResponse(
        file_name="[브로우-스크류캡,버진씰]10228 (CKR) 로얄 프레쉬 수딩 토너-V1-CT연구팀-20220513_refined.json",
        test_no="내곡2205-10228●",
        product_name="로얄 프레쉬 수딩 토너",
        customer="CKR",
        developer="이승재",
        requester="이주홍",
        test_count="2차(네크규격조정)",
        test_quantity="10ea",
        test_date="2022.05.13",
        expected_date="2022.06.13",
        writer="유태준",
        reviewer="최형",
        approver="강수진",
        packing_info=[
            PackingInfo(type="용기", material="PET", spec="인젝션 브로우 / 내경 : 17.8Φ", company="우성"),
            PackingInfo(type="박킹", material="PE", spec="버진씰타입/ 토출구 2.4Φ / 외경 : 18.5Φ", company="우성")
        ],
        lab_id="GB1915-DAI",
        lab_info="초록색 무점도 액상\n비중 1.002 - 1.017",
        experiment_info=[
            ExperimentInfo(code="TMM005", item="내내압", period="1일", check="-", standard="원형 10Kg/㎠, 타원 8Kg/㎠, 사각 5Kg/㎠", result="-"),
            ExperimentInfo(code="TMM306", item="분사각", period="1일", check="-", standard="분사각 35도 이하: 좁음(Narrow)\n분사각 45도 ± 10도: 보통(Normal)\n분사각 55도 이상: 넓음(Wide)", result="-")
        ],
        special_notes={
            "포장재 특이사항": "1. 기밀 관련 \n=>물로 진공감압테스트 시 기밀 양호하나, 용기 네크 및 캡 나사선 규격 관리 철저 요망.\n=>횡도누액테스트 결과 확인 후 진행 요망.\n\n2. 포장재 규격 관리 철저 요망.\n 1) 용기 바닥 및 배두께 규격 관리 철저 요망.\n 2) 용기 네크 늘어짐 관리 철저 요망.\n   → 미관리 시 적정용량 충전 불가.\n 3) 용기, 캡 체결 시 미세 공차 및 편심, 기울어짐 현상 발생.\n\n3. 불투명 용기사용\n=>투명 용기 사용 시 공기층 및 기포 보일 수 있으며, 일광,형광에 노출되어 내용물 변색, 변취 등 장기 안정성에 취약할 수 있음.\n=>충전 후 발생되는 상단 빈공간(헤드 스페이스) 마스킹 필요.\n=>포장재 생산 시 정전기로 인하여 이물이 용기안쪽에 흡착되어 내용물 충전 후 미세하게 보일 수 있음.\n=>투명 용기 사용 시 발생할 수 있는 특이사항에 대해 자사 품질 개런티 불가.\n\n4. 낙하 등의 외부 충격 발생 시 제품 파손 발생될 수 있으므로 제품 운송(택배) 및 소비자 보관 시 주의 필요.\n\n5. 내용물과 직접적으로 닿는 부분의 부자재에서는 형광증백제 사용불가 (*자재 입고검사에서 형광증백제 검출 시 반출사유)\n=>유통화장품 안전관리 기준에 근거하여 ,형광증백제는 화장품에 사용할 수 없는 원료이며 보관과정 중 포장재로부터 이염되면 안됨.",
            "상용성 특이사항": "1. 토출 관련 \n=>박킹 토출구 내경 2.4파이로 토출감 양호.\n=>버진씰 개봉 시 내압으로 인해 내용물이 소량 튈 수 있음.\n=>내용물 제조 로트 편차, 보관 조건, 소비자 사용 방법에 따라 토출량, 토출감도, 발림성 차이 발생할 수 있음.\n\n2. 기밀 유지를 위해 정립 상태로 제품 이동 및 보관 요망.",
            "생산관련": "1. 토크 관련\n   잠금 토크 약 23.14kgf / 풀림 토크 약 21.19kgf",
            "기타": "특이사항 없음."
        }
    )

@app.post("/api/download", response_model=DownloadResponse)
async def download(request: DownloadRequest):
    return DownloadResponse(
        downloadUrl="https://example.com/downloads/DOC20250723003.xlsx",
        fileName="CT20240001_성적서_20250723.xlsx",
        status="ready"
    ) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
