import os
import pandas as pd
import json
import traceback
import datetime

EXCEL_DIR = os.path.join('data', 'excel')
RESULT_DIR = os.path.join('data', 'json')

# data/excel 내의 모든 엑셀 파일 목록 가져오기 (임시 파일 제외)
def get_excel_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.xlsx') and not f.startswith('~$')]

def convert_excel_date_to_string(value):
    """Excel 날짜 숫자를 문자열로 변환"""
    if pd.isna(value) or value == '':
        return str(value).strip()
    
    try:
        # 숫자인지 확인
        if isinstance(value, (int, float)) and value > 1:
            # Excel 날짜는 1900년 1월 1일부터의 일수
            # 1은 1900년 1월 1일, 2는 1900년 1월 2일...
            excel_epoch = datetime.datetime(1900, 1, 1)
            days = int(value) - 1  # Excel은 1부터 시작하므로 1을 빼줌
            result_date = excel_epoch + datetime.timedelta(days=days)
            return result_date.strftime('%Y-%m-%d').strip()
        else:
            return str(value).strip()
    except:
        return str(value).strip()

def excel_to_json(excel_path, json_path):
    try:
        print(f"처리 중: {excel_path}")
        
        # 여러 엔진을 시도하여 Excel 파일 읽기
        df = None
        engines_to_try = ['openpyxl', 'xlrd', 'odf']
        
        for engine in engines_to_try:
            try:
                print(f"  엔진 '{engine}' 시도 중...")
                if engine == 'openpyxl':
                    df = pd.read_excel(excel_path, sheet_name=0, header=None, engine='openpyxl')
                elif engine == 'xlrd':
                    df = pd.read_excel(excel_path, sheet_name=0, header=None, engine='xlrd')
                elif engine == 'odf':
                    df = pd.read_excel(excel_path, sheet_name=0, header=None, engine='odf')
                print(f"  엔진 '{engine}'로 성공적으로 읽음")
                break
            except Exception as engine_error:
                print(f"  엔진 '{engine}' 실패: {str(engine_error)}")
                continue
        
        if df is None:
            raise Exception("모든 엔진으로 파일을 읽을 수 없습니다.")
        
        # 컬럼명을 unnamed로 변경
        df.columns = [f'Unnamed: {i}' for i in range(len(df.columns))]
        
        # 데이터를 딕셔너리로 변환하면서 날짜 변환 적용
        data = []
        for _, row in df.iterrows():
            row_dict = {}
            for col, value in row.items():
                row_dict[col] = convert_excel_date_to_string(value)
            data.append(row_dict)
        
        # datetime 등 직렬화 불가 객체 처리
        def default_converter(o):
            if isinstance(o, (datetime.datetime, datetime.date)):
                return o.isoformat()
            return str(o)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=default_converter)
    except Exception as e:
        print(f"[에러] 파일: {excel_path}")
        print(traceback.format_exc())

def main():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    excel_files = get_excel_files(EXCEL_DIR)
    print("##excel_files", excel_files)
    for excel_file in excel_files:
        excel_path = os.path.join(EXCEL_DIR, excel_file)
        json_file = os.path.splitext(excel_file)[0] + '.json'
        json_path = os.path.join(RESULT_DIR, json_file)
        excel_to_json(excel_path, json_path)
        print(f"변환 완료: {excel_file} -> {json_file}")

if __name__ == '__main__':
    main()
