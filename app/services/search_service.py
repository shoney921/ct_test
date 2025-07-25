from app.schemas.common import Document, PackingInfo
from app.services.ct_document_search import *
from app.schemas.api.search import SearchRequest

def get_ct_document(input: SearchRequest):
    packing_spec_list = [
        {"type": package.type, "material": package.material, "company": package.company}
        for package in input.packages
    ]
    result = search_ct_documents_by_multiple_packing_sets("ct_documents", packing_spec_list)
    hits = result['hits']['hits']

    documents = []
    for hit in hits:
        try:
            doc = Document(**hit['_source'])
            documents.append(doc)
        except Exception as e:
            print("에러 발생 hit:", hit)
            print("에러 메시지:", e)

    for document in documents:
        print(document.file_name)
    return documents


def get_ct_document_by_packing_info(packing_type: str, material: str, spec: str = None, company: str = None):
    result = search_ct_documents_by_packing_info("ct_documents", packing_type, material, spec=spec, company=company)
    print(result['hits']['hits'])
    return result

def get_ct_document_by_packing_info_list(packing_spec_list: list):
    result = search_ct_documents_by_multiple_packing_sets("ct_documents", packing_spec_list)
    print(result['hits']['hits'])
    return result

if __name__ == "__main__":
    index_name = "ct_documents"
    
    print("=== CT 문서 검색 시스템 테스트 ===\n")
    
    # search_params = {
    #     "product_name": "앰플",
    #     # "customer": "Interstory",
    #     "search_text": "진공감압"
    # }
    # result = advanced_search_ct_documents(index_name, search_params)
    # print_ct_search_results(result, "고급 검색 (Lip + Interstory + 펌핑)")

    # result = search_ct_documents_by_packing_info(index_name, packing_type="용기", material="PET", company="건동")
    # print_ct_search_results(result, "키워드 검색 (용기 + PET + 건동)")
    

    # get_ct_document_by_packing_info(packing_type="용기", material="PET", company="건동")

    # packing_spec_list = [
    #     {"type": "용기", "material": "PET", "company": "건동"},
    #     {"type": "캡", "material": "PP", "company": "건동"},
    #     # {"type": "튜브", "material": "PE", "company": "건동"},
    # ]
    # get_ct_document_by_packing_info_list(packing_spec_list)

    input = SearchRequest(
        packages=[
            PackingInfo(type="용기", material="PET",spec="", company="건동"),
            PackingInfo(type="캡", material="PP",spec="", company="건동"),
        ],
        lab_id="LAB001",
        lab_info="건동 실험실",
        optimum_capacity="100ml",
        special_note="특이사항 없음"
    )

    input = SearchRequest(
        packages=[
            PackingInfo(type="", material="",spec="", company="두코"),
        ],
        lab_id="",
        lab_info="",
        optimum_capacity="",
        special_note=""
    )

    input = SearchRequest(
        packages=[
            PackingInfo(type="용기", material="PET",spec="", company=""),
        ],
        lab_id="",
        lab_info="",
        optimum_capacity="",
        special_note=""
    )

    get_ct_document(input)