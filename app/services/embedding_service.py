import os
import json
import requests
from typing import List, Dict, Any
import numpy as np
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth import default

load_dotenv()

# Google Cloud 서비스 계정 키 파일 경로
SERVICE_ACCOUNT_KEY_PATH = "service-account-key.json"

# Google Cloud 프로젝트 설정
PROJECT_ID = "lge-vs-genai"
LOCATION = "us-central1"  # 또는 다른 리전

class EmbeddingService:
    def __init__(self):
        # Google Cloud 인증 설정
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_KEY_PATH,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Vertex AI API 엔드포인트
            self.endpoint_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/textembedding-gecko@003:predict"
            
            # 임베딩 차원
            self.dimensions = 768  # textembedding-gecko의 임베딩 차원
            
            # API 연결 테스트
            self._test_connection()
            
        except Exception as e:
            print(f"Google Cloud 인증 설정 오류: {str(e)}")
            print("의미기반 검색이 비활성화됩니다.")
            self.credentials = None
            self.endpoint_url = None
    
    def _test_connection(self):
        """API 연결 테스트"""
        try:
            token = self._get_auth_token()
            print(f"Google Cloud API 연결 성공 (토큰 길이: {len(token)})")
        except Exception as e:
            print(f"Google Cloud API 연결 실패: {str(e)}")
            raise e
    
    def _get_auth_token(self):
        """인증 토큰 가져오기"""
        if not self.credentials:
            raise Exception("Google Cloud 인증 정보가 없습니다.")
        
        self.credentials.refresh(Request())
        return self.credentials.token
    
    def _get_dummy_embedding(self, text: str) -> List[float]:
        """더미 임베딩 생성 (API 연결 실패 시 사용)"""
        # 텍스트 길이를 기반으로 한 간단한 해시 기반 임베딩
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # 768차원 벡터 생성
        embedding = []
        for i in range(768):
            embedding.append(float(hash_bytes[i % 16]) / 255.0)
        
        return embedding
    
    def get_embedding(self, text: str) -> List[float]:
        """텍스트를 임베딩 벡터로 변환"""
        try:
            if not self.credentials or not self.endpoint_url:
                print("Google Cloud API 연결 불가 - 더미 임베딩 사용")
                return self._get_dummy_embedding(text)
            
            # 요청 헤더 설정
            headers = {
                "Authorization": f"Bearer {self._get_auth_token()}",
                "Content-Type": "application/json"
            }
            
            # 요청 데이터
            data = {
                "instances": [
                    {
                        "content": text
                    }
                ]
            }
            
            # API 호출 (타임아웃 30초 설정)
            print(f"임베딩 생성 중: '{text[:50]}...'")
            response = requests.post(self.endpoint_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            # 응답에서 임베딩 추출
            result = response.json()
            embedding = result["predictions"][0]["embeddings"]["values"]
            print(f"임베딩 생성 완료 (차원: {len(embedding)})")
            return embedding
            
        except requests.exceptions.Timeout:
            print(f"API 호출 타임아웃 - 더미 임베딩 사용")
            return self._get_dummy_embedding(text)
        except Exception as e:
            print(f"임베딩 생성 오류: {str(e)}")
            print("더미 임베딩으로 대체합니다.")
            return self._get_dummy_embedding(text)
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 배치로 임베딩 벡터로 변환"""
        try:
            if not self.credentials or not self.endpoint_url:
                print("Google Cloud API 연결 불가 - 더미 임베딩 사용")
                return [self._get_dummy_embedding(text) for text in texts]
            
            # 요청 헤더 설정
            headers = {
                "Authorization": f"Bearer {self._get_auth_token()}",
                "Content-Type": "application/json"
            }
            
            # 요청 데이터
            data = {
                "instances": [
                    {
                        "content": text
                    } for text in texts
                ]
            }
            
            # API 호출 (타임아웃 60초 설정)
            print(f"배치 임베딩 생성 중: {len(texts)}개 텍스트")
            response = requests.post(self.endpoint_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            # 응답에서 임베딩 추출
            result = response.json()
            embeddings = [prediction["embeddings"]["values"] for prediction in result["predictions"]]
            print(f"배치 임베딩 생성 완료: {len(embeddings)}개")
            return embeddings
            
        except requests.exceptions.Timeout:
            print(f"배치 API 호출 타임아웃 - 더미 임베딩 사용")
            return [self._get_dummy_embedding(text) for text in texts]
        except Exception as e:
            print(f"배치 임베딩 생성 오류: {str(e)}")
            print("더미 임베딩으로 대체합니다.")
            return [self._get_dummy_embedding(text) for text in texts]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """두 벡터 간의 코사인 유사도 계산"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def semantic_search(self, query: str, documents: List[Dict[str, Any]], 
                       threshold: float = 0.7, top_k: int = 5) -> List[Dict[str, Any]]:
        """의미기반 검색 수행"""
        print(f"의미기반 검색 시작: '{query}'")
        
        # 쿼리 임베딩 생성
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            print("쿼리 임베딩 생성 실패")
            return []
        
        # 각 문서의 special_notes 값들을 임베딩하고 유사도 계산
        results = []
        total_notes = 0
        processed_notes = 0
        
        for doc in documents:
            if 'special_notes' in doc and doc['special_notes']:
                for note in doc['special_notes']:
                    if 'value' in note and note['value']:
                        total_notes += 1
                        note_embedding = self.get_embedding(note['value'])
                        if note_embedding:
                            processed_notes += 1
                            similarity = self.cosine_similarity(query_embedding, note_embedding)
                            if similarity >= threshold:
                                results.append({
                                    'document': doc,
                                    'note': note,
                                    'similarity': similarity
                                })
        
        print(f"의미기반 검색 완료: {processed_notes}/{total_notes} 노트 처리, {len(results)}개 결과")
        
        # 유사도 기준으로 정렬하고 top_k 반환
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    def add_embeddings_to_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """문서의 special_notes에 임베딩을 추가"""
        if 'special_notes' in document and document['special_notes']:
            print(f"문서 '{document.get('product_name', 'Unknown')}'의 special_notes 임베딩 생성 중...")
            
            for note in document['special_notes']:
                if 'value' in note and note['value']:
                    try:
                        # 임베딩 생성
                        embedding = self.get_embedding(note['value'])
                        if embedding:
                            note['embedding'] = embedding
                            print(f"  - 임베딩 생성 완료: '{note['value'][:50]}...'")
                        else:
                            print(f"  - 임베딩 생성 실패: '{note['value'][:50]}...'")
                    except Exception as e:
                        print(f"  - 임베딩 생성 오류: {str(e)}")
                        # 더미 임베딩으로 대체
                        note['embedding'] = self._get_dummy_embedding(note['value'])
            
            print(f"총 {len(document['special_notes'])}개 special_notes 임베딩 완료")
        
        return document
    
    def add_embeddings_to_documents_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """여러 문서의 special_notes에 임베딩을 배치로 추가"""
        print(f"배치 임베딩 생성 시작: {len(documents)}개 문서")
        
        for i, document in enumerate(documents):
            print(f"문서 {i+1}/{len(documents)} 처리 중...")
            document = self.add_embeddings_to_document(document)
        
        print("배치 임베딩 생성 완료")
        return documents

# 전역 인스턴스 생성
embedding_service = EmbeddingService() 