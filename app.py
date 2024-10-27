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


# Set page configuration
st.set_page_config(layout="wide")

# Function to get location name from coordinates
def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="my_streamlit_app")
    try:
        location = geolocator.reverse(f"{latitude}, {longitude}")
        return location.address if location else "Unknown location"
    except GeocoderTimedOut:
        return "Location lookup timed out"

# Initialize session state for chat messages
if 'contents' not in st.session_state:
    st.session_state['contents'] = []

st.header("Interactive Map")
location = streamlit_geolocation()

# Create a two-column layout
col1, col2 = st.columns([2, 1])

# Map in the first column (2/3 of the container)
with col1:
    if location and location.get('latitude') and location.get('longitude'):
        user_lat = location['latitude']
        user_lon = location['longitude']
        location_name = get_location_name(user_lat, user_lon)
        st.success(f"Location obtained: {location_name}")
    else:
        user_lat, user_lon = 29.6516, -82.3248  # Default to Gainesville, Florida
        location_name = "Gainesville, Florida"
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
    # data["icon_data"] = None
    # for i in data.index:
    #     data["icon_data"][i] = icon_data

    # # Create the pydeck chart with IconLayer and tooltip
    # st.pydeck_chart(
    #     pdk.Deck(
    #         map_style="mapbox://styles/mapbox/light-v9",
    #         initial_view_state=pdk.ViewState(
    #             latitude=user_lat,
    #             longitude=user_lon,
    #             zoom=14,
    #             pitch=50
    #         ),
    #         layers=[
    #             pdk.Layer(
    #                 "IconLayer",
    #                 data=data,
    #                 get_icon="icon_data",
    #                 get_size=4,
    #                 size_scale=10,
    #                 get_position=["longitude", "latitude"],
    #             ),
    #         ],
    #         tooltip={"text": "{location_name}"},  # Tooltip to display the location name
    #     )
    # )

    m = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
    folium.Marker(
        [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
    ).add_to(m)

    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725)

# Chatbot in the second column (1/3 of the container)

with col2:
    st.header("Chatbot")

    # # Custom CSS for chat layout using your provided styles
    # st.markdown("""
    # <style>
    # .chat-row {
    #     display: flex;
    #     margin: 5px;
    #     width: 100%;
    # }
    # .row-reverse {
    #     flex-direction: row-reverse;
    # }
    # .chat-bubble {
    #     font-family: "Source Sans Pro", sans-serif, "Segoe UI", "Roboto", sans-serif;
    #     border: 1px solid transparent;
    #     padding: 5px 10px;
    #     margin: 0px 7px;
    #     max-width: 70%;
    # }
    # .ai-bubble {
    #     background: orange;
    #     border-radius: 10px;
    # }
    # .human-bubble {
    #     background: linear-gradient(135deg, rgb(0, 178, 255) 0%, rgb(0, 106, 255) 100%); 
    #     color: white;
    #     border-radius: 20px;
    # }
    # .chat-icon {
    #     border-radius: 5px;
    #     width: 32px;
    #     height: 32px;
    # }
    # </style>
    # """, unsafe_allow_html=True)

    #writing stream
    def generate_text(message):
        for char in message:
            yield char
            time.sleep(0.1)
        # Handle chat input
    def on_submit_chat():
        prompt = st.session_state.user_input

        # Add user message to chat history
        st.session_state.contents.append({
            "author": "user",
            "message": prompt,
        })

        # Call your API or middleware
        api_res = base_mw.common_middleware(prompt, [msg['message'] for msg in st.session_state.contents], location)

        if api_res['status'] == "success":
            response = str(api_res['res'])
        else:
            response = "Something went wrong"
        
        # Add bot response to chat history
        st.session_state.contents.append({
            "author": "assistant",
            "message": response,
        })
    

    with st.container(height=450):

        # Display chat messages
        for i, message in enumerate(st.session_state.contents):
            with st.chat_message(message["author"]):
                if message["author"] == "assistant" and i >= len(st.session_state.contents)-2:
                    st.write_stream(generate_text(message['message']))
                else:
                    st.write(message["message"])
    # HTML for chat history
    # chat_history = ""
    # for each_message in st.session_state.contents:
    #     if "You said:" in each_message:
    #         # User message style
    #         # chat_history += f"""
    #         # <div class='chat-row row-reverse'>
    #         #     <img class='chat-icon' src='https://img.icons8.com/?size=100&id=43460&format=png&color=000000'>
    #         #     <div class='chat-bubble human-bubble'>{message}</div>
    #         # </div>
    #         # """
    #         message = st.chat_message("user")
    #         message.write(each_message)
    #     else:
    #         # Bot message style
    #         # chat_history += f"""
    #         # <div class='chat-row'>
    #         #     <img class='chat-icon' src='https://img.icons8.com/ios-filled/50/000000/bot.png'>
    #         #     <div class='chat-bubble ai-bubble'>{message}</div>
    #         # </div>
    #         # """
    #         message = st.chat_message("assistant")
    #         message.write(each_message)

    # Display chat history container
    # with st.container():
        # st.markdown(chat_history, unsafe_allow_html=True)




    # Chat input at the bottom
    st.chat_input("What would you like to know?", key='user_input', on_submit=on_submit_chat)
