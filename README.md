# YOLO Object Detection Streamlit App

A comprehensive Streamlit application for managing custom-trained YOLO object detection models and processing images with real-time detection results.

## Features

- **Project Management**: Create and manage multiple YOLO projects
- **Custom Model Support**: Upload your own custom-trained YOLO models in PyTorch format
- **Class Name Management**: Upload text files with custom class names
- **Image Processing**: Upload and process images with YOLO detection
- **Database Storage**: All projects and images are stored in SQLite database
- **Image Gallery**: View all processed images with detection results
- **Bounding Box Visualization**: Display detected objects with bounding boxes and labels
- **Detection Results**: View detailed detection results with confidence scores

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd yolo_test
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run yolo_test_app.py
   ```

## Usage

### 1. Create a Project

1. Navigate to "Create Project" in the sidebar
2. Enter project name and creator name
3. Upload your custom-trained YOLO model (.pt file)
4. Upload a text file with class names (one per line)
5. Click "Create Project"

**Example class names file (classes.txt)**:
```
person
car
dog
cat
bicycle
```

### 2. Upload and Process Images

1. Navigate to "Upload Images" in the sidebar
2. Select the project you want to use
3. Upload one or more images (JPG, PNG, BMP)
4. The app will automatically process images with YOLO detection
5. View original and processed images side by side
6. Check detection results in the data table

### 3. View Processed Images

1. Navigate to "View Images" in the sidebar
2. Select a project to view its processed images
3. Browse through the image gallery
4. Click "View Details" to see full-size images with detection results
5. View detection statistics and bounding box information

### 4. Project Management

1. Navigate to "Project Management" in the sidebar
2. View all created projects
3. See project details including model file and class names
4. Check the number of processed images per project
5. Delete projects if needed

## File Structure

```
yolo_test/
├── yolo_test_app.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── yolo_projects.db     # SQLite database (created automatically)
└── models/              # Directory for stored YOLO models (created automatically)
```

## Database Schema

### Projects Table
- `id`: Unique project identifier
- `name`: Project name
- `creator`: Creator name
- `model_path`: Path to the YOLO model file
- `class_names`: Text content of class names file
- `created_at`: Project creation timestamp

### Images Table
- `id`: Unique image identifier
- `project_id`: Foreign key to projects table
- `original_image`: Original image as BLOB
- `processed_image`: Processed image with detections as BLOB
- `detection_results`: JSON string of detection results
- `uploaded_at`: Image upload timestamp

## Technical Details

- **Framework**: Streamlit for web interface
- **YOLO Library**: Ultralytics YOLO for object detection
- **Database**: SQLite for data persistence
- **Image Processing**: PIL (Pillow) for image manipulation
- **Data Visualization**: Pandas for data tables

## Requirements

- Python 3.8+
- CUDA-compatible GPU (optional, for faster processing)
- Custom-trained YOLO model in PyTorch format (.pt)
- Text file with class names

## Troubleshooting

### Common Issues

1. **Model loading errors**: Ensure your YOLO model is in the correct PyTorch format
2. **Memory issues**: Large images may cause memory problems; consider resizing images
3. **CUDA errors**: If you don't have a GPU, the app will use CPU processing
4. **Database errors**: Delete `yolo_projects.db` to reset the database

### OpenCV Library Error (libGL.so.1)

If you encounter the error `ImportError: libGL.so.1: cannot open shared object file`, this is a common OpenCV dependency issue on Linux systems.

**Quick Fix:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y libgl1-mesa-glx libglib2.0-0

# CentOS/RHEL
sudo yum install mesa-libGL

# Fedora
sudo dnf install mesa-libGL

# Arch Linux
sudo pacman -S mesa
```

**Alternative Solutions:**

1. **Use the provided fix script:**
   ```bash
   python fix_opencv_deps.py
   ```

2. **Use headless OpenCV (no GUI features):**
   ```bash
   pip uninstall opencv-python
   pip install opencv-python-headless
   ```

3. **Use Docker (recommended for consistent environment):**
   ```bash
   docker run -p 8501:8501 -v $(pwd):/app streamlit/streamlit:latest
   ```

4. **The app will show helpful error messages** with specific instructions for your system.

**Note:** The app includes built-in error handling and will show you exactly what to do when this error occurs.

### Performance Tips

- Use smaller images for faster processing
- Ensure your YOLO model is optimized for inference
- Consider using GPU acceleration if available

## License

This project is open source and available under the MIT License.
