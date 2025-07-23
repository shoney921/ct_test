from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

# .env 파일에서 환경변수 로드
load_dotenv()

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")

# 엘라스틱서치 클라이언트 생성 (ID/PW 인증)
es = Elasticsearch(
    ELASTICSEARCH_HOST,
    basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    verify_certs=False
)

def insert_test_document(index_name: str, doc_id: str, document: dict):
    # 데이터 인서트
    response = es.index(index=index_name, id=doc_id, document=document)
    return response

def get_test_document(index_name: str, doc_id: str):
    # 데이터 조회
    response = es.get(index=index_name, id=doc_id)
    return response

if __name__ == "__main__":
    # 테스트용 인덱스와 데이터
    index_name = "test_index"
    doc_id = "1"
    document = {
        "name": "홍길동",
        "age": 30,
        "message": "엘라스틱서치 테스트"
    }

    # 데이터 인서트
    # insert_result = insert_test_document(index_name, doc_id, document)
    # print("Insert Result:", insert_result)

    # 데이터 조회
    get_result = get_test_document(index_name, doc_id)
    print("Get Result:", get_result["_source"])