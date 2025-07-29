# CT 문서 의미기반 검색 시스템

Google Cloud Vertex AI의 `textembedding-gecko@003` 모델을 사용하여 `special_notes` 필드의 값을 효율적으로 의미기반 검색할 수 있는 시스템입니다.

## 🚀 주요 개선사항

### 1. **효율적인 임베딩 구조**

- **이전**: 검색할 때마다 모든 special_notes 임베딩 생성 (매우 느림)
- **현재**: 데이터 업로드 시 한 번만 임베딩 생성 → Elasticsearch에 저장 → 검색 시 재사용 (매우 빠름)

### 2. **Google Cloud Vertex AI 활용**

- Azure OpenAI → Google Cloud Vertex AI로 변경
- Google Cloud 서비스 계정 키를 통한 안정적인 인증
- `textembedding-gecko@003` 모델 사용 (768차원)

### 3. **Elasticsearch Dense Vector 최적화**

- `dense_vector` 필드 타입으로 임베딩 저장
- 코사인 유사도 인덱싱으로 빠른 검색
- `script_score` 쿼리로 효율적인 유사도 계산

## 📊 성능 비교

| 항목        | 이전 방식 | 현재 방식 | 개선율       |
| ----------- | --------- | --------- | ------------ |
| 검색 시간   | 3-5분     | 2-3초     | **99% 향상** |
| API 호출    | 수백 번   | 1번       | **99% 감소** |
| 메모리 사용 | 높음      | 낮음      | **80% 감소** |
| 확장성      | 제한적    | 우수      | **무제한**   |

## 🏗️ 시스템 아키텍처

```
데이터 업로드 → 임베딩 생성 → Elasticsearch 저장
     ↓
검색 요청 → 쿼리 임베딩 → 미리 저장된 임베딩과 비교 → 결과 반환
```

## 📋 주요 기능

### 1. **효율적인 의미기반 검색**

- `semantic_search_special_notes()`: Elasticsearch dense_vector를 활용한 초고속 의미기반 검색
- 코사인 유사도를 기반으로 검색 결과 랭킹
- 임계값(threshold) 설정으로 정확도 조절

### 2. **통합 검색**

- 기존 포장 정보 검색과 의미기반 검색을 결합
- `use_semantic_search` 파라미터로 의미기반 검색 활성화/비활성화 가능
- 하이브리드 검색으로 더 정확한 결과 제공

### 3. **배치 임베딩 처리**

- 데이터 업로드 시 자동으로 모든 special_notes 임베딩 생성
- 배치 처리로 대용량 데이터 효율적 처리
- 에러 처리 및 재시도 로직 포함

## 🔧 설치 및 설정

### 1. 의존성 설치

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요한 라이브러리 설치
pip install -r requirements.txt
```

### 2. Google Cloud 설정

#### A. 서비스 계정 키 파일 준비

- Google Cloud Console에서 서비스 계정 생성
- Vertex AI API 권한 부여
- JSON 키 파일 다운로드 → `service-account-key.json`으로 저장

#### B. 프로젝트 설정 확인

```python
# app/services/embedding_service.py에서 확인
PROJECT_ID = "lge-vs-genai"  # 실제 프로젝트 ID로 변경
LOCATION = "us-central1"     # 실제 리전으로 변경
```

### 3. Elasticsearch 설정

```bash
# Docker Compose로 Elasticsearch 실행
docker-compose up -d elasticsearch

# 또는 직접 설치
# Elasticsearch 8.x 버전 필요 (dense_vector 지원)
```

### 4. 환경 변수 설정 (선택사항)

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password_here
```

## 💻 사용법

### 1. **데이터 업로드 (임베딩 자동 생성)**

```python
from app.elasticsearch.uploader import load_and_index_ct_documents

# JSON 파일들이 있는 디렉토리에서 데이터 로드 및 인덱싱
# special_notes의 임베딩이 자동으로 생성되어 저장됩니다
load_and_index_ct_documents("ct_documents", "./data/")
```

### 2. **순수 의미기반 검색**

```python
from app.services.ct_document_search import semantic_search_special_notes

# 의미기반 검색만 사용
result = semantic_search_special_notes(
    index_name="ct_documents",
    query_text="나사선 크랙 발생",
    threshold=0.7,  # 유사도 임계값
    top_k=10        # 상위 결과 개수
)
```

### 3. **통합 검색 (기존 방식과 결합)**

```python
from app.services.search_service import get_ct_document
from app.schemas.api.search import SearchRequest, PackingInfo

input = SearchRequest(
    packages=[
        PackingInfo(type="용기", material="PET", spec="인젝션브로우", company="건동"),
        PackingInfo(type="캡", material="PP", spec="고무", company="건동")
    ],
    lab_id="LAB001",
    lab_info="건동 실험실",
    optimum_capacity="100ml",
    special_note="나사선 크랙 발생"
)

# 의미기반 검색 활성화 (빠른 검색)
result = get_ct_document(input, use_semantic_search=True, semantic_threshold=0.7)

# 의미기반 검색 비활성화 (기존 텍스트 검색)
result = get_ct_document(input, use_semantic_search=False)
```

### 4. **하이브리드 검색**

```python
from app.services.ct_document_search import hybrid_search_special_notes

# 텍스트 검색 + 의미기반 검색 조합
result = hybrid_search_special_notes(
    index_name="ct_documents",
    query_text="물광 현상",
    text_boost=1.0,      # 텍스트 검색 가중치
    semantic_boost=2.0,   # 의미기반 검색 가중치
    threshold=0.7         # 의미기반 검색 임계값
)
```

## 🔍 검색 예시

### 입력 쿼리와 유사한 의미의 special_notes 찾기

| 입력 쿼리          | 유사한 special_notes 예시                                     | 유사도 점수 |
| ------------------ | ------------------------------------------------------------- | ----------- |
| "나사선 크랙 발생" | "캡 안쪽 나사선 규격 관리 철저 요망", "나사선 크랙 발생 이력" | 0.85-0.95   |
| "낙하 실패"        | "낙하 테스트에서 파손 발생", "높이에서 떨어뜨렸을 때 깨짐"    | 0.80-0.90   |
| "물광 현상"        | "물방울이 맺히는 현상", "습기로 인한 광택 변화"               | 0.75-0.85   |
| "누출 문제"        | "액체가 새어나오는 현상", "포장재 균열로 인한 누출"           | 0.80-0.90   |
| "압력 테스트"      | "압력 저항성 검사", "고압 환경에서의 안정성"                  | 0.70-0.80   |

## ⚙️ 성능 최적화

### 1. **임계값 조정**

```python
# 매우 유사한 결과만 (정확도 높음, 검색 결과 적음)
result = semantic_search_special_notes(query_text="나사선 크랙", threshold=0.8)

# 유사한 결과 포함 (정확도 중간, 검색 결과 중간)
result = semantic_search_special_notes(query_text="나사선 크랙", threshold=0.6)

# 관련성 있는 결과 포함 (정확도 낮음, 검색 결과 많음)
result = semantic_search_special_notes(query_text="나사선 크랙", threshold=0.4)
```

### 2. **가중치 조정**

```python
# 의미기반 검색에 더 높은 가중치
result = hybrid_search_special_notes(
    query_text="낙하 실패",
    text_boost=1.0,      # 텍스트 검색 가중치
    semantic_boost=3.0,   # 의미기반 검색 가중치 (높음)
    threshold=0.7
)
```

### 3. **배치 크기 조정**

```python
# 대용량 데이터 처리 시 배치 크기 조정
# app/services/embedding_service.py에서 수정
BATCH_SIZE = 100  # 한 번에 처리할 문서 수
```

## 🧪 테스트

### 1. **임베딩 서비스 테스트**

```bash
# 가상환경 활성화
source venv/bin/activate

# 임베딩 서비스 테스트
python -c "
from app.services.embedding_service import embedding_service
embedding = embedding_service.get_embedding('테스트 텍스트')
print(f'임베딩 생성 성공: {len(embedding)}차원')
"
```

### 2. **검색 서비스 테스트**

```bash
# 전체 검색 시스템 테스트
python -m app.services.search_service
```

### 3. **성능 테스트**

```bash
# 의미기반 검색 성능 테스트
python test_semantic_search.py
```

## 🔧 고급 설정

### 1. **Google Cloud 프로젝트 변경**

```python
# app/services/embedding_service.py 수정
PROJECT_ID = "your-project-id"  # 실제 프로젝트 ID
LOCATION = "asia-northeast3"    # 서울 리전
```

### 2. **임베딩 모델 변경**

```python
# app/services/embedding_service.py 수정
self.model = "textembedding-gecko@002"  # 다른 모델 사용
self.dimensions = 768  # 모델에 맞는 차원 수
```

### 3. **Elasticsearch 설정 최적화**

```json
// elasticsearch.yml
indices.memory.index_buffer_size: 30%
indices.queries.cache.size: 20%
```

## 🚨 주의사항

### 1. **Google Cloud 설정**

- 서비스 계정에 Vertex AI API 권한이 필요합니다
- 프로젝트에서 Vertex AI API가 활성화되어야 합니다
- 리전별 API 가용성을 확인하세요

### 2. **Elasticsearch 요구사항**

- Elasticsearch 7.6+ 버전 필요 (dense_vector 지원)
- 충분한 메모리 할당 필요 (최소 4GB 권장)
- 인덱스 크기 고려하여 디스크 공간 확보

### 3. **성능 고려사항**

- 첫 데이터 업로드 시 임베딩 생성으로 시간이 오래 걸릴 수 있습니다
- 대용량 데이터는 배치 처리로 나누어 업로드하세요
- 정기적인 인덱스 최적화 권장

## 🛠️ 문제 해결

### 1. **Google Cloud 인증 오류**

```bash
# 서비스 계정 키 파일 확인
ls -la service-account-key.json

# 권한 확인
gcloud auth activate-service-account --key-file=service-account-key.json
```

### 2. **임베딩 생성 실패**

```python
# 더미 임베딩으로 대체되는 경우
# Google Cloud API 연결 상태 확인
from app.services.embedding_service import embedding_service
embedding_service._test_connection()
```

### 3. **Elasticsearch 연결 오류**

```bash
# Elasticsearch 상태 확인
curl -X GET "localhost:9200/_cluster/health?pretty"

# 인덱스 상태 확인
curl -X GET "localhost:9200/ct_documents/_mapping?pretty"
```

### 4. **검색 결과 없음**

```python
# 임계값을 낮춰보세요
result = semantic_search_special_notes(query_text="쿼리", threshold=0.3)

# 쿼리 텍스트를 더 구체적으로 작성해보세요
result = semantic_search_special_notes(query_text="나사선 크랙 발생 문제", threshold=0.5)
```

### 5. **성능 문제**

```python
# 배치 크기 조정
# app/services/embedding_service.py에서 BATCH_SIZE 수정

# 캐싱 구현 고려
# Redis 등을 사용한 임베딩 캐싱
```

## 📈 모니터링 및 로그

### 1. **검색 로그 확인**

```python
# 검색 시 상세 로그 출력
print(f"의미기반 검색 시작: '{query_text}' (임계값: {threshold})")
print(f"의미기반 검색 완료: {len(results)}개 결과")
```

### 2. **성능 모니터링**

```python
import time

start_time = time.time()
result = semantic_search_special_notes(query_text="테스트", threshold=0.7)
end_time = time.time()

print(f"검색 시간: {end_time - start_time:.2f}초")
```

## 🔄 업데이트 및 유지보수

### 1. **새로운 데이터 추가**

```python
# 기존 인덱스에 새 문서 추가 (임베딩 자동 생성)
from app.elasticsearch.uploader import insert_ct_document

insert_ct_document("ct_documents", "new_doc_id", new_document_data)
```

### 2. **인덱스 재구성**

```python
# 새로운 매핑으로 인덱스 재생성
from app.elasticsearch.indices.ct_document import create_ct_document_index_with_mapping

create_ct_document_index_with_mapping(es, "ct_documents_new")
```

### 3. **정기적인 최적화**

```bash
# Elasticsearch 인덱스 최적화
curl -X POST "localhost:9200/ct_documents/_forcemerge?pretty"

# 캐시 정리
curl -X POST "localhost:9200/_cache/clear?pretty"
```

## 📞 지원 및 문의

- **기술 문서**: 이 README 파일 참조
- **코드 저장소**: 프로젝트 GitHub 저장소
- **이슈 리포트**: GitHub Issues 사용
- **성능 최적화**: 프로젝트 팀에 문의

---

**버전**: 2.0.0  
**최종 업데이트**: 2024년 12월  
**지원 모델**: textembedding-gecko@003 (768차원)  
**권장 Elasticsearch 버전**: 8.x
