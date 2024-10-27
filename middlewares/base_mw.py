import json
from typing import Dict
import requests

from geopy.distance import geodesic
from typing import List, Optional
import pandas as pd

from src.res_req_schema import get_status_payload
from src.agents.watsonx_utils import get_education_content_help


def watsonx_base_call(payload, context):
    # r = requests.post('https://example.com', json=json.dumps(payload))
    # r = requests.get('http://time.jsontest.com/')

    response_text = get_education_content_help(payload)
    return response_text
                 

def common_middleware(context, data=None) -> Dict[str, str]:
    """
    query: text prompt by the user
    data: Additional data when required. For example lat and lng for the first prompt.
    context: history of the prompts for a particular user
    """

    payload = {
        "context": context,
        "data": data,
    }
    watson_res = watsonx_base_call(payload, context)
    return watson_res

    

def filter_nearby_people(target_location: tuple, max_distance: float, helps_filters: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Filters the dataframe to find people within a specified distance from a given location
    and optionally filters based on 'Helps' criteria.

    Parameters:
    - data: pd.DataFrame - Data containing people's information.
    - target_location: tuple - Target latitude and longitude.
    - max_distance: float - Maximum distance in miles.
    - helps_filters: Optional[List[str]] - List of 'Helps' filters to apply.

    Returns:
    - pd.DataFrame: Filtered DataFrame.
    """

    data = pd.read_csv("fixtures/volunteers_gainesville.csv")

    filtered_data = []

    
    # Iterate through each row to calculate distance and filter
    for _, row in data.iterrows():
        person_location = (row['Latitude'], row['Longitude'])
        distance = geodesic(target_location, person_location).miles
        
        # Check if within max distance
        if distance <= max_distance:
            # Check if helps filter applies, if provided
            if helps_filters:
                helps_list = row['Helps'].split(';')
                if any(help_filter in helps_list for help_filter in helps_filters):
                    filtered_data.append(row)
            else:
                filtered_data.append(row)
    
    # Convert list of rows back to DataFrame
    return pd.DataFrame(filtered_data)



