import json
import requests


WATSONX_BASE_URL = "https://iam.cloud.ibm.com"
WATSONX_ML_BASE_URL = "https://us-south.ml.cloud.ibm.com"
API_KEY = "d_Q0URhrAYNwMFnC5YKVIHZoGOL_2RUImzasPoWlVEyl"


headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}


def _get_access_token():
    payload = (
        f"grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey={API_KEY}"
    )
    url = f"{WATSONX_BASE_URL}/identity/token"
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


def _get_documents(query):

    mltoken = _get_access_token()
    payload = {
        "input_data": [
            {
                "fields": ["Search", "access_token"],
                "values": [[{"role": "user", "content": query}], [mltoken]],
            }
        ]
    }
    response = requests.post(
        "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/4db7a18d-594d-47ba-ba22-457b43fd6a6b/predictions?version=2023-05-29",
        json=payload,
        headers={"Authorization": "Bearer " + mltoken},
    )

    return response.json()["predictions"][0]["values"][1]


def get_education_content_help(history):
    # add all user queries and append
    query = "\n".join(
        [mess["message"] for mess in history["context"] if mess["author"] == "user"]
    )
    return _get_documents(query)


# def get_education_content_help(history):
#     access_token = _get_access_token()
#     bearer_token = f"Bearer {access_token}"
#     url = f"{WATSONX_ML_BASE_URL}/ml/v1/text/generation?version=2023-05-29"

#     # message history (adding query to history)
#     if not history:
#         history = []

#     final_message = ""
#     for mess in history["context"]:

#         final_message += f"<|{mess['author']}|> {mess['message']}\n"

#     payload = json.dumps(
#         {
#             "input": f"""
#       <|system|>\n
# You are Map Assist, an AI language model. You are a cautious assistant. You carefully follow instructions. You are helpful and harmless and you follow ethical guidelines and promote positive behavior. You are a AI language model designed to function as a specialized Retrieval Augmented Generation (RAG) assistant. When generating responses, prioritize correctness, i.e., ensure that your response is correct given the context and user query, and that it is grounded in the context. Furthermore, make sure that the response is supported by the given document or context. Always make sure that your response is relevant to the question. If an explanation is needed, first provide the explanation or reasoning, and then give the final answer. Avoid repeating information unless asked.

#   {final_message}
# \n""",
#             "parameters": {
#                 "decoding_method": "greedy",
#                 "max_new_tokens": 900,
#                 "min_new_tokens": 0,
#                 "stop_sequences": [],
#                 "repetition_penalty": 1.05,
#             },
#             "model_id": "ibm/granite-13b-chat-v2",
#             "project_id": "d94470cd-0e46-4732-bd4a-fb47f687f7be",
#             "moderations": {
#                 "hap": {
#                     "input": {
#                         "enabled": True,
#                         "threshold": 0.5,
#                         "mask": {"remove_entity_value": True},
#                     },
#                     "output": {
#                         "enabled": True,
#                         "threshold": 0.5,
#                         "mask": {"remove_entity_value": True},
#                     },
#                 },
#                 "pii": {
#                     "input": {
#                         "enabled": True,
#                         "threshold": 0.5,
#                         "mask": {"remove_entity_value": True},
#                     },
#                     "output": {
#                         "enabled": True,
#                         "threshold": 0.5,
#                         "mask": {"remove_entity_value": True},
#                     },
#                 },
#             },
#         }
#     )
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#         "Authorization": bearer_token,
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)

#     print(response.text)
#     return response.json().get("results")[0]["generated_text"]
