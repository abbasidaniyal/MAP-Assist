from src.agents.watsonx_utils import (
    HELP_IS_BUCKET_MAPPING,
    classify_user_message,
    is_user_input_enough_to_classify,
    score_user_urgency,
)
import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pydeck as pdk
from middlewares import base_mw
import html
import streamlit.components.v1 as components
import time
import numpy as np
import folium
from streamlit_folium import st_folium
import pandas as pd
from assets import *


# Set page configuration
st.set_page_config(layout="wide")
col1, col2 = st.columns([0.1, 0.9])

# Display the logo in the first column with specified width and height for a logo effect
with col1:
    st.image("assets/MAPAssist (3).png", width=200)



# Function to get location name from coordinates
def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="my_streamlit_app")
    try:
        location = geolocator.reverse(f"{latitude}, {longitude}")
        return location.address if location else "Unknown location"
    except GeocoderTimedOut:
        return "Location lookup timed out"

new_text_gen = False

if "help_filters" not in st.session_state:
    st.session_state["help_filters"] = []

if "refetch_volunteers" not in st.session_state:
    st.session_state["refetch_volunteers"] = True

if 'contents' not in st.session_state:
    st.session_state['contents'] = [
        {
                "author": "assistant",
                "message": "Hey I am Diya! Click on the location icon so that I can help you better. Now tell me, how may I assist you?",
        }
    ]

if "volunteers" not in st.session_state:
    st.session_state["volunteers"] = []

if "location" not in st.session_state:
    st.session_state["location"] = []


if "user_risk_category" not in st.session_state:
    st.session_state["user_risk_category"] = None

if "user_risk_score" not in st.session_state:
    st.session_state["user_risk_score"] = None

    
with st.container(height = 1024, border=False):


    coll1, coll2 = st.columns([0.1,4])
    with coll1:
        # st.header("MAPAssist")
        location = streamlit_geolocation()
    

    if st.session_state['location'] != location:
        st.session_state['refetch_volunteers']  = True

    st.session_state['location'] = location

    # Create a two-column layout
    col1, col2 = st.columns([2, 1])
        # Map in the first column (2/3 of the container)
    with col1:
        if location and location.get('latitude') and location.get('longitude'):
            user_lat = location['latitude']
            user_lon = location['longitude']
            location_name = get_location_name(user_lat, user_lon)
            with coll2:
                
                st.success(f"Location obtained: {location_name}")
        else:
            user_lat, user_lon = 29.6516, -82.3248  # Default to Gainesville, Florida
            location_name = "Gainesville, Florida"
            with coll2:
                st.info(f"Using default location: {location_name}")

        data = pd.DataFrame({
            'latitude': [user_lat],
            'longitude': [user_lon],
            'location_name': [location_name]
        })
        
        # Define icon properties
        icon_data = {
            "url": "https://img.icons8.com/ios-filled/50/000000/marker.png",  # Change this URL to your preferred icon
            "width": 128,
            "height": 128,
            "anchorY": 128  # Adjust this based on the icon’s dimensions
        }
       
        m = folium.Map(location=[user_lat, user_lon], zoom_start=14, height=50)

        RADIUS = 2  # in miles
        CLOSE_RADIUS = 0.5  # in miles

        markers = None
        if st.session_state.refetch_volunteers:
            markers = base_mw.filter_nearby_people((user_lat, user_lon), max_distance=RADIUS, helps_filters=st.session_state.help_filters)
            st.session_state.refetch_volunteers = False
            st.session_state.volunteers = markers
        else:
            markers = st.session_state.volunteers
        markers = markers[:100]

        volunteer_popup_icon =folium.Icon("blue")
        for _, marker in markers.iterrows():

            address_link = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/{marker['Latitude']},{marker['Longitude']}/"
            # address_link = f"http://maps.google.com/maps?z=14&t=m&q=loc:{marker['Latitude']}+{marker['Longitude']}"

            if marker['Type'] == "Police":
                marker_icon = folium.CustomIcon(
                icon_image='assets/police-station.png',  # Path to your PNG icon
                icon_size=(30, 30)) # Adjust size as needed
                
            elif marker['Type'] == "Medical":
                marker_icon = folium.CustomIcon(
                icon_image='assets/healthcare.png',  # Path to your PNG icon
                icon_size=(30, 30)) # Adjust size as needed
                

            elif marker['Type'] == "Supplies":
                marker_icon = folium.CustomIcon(
                icon_image='assets/grocery.png',  # Path to your PNG icon
                icon_size=(30, 30))  # Adjust size as needed
                
            elif marker['Gender'] == 'Female':
                marker_icon = folium.Icon('pink')
            elif marker['Gender'] == 'Male':
                marker_icon = folium.Icon('blue')
            else:
                marker_icon = folium.Icon('pink')

            folium.Marker(
                location=[float(marker["Latitude"]), float(marker["Longitude"])], popup=folium.Popup(f"""
                <b>{marker["Name"]}</b> <br>
                <a href='tel:{marker["Phone"]}'> {str(marker["Phone"])} </a> <br>
                <a href={address_link} target='_blank'>Directions </a> <br>
                {marker["Gender"] if str(marker["Gender"]) != "nan" else "Organization" } <br>
                Can help with {"  ".join(marker["Helps"].split(";"))}
                """, parse_html=False), tooltip=marker["Name"], icon=marker_icon).add_to(m)

        user_popup_icon =folium.Icon("red")
        folium.Marker(
            location=[user_lat, user_lon], popup=folium.Popup(f"""You are here!""", parse_html=False), 
            tooltip="Me", icon=user_popup_icon).add_to(m)

        folium.Circle([user_lat, user_lon], radius=RADIUS*1609, color="Orange").add_to(m)
        folium.Circle([user_lat, user_lon], radius=CLOSE_RADIUS*1609, color="Green").add_to(m)
            # call to render Folium map in Streamlit
        st_data = st_folium(m, width=None)

    # Chatbot in the second column (1/3 of the container)

    
    with col2:
        
        st.markdown("<h3 style='text-align: left; color: white;'>Diya! Your virtual buddy..</h3>", unsafe_allow_html=True)

        #writing stream
        def generate_text(message):
            for char in message:
                yield char
                time.sleep(0.01)
            # Handle chat input
        

        def on_submit_chat():
            global new_text_gen
            new_text_gen = True
            prompt = st.session_state.user_input

            # Add user message to chat history
            st.session_state.contents.append({
                "author": "user",
                "message": prompt,
            })

            # Call your API or middleware
            response = None

            # we need to predict category
            if st.session_state.user_risk_category is None:
                # check if we can predict the category

                all_user_prompts_concat = "\n".join(
                    [
                        mess["message"]
                        for mess in st.session_state.contents
                        if mess["author"] == "user"
                    ]
                )

                # can_classify = is_user_input_enough_to_classify(all_user_prompts_concat)
                can_classify = "DONE" # skipping the classification for now since it does not perform well

                print(f"{can_classify=}")

                if can_classify == "DONE":
                    st.session_state.user_risk_category = classify_user_message(
                        all_user_prompts_concat
                    )
                    print(f"{st.session_state.user_risk_category=}")
                    st.session_state.user_risk_score = score_user_urgency(
                        all_user_prompts_concat
                    )
                    print(f"{st.session_state.user_risk_score=}")

                    # branch out
                    if st.session_state.user_risk_score > 90:
                        response = "I’m sorry to hear you’re in distress. Unfortunately, I’m not able to assist with urgent situations. Please reach out to emergency services like 911 if you need immediate help."
                    elif st.session_state.user_risk_score > 50:
                        # community
                        response = "I’m sorry to hear that you’re in distress. Let me help you find support nearby. On your left, you’ll see details of local volunteers who may be able to assist\n\n"
                        response += base_mw.common_middleware(
                            st.session_state.contents, location
                        )

                        st.session_state.help_filters = HELP_IS_BUCKET_MAPPING[
                            st.session_state.user_risk_category.name
                        ]
                        print(f"{st.session_state.help_filters=}")
                        st.session_state.refetch_volunteers = True

                    else:
                        # education
                        response = "I’m sorry to hear that you’re in distress. Let me get some help for you.\n\n"
                        response += base_mw.common_middleware(
                            st.session_state.contents, location
                        )

                elif can_classify == "Others":
                    # edge case, ask for more information
                    response = "I am sorry to hear that you are in distress. Can you provide me with more information?"
                else:
                    response = can_classify.title()
            else:
                response = "I am sorry to hear that you are in distress. Let me get some help for you.\n\n"
                response += base_mw.common_middleware(
                    st.session_state.contents, location
                )
            

            # Add bot response to chat history
            st.session_state.contents.append(
                {
                    "author": "assistant",
                    "message": response,
                }
            )
            

        with st.container(height=450):

            # Display chat messages
            for i, message in enumerate(st.session_state.contents):
                with st.chat_message(message["author"]):
                    if message["author"] == "assistant" and i >= len(st.session_state.contents)-2 and new_text_gen:
                        st.write_stream(generate_text(message['message']))
                        new_text_gen = False
                    else:
                        st.write(message["message"])



        st.chat_input("What would you like to know?", key='user_input', on_submit=on_submit_chat)
