from enum import Enum
import json
import requests


WATSONX_BASE_URL = "https://iam.cloud.ibm.com"
WATSONX_ML_BASE_URL = "https://us-south.ml.cloud.ibm.com"
API_KEY = "d_Q0URhrAYNwMFnC5YKVIHZoGOL_2RUImzasPoWlVEyl"


headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}


class Buckets(Enum):
    HEALTH = "Health"
    SUPPLIES = "Supplies"
    SHELTERS = "Shelters"
    MENTAL_DISTRESS = "Mental Distress"
    OTHERS = "Others"


HELP_IS_BUCKET_MAPPING = {
    "HEALTH": [
        "First Aid",
        "Medical",
        "Food",
        "Water",
        "Hygiene",
        "Trauma Support",
        "Triage",
        "Blood Donation",
        "Vaccination",
        "Health Kits",
        "Medication",
    ],
    "SUPPLIES": [
        "Supplies",
        "Sandbags",
        "Food Packs",
        "Emergency Kits",
        "Equipment",
        "Toolkits",
    ],
    "SHELTERS": [
        "Shelter",
        "Temporary Shelter",
        "Temporary Schools",
        "Housing",
        "Relocation",
    ],
    "MENTAL_DISTRESS": [
        "Counseling",
        "Psych Support",
        "Mental Health",
        "Awareness",
        "Childcare",
        "Follow-up",
        "Lost & Found",
    ],
    "OTHERS": [
        "Training",
        "Evacuation",
        "Drills",
        "Contacts",
        "Hazard Map",
        "Alerts",
        "Translation",
        "Collection",
        "Recruitment",
        "Support",
        "Communication",
        "Rescue",
        "Clearance",
        "Assessment",
        "Information",
        "Transport",
        "Relief",
        "Clean-up",
        "Legal",
        "Rebuild",
        "Financial",
        "Recovery",
        "Job Aid",
        "School",
        "Clothing",
        "Pet Care",
        "Documentation",
        "Financial Aid",
        "Power Supply",
        "Waste Removal",
        "Coordination",
        "Cash Aid",
        "Resource Sharing",
        "Debris Removal",
        "Construction",
        "Remapping",
        "Crowd Control",
    ],
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


def classify_user_message(query):
    access_token = _get_access_token()
    bearer_token = f"Bearer {access_token}"
    url = f"{WATSONX_ML_BASE_URL}/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": f"""During a natural disaster, you will categorize user queries into the following categories:

Health: Physical health related issues
Supplies: Food and other house supplies based issues
Shelters: Housing or shelter based issues
Mental Distress: Mental distresses
Others: None of the above
If additional information is needed to make a classification, feel free to ask clarifying questions. If you'\''re uncertain about the appropriate category, classify the query as \"Others\".

Stop after returning the correct category.

Some example

Input: I am looking for a place to stay
Output: Shelter

Input: I am hurt
Output:  Health

Input: My house is on file
Output: Shelter

Input: I have run out of food
Output:  Supplies


Input: Running out of water
Output: Supplies

Input: I am panicing
Output: Mental Distress

User Input: {query}""",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "repetition_penalty": 1,
        },
        "model_id": "google/flan-ul2",
        "project_id": "d94470cd-0e46-4732-bd4a-fb47f687f7be",
        "moderations": {
            "hap": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
            },
            "pii": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
            },
        },
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": bearer_token,
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    predicted_text = (
        response.json()["results"][0]["generated_text"].replace("Output:", "").strip()
    )

    return Buckets(predicted_text)



def is_user_input_enough_to_classify(query):
    access_token = _get_access_token()
    bearer_token = f"Bearer {access_token}"
    url = f"{WATSONX_ML_BASE_URL}/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": f"""Task: During a natural disaster, evaluate user queries to determine if there is enough information provided to categorize them into the following categories: Health, Supplies, Shelters/housing, Mental Distress, and Others.

Instructions:

If the user query contains sufficient information for categorization, return DONE.
If more information is needed to accurately categorize the query, return a message requesting additional details.
Do not return anything else.

Stop after returning the response string.

Example Evaluations:

Input: I am looking for a place to stay
Output: DONE

Input: I am hurt
Output: DONE

Input: I need help
Output: Please tell us what sort of assistance do you require?

Input: I have run out of food
Output: DONE

Input: This cannot be real
Output: Please provide more information to us in order to help you.

Input: This can not be real. I am so scared

Output:

User Input: {query}""",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "repetition_penalty": 1,
        },
        "model_id": "google/flan-ul2",
        "project_id": "d94470cd-0e46-4732-bd4a-fb47f687f7be",
        "moderations": {
            "hap": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
            },
            "pii": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
            },
        },
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": bearer_token,
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    predicted_text = (
        response.json()["results"][0]["generated_text"].replace("Output:", "").strip()
    )

    return predicted_text


def score_user_urgency(query):
    access_token = _get_access_token()
    bearer_token = f"Bearer {access_token}"
    url = f"{WATSONX_ML_BASE_URL}/ml/v1/text/generation?version=2023-05-29"

    body = {
        "input": f"""During a natural disaster, you will score the users urgency based on their query. The urgency score should be a number between 0 and 100, where 0 indicates no urgency and 100 indicates extreme urgency. Stop after returning the urgency score.

Some example

Input: I am looking for a place to stay
Output: 20

Input: I am hurt
Output:  70

Input: My house is on file
Output: 90

Input: I have run out of food
Output:  80


Input: Running out of water
Output: 70

Input: I am panicing
Output: 80

User Input: {query}""",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "repetition_penalty": 1,
        },
        "model_id": "google/flan-ul2",
        "project_id": "d94470cd-0e46-4732-bd4a-fb47f687f7be",
        "moderations": {
            "hap": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
            },
            "pii": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True},
                },
            },
        },
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": bearer_token,
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    predicted_text = (
        response.json()["results"][0]["generated_text"].replace("Output:", "").strip()
    )

    return int(predicted_text)


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
