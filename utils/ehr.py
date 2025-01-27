import os
import streamlit as st

def load_ehr_data(patient_id):
    """
    Load and concatenate all text files in the EHR directory for a given patient.
    
    :param patient_id: ID of the patient (e.g., "1").
    :return: A single string containing the concatenated EHR data or an error message.
    """
    ehr_folder = os.path.join("EHRs", f"EHR {patient_id}")
    ehr_texts = []

    if not os.path.exists(ehr_folder):
        return "EHR data not found for the specified patient."

    for file_name in os.listdir(ehr_folder):
        file_path = os.path.join(ehr_folder, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".txt"):
            try:
                with open(file_path, "r") as file:
                    ehr_texts.append(file.read())
            except Exception as e:
                st.write(f"Error reading {file_name}: {e}")

    return "\n\n".join(ehr_texts)
