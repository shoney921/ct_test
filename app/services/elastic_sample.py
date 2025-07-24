from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import json
import warnings
import urllib3

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

def create_index_with_mapping(index_name: str):
    """인덱스 생성 및 매핑 설정"""
    mapping = {
        "mappings": {
            "properties": {
                "name": {"type": "text", "analyzer": "standard"},
                "age": {"type": "integer"},
                "email": {"type": "keyword"},
                "department": {"type": "keyword"},
                "salary": {"type": "float"},
                "skills": {"type": "text", "analyzer": "standard"},
                "description": {"type": "text", "analyzer": "standard"},  # korean -> standard로 변경
                "location": {"type": "geo_point"},
                "created_at": {"type": "date"},
                "tags": {"type": "keyword"},
                "rating": {"type": "float"}
            }
        }
    }
    
    try:
        # 인덱스가 존재하면 삭제
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        
        # 새 인덱스 생성
        es.indices.create(index=index_name, body=mapping)
        print(f"인덱스 '{index_name}' 생성 완료")
        return True
    except Exception as e:
        print(f"인덱스 생성 오류: {str(e)}")
        return False

def insert_sample_data(index_name: str):
    """다양한 샘플 데이터 삽입"""
    sample_data = [
        {
            "id": "1",
            "name": "김개발",
            "age": 28,
            "email": "kim@company.com",
            "department": "개발팀",
            "salary": 45000.0,
            "skills": "Python Java JavaScript 개발",
            "description": "풀스택 개발자로 웹 애플리케이션 개발에 전문성을 가지고 있습니다. 개발 경험 5년",
            "location": {"lat": 37.5665, "lon": 126.9780},  # 서울
            "created_at": "2024-01-15T10:00:00",
            "tags": ["senior", "fullstack", "python", "개발"],
            "rating": 4.5
        },
        {
            "id": "2", 
            "name": "이디자인",
            "age": 32,
            "email": "lee@company.com",
            "department": "디자인팀",
            "salary": 52000.0,
            "skills": "Photoshop Illustrator Figma 디자인",
            "description": "UI/UX 디자이너로 사용자 경험을 중시하는 디자인을 만듭니다. 디자인 경험 8년",
            "location": {"lat": 37.5665, "lon": 126.9780},  # 서울
            "created_at": "2024-01-20T14:30:00",
            "tags": ["senior", "design", "ui", "디자인"],
            "rating": 4.8
        },
        {
            "id": "3",
            "name": "박프론트",
            "age": 25,
            "email": "park@company.com", 
            "department": "개발팀",
            "salary": 35000.0,
            "skills": "React Node.js MongoDB 개발",
            "description": "주니어 개발자로 프론트엔드 개발에 열정을 가지고 있습니다. 개발 학습 중",
            "location": {"lat": 35.1796, "lon": 129.0756},  # 부산
            "created_at": "2024-02-01T09:15:00",
            "tags": ["junior", "frontend", "react", "개발"],
            "rating": 3.9
        },
        {
            "id": "4",
            "name": "정마케팅",
            "age": 29,
            "email": "jung@company.com",
            "department": "마케팅팀", 
            "salary": 48000.0,
            "skills": "SEO Google Analytics Facebook Ads 마케팅",
            "description": "디지털 마케팅 전문가로 온라인 마케팅 전략을 수립합니다. 마케팅 경험 6년",
            "location": {"lat": 37.5665, "lon": 126.9780},  # 서울
            "created_at": "2024-02-10T16:45:00",
            "tags": ["senior", "marketing", "digital", "마케팅"],
            "rating": 4.2
        },
        {
            "id": "5",
            "name": "최백엔드",
            "age": 35,
            "email": "choi@company.com",
            "department": "개발팀",
            "salary": 65000.0,
            "skills": "Python Django PostgreSQL Docker",
            "description": "백엔드 개발자로 안정적이고 확장 가능한 시스템을 구축합니다. 개발 경험 10년",
            "location": {"lat": 35.8714, "lon": 128.6014},  # 대구
            "created_at": "2024-02-15T11:20:00",
            "tags": ["senior", "backend", "python", "개발"],
            "rating": 4.7
        },
        {
            "id": "6",
            "name": "한테스트",
            "age": 27,
            "email": "han@company.com",
            "department": "개발팀",
            "salary": 38000.0,
            "skills": "JUnit Selenium TestNG 테스트",
            "description": "QA 엔지니어로 소프트웨어 테스트와 품질 보증을 담당합니다. 테스트 자동화 전문",
            "location": {"lat": 37.5665, "lon": 126.9780},  # 서울
            "created_at": "2024-02-20T13:00:00",
            "tags": ["junior", "qa", "testing", "테스트"],
            "rating": 4.0
        },
        {
            "id": "7",
            "name": "윤데이터",
            "age": 31,
            "email": "yoon@company.com",
            "department": "데이터팀",
            "salary": 55000.0,
            "skills": "Python R SQL 데이터분석",
            "description": "데이터 분석가로 비즈니스 인사이트를 도출합니다. 데이터 분석 경험 7년",
            "location": {"lat": 37.5665, "lon": 126.9780},  # 서울
            "created_at": "2024-02-25T15:30:00",
            "tags": ["senior", "data", "analysis", "데이터"],
            "rating": 4.6
        }
    ]
    
    for data in sample_data:
        try:
            es.index(index=index_name, id=data["id"], document=data)
            print(f"문서 {data['id']} 삽입 완료: {data['name']}")
        except Exception as e:
            print(f"문서 {data['id']} 삽입 오류: {str(e)}")
    
    # 인덱스 새로고침
    es.indices.refresh(index=index_name)
    print("샘플 데이터 삽입 완료!")

def keyword_search(index_name: str, field: str, value: str):
    """키워드 검색 (정확한 값 매칭)"""
    query = {
        "query": {
            "term": {
                field: value
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"키워드 검색 오류: {str(e)}")
        return None

def text_search(index_name: str, field: str, text: str):
    """텍스트 검색 (부분 매칭)"""
    query = {
        "query": {
            "match": {
                field: text
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"텍스트 검색 오류: {str(e)}")
        return None

def multi_field_search(index_name: str, text: str):
    """다중 필드 검색"""
    query = {
        "query": {
            "multi_match": {
                "query": text,
                "fields": ["name", "skills", "description"],
                "type": "best_fields"
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"다중 필드 검색 오류: {str(e)}")
        return None

def range_search(index_name: str, field: str, min_value=None, max_value=None):
    """범위 검색"""
    range_query = {}
    if min_value is not None:
        range_query["gte"] = min_value
    if max_value is not None:
        range_query["lte"] = max_value
    
    query = {
        "query": {
            "range": {
                field: range_query
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"범위 검색 오류: {str(e)}")
        return None

def geo_search(index_name: str, lat: float, lon: float, distance: str = "10km"):
    """지리적 위치 검색"""
    query = {
        "query": {
            "geo_distance": {
                "distance": distance,
                "location": {
                    "lat": lat,
                    "lon": lon
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"지리 검색 오류: {str(e)}")
        return None

def aggregation_search(index_name: str):
    """집계 검색 (통계)"""
    query = {
        "size": 0,  # 문서는 반환하지 않고 집계만
        "aggs": {
            "avg_salary": {
                "avg": {"field": "salary"}
            },
            "avg_age": {
                "avg": {"field": "age"}
            },
            "department_count": {
                "terms": {"field": "department"}
            },
            "age_ranges": {
                "range": {
                    "field": "age",
                    "ranges": [
                        {"to": 25},
                        {"from": 25, "to": 30},
                        {"from": 30, "to": 35},
                        {"from": 35}
                    ]
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"집계 검색 오류: {str(e)}")
        return None

def fuzzy_search(index_name: str, field: str, text: str):
    """퍼지 검색 (오타 허용)"""
    query = {
        "query": {
            "fuzzy": {
                field: {
                    "value": text,
                    "fuzziness": "AUTO"
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"퍼지 검색 오류: {str(e)}")
        return None

def wildcard_search(index_name: str, field: str, pattern: str):
    """와일드카드 검색"""
    query = {
        "query": {
            "wildcard": {
                field: pattern
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"와일드카드 검색 오류: {str(e)}")
        return None

def print_search_results(response, search_type: str):
    """검색 결과 출력"""
    if not response:
        print(f"{search_type} 검색 결과 없음")
        return
    
    print(f"\n=== {search_type} 검색 결과 ===")
    print(f"총 검색 결과: {response['hits']['total']['value']}개")
    
    for hit in response['hits']['hits']:
        source = hit['_source']
        score = hit['_score']
        print(f"\n문서 ID: {hit['_id']} (점수: {score})")
        print(f"이름: {source.get('name', 'N/A')}")
        print(f"부서: {source.get('department', 'N/A')}")
        print(f"나이: {source.get('age', 'N/A')}")
        print(f"급여: {source.get('salary', 'N/A')}")
        print(f"기술: {source.get('skills', 'N/A')}")

def print_aggregation_results(response, search_type: str):
    """집계 결과 출력"""
    if not response:
        print(f"{search_type} 집계 결과 없음")
        return
    
    print(f"\n=== {search_type} 집계 결과 ===")
    
    aggs = response['aggregations']
    
    if 'avg_salary' in aggs:
        print(f"평균 급여: {aggs['avg_salary']['value']:.2f}")
    
    if 'avg_age' in aggs:
        print(f"평균 나이: {aggs['avg_age']['value']:.2f}")
    
    if 'department_count' in aggs:
        print("\n부서별 인원:")
        for bucket in aggs['department_count']['buckets']:
            print(f"  {bucket['key']}: {bucket['doc_count']}명")
    
    if 'age_ranges' in aggs:
        print("\n나이대별 분포:")
        for bucket in aggs['age_ranges']['buckets']:
            print(f"  {bucket['key']}: {bucket['doc_count']}명")

if __name__ == "__main__":
    index_name = "employee_test"
    
    print("=== 엘라스틱서치 다양한 검색 기능 테스트 ===\n")
    
    # 1. 인덱스 생성
    print("1. 인덱스 생성 중...")
    if create_index_with_mapping(index_name):
        # 2. 샘플 데이터 삽입
        print("\n2. 샘플 데이터 삽입 중...")
        insert_sample_data(index_name)
        
        # 3. 다양한 검색 테스트
        print("\n3. 다양한 검색 테스트 시작...")
        
        # 키워드 검색 (정확한 값)
        print("\n--- 키워드 검색 테스트 ---")
        result = keyword_search(index_name, "department", "개발팀")
        print_search_results(result, "개발팀 키워드 검색")
        
        # 텍스트 검색 (부분 매칭)
        print("\n--- 텍스트 검색 테스트 ---")
        result = text_search(index_name, "skills", "Python")
        print_search_results(result, "Python 기술 검색")
        
        # 다중 필드 검색
        print("\n--- 다중 필드 검색 테스트 ---")
        result = multi_field_search(index_name, "개발")
        print_search_results(result, "개발 관련 다중 필드 검색")
        
        result = multi_field_search(index_name, "Python")
        print_search_results(result, "Python 관련 다중 필드 검색")
        
        result = multi_field_search(index_name, "디자인")
        print_search_results(result, "디자인 관련 다중 필드 검색")
        
        # 범위 검색
        print("\n--- 범위 검색 테스트 ---")
        result = range_search(index_name, "age", 25, 30)
        print_search_results(result, "25-30세 나이 범위 검색")
        
        result = range_search(index_name, "salary", 40000)
        print_search_results(result, "급여 40,000 이상 검색")
        
        # 지리 검색
        print("\n--- 지리 검색 테스트 ---")
        result = geo_search(index_name, 37.5665, 126.9780, "50km")
        print_search_results(result, "서울 50km 반경 검색")
        
        # 집계 검색
        print("\n--- 집계 검색 테스트 ---")
        result = aggregation_search(index_name)
        print_aggregation_results(result, "전체 통계")
        
        # 퍼지 검색
        print("\n--- 퍼지 검색 테스트 ---")
        result = fuzzy_search(index_name, "name", "김철수")
        print_search_results(result, "김철수 퍼지 검색")
        
        # 와일드카드 검색
        print("\n--- 와일드카드 검색 테스트 ---")
        result = wildcard_search(index_name, "email", "*@company.com")
        print_search_results(result, "회사 이메일 와일드카드 검색")
        
    else:
        print("인덱스 생성 실패!")