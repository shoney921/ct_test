import os
import json

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

# 의미있는 정보만 추출하는 함수
def refine_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    packing_info = []
    start = False
    prev_company = None
    for row in data:

        """
        1) 포장재 정보 찾는 로직
        """
        # 헤더(포장재정보) 찾기: Unnamed: 8에 '포장재업체'가 있으면 그 다음 row부터 시작
        if not start and str(row.get('Unnamed: 0', '')).strip() == '포장재정보':
            start = True
            continue
        if not start:
            continue
        # '사양'이 '시료사진'이면 종료
        if str(row.get('Unnamed: 0', '')).strip() == '처방정보' or str(row.get('Unnamed: 0', '')).strip() == '내용물정보':
            break
        # 포장재 정보 row만 추출 (타입/재질/세부사양/포장재업체)
        type_ = clean_value(row.get('Unnamed: 2'))
        material = clean_value(row.get('Unnamed: 4'))
        spec = clean_value(row.get('종류'))
        company = clean_value(row.get('Unnamed: 8'))

        # 실제 데이터가 모두 존재할 때만 저장 (타입만 None이 아니면 됨)
        if type_ is not None:
            if not company:  # None 또는 빈 문자열 처리
                company = prev_company
            else:
                prev_company = company

            packing_info.append({
                'type': type_,
                'material': material,
                'spec': spec,
                'company': company
            })

        """
        2) 처방번호(lab id) 찾는 로직
        """
        if str(row.get("Unnamed: 2", "")).strip() == "처방번호":
            lab_id = row.get("종류")


    # packing_info 리스트를 'packing_info'라는 상위 키로 감싸서 json으로 저장
    result = {'packing_info': packing_info, 'lab_id': lab_id}
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