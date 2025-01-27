import os
import streamlit as st
from openai import OpenAI
from utils import load_ehr_data, load_images, load_full_images, display_sidebar_content

# Constants for the Hugging Face Inference Endpoint
BASE_URL = "https://qi9uxbfumzrk421l.us-east4.gcp.endpoints.huggingface.cloud/v1/"
API_KEY = st.secrets["HUGGINGFACE_API_KEY"]  # Retrieve API key from secrets.toml

# Initialize the OpenAI client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# Streamlit App
def main():
    st.set_page_config(layout="wide")
    st.title("Radiologist's Companion")

    # Get list of available patient folders
    ehr_root = "EHRs"
    patient_folders = [folder for folder in os.listdir(ehr_root) if folder.startswith("EHR") and os.path.isdir(os.path.join(ehr_root, folder))]
    patient_ids = sorted([folder.split(" ")[1] for folder in patient_folders])

    # Sidebar for Patient Selection
    patient_id = st.sidebar.selectbox("Select Patient", options=patient_ids, index=0)

    # Load EHR Data and Images
    ehr_data = load_ehr_data(patient_id)
    available_images, images = load_images(patient_id)

    # Display Sidebar Content
    display_sidebar_content(ehr_data, images)

    # Initialize session state for conversation history per patient
    if "patient_chats" not in st.session_state:
        st.session_state.patient_chats = {}

    if patient_id not in st.session_state.patient_chats:
        st.session_state.patient_chats[patient_id] = []

    # Main Content: Chat
    st.subheader("Chat")
    messages = st.session_state.patient_chats[patient_id]

    # Display existing chat messages
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input and stream assistant response
    if prompt := st.chat_input("Enter your query:"):
        # Add user message to the chat history
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare full conversation with system context
        full_messages = [{"role": "system", "content": "You are a radiologist's companion, here to answer questions about the patient and assist in the diagnosis if asked to do so."}]
        if ehr_data:
            full_messages.append({"role": "system", "content": f"Patient Information: {ehr_data}"})
        if available_images:
            full_messages.append({"role": "system", "content": f"Available image types for the patient: {', '.join(available_images)}."})
        full_messages.extend(messages)

        # Stream assistant response
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="tgi",
                messages=full_messages,
                max_tokens=300,
                stream=True
            )
            response = st.write_stream(stream)
            
        # Add assistant message to the chat history
        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
