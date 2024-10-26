import json
from typing import Dict
import requests

from src.res_req_schema import get_status_payload


def watsonx_base_call(payload):
    # r = requests.post('https://example.com', json=json.dumps(payload))
    r = requests.get('http://time.jsontest.com/')
    return get_status_payload(r)
                 

def common_middleware(query, context, data=None) -> Dict[str, str]:
    """
    query: text prompt by the user
    data: Additional data when required. For example lat and lng for the first prompt.
    context: history of the prompts for a particular user
    """
    context.append(query)
    payload = {
        "query": query,
        "context": context,
        "data": data,
    }
    watson_res = watsonx_base_call(payload)
    return watson_res

    
print(common_middleware('test', ['test1', 'test2']))
    

