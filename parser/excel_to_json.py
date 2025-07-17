import os
import pandas as pd
import json
import traceback
import datetime

EXCEL_DIR = os.path.join('data', 'excel')
RESULT_DIR = os.path.join('data', 'json')

# data/excel 내의 모든 엑셀 파일 목록 가져오기
def get_excel_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.xlsx')]

def excel_to_json(excel_path, json_path):
    try:
        print(f"처리 중: {excel_path}")
        df = pd.read_excel(excel_path, sheet_name=0)
        data = df.to_dict(orient='records')
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
