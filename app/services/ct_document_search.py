from app.elasticsearch.client import get_es_client
from app.services.embedding_service import embedding_service
from typing import Dict, Any, List
import json

es = get_es_client()

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
    
    print(f"[쿼리 로그][전체 텍스트 검색]\n{json.dumps(query, ensure_ascii=False, indent=2)}")
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
    
    print(f"[쿼리 로그][고급 검색]\n{json.dumps(query, ensure_ascii=False, indent=2)}")
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
    
    print(f"[쿼리 로그][통계 조회]\n{json.dumps(query, ensure_ascii=False, indent=2)}")
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
        print(f"제품명: {source.get('product_name', 'N/A')}")
        print(f"고객사: {source.get('customer', 'N/A')}")
        print(f"개발자: {source.get('developer', 'N/A')}")
        print(f"테스트 날짜: {source.get('test_date', 'N/A')}")
        print(f"실험실 ID: {source.get('lab_id', 'N/A')}")
        print(f"포장 정보: {source.get('packing_info', 'N/A')}")
        
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

def search_ct_documents_by_packing_info(index_name: str, packing_type: str, material: str, spec: str = None, company: str = None):
    """포장 정보(타입, 재질, 세부사양, 업체)로 CT 문서 검색 (타입, 재질 필수, 세부사양/업체 선택)"""
    nested_query = {
        "bool": {
            "must": [
                {"term": {"packing_info.type": packing_type}},
                {"term": {"packing_info.material": material}}
            ]
        }
    }
    # 세부사양(spec) 조건 추가 (있을 때만)
    if spec:
        nested_query["bool"]["must"].append({
            "match": {"packing_info.spec": spec}
        })
    # 포장재업체(company) 조건 추가 (있을 때만)
    if company:
        nested_query["bool"]["must"].append({
            "match": {"packing_info.company": company}
        })

    query = {
        "query": {
            "nested": {
                "path": "packing_info",
                "query": nested_query
            }
        }
    }
    print(f"[쿼리 로그][포장 정보 검색]\n{json.dumps(query, ensure_ascii=False, indent=2)}")
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"포장 정보 검색 오류: {str(e)}")
        return None
    
def semantic_search_special_notes(index_name: str, query_text: str, threshold: float = 0.7, top_k: int = 10):
    """special_notes의 의미기반 검색 (Elasticsearch dense_vector 사용)"""
    try:
        # 쿼리 텍스트의 임베딩 생성
        query_embedding = embedding_service.get_embedding(query_text)
        if not query_embedding:
            print("쿼리 임베딩 생성 실패")
            return None
        
        print(f"의미기반 검색 시작: '{query_text}' (임계값: {threshold})")
        
        # Elasticsearch의 dense_vector 검색 쿼리
        query = {
            "query": {
                "nested": {
                    "path": "special_notes",
                    "query": {
                        "script_score": {
                            "query": {
                                "exists": {
                                    "field": "special_notes.embedding"
                                }
                            },
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'special_notes.embedding') + 1.0",
                                "params": {
                                    "query_vector": query_embedding
                                }
                            }
                        }
                    },
                    "inner_hits": {
                        "size": top_k,
                        "_source": ["special_notes.key", "special_notes.value"]
                    }
                }
            },
            "size": top_k
        }
        
        print(f"[쿼리 로그][의미기반 검색]\n{json.dumps(query, ensure_ascii=False, indent=2)}")
        
        response = es.search(index=index_name, body=query)
        
        # 결과 처리
        formatted_results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            score = hit['_score']
            
            # inner_hits에서 special_notes 결과 추출
            if 'inner_hits' in hit and 'special_notes' in hit['inner_hits']:
                for inner_hit in hit['inner_hits']['special_notes']['hits']['hits']:
                    inner_score = inner_hit['_score']
                    if inner_score >= threshold:
                        note = inner_hit['_source']
                        formatted_results.append({
                            '_id': hit['_id'],
                            '_score': inner_score,
                            '_source': source,
                            'highlight': {
                                'special_notes.value': [note['value']],
                                'special_notes.key': [note.get('key', '')]
                            }
                        })
        
        print(f"의미기반 검색 완료: {len(formatted_results)}개 결과")
        
        return {
            'hits': {
                'total': {'value': len(formatted_results)},
                'hits': formatted_results
            }
        }
        
    except Exception as e:
        print(f"의미기반 검색 오류: {str(e)}")
        return None

def hybrid_search_special_notes(index_name: str, query_text: str, 
                              text_boost: float = 1.0, semantic_boost: float = 2.0,
                              threshold: float = 0.7):
    """하이브리드 검색 (텍스트 검색 + 의미기반 검색)"""
    # 텍스트 기반 검색
    text_query = {
        "query": {
            "nested": {
                "path": "special_notes",
                "query": {
                    "match": {
                        "special_notes.value": {
                            "query": query_text,
                            "boost": text_boost
                        }
                    }
                }
            }
        },
        "highlight": {
            "fields": {
                "special_notes.value": {
                    "fragment_size": 200,
                    "number_of_fragments": 3
                },
                "special_notes.key": {
                    "fragment_size": 100,
                    "number_of_fragments": 2
                }
            }
        }
    }
    
    try:
        text_response = es.search(index=index_name, body=text_query)
        semantic_response = semantic_search_special_notes(index_name, query_text, threshold)
        
        # 결과 병합
        combined_hits = []
        
        # 텍스트 검색 결과 추가
        for hit in text_response['hits']['hits']:
            hit['_score'] *= text_boost
            combined_hits.append(hit)
        
        # 의미기반 검색 결과 추가 (중복 제거)
        existing_ids = {hit['_id'] for hit in combined_hits}
        for hit in semantic_response['hits']['hits']:
            if hit['_id'] not in existing_ids:
                hit['_score'] *= semantic_boost
                combined_hits.append(hit)
        
        # 점수 기준으로 정렬
        combined_hits.sort(key=lambda x: x['_score'], reverse=True)
        
        return {
            'hits': {
                'total': {'value': len(combined_hits)},
                'hits': combined_hits
            }
        }
        
    except Exception as e:
        print(f"하이브리드 검색 오류: {str(e)}")
        return None

def search_ct_documents_by_multiple_packing_sets(
        index_name: str, 
        packing_sets: list, 
        lab_id: str = None, 
        lab_info: str = None, 
        optimum_capacity: str = None, 
        special_note: str = None,
        test_date_start: str = None,
        test_date_end: str = None,
        use_semantic_search: bool = True,
        semantic_threshold: float = 0.7
    ):
    """
    여러 포장 정보 세트 중 하나라도 일치하는 CT 문서 검색 + lab_id로도 검색
    packing_sets: [
        {"type": "튜브", "material": "AS", "company": "건동"},
        {"type": "용기", "material": "PP"}
    ]
    lab_id: str (optional)
    use_semantic_search: bool - special_note 검색 시 의미기반 검색 사용 여부
    """
    should_nested_queries = []
    for packing in packing_sets:
        must_conditions = []
        if packing.get("type"):
            must_conditions.append({"term": {"packing_info.type": packing["type"]}})
        if packing.get("material"):
            must_conditions.append({"term": {"packing_info.material": packing["material"]}})
        if packing.get("spec"):
            must_conditions.append({"match": {"packing_info.spec": packing["spec"]}})
        if packing.get("company"):
            must_conditions.append({"match": {"packing_info.company": packing["company"]}})
        if must_conditions:
            should_nested_queries.append({
                "nested": {
                    "path": "packing_info",
                    "query": {
                        "bool": {
                            "must": must_conditions
                        }
                    }
                }
            })
    
    # lab_id 조건 추가
    must_queries = []
    if lab_id:
        must_queries.append({"term": {"lab_id": lab_id}})
    if lab_info:
        must_queries.append({"match": {"lab_info": lab_info}})
    if optimum_capacity:
        must_queries.append({"match": {"optimum_capacity": optimum_capacity}})

    # special_note 조건 추가 (의미기반 검색 사용 시)
    if special_note and use_semantic_search:
        # 의미기반 검색을 별도로 수행하고 결과를 필터링 조건으로 사용
        semantic_results = semantic_search_special_notes(
            index_name, special_note, semantic_threshold
        )
        if semantic_results and semantic_results['hits']['hits']:
            # 의미기반 검색 결과의 문서 ID들을 필터링 조건으로 사용
            doc_ids = [hit['_id'] for hit in semantic_results['hits']['hits']]
            must_queries.append({"terms": {"document_id": doc_ids}})
    elif special_note:
        # 기존 텍스트 기반 검색
        must_queries.append({
            "nested": {
                "path": "special_notes",
                "query": {
                    "match_phrase": {
                        "special_notes.value": {
                            "query": special_note
                        }
                    }
                }
            }
        })

    # should 조건이 있을 때만 minimum_should_match 추가
    bool_query = {
        "must": must_queries
    }
    if should_nested_queries:
        bool_query["should"] = should_nested_queries
        bool_query["minimum_should_match"] = 1
    
    if test_date_start:
        bool_query["must"].append({"range": {"test_date": {"gte": test_date_start}}})
    if test_date_end:
        bool_query["must"].append({"range": {"test_date": {"lte": test_date_end}}})
    
    query = {
        "query": {
            "bool": bool_query
        },
        "highlight": {
            "fields": {
                "special_notes.value": {
                    "fragment_size": 200,
                    "number_of_fragments": 3
                },
                "special_notes.key": {
                    "fragment_size": 100,
                    "number_of_fragments": 2
                }
            }
        }
    }
    
    print(f"[쿼리 로그][여러 포장 정보 세트 검색]\n{json.dumps(query, ensure_ascii=False, indent=2)}")
    try:
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"여러 포장 정보 세트 검색 오류: {str(e)}")
        return None

if __name__ == "__main__":
    index_name = "ct_documents"

    # 3. 검색 테스트
    print("\n3. 검색 기능 테스트 시작...")
    
    # 제품명 검색 테스트
    # print("\n--- 제품명 검색 테스트 ---")
    # result = search_ct_documents_by_product_name(index_name, "Lip")
    # print_ct_search_results(result, "Lip 제품 검색")
    
    # # 고객사 검색 테스트
    # print("\n--- 고객사 검색 테스트 ---")
    # result = search_ct_documents_by_customer(index_name, "Interstory")
    # print_ct_search_results(result, "Interstory 고객사 검색")
    
    # # 전체 텍스트 검색 테스트
    # print("\n--- 전체 텍스트 검색 테스트 ---")
    # result = full_text_search_ct_documents(index_name, "펌핑 테스트")
    # print_ct_search_results(result, "펌핑 테스트 검색")
    
    # # 재질 검색 테스트
    # print("\n--- 재질 검색 테스트 ---")
    # result = search_ct_documents_by_material(index_name, "AS")
    # print_ct_search_results(result, "AS 재질 검색")
    
    # # 테스트 코드 검색 테스트
    # print("\n--- 테스트 코드 검색 테스트 ---")
    # result = search_ct_documents_by_test_code(index_name, "TMM202")
    # print_ct_search_results(result, "TMM202 테스트 코드 검색")
    
    # 고급 검색 테스트
    # print("\n--- 고급 검색 테스트 ---")
    # search_params = {
    #     # "product_name": "Lip",
    #     # "customer": "Interstory",
    #     "search_text": "물광"
    # }
    # result = advanced_search_ct_documents(index_name, search_params)
    # print_ct_search_results(result, "고급 검색 (Lip + Interstory + 펌핑)")
    
    # # 통계 조회 테스트
    # print("\n--- 통계 조회 테스트 ---")
    # stats_result = get_ct_document_statistics(index_name)
    # print_ct_statistics(stats_result)
            

    input_data = {
        "packages": [
            {"type": "용기", "material": "PET", "spec": "인젝션브로우", "company": "건동"},
            {"type": "캡", "material": "PP", "spec": "고무", "company": "건동"}
        ],
        "lab_id": "LAB001",
        "lab_info": "건동 실험실",
        "optimum_capacity": "100ml"
    }

    result = search_ct_documents_by_multiple_packing_sets(index_name, input_data['packages'], input_data['lab_id'])
    # result
