import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import os
import streamlit as st

def segment_organ(file_path, organ_name):
    """
    Simulates a tool call for organ segmentation by overlaying the organ's segmentation on the CT scan.

    :param ct_path: Path to the CT scan file.
    :param organ_name: Name of the organ to segment (e.g., "spleen").
    :return: Tuple (success: bool, message: str).
    """
    segmentation_folder = os.path.join(os.path.dirname(file_path), "Segmentations")
    segmentation_file = os.path.join(segmentation_folder, f"{organ_name}.nii.gz")

    if not os.path.exists(segmentation_file):
        return False, f"Segmentation for {organ_name} not found."

    try:
        # Load CT scan and segmentation
        scan = nib.load(file_path).get_fdata()
        segmentation = nib.load(segmentation_file).get_fdata()

        # # Normalize and prepare overlay
        # middle_slice = scan[:, :, scan.shape[2] // 2]
        # middle_slice_seg = segmentation[:, :, segmentation.shape[2] // 2]

        # middle_slice = (middle_slice - np.min(middle_slice)) / (np.max(middle_slice) - np.min(middle_slice))

        # # Create overlay
        # fig, ax = plt.subplots()
        # ax.imshow(middle_slice, cmap="gray")
        # ax.imshow(middle_slice_seg*128, cmap="viridis", alpha=0.5)
        # ax.axis("off")
        # st.pyplot(fig)

        return f"Segmentation for {organ_name} performed successfully.", scan, segmentation
    except Exception as e:
        return f"Error during segmentation: {str(e)}", None, None


def display_interactive_viewer(scan, segmentation, scan_path, organ_name):
    """
    Display an interactive slice viewer for the CT scan and its segmentation in the sidebar, always at the top.

    :param scan: Numpy array of the CT scan data.
    :param segmentation: Numpy array of the segmentation data.
    :param scan_path: Path to the CT scan file (used for unique key generation).
    :param organ_name: Name of the organ to segment (used for unique key generation).
    """
    # Sidebar container to force consistent placement
    viewer_container = st.sidebar.container()

    with viewer_container:
        # Generate a unique key for the slider based on scan_path and organ_name
        unique_key = f"slice_slider_{os.path.basename(scan_path)}_{organ_name}"

        # Slider to select the slice
        num_slices = scan.shape[2]
        selected_slice = st.slider("Select Slice", 0, num_slices - 1, num_slices // 2, key=unique_key)

        # Display the selected slice
        slice_data = scan[:, :, selected_slice]
        slice_data = (slice_data - np.min(slice_data)) / (np.max(slice_data) - np.min(slice_data))

        st.write(f"Displaying slice {selected_slice}/{num_slices - 1}")
        fig, ax = plt.subplots()
        ax.imshow(slice_data, cmap="gray")
        if segmentation is not None:
            seg_slice = segmentation[:, :, selected_slice]
            ax.imshow(seg_slice, cmap="viridis", alpha=0.5)
        ax.axis("off")
        st.pyplot(fig)



