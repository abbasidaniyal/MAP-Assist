import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

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
        'longitude': [user_lon]
    })
    
    st.map(data, zoom=14)

# Chatbot in the second column (1/3 of the container)
with col2:
    st.header("Chatbot")

    # Custom CSS for chat layout
    st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column-reverse;
        height: 400px;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 10px;
    }
    .chat-input {
        margin-top: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    html_string = f"""
        <div class='chat-container'>
        {'<br>'.join([message for message in st.session_state.contents])}
        </div>
    """

    # Chat message container
    # st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.markdown(html_string, unsafe_allow_html=True)
    
    # print(f"{st.session_state.contents=}")
    # # import pdb; pdb.set_trace()
    # for message in reversed(st.session_state.contents):
    #     st.markdown("<p>" + message + "<p>")

    # # Close chat container div
    # st.markdown("</div>", unsafe_allow_html=True)

    # Chat input at the bottom
    prompt = st.chat_input("What would you like to know?", key='content')
    print(f"{prompt=}")

    if prompt:
        # Add user message to chat history
        st.session_state.contents.append(f"You said: {prompt}")
        
        # Simple bot response (you can replace this with your chatbot logic)
        response = f"Bot says: {prompt}"
        
        # Add assistant response to chat history
        st.session_state.contents.append(response)