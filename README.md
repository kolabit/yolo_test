# YOLO Object Detection Streamlit App

A comprehensive Streamlit application for managing custom-trained YOLO object detection models and processing images with real-time detection results.

## Features

- **Project Management**: Create and manage multiple YOLO projects
- **Custom Model Support**: Upload your own custom-trained YOLO models in PyTorch format
- **Unified Class Configuration**: Upload a single file with class names and optional colors
- **Data Validation**: Comprehensive validation using PyDantic for files and images
- **Image Processing**: Upload and process images with YOLO detection
- **Database Storage**: All projects and images are stored in SQLite database
- **Image Gallery**: View all processed images with detection results
- **Bounding Box Visualization**: Display detected objects with colored bounding boxes and large labels
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
4. Upload a unified class names and colors file (.txt)
5. Click "Create Project"

**Unified Class Names and Colors File Format:**

**Option 1 - Class names with custom colors:**
```
person:red
car:blue
dog:green
cat:yellow
bicycle:purple
```

**Option 2 - Class names only (default colors will be used):**
```
person
car
dog
cat
bicycle
```

**Option 3 - Mixed format (some with colors, some without):**
```
person:red
car:blue
dog:green
cat
bicycle:purple
motorcycle
```

**Available colors**: red, blue, green, yellow, purple, orange, cyan, magenta, lime, pink, brown, gray, navy, olive, teal, maroon, fuchsia, aqua

**Notes:**
- Lines starting with `#` are treated as comments
- If no color is specified for a class, default colors will be used in sequence
- You can mix both formats in the same file

### Data Validation

The app includes comprehensive data validation using PyDantic to ensure data integrity and prevent errors.

#### Class Names and Colors File Validation:
- **Class Name Validation**: Must be 1-100 characters, no special characters
- **Color Validation**: Must be one of the 18 predefined colors
- **Duplicate Detection**: No duplicate class names allowed
- **File Size**: Maximum 1000 classes per file
- **Format Validation**: Supports both `class_name:color` and `class_name` formats

#### Image Validation:
- **File Type**: Only JPG, JPEG, PNG, BMP files allowed
- **File Size**: Maximum 50MB per image
- **Dimensions**: Maximum 10000x10000 pixels
- **File Name**: No dangerous characters allowed
- **Image Format**: Must be a valid, readable image file

#### Validation Tool:
Use the standalone validation tool to check files before uploading:

```bash
# Validate class names and colors file
python validation_tool.py class_file sample_classes_with_colors.txt

# Validate a single image
python validation_tool.py image sample_images/image1.jpg

# Validate all images in a directory
python validation_tool.py directory sample_images/
```

### 2. Upload and Process Images

1. Navigate to "Upload Images" in the sidebar
2. Select the project you want to use
3. Upload one or more images (JPG, PNG, BMP)
4. The app will automatically process images with YOLO detection
5. View original and processed images side by side
6. Check detection results in the data table

**Enhanced Visualization Features:**
- **Colored Bounding Boxes**: Each object class can have a custom color
- **Large Text Labels**: Class names and confidence scores are displayed in 2x larger text
- **Background Labels**: Text labels have colored backgrounds for better readability
- **Thicker Box Lines**: Bounding boxes are drawn with thicker lines (4px) for better visibility

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