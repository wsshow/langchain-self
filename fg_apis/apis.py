import requests


def api_post(url, json):
    return requests.post(f'http://127.0.0.1:5000{url}', json=json)


def chat_with_vdb(prompt):
    resp = api_post('/query', json={
        'prompt': prompt
    })
    rj = resp.json()
    if rj['code'] == 0:
        content = rj['data'][0]['content']
        source = rj['data'][0]['source']
        page = rj['data'][0]['page_num']
        return {
            'content': content,
            'source': source,
            'page': page
        }
    else:
        return {
            'content': rj['desc'],
            'source': ''
        }


def doc_to_vdb(filepath):
    resp = api_post('/add_doc', json={
        'filepath': filepath
    })
    rj = resp.json()
    return rj['desc']
