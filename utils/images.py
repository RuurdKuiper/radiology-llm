import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def load_images(patient_id):
    """
    Load the 2D middle slices of medical images for a given patient.
    
    :param patient_id: ID of the patient (e.g., "1").
    :return: A tuple containing available image types and their corresponding middle slices.
    """
    image_folder = os.path.join("EHRs", f"EHR {patient_id}")
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
                    slice_data = np.rot90(slice_data)  # Rotate for proper orientation
                    slice_data = (slice_data - np.min(slice_data)) / (np.max(slice_data) - np.min(slice_data))

                    if subfolder not in images:
                        images[subfolder] = []
                    images[subfolder].append((nifti_file, slice_data))
                except Exception as e:
                    st.write(f"Error loading {nifti_file}: {e}")

    return available_images, images

def display_sidebar_content(ehr_data, images):
    """
    Display patient EHR data and 2D image slices in the sidebar.
    
    :param ehr_data: The EHR data string for the selected patient.
    :param images: Dictionary containing image types and corresponding slices.
    """
    st.sidebar.subheader("Patient EHR Data")
    st.sidebar.text_area("EHR Details", value=ehr_data, height=300, disabled=True)

    st.sidebar.subheader("Patient Image Data")
    for image_type, slices in images.items():
        st.sidebar.subheader(f"{image_type}")
        for nifti_file, slice_data in slices:
            st.sidebar.text(f"{nifti_file} - Middle Slice")
            fig, ax = plt.subplots()
            ax.imshow(slice_data, cmap="gray")
            ax.axis("off")
            st.sidebar.pyplot(fig)