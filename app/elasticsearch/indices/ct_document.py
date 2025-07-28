from elasticsearch import Elasticsearch

def create_ct_document_index_with_mapping(es: Elasticsearch, index_name: str):
    """CT 문서 검색을 위한 인덱스 생성 및 매핑 설정"""
    mapping = {
        "mappings": {
            "properties": {
                # 기본 정보
                "document_id": {"type": "keyword"},
                "file_name": {"type": "text", "analyzer": "korean_analyzer"},
                "test_no": {"type": "keyword"},
                "product_name": {"type": "text", "analyzer": "korean_analyzer"},
                "customer": {"type": "keyword"},
                "developer": {"type": "keyword"},
                "requester": {"type": "keyword"},
                "test_count": {"type": "keyword"},
                "test_quantity": {"type": "keyword"},
                "test_date": {"type": "date"},
                "expected_date": {"type": "date"},
                "writer": {"type": "keyword"},
                "reviewer": {"type": "keyword"},
                "approver": {"type": "keyword"},

                "optimum_capacity": {"type": "text", "analyzer": "korean_analyzer"},
                "summary": {"type": "text", "analyzer": "korean_analyzer"},
                "download_url": {"type": "keyword"},
                
                # 실험실 정보
                "lab_id": {"type": "keyword"},
                "lab_info": {"type": "text", "analyzer": "korean_analyzer"},
                
                # 포장 정보 (nested object)
                "packing_info": {
                    "type": "nested",
                    "properties": {
                        "type": {"type": "text", "analyzer": "korean_analyzer"},
                        "material": {"type": "keyword"},
                        "spec": {"type": "text", "analyzer": "korean_analyzer"},
                        "company": {"type": "text", "analyzer": "korean_analyzer"}
                    }
                },
                
                # 실험 정보 (nested object)
                "experiment_info": {
                    "type": "nested",
                    "properties": {
                        "code": {"type": "keyword"},
                        "item": {"type": "text", "analyzer": "korean_analyzer"},
                        "period": {"type": "keyword"},
                        "check": {"type": "keyword"},
                        "standard": {"type": "text", "analyzer": "korean_analyzer"},
                        "result": {"type": "text", "analyzer": "korean_analyzer"}
                    }
                },
                
                # 특별 참고사항 (nested object)
                "special_notes": {
                    "type": "nested",
                    "properties": {
                        "key": {"type": "text", "analyzer": "korean_analyzer"},
                        "value": {"type": "text", "analyzer": "korean_analyzer"}
                    }
                },
                
                # 검색을 위한 통합 텍스트 필드
                "search_text": {"type": "text", "analyzer": "korean_analyzer"},
                
                # 메타데이터
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "tags": {"type": "keyword"},
                "status": {"type": "keyword"}
            }
        },
        "settings": {
            "analysis": {
                "analyzer": {
                    "korean_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "stop"]
                    }
                }
            }
        }
    }
    
    try:
        # 인덱스가 존재하면 삭제
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        
        # 새 인덱스 생성
        es.indices.create(index=index_name, body=mapping)
        print(f"CT 문서 인덱스 '{index_name}' 생성 완료")
        return True
    except Exception as e:
        print(f"인덱스 생성 오류: {str(e)}")
        return False