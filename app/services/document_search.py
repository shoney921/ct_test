from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import json
import warnings
import urllib3
from typing import List, Dict, Any, Optional

# SSL 경고 억제
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# .env 파일에서 환경변수 로드
load_dotenv()

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")

# 엘라스틱서치 클라이언트 생성 (ID/PW 인증)
es = Elasticsearch(
    ELASTICSEARCH_HOST,
    basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    verify_certs=False,
    ssl_show_warn=False  # SSL 경고 억제
)

def create_ct_document_index_with_mapping(index_name: str):
    """CT 문서 검색을 위한 인덱스 생성 및 매핑 설정"""
    mapping = {
        "mappings": {
            "properties": {
                # 기본 정보
                "file_name": {"type": "text", "analyzer": "standard"},
                "test_no": {"type": "keyword"},
                "product_name": {"type": "text", "analyzer": "standard"},
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
                
                # 실험실 정보
                "lab_id": {"type": "keyword"},
                "lab_info": {"type": "text", "analyzer": "standard"},
                
                # 포장 정보 (nested object)
                "packing_info": {
                    "type": "nested",
                    "properties": {
                        "type": {"type": "keyword"},
                        "material": {"type": "keyword"},
                        "spec": {"type": "text", "analyzer": "standard"},
                        "company": {"type": "keyword"}
                    }
                },
                
                # 실험 정보 (nested object)
                "experiment_info": {
                    "type": "nested",
                    "properties": {
                        "code": {"type": "keyword"},
                        "item": {"type": "text", "analyzer": "standard"},
                        "period": {"type": "keyword"},
                        "check": {"type": "keyword"},
                        "standard": {"type": "text", "analyzer": "standard"},
                        "result": {"type": "text", "analyzer": "standard"}
                    }
                },
                
                # 특별 참고사항 (nested object)
                "special_notes": {
                    "type": "nested",
                    "properties": {
                        "General": {"type": "text", "analyzer": "standard"},
                        "Package": {"type": "text", "analyzer": "standard"},
                        "Bulk": {"type": "text", "analyzer": "standard"},
                        "Productivity": {"type": "text", "analyzer": "standard"}
                    }
                },
                
                # 검색을 위한 통합 텍스트 필드
                "search_text": {"type": "text", "analyzer": "standard"},
                
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

def process_ct_document_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """CT 문서 데이터를 엘라스틱서치에 적합한 형태로 전처리"""
    processed_data = raw_data.copy()
    
    # 검색을 위한 통합 텍스트 필드 생성
    search_text_parts = []
    
    # 기본 정보 추가
    if raw_data.get('product_name'):
        search_text_parts.append(raw_data['product_name'])
    if raw_data.get('customer'):
        search_text_parts.append(raw_data['customer'])
    if raw_data.get('lab_info'):
        search_text_parts.append(raw_data['lab_info'])
    
    # 실험 정보에서 검색 가능한 텍스트 추출
    if raw_data.get('experiment_info'):
        for exp in raw_data['experiment_info']:
            if exp.get('item'):
                search_text_parts.append(exp['item'])
            if exp.get('standard'):
                search_text_parts.append(exp['standard'])
            if exp.get('result'):
                search_text_parts.append(exp['result'])
    
    # 특별 참고사항 추가
    if raw_data.get('special_notes'):
        for key, value in raw_data['special_notes'].items():
            if value:
                search_text_parts.append(value)
    
    # 포장 정보 추가
    if raw_data.get('packing_info'):
        for pack in raw_data['packing_info']:
            if pack.get('type'):
                search_text_parts.append(pack['type'])
            if pack.get('material'):
                search_text_parts.append(pack['material'])
            if pack.get('spec'):
                search_text_parts.append(pack['spec'])
    
    # 통합 검색 텍스트 생성
    processed_data['search_text'] = ' '.join(search_text_parts)
    
    # 메타데이터 추가
    from datetime import datetime
    processed_data['created_at'] = datetime.now().isoformat()
    processed_data['updated_at'] = datetime.now().isoformat()
    
    # 태그 생성
    tags = []
    if raw_data.get('customer'):
        tags.append(f"customer:{raw_data['customer']}")
    if raw_data.get('test_count'):
        tags.append(f"test_count:{raw_data['test_count']}")
    if raw_data.get('developer'):
        tags.append(f"developer:{raw_data['developer']}")
    
    processed_data['tags'] = tags
    
    return processed_data

def insert_ct_document(index_name: str, document_id: str, document_data: Dict[str, Any]):
    """CT 문서를 인덱스에 삽입"""
    try:
        processed_data = process_ct_document_data(document_data)
        es.index(index=index_name, id=document_id, document=processed_data)
        print(f"문서 {document_id} 삽입 완료: {document_data.get('product_name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"문서 {document_id} 삽입 오류: {str(e)}")
        return False

def bulk_insert_ct_documents(index_name: str, documents: List[Dict[str, Any]]):
    """여러 CT 문서를 일괄 삽입"""
    success_count = 0
    error_count = 0
    
    for doc in documents:
        document_id = doc.get('test_no', f"doc_{success_count + error_count}")
        if insert_ct_document(index_name, document_id, doc):
            success_count += 1
        else:
            error_count += 1
    
    # 인덱스 새로고침
    es.indices.refresh(index=index_name)
    print(f"일괄 삽입 완료: 성공 {success_count}개, 실패 {error_count}개")
    return success_count, error_count

def search_ct_documents_by_product_name(index_name: str, product_name: str):
    """제품명으로 CT 문서 검색"""
    query = {
        "query": {
            "match": {
                "product_name": {
                    "query": product_name,
                    "operator": "or"
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"제품명 검색 오류: {str(e)}")
        return None

def search_ct_documents_by_customer(index_name: str, customer: str):
    """고객사로 CT 문서 검색"""
    query = {
        "query": {
            "term": {
                "customer": customer
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"고객사 검색 오류: {str(e)}")
        return None

def search_ct_documents_by_test_code(index_name: str, test_code: str):
    """테스트 코드로 CT 문서 검색"""
    query = {
        "query": {
            "nested": {
                "path": "experiment_info",
                "query": {
                    "term": {
                        "experiment_info.code": test_code
                    }
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"테스트 코드 검색 오류: {str(e)}")
        return None

def search_ct_documents_by_material(index_name: str, material: str):
    """포장 재질로 CT 문서 검색"""
    query = {
        "query": {
            "nested": {
                "path": "packing_info",
                "query": {
                    "match": {
                        "packing_info.material": material
                    }
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"재질 검색 오류: {str(e)}")
        return None

def search_ct_documents_by_date_range(index_name: str, start_date: str, end_date: str):
    """날짜 범위로 CT 문서 검색"""
    query = {
        "query": {
            "range": {
                "test_date": {
                    "gte": start_date,
                    "lte": end_date
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"날짜 범위 검색 오류: {str(e)}")
        return None

def full_text_search_ct_documents(index_name: str, search_text: str):
    """전체 텍스트 검색"""
    query = {
        "query": {
            "multi_match": {
                "query": search_text,
                "fields": [
                    "product_name^3",
                    "search_text^2", 
                    "lab_info^1.5",
                    "special_notes.*^1"
                ],
                "type": "best_fields",
                "fuzziness": "AUTO"
            }
        },
        "highlight": {
            "fields": {
                "product_name": {},
                "search_text": {
                    "fragment_size": 150,
                    "number_of_fragments": 3
                },
                "lab_info": {
                    "fragment_size": 100,
                    "number_of_fragments": 2
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"전체 텍스트 검색 오류: {str(e)}")
        return None

def advanced_search_ct_documents(index_name: str, search_params: Dict[str, Any]):
    """고급 검색 (다중 조건)"""
    must_conditions = []
    filter_conditions = []
    
    # 제품명 검색
    if search_params.get('product_name'):
        must_conditions.append({
            "match": {
                "product_name": {
                    "query": search_params['product_name'],
                    "operator": "or"
                }
            }
        })
    
    # 고객사 필터
    if search_params.get('customer'):
        filter_conditions.append({
            "term": {"customer": search_params['customer']}
        })
    
    # 테스트 코드 검색
    if search_params.get('test_code'):
        must_conditions.append({
            "nested": {
                "path": "experiment_info",
                "query": {
                    "term": {"experiment_info.code": search_params['test_code']}
                }
            }
        })
    
    # 재질 검색
    if search_params.get('material'):
        must_conditions.append({
            "nested": {
                "path": "packing_info",
                "query": {
                    "match": {"packing_info.material": search_params['material']}
                }
            }
        })
    
    # 날짜 범위 필터
    if search_params.get('start_date') or search_params.get('end_date'):
        date_range = {}
        if search_params.get('start_date'):
            date_range['gte'] = search_params['start_date']
        if search_params.get('end_date'):
            date_range['lte'] = search_params['end_date']
        
        filter_conditions.append({
            "range": {"test_date": date_range}
        })
    
    # 전체 텍스트 검색
    if search_params.get('search_text'):
        must_conditions.append({
            "multi_match": {
                "query": search_params['search_text'],
                "fields": ["search_text^2", "lab_info", "special_notes.*"],
                "type": "best_fields"
            }
        })
    
    query = {
        "query": {
            "bool": {
                "must": must_conditions,
                "filter": filter_conditions
            }
        },
        "highlight": {
            "fields": {
                "product_name": {},
                "search_text": {
                    "fragment_size": 150,
                    "number_of_fragments": 3
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"고급 검색 오류: {str(e)}")
        return None

def get_ct_document_statistics(index_name: str):
    """CT 문서 통계 정보 조회"""
    query = {
        "size": 0,
        "aggs": {
            "customer_count": {
                "terms": {"field": "customer", "size": 20}
            },
            "test_count_distribution": {
                "terms": {"field": "test_count"}
            },
            "date_distribution": {
                "date_histogram": {
                    "field": "test_date",
                    "calendar_interval": "month"
                }
            },
            "material_distribution": {
                "nested": {
                    "path": "packing_info"
                },
                "aggs": {
                    "materials": {
                        "terms": {"field": "packing_info.material"}
                    }
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"통계 조회 오류: {str(e)}")
        return None

def print_ct_search_results(response, search_type: str):
    """CT 문서 검색 결과 출력"""
    if not response:
        print(f"{search_type} 검색 결과 없음")
        return
    
    print(f"\n=== {search_type} 검색 결과 ===")
    print(f"총 검색 결과: {response['hits']['total']['value']}개")
    
    for hit in response['hits']['hits']:
        source = hit['_source']
        score = hit['_score']
        print(f"\n문서 ID: {hit['_id']} (점수: {score:.2f})")
        print(f"테스트 번호: {source.get('test_no', 'N/A')}")
        print(f"제품명: {source.get('product_name', 'N/A')}")
        print(f"고객사: {source.get('customer', 'N/A')}")
        print(f"개발자: {source.get('developer', 'N/A')}")
        print(f"테스트 날짜: {source.get('test_date', 'N/A')}")
        print(f"실험실 ID: {source.get('lab_id', 'N/A')}")
        
        # 하이라이트 결과 출력
        if 'highlight' in hit:
            print("🔍 하이라이트된 매칭 부분:")
            for field, highlights in hit['highlight'].items():
                print(f"  📝 {field}: {' ... '.join(highlights)}")
        
        print("-" * 80)

def print_ct_statistics(response):
    """CT 문서 통계 결과 출력"""
    if not response:
        print("통계 결과 없음")
        return
    
    print(f"\n=== CT 문서 통계 ===")
    
    aggs = response['aggregations']
    
    if 'customer_count' in aggs:
        print("\n고객사별 문서 수:")
        for bucket in aggs['customer_count']['buckets']:
            print(f"  {bucket['key']}: {bucket['doc_count']}개")
    
    if 'test_count_distribution' in aggs:
        print("\n테스트 차수별 분포:")
        for bucket in aggs['test_count_distribution']['buckets']:
            print(f"  {bucket['key']}: {bucket['doc_count']}개")
    
    if 'date_distribution' in aggs:
        print("\n월별 문서 분포:")
        for bucket in aggs['date_distribution']['buckets']:
            print(f"  {bucket['key_as_string']}: {bucket['doc_count']}개")

def load_json_files_from_directory(directory_path: str) -> List[Dict[str, Any]]:
    """디렉토리에서 JSON 파일들을 로드"""
    import glob
    import os
    
    documents = []
    json_files = glob.glob(os.path.join(directory_path, "*.json"))
    
    print(f"발견된 JSON 파일 수: {len(json_files)}")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                documents.append(data)
                print(f"로드 완료: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"파일 로드 오류 {file_path}: {str(e)}")
    
    return documents

def load_and_index_ct_documents(index_name: str, directory_path: str):
    """JSON 파일들을 로드하고 인덱스에 삽입"""
    print(f"디렉토리에서 JSON 파일 로드 중: {directory_path}")
    documents = load_json_files_from_directory(directory_path)
    
    if not documents:
        print("로드할 JSON 파일이 없습니다.")
        return 0, 0
    
    print(f"총 {len(documents)}개의 문서를 인덱스에 삽입 중...")
    success_count, error_count = bulk_insert_ct_documents(index_name, documents)
    
    return success_count, error_count

if __name__ == "__main__":
    index_name = "ct_documents"
    
    print("=== CT 문서 검색 시스템 테스트 ===\n")
    
    # 1. 인덱스 생성
    print("1. CT 문서 인덱스 생성 중...")
    if create_ct_document_index_with_mapping(index_name):
        print("CT 문서 인덱스 생성 완료!")
        
        # 2. JSON 파일들 로드 및 인덱싱
        print("\n2. JSON 파일 로드 및 인덱싱 중...")
        refine_directory = "data/refine"
        success_count, error_count = load_and_index_ct_documents(index_name, refine_directory)
        
        if success_count > 0:
            print(f"\n인덱싱 완료: 성공 {success_count}개, 실패 {error_count}개")
            
            # 3. 검색 테스트
            print("\n3. 검색 기능 테스트 시작...")
            
            # 제품명 검색 테스트
            print("\n--- 제품명 검색 테스트 ---")
            result = search_ct_documents_by_product_name(index_name, "Lip")
            print_ct_search_results(result, "Lip 제품 검색")
            
            # 고객사 검색 테스트
            print("\n--- 고객사 검색 테스트 ---")
            result = search_ct_documents_by_customer(index_name, "Interstory")
            print_ct_search_results(result, "Interstory 고객사 검색")
            
            # 전체 텍스트 검색 테스트
            print("\n--- 전체 텍스트 검색 테스트 ---")
            result = full_text_search_ct_documents(index_name, "펌핑 테스트")
            print_ct_search_results(result, "펌핑 테스트 검색")
            
            # 재질 검색 테스트
            print("\n--- 재질 검색 테스트 ---")
            result = search_ct_documents_by_material(index_name, "AS")
            print_ct_search_results(result, "AS 재질 검색")
            
            # 테스트 코드 검색 테스트
            print("\n--- 테스트 코드 검색 테스트 ---")
            result = search_ct_documents_by_test_code(index_name, "TMM202")
            print_ct_search_results(result, "TMM202 테스트 코드 검색")
            
            # 고급 검색 테스트
            print("\n--- 고급 검색 테스트 ---")
            search_params = {
                "product_name": "Lip",
                "customer": "Interstory",
                "search_text": "펌핑"
            }
            result = advanced_search_ct_documents(index_name, search_params)
            print_ct_search_results(result, "고급 검색 (Lip + Interstory + 펌핑)")
            
            # 통계 조회 테스트
            print("\n--- 통계 조회 테스트 ---")
            stats_result = get_ct_document_statistics(index_name)
            print_ct_statistics(stats_result)
            
        else:
            print("인덱싱에 실패했습니다.")
    else:
        print("CT 문서 인덱스 생성 실패!")
