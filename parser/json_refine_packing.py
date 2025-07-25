import os
import json
import pandas as pd
import datetime

INPUT_DIR = os.path.join('data', 'json')
OUTPUT_DIR = os.path.join('data', 'refine')

# NaN, None, 빈 문자열 등을 모두 None으로 변환
def clean_value(val):
    if val is None:
        return None
    sval = str(val).strip()
    if sval.lower() == 'nan' or sval == '':
        return None
    return val


def convert_excel_date_to_string(value):
    """
    다양한 날짜 포맷(문자열, 엑셀 숫자 등)을 YYYY-MM-DD 형식의 문자열로 변환
    변환 불가 시 원본(str) 반환
    """
    import re
    from dateutil import parser as date_parser

    # 1. NaN, None, 빈 문자열 처리
    if pd.isna(value) or value is None or str(value).strip() == '':
        return ''

    # 2. 엑셀 날짜(숫자) 처리
    try:
        # 엑셀 날짜는 1900년 1월 1일부터 시작 (1=1900-01-01)
        if isinstance(value, (int, float)) and value > 1:
            excel_epoch = datetime.datetime(1899, 12, 30)
            result_date = excel_epoch + datetime.timedelta(days=float(value))
            return result_date.strftime('%Y-%m-%d')
    except Exception:
        pass

    # 2-1. str 타입이지만 숫자만 있는 경우 엑셀 날짜로 시도
    str_value = str(value).strip()
    if str_value.isdigit():
        num_value = float(str_value)
        if num_value > 1:
            try:
                excel_epoch = datetime.datetime(1899, 12, 30)
                result_date = excel_epoch + datetime.timedelta(days=num_value)
                return result_date.strftime('%Y-%m-%d')
            except Exception:
                pass

    # 3. 문자열로 들어온 경우 다양한 포맷 시도
    # 숫자만 있는 8자리(YYYYMMDD) 혹은 6자리(YYMMDD) 등
    if re.fullmatch(r'\d{8}', str_value):
        try:
            return datetime.datetime.strptime(str_value, '%Y%m%d').strftime('%Y-%m-%d')
        except Exception:
            pass
    if re.fullmatch(r'\d{6}', str_value):
        try:
            return datetime.datetime.strptime(str_value, '%y%m%d').strftime('%Y-%m-%d')
        except Exception:
            pass
    # 한글 날짜(예: 2024년 6월 1일)
    m = re.match(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', str_value)
    if m:
        try:
            y, m_, d = m.groups()
            return f"{int(y):04d}-{int(m_):02d}-{int(d):02d}"
        except Exception:
            pass
    # 다양한 구분자(., -, /) 처리
    for fmt in [
        '%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d',
        '%Y-%m-%d %H:%M:%S', '%Y.%m.%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
        '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y',
        '%m-%d-%Y', '%m.%d.%Y', '%m/%d/%Y',
    ]:
        try:
            return datetime.datetime.strptime(str_value, fmt).strftime('%Y-%m-%d')
        except Exception:
            continue
    # dateutil 파서로 마지막 시도
    try:
        dt = date_parser.parse(str_value, fuzzy=True)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    # 변환 실패 시 원본 반환
    return str_value

def generate_uuid():
    """
    UUID를 생성하여 문자열로 반환하는 함수
    
    Returns:
        str: 생성된 UUID 문자열
    """
    import uuid
    # UUID에서 '-' 제거하고 'DOC' 프리픽스 추가
    uuid_str = str(uuid.uuid4()).upper()
    uuid_str = uuid_str.replace('-', '')
    uuid_str = 'DOC' + uuid_str
    return uuid_str

# 의미있는 정보만 추출하는 함수
def refine_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    packing_info = []
    packing_info_start = False
    prev_company = None
    lab_id = None
    experiment_info = []
    experiment_info_start = False
    prev_code = None
    special_notes = []
    special_notes_start = False

    # 결재자 정보 추출을 위한 불린 변수들 초기화
    approval_info_start = False  # 결재 섹션 시작 여부
    writer = False  # 작성자 존재 여부 
    reviewer = False  # 검토자 존재 여부
    approver = False  # 승인자 존재 여부
    
    # 변수들 초기화
    test_no = None
    test_date = None
    expected_date = None
    product_name = None
    customer = None
    developer = None
    requester = None
    test_count = None
    test_quantity = None
    lab_info = None
    optimum_capacity = None

    for row in data:
        # 1) 포장재 정보 구간 제어
        if not packing_info_start and str(row.get('Unnamed: 0', '')).strip() in ['포장재정보', 'Component Info.']:
            packing_info_start = True
            continue
        if packing_info_start:
            if str(row.get('Unnamed: 0', '')).strip() in ['처방정보', '내용물정보', 'Formula Info.']:
                packing_info_start = False 

        # 2) 포장재 정보 추출 (start가 True일 때만)
        if packing_info_start:
            type_ = clean_value(row.get('Unnamed: 2'))
            material = clean_value(row.get('Unnamed: 4'))
            spec = clean_value(row.get('Unnamed: 6'))
            company = clean_value(row.get('Unnamed: 8'))
            if type_ is not None:
                if not company:
                    company = prev_company
                else:
                    prev_company = company
                packing_info.append({
                    'type': type_,
                    'material': material,
                    'spec': spec,
                    'company': company
                })

        # 3) lab_id는 반복문 전체에서 항상 체크
        if str(row.get("Unnamed: 2", "")).strip() in ["처방번호", "Lab No."]:
            lab_id = clean_value(row.get("Unnamed: 6"))
            if lab_id is not None:
                lab_id = lab_id.replace(" ", "")
        if str(row.get("Unnamed: 2", "")).strip() in ["물성정보", "Bulk Specification"]:
            lab_info = clean_value(row.get("Unnamed: 6"))

        # 4) 실험정보 추출
        if not experiment_info_start and (str(row.get('Unnamed: 0', '')).strip() in ['시험코드', 'Test Code']):
            experiment_info_start = True
            continue
        if experiment_info_start:
            if str(row.get('Unnamed: 0', '')).strip() in ['처방정보', '내용물정보', 'Formula Info.'] or str(row.get('Unnamed: 0', '')).strip().startswith('※'):
                experiment_info_start = False

        # 5) 실험정보 추출 (start가 True일 때만)
        if experiment_info_start:
            # 각 컬럼에서 값 추출
            code = clean_value(row.get('Unnamed: 0'))
            item = clean_value(row.get('Unnamed: 1'))
            period = clean_value(row.get('Unnamed: 4'))
            check = clean_value(row.get('Unnamed: 5'))
            standard = clean_value(row.get('Unnamed: 6'))
            result = clean_value(row.get('Unnamed: 12')) or clean_value(row.get('Unnamed: 11'))
            # 시험코드가 None이 아니고, 실제 데이터가 있는 경우만 저장

            if item is not None and item != "-":
                if code is None:
                    code = prev_code
                else:
                    prev_code = code
                experiment_info.append({
                    'code': code,
                    'item': item,
                    'period': period,
                    'check': check,
                    'standard': standard,
                    'result': result
                })
            
            # 적정용량 변수 따로 관리하기 위한 코드
            if code == "TMM202" and (item == "Optimum Capacity" or item == "적정용량"):
                optimum_capacity = result

        # 6) 특이사항 추출
        if not special_notes_start and str(row.get('Unnamed: 0', '')).strip() in ['시험 특이사항', 'Test Remarks']:
            special_notes_start = True
            continue
        if special_notes_start:
            if str(row.get('Unnamed: 0', '')).strip().startswith('※'):
                special_notes_start = False

        # 7) 특이사항 추출 (start가 True일 때만)
        if special_notes_start:
            special_notes_header = clean_value(row.get('Unnamed: 0'))
            special_notes_content = clean_value(row.get('Unnamed: 2')) or clean_value(row.get('Unnamed: 1'))

            if special_notes_header is not None and special_notes_header != "-":
                special_notes.append({
                    'key': special_notes_header,
                    'value': special_notes_content
                })

        # 8) 기타 정보들 추출
        if str(row.get('Unnamed: 0', '')).strip().startswith('Test No'):
            test_no = clean_value(row.get('Unnamed: 0'))
            if test_no:
                test_no = test_no.replace("Test No : ", "")

        if str(row.get('Unnamed: 0', '')).strip() in ['시험일자', 'Tested Date']:
            test_date = clean_value(row.get('Unnamed: 2'))

        if str(row.get('Unnamed: 0', '')).strip() in ['판정예정일자', 'Estimated date']:
            expected_date = clean_value(row.get('Unnamed: 2'))

        if str(row.get('Unnamed: 0', '')).strip() in ['제품명', 'Product Name']:
            product_name = clean_value(row.get('Unnamed: 2'))

        if str(row.get('Unnamed: 0', '')).strip() in ['고객사명', 'Client']:
            customer = clean_value(row.get('Unnamed: 2'))

        if str(row.get('Unnamed: 6', '')).strip() in ['개발담당자', 'Developer']:
            developer = clean_value(row.get('Unnamed: 7'))
        elif str(row.get('Unnamed: 8', '')).strip() in ['개발담당자', 'Developer']:
            developer = clean_value(row.get('Unnamed: 11'))


        if str(row.get('Unnamed: 6', '')).strip() in ['시험의뢰자', 'Test Requestor']:
            requester = clean_value(row.get('Unnamed: 7'))
        elif str(row.get('Unnamed: 8', '')).strip() in ['시험의뢰자', 'Test Requestor']:
            requester = clean_value(row.get('Unnamed: 11'))

        if str(row.get('Unnamed: 6', '')).strip() in ['시험의뢰차수', '# of test']:
            test_count = clean_value(row.get('Unnamed: 7'))
        elif str(row.get('Unnamed: 8', '')).strip() in ['시험의뢰차수', '# of test']:
            test_count = clean_value(row.get('Unnamed: 11'))

        if str(row.get('Unnamed: 6', '')).strip() in ['시험의뢰수량', 'Quantity for Test']:
            test_quantity = clean_value(row.get('Unnamed: 7'))
        elif str(row.get('Unnamed: 8', '')).strip() in ['시험의뢰수량', 'Quantity for Test']:
            test_quantity = clean_value(row.get('Unnamed: 11'))

        file_name = os.path.basename(input_path).replace('.json', '')

        if str(row.get('Unnamed: 6', '')).strip() in ['결재', 'Approval'] or str(row.get('Unnamed: 7', '')).strip() in ['결재', 'Approval']:
            approval_info_start = True
            continue
        if approval_info_start:
            writer = clean_value(row.get('Unnamed: 7')) or clean_value(row.get('Unnamed: 8'))
            reviewer = clean_value(row.get('Unnamed: 9')) or clean_value(row.get('Unnamed: 10'))
            approver = clean_value(row.get('Unnamed: 11')) or clean_value(row.get('Unnamed: 12'))
            if writer:
                writer = writer.replace(" ", "").replace("　", "")
            if reviewer:
                reviewer = reviewer.replace(" ", "").replace("　", "")
            if approver:
                approver = approver.replace(" ", "").replace("　", "")
            approval_info_start = False


    # packing_info 리스트를 'packing_info'라는 상위 키로 감싸서 json으로 저장
    result = {
        'document_id': generate_uuid(),
        'summary': '#### TODO : 추가 llm 로직으로 업데이트 예정',
        'file_name': file_name,
        'test_no': test_no,
        'product_name': product_name,
        'customer': customer,
        'developer': developer,
        'requester': requester,
        'test_count': test_count,
        'test_quantity': test_quantity,
        'test_date': convert_excel_date_to_string(test_date),
        'expected_date': convert_excel_date_to_string(expected_date),
        'writer': writer,
        'reviewer': reviewer,
        'approver': approver,
        'packing_info': packing_info,
        'lab_id': lab_id,
        'lab_info': lab_info,
        'optimum_capacity': optimum_capacity,
        'experiment_info': experiment_info,
        'special_notes': special_notes,
        'download_url': '#### TODO : 추가 스토리지 업로드 로직으로 업데이트 예정',
        }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # 출력 폴더가 없으면 생성
    for file in os.listdir(INPUT_DIR):
        if file.endswith('.json') and not file.endswith('_refined.json'):
            input_path = os.path.join(INPUT_DIR, file)
            output_path = os.path.join(OUTPUT_DIR, file.replace('.json', '_refined.json'))
            refine_json(input_path, output_path)
            print(f"가공 완료: {file} -> {os.path.basename(output_path)}")

if __name__ == '__main__':
    main() 