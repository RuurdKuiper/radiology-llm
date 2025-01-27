# Function to send query to the LLM endpoint
import os
import streamlit as st
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Function to load full image volumes
def load_full_images(patient_id):
    image_folder = os.path.join("EHRs", f"EHR {patient_id}")  # Corresponding folder for the patient
    full_images = {}

    if not os.path.exists(image_folder):
        return full_images

    subfolders = [f for f in os.listdir(image_folder) if os.path.isdir(os.path.join(image_folder, f))]
    for subfolder in subfolders:
        if subfolder.startswith("CT") or subfolder.startswith("MRI"):
            subfolder_path = os.path.join(image_folder, subfolder)
            nifti_files = [f for f in os.listdir(subfolder_path) if f.endswith(".nii") or f.endswith(".nii.gz")]

            for nifti_file in nifti_files:
                file_path = os.path.join(subfolder_path, nifti_file)
                try:
                    img = nib.load(file_path)
                    data = img.get_fdata()

                    # Normalize for display
                    data = (data - np.min(data)) / (np.max(data) - np.min(data))

                    if subfolder not in full_images:
                        full_images[subfolder] = []
                    full_images[subfolder].append((nifti_file, data))
                except Exception as e:
                    st.write(f"Error loading {nifti_file}: {e}")

    return full_images

# Function to load EHR data from text files
def load_ehr_data(patient_id):
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

# Function to load images from nifti files
def load_images(patient_id):
    image_folder = os.path.join("EHRs", f"EHR {patient_id}")  # Corresponding folder for the patient
    available_images = []
    images = {}

    if not os.path.exists(image_folder):
        return available_images, images

    subfolders = [f for f in os.listdir(image_folder) if os.path.isdir(os.path.join(image_folder, f))]
    for subfolder in subfolders:
        if subfolder.startswith("CT") or subfolder.startswith("MRI"):
            available_images.append(subfolder)
            subfolder_path = os.path.join(image_folder, subfolder)
            nifti_files = [f for f in os.listdir(subfolder_path) if f.endswith(".nii") or f.endswith(".nii.gz")]

            for nifti_file in nifti_files:
                file_path = os.path.join(subfolder_path, nifti_file)
                try:
                    img = nib.load(file_path)
                    data = img.get_fdata()
                    middle_slice = data.shape[2] // 2  # Take the middle slice
                    slice_data = data[:, :, middle_slice]

                    # Normalize for display
                    slice_data = np.rot90(slice_data)  # Rotate for better orientation
                    slice_data = (slice_data - np.min(slice_data)) / (np.max(slice_data) - np.min(slice_data))

                    if subfolder not in images:
                        images[subfolder] = []
                    images[subfolder].append((nifti_file, slice_data))

                except Exception as e:
                    st.write(f"Error loading {nifti_file}: {e}")

    return available_images, images

# Function to display images and EHR in the sidebar
def display_sidebar_content(ehr_data, images):
    st.sidebar.subheader("Patient EHR Data")
    st.sidebar.text_area("EHR Details", value=ehr_data, height=300, disabled=False)

    st.sidebar.subheader("Patient Image Data")
    for image_type, slices in images.items():
        st.sidebar.subheader(f"{image_type}")
        for nifti_file, slice_data in slices:
            st.sidebar.text(f"{nifti_file} - Middle Slice")
            fig, ax = plt.subplots()
            ax.imshow(slice_data, cmap="gray")
            ax.axis("off")
            st.sidebar.pyplot(fig)