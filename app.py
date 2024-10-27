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

# Initialize session state for chat messages
if 'contents' not in st.session_state:
    st.session_state['contents'] = [
        {
                "author": "assistant",
                "message": "Hey I am Diya! How may I assist you?",
        }
    ]

if 'help_filters' not in st.session_state:
    st.session_state['help_filters'] = []

if 'refetch_volunteers' not in st.session_state:
    st.session_state['refetch_volunteers'] = True

if 'volunteers' not in st.session_state:
    st.session_state['volunteers'] = []

if 'location' not in st.session_state:
    st.session_state['location'] = []

with st.container(height = 600, border=False):

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

        # m = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
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
        markers = markers[:10]

        volunteer_popup_icon =folium.Icon("blue")
        for _, marker in markers.iterrows():

            address_link = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/{marker['Latitude']},{marker['Longitude']}/"
            # address_link = f"http://maps.google.com/maps?z=14&t=m&q=loc:{marker['Latitude']}+{marker['Longitude']}"

            if marker['Gender'] == 'Female':
                marker_icon = folium.Icon('pink')
            else:
                marker_icon = folium.Icon('blue')

            folium.Marker(
                location=[float(marker["Latitude"]), float(marker["Longitude"])], popup=folium.Popup(f"""
                <b>{marker["Name"]}</b> <br>
                <a href='tel:{marker["Phone"]}'> {str(marker["Phone"])} </a> <br>
                <a href={address_link} target='_blank'>Directions </a> <br>
                {marker["Gender"]} <br>
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
        
        # st.header("MAPAssist", align=right)
        st.markdown("<h3 style='text-align: left; color: white;'>Diya! Your virtual buddy..</h3>", unsafe_allow_html=True)
        # st.image("assets\MAPAssist (3).png")


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
                time.sleep(0.01)
            # Handle chat input
        
        new_text_gen = False

        def on_submit_chat():
            prompt = st.session_state.user_input

            # Add user message to chat history
            st.session_state.contents.append({
                "author": "user",
                "message": prompt,
            })

            # Call your API or middleware
            response = base_mw.common_middleware(st.session_state.contents, location)

            new_text_gen = True

            
            # Add bot response to chat history
            st.session_state.contents.append({
                "author": "assistant",
                "message": response,
            })
        

        with st.container(height=450):

            # Display chat messages
            for i, message in enumerate(st.session_state.contents):
                with st.chat_message(message["author"]):
                    if message["author"] == "assistant" and i >= len(st.session_state.contents)-2 and new_text_gen:
                        st.write_stream(generate_text(message['message']))
                        new_text_gen = False
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