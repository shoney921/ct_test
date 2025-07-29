from app.schemas.common import Document, PackingInfo
from app.services.ct_document_search import *
from app.schemas.api.search import SearchRequest

def get_ct_document(input: SearchRequest, use_semantic_search: bool = True, semantic_threshold: float = 0.7):
    # 빈 값들을 필터링하여 실제 검색 조건만 추출
    packing_spec_list = []
    for package in input.packages:
        packing_spec = {}
        if package.type and package.type.strip():
            packing_spec["type"] = package.type
        if package.material and package.material.strip():
            packing_spec["material"] = package.material
        if package.spec and package.spec.strip():
            packing_spec["spec"] = package.spec
        if package.company and package.company.strip():
            packing_spec["company"] = package.company
        
        # 최소한 하나의 조건이라도 있으면 추가
        if packing_spec:
            packing_spec_list.append(packing_spec)
    
    # TODO : 나중에 검색 조건이 없는경우 벨리데이션 조건 붙여야 할 때 붙이기
    # # 검색 조건이 없으면 빈 결과 반환 
    # if not packing_spec_list and not input.lab_id and not input.lab_info and not input.optimum_capacity:
    #     print("검색 조건이 없습니다.")
    #     return []
    
    result = search_ct_documents_by_multiple_packing_sets(
        "ct_documents", 
        packing_spec_list, 
        input.lab_id, 
        input.lab_info, 
        input.optimum_capacity, 
        input.special_note,
        use_semantic_search,
        semantic_threshold
    )
    hits = result['hits']['hits']

    documents = []
    for hit in hits:
        try:
            doc = Document(**hit['_source'])
            documents.append(doc)
        except Exception as e:
            print("에러 발생 hit:", hit)
            print("에러 메시지:", e)

    for i, document in enumerate(documents):
        print("ㅁ   ", document.file_name)
        print("    포장재정보 :", document.packing_info)
        
        # 하이라이트 정보 출력
        if i < len(hits) and 'highlight' in hits[i]:
            print("🔍 하이라이트된 매칭 부분:")
            for field, highlights in hits[i]['highlight'].items():
                print(f"  📝 {field}: {' ... '.join(highlights)}")
        
        print("-" * 80)
    return documents


def get_ct_document_by_packing_info(packing_type: str, material: str, spec: str = None, company: str = None):
    result = search_ct_documents_by_packing_info("ct_documents", packing_type, material, spec=spec, company=company)
    print(result['hits']['hits'])
    return result

def get_ct_document_by_packing_info_list(packing_spec_list: list):
    result = search_ct_documents_by_multiple_packing_sets("ct_documents", packing_spec_list)
    print(result['hits']['hits'])
    return result

def get_ct_document_semantic_only(special_note: str, threshold: float = 0.7, top_k: int = 10):
    """의미기반 검색만 사용하여 special_notes 검색"""
    result = semantic_search_special_notes("ct_documents", special_note, threshold, top_k)
    hits = result['hits']['hits']

    documents = []
    for hit in hits:
        try:
            doc = Document(**hit['_source'])
            documents.append(doc)
        except Exception as e:
            print("에러 발생 hit:", hit)
            print("에러 메시지:", e)

    print(f"\n=== 의미기반 검색 결과 (쿼리: '{special_note}') ===")
    print(f"총 검색 결과: {len(documents)}개")
    
    for i, document in enumerate(documents):
        print(f"\n문서 ID: {hits[i]['_id']} (유사도 점수: {hits[i]['_score']:.3f})")
        print("ㅁ   ", document.file_name)
        print("    포장재정보 :", document.packing_info)
        
        # 하이라이트 정보 출력
        if 'highlight' in hits[i]:
            print("🔍 하이라이트된 매칭 부분:")
            for field, highlights in hits[i]['highlight'].items():
                print(f"  📝 {field}: {' ... '.join(highlights)}")
        
        print("-" * 80)
    return documents

def get_ct_document_hybrid_search(special_note: str, text_boost: float = 1.0, semantic_boost: float = 2.0, threshold: float = 0.7):
    """하이브리드 검색 (텍스트 + 의미기반)"""
    result = hybrid_search_special_notes("ct_documents", special_note, text_boost, semantic_boost, threshold)
    hits = result['hits']['hits']

    documents = []
    for hit in hits:
        try:
            doc = Document(**hit['_source'])
            documents.append(doc)
        except Exception as e:
            print("에러 발생 hit:", hit)
            print("에러 메시지:", e)

    print(f"\n=== 하이브리드 검색 결과 (쿼리: '{special_note}') ===")
    print(f"총 검색 결과: {len(documents)}개")
    
    for i, document in enumerate(documents):
        print(f"\n문서 ID: {hits[i]['_id']} (점수: {hits[i]['_score']:.3f})")
        print("ㅁ   ", document.file_name)
        print("    포장재정보 :", document.packing_info)
        
        # 하이라이트 정보 출력
        if 'highlight' in hits[i]:
            print("🔍 하이라이트된 매칭 부분:")
            for field, highlights in hits[i]['highlight'].items():
                print(f"  📝 {field}: {' ... '.join(highlights)}")
        
        print("-" * 80)
    return documents

if __name__ == "__main__":
    index_name = "ct_documents"
    
    print("=== CT 문서 검색 시스템 테스트 ===\n")
    
    # # 의미기반 검색 테스트
    # print("1. 의미기반 검색 테스트")
    # print("=" * 50)
    
    # test_queries = [
    #     "낙하 실패",
    #     "물광 현상",
    #     "누출 문제",
    #     "포장 불량"
    # ]
    
    # for query in test_queries:
    #     print(f"\n🔍 쿼리: '{query}'")
    #     try:
    #         result = get_ct_document_semantic_only(query, threshold=0.6, top_k=3)
    #         if not result:
    #             print("   결과 없음")
    #     except Exception as e:
    #         print(f"   오류: {str(e)}")
    
    # print("\n\n2. 하이브리드 검색 테스트")
    # print("=" * 50)
    
    # for query in test_queries[:2]:
    #     print(f"\n🔍 쿼리: '{query}'")
    #     try:
    #         result = get_ct_document_hybrid_search(query, text_boost=1.0, semantic_boost=2.0, threshold=0.6)
    #         if not result:
    #             print("   결과 없음")
    #     except Exception as e:
    #         print(f"   오류: {str(e)}")
    
    # print("\n\n3. 기존 검색 방식 테스트 (의미기반 검색 비활성화)")
    # print("=" * 50)
    
    input = SearchRequest(
        packages=[
            PackingInfo(type="", material="",spec="", company=""),
        ],
        lab_id="",
        lab_info="",
        optimum_capacity="",
        special_note="나사선 크랙 발생"
    )
    
    # 의미기반 검색 비활성화
    get_ct_document(input, use_semantic_search=False)
    
    print("\n\n4. 의미기반 검색 활성화 테스트")
    print("=" * 50)
    
    # 의미기반 검색 활성화
    get_ct_document(input, use_semantic_search=True, semantic_threshold=0.6)