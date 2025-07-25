from app.services.document_search import advanced_search_ct_documents, print_ct_search_results
from app.elasticsearch.client import get_es_client
from app.elasticsearch.indices.ct_document import create_ct_document_index_with_mapping

if __name__ == "__main__":

    index_name = "ct_documents"
    es = get_es_client()
    create_ct_document_index_with_mapping(es, index_name)

    search_params = {
        # "product_name": "Lip",
        # "customer": "Interstory",
        "search_text": "물광"
    }

    result = advanced_search_ct_documents(index_name, search_params)
    print_ct_search_results(result, "고급 검색 (Lip + Interstory + 펌핑)")