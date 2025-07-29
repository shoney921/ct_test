from typing import Dict, Any, List
import json
from app.elasticsearch.indices.ct_document import create_ct_document_index_with_mapping
from app.elasticsearch.client import get_es_client
from app.services.embedding_service import embedding_service

es = get_es_client()

def process_ct_document_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """CT 문서 데이터를 엘라스틱서치에 적합한 형태로 전처리"""
    processed_data = raw_data.copy()
    
    # 날짜 필드 전처리
    def clean_date_field(date_value):
        if not date_value or date_value == '' or date_value == '-':
            return None
        
        # 날짜 형식 정리 (예: 2023.02.30 -> 2023-02-28)
        if isinstance(date_value, str):
            # 점(.)을 하이픈(-)으로 변경
            date_value = date_value.replace('.', '-')
            
            # 잘못된 날짜 처리 (예: 2023-02-30 -> 2023-02-28)
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(date_value, '%Y-%m-%d')
                return parsed_date.isoformat()
            except ValueError:
                # 잘못된 날짜인 경우 None 반환
                return None
        
        return date_value
    
    # 날짜 필드 정리
    if 'test_date' in processed_data:
        processed_data['test_date'] = clean_date_field(processed_data['test_date'])
    
    if 'expected_date' in processed_data:
        processed_data['expected_date'] = clean_date_field(processed_data['expected_date'])
    
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
        for note in raw_data['special_notes']:
            if note.get('key'):
                search_text_parts.append(note['key'])
            if note.get('value'):
                search_text_parts.append(note['value'])
    
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
    
    # special_notes에 임베딩 추가
    processed_data = embedding_service.add_embeddings_to_document(processed_data)
    
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
    if create_ct_document_index_with_mapping(es, index_name):
        print("CT 문서 인덱스 생성 완료!")
        
        # 2. JSON 파일들 로드 및 인덱싱
        print("\n2. JSON 파일 로드 및 인덱싱 중...")
        refine_directory = "data/refine"
        success_count, error_count = load_and_index_ct_documents(index_name, refine_directory)
        
    