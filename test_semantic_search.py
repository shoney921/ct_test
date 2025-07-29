from app.services.search_service import get_ct_document_semantic_only, get_ct_document_hybrid_search
from app.services.ct_document_search import semantic_search_special_notes, hybrid_search_special_notes
from app.elasticsearch.client import get_es_client
from app.elasticsearch.indices.ct_document import create_ct_document_index_with_mapping

def test_semantic_search():
    """의미기반 검색 테스트"""
    print("=== 의미기반 검색 테스트 시작 ===\n")
    
    # 인덱스 생성 (필요시)
    es = get_es_client()
    create_ct_document_index_with_mapping(es, "ct_documents")
    
    # 테스트 쿼리들
    test_queries = [
        "낙하 실패",
        "물광 현상",
        "누출 문제",
        "포장 불량",
        "압력 테스트",
        "온도 변화",
        "습도 영향",
        "충격 테스트",
        "진공 감압",
        "펌핑 테스트"
    ]
    
    print("1. 순수 의미기반 검색 테스트")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n🔍 쿼리: '{query}'")
        try:
            result = get_ct_document_semantic_only(query, threshold=0.6, top_k=5)
            if not result:
                print("   결과 없음")
        except Exception as e:
            print(f"   오류: {str(e)}")
    
    print("\n\n2. 하이브리드 검색 테스트")
    print("=" * 50)
    
    for query in test_queries[:3]:  # 처음 3개만 테스트
        print(f"\n🔍 쿼리: '{query}'")
        try:
            result = get_ct_document_hybrid_search(query, text_boost=1.0, semantic_boost=2.0, threshold=0.6)
            if not result:
                print("   결과 없음")
        except Exception as e:
            print(f"   오류: {str(e)}")

def test_embedding_service():
    """임베딩 서비스 테스트"""
    from app.services.embedding_service import embedding_service
    
    print("\n=== 임베딩 서비스 테스트 ===")
    
    test_texts = [
        "낙하 실패",
        "물광 현상 발생",
        "포장재 누출 문제",
        "압력 테스트 통과"
    ]
    
    for text in test_texts:
        print(f"\n텍스트: '{text}'")
        embedding = embedding_service.get_embedding(text)
        if embedding:
            print(f"임베딩 차원: {len(embedding)}")
            print(f"임베딩 샘플: {embedding[:5]}...")
        else:
            print("임베딩 생성 실패")

if __name__ == "__main__":
    # 임베딩 서비스 테스트
    test_embedding_service()
    
    # 의미기반 검색 테스트
    test_semantic_search() 