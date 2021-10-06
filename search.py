from flask import current_app


def add_to_index(index, model):
    if not current_app.config['ELASTICSEARCH_URL']:
        return 
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload) 


def remove_from_index(index, model):
    if not current_app.config['ELASTICSEARCH_URL']:
        return 
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.config['ELASTICSEARCH_URL']:
        return [], 0
    search = current_app.elasticsearch.search(index=index, 
                                     body={'query': {'multi_match': {'query': query, 'fields': ['*']}}, 'from': (page-1) * per_page, 'size': per_page})
    ids = [hits['_id'] for hits in search['hits']['hits']]
    return ids, search['hits']['total']['value']  