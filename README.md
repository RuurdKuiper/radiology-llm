# Radiologist's Companion Streamlit App

## Overview

The Radiologist's Companion is an interactive Streamlit app designed to assist radiologists in analyzing patient data, including textual Electronic Health Records (EHRs) and medical images (e.g., CT and MRI scans). The app integrates with a language model hosted on a Hugging Face Inference Endpoint to provide AI-driven insights and answer radiologist queries.

---

## Features

1. **Dynamic Patient Selection**:

   - Automatically detects available patient data folders in the `EHRs` directory.
   - Provides a dropdown menu to select patients dynamically.

2. **EHR Data Display**:

   - Concatenates all text files in the selected patient's folder and displays them in the sidebar.

3. **Medical Image Visualization**:

   - Supports NIfTI (.nii, .nii.gz) files organized under image-specific subfolders (e.g., `CT 1`, `MRI 2`).
   - Displays middle slices of 3D medical images in the sidebar.

4. **AI-Powered Chat**:

   - Provides an AI-driven chat interface for radiologists to ask questions and get contextual responses based on EHR and available images.
   - Keeps conversation history for each patient.

5. **Interactive Sidebar**:

   - Combines both EHR data and medical image visualizations for convenient access.

---

## Folder Structure

The app expects the following folder structure:

```
EHRs/
│
├── EHR 1/
│   ├── record1.txt
│   ├── record2.txt
│   ├── CT 1/
│   │   ├── image1.nii
│   │   └── image2.nii.gz
│   └── MRI 2/
│       └── image1.nii
│
├── EHR 2/
│   ├── record1.txt
│   ├── CT 1/
│   │   └── image1.nii.gz
│   └── MRI 1/
│       └── image1.nii
│
└── ...
```

- **Text Files**: Contain EHR data for each patient.
- **Image Folders**: Contain subfolders named by modality (e.g., `CT 1`, `MRI 2`) with NIfTI image files.

---

## Installation

1. Clone this repository:

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your Hugging Face API key to `secrets.toml`:

   ```toml
   [secrets]
   HUGGINGFACE_API_KEY = "your_api_key_here"
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

---

## Usage

1. Place patient data in the `EHRs` folder following the folder structure described above.
2. Launch the app and select a patient from the dropdown menu in the sidebar.
3. View EHR data and images in the sidebar.
4. Use the chat interface to ask questions or seek assistance from the AI model.

---

## Requirements

- Python 3.8+
- Libraries: `streamlit`, `numpy`, `nibabel`, `matplotlib`, `openai`

---

## Limitations

- The app processes only the middle slice of 3D medical images for visualization.
- Requires an active Hugging Face API key for the AI chat functionality.

---

## Future Enhancements

- Enable visualization of multiple slices or full 3D volume.
- Add support for more medical image formats.
- Integrate additional AI tools for image segmentation and analysis.

---

## License

This project is licensed under the MIT License.

