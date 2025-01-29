import os
import json
import streamlit as st
from openai import OpenAI
from utils.ehr import load_ehr_data
from utils.images import load_images, display_sidebar_content
from utils.segmentation import segment_organ, display_interactive_viewer

# Constants for the Hugging Face Inference Endpoint
BASE_URL = "https://qi9uxbfumzrk421l.us-east4.gcp.endpoints.huggingface.cloud/v1/"
BASE_URL = "https://jvpm7uo9o5f8kcsl.us-east4.gcp.endpoints.huggingface.cloud/v1/"
API_KEY = st.secrets["HUGGINGFACE_API_KEY"]  # Retrieve API key from secrets.toml

# Initialize the OpenAI client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
st.set_page_config(layout="wide")

# Streamlit App
def main():
    
    st.title("Radiologist's Companion")

    viewer_container = st.sidebar.container()

    # Ensure the interactive viewer persists across reruns
    if "current_scan" in st.session_state and "current_segmentation" in st.session_state:
        with viewer_container:    
            display_interactive_viewer(
                st.session_state["current_scan"],
                st.session_state["current_segmentation"],
                st.session_state["current_scan_path"],
                st.session_state["current_organ"],
            )

    # Get list of available patient folders
    ehr_root = "EHRs"
    patient_folders = [folder for folder in os.listdir(ehr_root) if os.path.isdir(os.path.join(ehr_root, folder))]
    patient_ids = sorted(patient_folders)

    # Sidebar for Patient Selection
    patient_id = st.sidebar.selectbox("Select Patient", options=patient_ids, index=0)
    # Reset segmentation state when switching patients
    if st.session_state.get("previous_patient_id") != patient_id:
        st.session_state["previous_patient_id"] = patient_id
        for key in ["current_scan", "current_segmentation", "current_scan_path", "current_organ"]:
            st.session_state.pop(key, None)
            
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

    # Initialize session state for conversation history per patient
    if "patient_chats" not in st.session_state:
        st.session_state.patient_chats = {}

    if patient_id not in st.session_state.patient_chats:
        st.session_state.patient_chats[patient_id] = []

    messages = st.session_state.patient_chats[patient_id]

    # Add an AI-generated system message at the top of the chat if it's the first message
    if len(messages) == 0:
        welcome_message = (
            "**Welcome to the Radiologist's Companion!**\n\n"
            "You can ask me about the patient's medical history or available imaging data.\n"
            "- I can summarize key details from the EHR.\n"
            "- I can tell you which medical images are available.\n"
            "- If you'd like an organ segmentation (e.g. spleen, liver, kidney_left, colon, femur_right) on an abdominal CT scan, just ask!\n\n"
            "**Example Requests:**\n"
            "- \"What do we know about this patient?\"\n"
            "- \"Which images are available for this patient?\"\n"
            "- \"Can you segment the spleen from the CT scan?\"\n"
        )
        messages.append({"role": "assistant", "content": welcome_message})

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
        full_messages = [
            {
                "role": "system",
                "content": (
                    "You are a radiologist's companion, here to answer questions about the patient and assist in the diagnosis if asked to do so. "
                    "You are also able to call specialized tools. "
                    "At the moment, you only have one tool available: an organ segmentation algorithm for abdominal CTs."
                    "If the user requests an organ segmentation, you can call the `segment_organ` function. "
                    "To call this function, output a JSON object in the following structure:\n\n"
                    "{\n"
                    "  \"function\": \"segment_organ\",\n"
                    "  \"arguments\": {\n"
                    "    \"scan_path\": \"<path_to_ct_scan>\",\n"
                    "    \"organ\": \"<organ_name>\"\n"
                    "  }\n"
                    "}\n\n"
                    "Where:\n"
                    "- `<path_to_ct_scan>` is the full path to the CT scan like 'EHRs/<PATIENT ID>/CT <CT_NUMBER>/ct.nii.gz' (e.g., 'EHRs/1/CT 1/ct.nii.gz', or 'EHRs/2/CT 1/ct.nii.gz').\n"
                    "- `<organ_name>` is the name of the organ to segment (e.g., 'spleen', 'bladder').\n\n"
                    "Once you call the function, the app will execute it and return the result to the user. You will not be able to see it and do not need to comment on it."
                ),
            }
        ]
        full_messages.append({"role": "system", "content": f"Patient Information: {ehr_data if ehr_data else 'None'}"})
        full_messages.append({"role": "system", "content": f"Available images for the patient: {', '.join(available_images) if available_images else 'None'}. If asked about the available images, only mention the ones available here, and not all the ones described the EHR. If no images are shown here, please tell the user."})
        print(available_images)
        full_messages.extend(messages)

        # Stream assistant response
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model="tgi",
                    messages=full_messages,
                    max_tokens=300,
                    stream=True,
                    temperature=0,
                )
                response_text = st.write_stream(stream)
            except:
                response_text = "The LLM appears to be offline, probably because it has been idle for more than 15 minutes. It should be starting back up now, please wait 5-10 minutes and try again."
        
        # Add assistant message to the chat history
        messages.append({"role": "assistant", "content": response_text})

        # Check if the response contains a function call
        try:
            # Separate JSON function call from any additional text
            response_json_start = response_text.find("{")
            response_json_end = response_text.rfind("}") + 1

            if response_json_start != -1 and response_json_end != -1:
                json_part = response_text[response_json_start:response_json_end]

                # Process the JSON function call
                response_json = json.loads(json_part)
                if response_json.get("function") == "segment_organ":
                    scan_path = response_json["arguments"].get("scan_path")
                    organ = response_json["arguments"].get("organ")

                    if scan_path and organ:
                        if "current_scan" in st.session_state:
                            del st.session_state["current_scan"]
                        if "current_segmentation" in st.session_state:
                            del st.session_state["current_segmentation"]

                        # Call the segmentation function
                        overlay_message, scan, segmentation = segment_organ(scan_path, organ)
                        
                        if scan is not None and segmentation is not None:
                            # Save the segmentation state in session_state
                            st.session_state["current_scan"] = scan
                            st.session_state["current_segmentation"] = segmentation
                            st.session_state["current_scan_path"] = scan_path
                            st.session_state["current_organ"] = organ

                        messages.append({"role": "assistant", "content": overlay_message})
                        with st.chat_message("assistant"):
                            st.markdown(overlay_message)
                        st.rerun()
                    else:
                        error_message = "Invalid arguments for function call. Please provide both `ct_path` and `organ`."
                        messages.append({"role": "assistant", "content": error_message})
                        with st.chat_message("assistant"):
                            st.markdown(error_message)
                            
        except json.JSONDecodeError:
            # If no valid JSON is present, just add the plain response
            messages.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    main()

# Hi! Can you show the spleen of EHR 1's CT?
