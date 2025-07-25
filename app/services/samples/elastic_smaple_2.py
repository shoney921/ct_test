from app.elasticsearch.client import get_es_client

es = get_es_client()

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
                "description": {"type": "text", "analyzer": "standard"},
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
            "description": "풀스택 개발자로 웹 애플리케이션 개발에 전문성을 가지고 있습니다. 개발 경험 5년. 사용자 친화적인 인터페이스를 만들고 서버 사이드 로직을 구현하는 것을 좋아합니다.",
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
            "description": "UI/UX 디자이너로 사용자 경험을 중시하는 디자인을 만듭니다. 디자인 경험 8년. 사용자가 쉽게 사용할 수 있는 직관적인 인터페이스를 만드는 것이 전문입니다.",
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
            "description": "주니어 개발자로 프론트엔드 개발에 열정을 가지고 있습니다. 개발 학습 중. 사용자 인터페이스를 만들고 사용자 경험을 개선하는 것에 관심이 많습니다.",
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
            "description": "디지털 마케팅 전문가로 온라인 마케팅 전략을 수립합니다. 마케팅 경험 6년. 고객의 니즈를 파악하고 효과적인 마케팅 캠페인을 기획합니다.",
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
            "skills": "Python Django PostgreSQL Docker 개발",
            "description": "백엔드 개발자로 안정적이고 확장 가능한 시스템을 구축합니다. 개발 경험 10년. 서버 아키텍처 설계와 데이터베이스 최적화에 전문성을 가지고 있습니다.",
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
            "description": "QA 엔지니어로 소프트웨어 테스트와 품질 보증을 담당합니다. 테스트 자동화 전문. 버그를 찾아내고 소프트웨어의 품질을 보장하는 것이 주요 업무입니다.",
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
            "description": "데이터 분석가로 비즈니스 인사이트를 도출합니다. 데이터 분석 경험 7년. 대용량 데이터를 분석하여 비즈니스 의사결정에 도움이 되는 인사이트를 제공합니다.",
            "location": {"lat": 37.5665, "lon": 126.9780},  # 서울
            "created_at": "2024-02-25T15:30:00",
            "tags": ["senior", "data", "analysis", "데이터"],
            "rating": 4.6
        },
        {
            "id": "8",
            "name": "송고객",
            "age": 33,
            "email": "song@company.com",
            "department": "고객지원팀",
            "salary": 42000.0,
            "skills": "고객서비스 문제해결 커뮤니케이션",
            "description": "고객 지원 전문가로 고객의 문의사항을 해결하고 만족도를 높이는 업무를 담당합니다. 고객 경험 5년. 고객의 니즈를 정확히 파악하고 적절한 해결책을 제시합니다.",
            "location": {"lat": 37.5665, "lon": 126.9780},  # 서울
            "created_at": "2024-03-01T10:00:00",
            "tags": ["senior", "customer", "support", "고객지원"],
            "rating": 4.3
        },
        {
            "id": "9",
            "name": "임보안",
            "age": 36,
            "email": "lim@company.com",
            "department": "보안팀",
            "salary": 58000.0,
            "skills": "네트워크보안 암호화 보안정책",
            "description": "보안 전문가로 회사의 정보 자산을 보호하고 보안 정책을 수립합니다. 보안 경험 12년. 사이버 위협으로부터 시스템과 데이터를 안전하게 지키는 것이 주요 업무입니다.",
            "location": {"lat": 37.5665, "lon": 126.9780},  # 서울
            "created_at": "2024-03-05T14:00:00",
            "tags": ["senior", "security", "cyber", "보안"],
            "rating": 4.9
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

def semantic_search(index_name: str, text: str):
    """의미 기반 검색 (description 필드)"""
    query = {
        "query": {
            "match": {
                "description": {
                    "query": text,
                    "operator": "or",
                    "minimum_should_match": "70%"
                }
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"의미 기반 검색 오류: {str(e)}")
        return None

def phrase_search(index_name: str, field: str, phrase: str):
    """구문 검색 (정확한 구문 매칭)"""
    query = {
        "query": {
            "match_phrase": {
                field: phrase
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"구문 검색 오류: {str(e)}")
        return None

def multi_field_search(index_name: str, text: str):
    """다중 필드 검색"""
    query = {
        "query": {
            "multi_match": {
                "query": text,
                "fields": ["name", "skills", "description"],
                "type": "best_fields",
                "minimum_should_match": "70%"
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

def hybrid_search(index_name: str, text: str, boost_text=1.0, boost_semantic=2.0):
    """하이브리드 검색 (텍스트 검색 + 의미 기반 검색)"""
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": text,
                            "fields": ["name^2", "skills^1.5", "description"],
                            "type": "best_fields",
                            "boost": boost_text
                        }
                    },
                    {
                        "match": {
                            "description": {
                                "query": text,
                                "operator": "or",
                                "minimum_should_match": "60%",
                                "boost": boost_semantic
                            }
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    }
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"하이브리드 검색 오류: {str(e)}")
        return None

def advanced_hybrid_search(index_name: str, text: str, filters=None):
    """고급 하이브리드 검색 (필터링 포함)"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                {
                                    "multi_match": {
                                        "query": text,
                                        "fields": ["name^3", "skills^2", "description^1.5", "tags^1"],
                                        "type": "best_fields",
                                        "fuzziness": "AUTO"
                                    }
                                },
                                {
                                    "match": {
                                        "description": {
                                            "query": text,
                                            "operator": "or",
                                            "minimum_should_match": "50%"
                                        }
                                    }
                                }
                            ],
                            "minimum_should_match": 1
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {
                "name": {},
                "skills": {},
                "description": {
                    "fragment_size": 150,
                    "number_of_fragments": 2
                }
            }
        }
    }
    
    # 필터 추가
    if filters:
        query["query"]["bool"]["filter"] = filters
    
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"고급 하이브리드 검색 오류: {str(e)}")
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
        print(f"\n문서 ID: {hit['_id']} (점수: {score:.2f})")
        print(f"이름: {source.get('name', 'N/A')}")
        print(f"부서: {source.get('department', 'N/A')}")
        print(f"나이: {source.get('age', 'N/A')}")
        print(f"급여: {source.get('salary', 'N/A')}")
        print(f"기술: {source.get('skills', 'N/A')}")
        print(f"설명: {source.get('description', 'N/A')[:100]}...")
        
        # 하이라이트 결과 출력
        if 'highlight' in hit:
            print("하이라이트:")
            for field, highlights in hit['highlight'].items():
                print(f"  {field}: {' ... '.join(highlights)}")

def print_hybrid_search_results(response, search_type: str):
    """하이브리드 검색 결과 출력 (더 상세한 정보)"""
    if not response:
        print(f"{search_type} 검색 결과 없음")
        return
    
    print(f"\n=== {search_type} 검색 결과 ===")
    print(f"총 검색 결과: {response['hits']['total']['value']}개")
    
    for hit in response['hits']['hits']:
        source = hit['_source']
        score = hit['_score']
        print(f"\n문서 ID: {hit['_id']} (점수: {score:.2f})")
        print(f"이름: {source.get('name', 'N/A')}")
        print(f"부서: {source.get('department', 'N/A')}")
        print(f"나이: {source.get('age', 'N/A')}")
        print(f"급여: {source.get('salary', 'N/A')}")
        print(f"기술: {source.get('skills', 'N/A')}")
        print(f"설명: {source.get('description', 'N/A')[:150]}...")
        
        # 하이라이트 결과 출력
        if 'highlight' in hit:
            print("🔍 하이라이트된 매칭 부분:")
            for field, highlights in hit['highlight'].items():
                print(f"  📝 {field}: {' ... '.join(highlights)}")
        
        print("-" * 80)

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

        result = text_search(index_name, "description", "백엔드")
        print_search_results(result, "백엔드 키워드 검색")
        
        # 의미 기반 검색 (description)
        print("\n--- 의미 기반 검색 테스트 ---")
        result = semantic_search(index_name, "사용자 경험")
        print_search_results(result, "사용자 경험 관련 의미 검색")
        
        result = semantic_search(index_name, "고객 니즈")
        print_search_results(result, "고객 니즈 관련 의미 검색")
        
        result = semantic_search(index_name, "보안 보호")
        print_search_results(result, "보안 보호 관련 의미 검색")
        
        result = semantic_search(index_name, "데이터 분석")
        print_search_results(result, "데이터 분석 관련 의미 검색")
        
        # 구문 검색
        print("\n--- 구문 검색 테스트 ---")
        result = phrase_search(index_name, "description", "개발 경험")
        print_search_results(result, "개발 경험 구문 검색")
        
        # # 다중 필드 검색
        # print("\n--- 다중 필드 검색 테스트 ---")
        # result = multi_field_search(index_name, "개발")
        # print_search_results(result, "개발 관련 다중 필드 검색")
        
        # result = multi_field_search(index_name, "Python")
        # print_search_results(result, "Python 관련 다중 필드 검색")
        
        # result = multi_field_search(index_name, "디자인")
        # print_search_results(result, "디자인 관련 다중 필드 검색")
        
        # # 범위 검색
        # print("\n--- 범위 검색 테스트 ---")
        # result = range_search(index_name, "age", 25, 30)
        # print_search_results(result, "25-30세 나이 범위 검색")
        
        # result = range_search(index_name, "salary", 40000)
        # print_search_results(result, "급여 40,000 이상 검색")
        
        # # 지리 검색
        # print("\n--- 지리 검색 테스트 ---")
        # result = geo_search(index_name, 37.5665, 126.9780, "50km")
        # print_search_results(result, "서울 50km 반경 검색")
        
        # # 집계 검색
        # print("\n--- 집계 검색 테스트 ---")
        # result = aggregation_search(index_name)
        # print_aggregation_results(result, "전체 통계")
        
        # # 퍼지 검색
        # print("\n--- 퍼지 검색 테스트 ---")
        # result = fuzzy_search(index_name, "name", "김개발")
        # print_search_results(result, "김개발 퍼지 검색")
        
        # # 와일드카드 검색
        # print("\n--- 와일드카드 검색 테스트 ---")
        # result = wildcard_search(index_name, "email", "*@company.com")
        # print_search_results(result, "회사 이메일 와일드카드 검색")
        
        # 하이브리드 검색 테스트
        print("\n--- 하이브리드 검색 테스트 ---")
        result = hybrid_search(index_name, "개발자 경험")
        print_hybrid_search_results(result, "개발자 경험 하이브리드 검색")

        result = hybrid_search(index_name, "사용자 경험", boost_text=1.5, boost_semantic=1.0)
        print_hybrid_search_results(result, "사용자 경험 하이브리드 검색 (Boosted)")

        result = advanced_hybrid_search(index_name, "개발자 경험")
        print_hybrid_search_results(result, "개발자 경험 고급 하이브리드 검색")
        
        # 추가 하이브리드 검색 테스트
        print("\n--- 추가 하이브리드 검색 테스트 ---")
        
        # Python 관련 하이브리드 검색
        result = hybrid_search(index_name, "Python 개발")
        print_hybrid_search_results(result, "Python 개발 하이브리드 검색")
        
        # 고객 관련 하이브리드 검색
        result = hybrid_search(index_name, "고객 서비스")
        print_hybrid_search_results(result, "고객 서비스 하이브리드 검색")
        
        # 보안 관련 하이브리드 검색
        result = hybrid_search(index_name, "보안 시스템")
        print_hybrid_search_results(result, "보안 시스템 하이브리드 검색")
        
        # 데이터 관련 하이브리드 검색
        result = hybrid_search(index_name, "데이터 분석")
        print_hybrid_search_results(result, "데이터 분석 하이브리드 검색")
        
        # 필터링이 포함된 고급 하이브리드 검색
        print("\n--- 필터링 포함 고급 하이브리드 검색 ---")
        
        # 개발팀에서만 검색
        dev_filter = [{"term": {"department": "개발팀"}}]
        result = advanced_hybrid_search(index_name, "개발 경험", filters=dev_filter)
        print_hybrid_search_results(result, "개발팀 내 개발 경험 검색")
        
        # 30세 이상에서만 검색
        age_filter = [{"range": {"age": {"gte": 30}}}]
        result = advanced_hybrid_search(index_name, "전문성", filters=age_filter)
        print_hybrid_search_results(result, "30세 이상 전문성 검색")
        
        # 급여 50,000 이상에서만 검색
        salary_filter = [{"range": {"salary": {"gte": 50000}}}]
        result = advanced_hybrid_search(index_name, "시니어", filters=salary_filter)
        print_hybrid_search_results(result, "고급여 시니어 검색")
        
    else:
        print("인덱스 생성 실패!")