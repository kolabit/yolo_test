import streamlit as st
import sqlite3
import os
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import torch
from ultralytics import YOLO
import pandas as pd
import numpy as np
from datetime import datetime
import tempfile

# Page configuration
st.set_page_config(
    page_title="YOLO Object Detection App",
    page_icon="🔍",
    layout="wide"
)

# Handle OpenCV import with error handling
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError as e:
    if "libGL.so.1" in str(e):
        st.error("""
        ⚠️ **OpenCV Library Error Detected**
        
        The application requires additional system libraries for OpenCV. Please install them using:
        
        ```bash
        sudo apt update && sudo apt install -y libgl1-mesa-glx libglib2.0-0
        ```
        
        Or if you're using a different Linux distribution:
        
        **Ubuntu/Debian:**
        ```bash
        sudo apt install libgl1-mesa-glx libglib2.0-0
        ```
        
        **CentOS/RHEL/Fedora:**
        ```bash
        sudo yum install mesa-libGL
        # or
        sudo dnf install mesa-libGL
        ```
        
        **Arch Linux:**
        ```bash
        sudo pacman -S mesa
        ```
        
        After installing the libraries, restart the Streamlit app.
        """)
        YOLO_AVAILABLE = False
    else:
        st.error(f"Error importing YOLO: {e}")
        YOLO_AVAILABLE = False

# Database setup
def init_database():
    """Initialize SQLite database with tables for projects and images"""
    conn = sqlite3.connect('yolo_projects.db')
    cursor = conn.cursor()
    
    # Create projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            creator TEXT NOT NULL,
            model_path TEXT NOT NULL,
            class_names TEXT NOT NULL,
            color_config TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            original_image BLOB,
            processed_image BLOB,
            detection_results TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

def show_installation_instructions():
    """Show installation instructions for missing dependencies"""
    st.error("""
    ⚠️ **System Dependencies Missing**
    
    The YOLO object detection functionality requires additional system libraries.
    
    **Quick Fix (Ubuntu/Debian):**
    ```bash
    sudo apt update && sudo apt install -y libgl1-mesa-glx libglib2.0-0
    ```
    
    **Alternative Solutions:**
    
    1. **Install system libraries:**
       - Ubuntu/Debian: `sudo apt install libgl1-mesa-glx libglib2.0-0`
       - CentOS/RHEL: `sudo yum install mesa-libGL`
       - Fedora: `sudo dnf install mesa-libGL`
       - Arch: `sudo pacman -S mesa`
    
    2. **Use headless OpenCV (if you don't need GUI):**
       ```bash
       pip uninstall opencv-python
       pip install opencv-python-headless
       ```
    
    3. **Use Docker (recommended for consistent environment):**
       ```bash
       docker run -p 8501:8501 -v $(pwd):/app streamlit/streamlit:latest
       ```
    
    After installing the libraries, restart the Streamlit app.
    """)
    
    st.info("""
    **Note:** This error occurs because OpenCV (used by YOLO) requires system graphics libraries.
    The app will work normally once the dependencies are installed.
    """)

def save_project_to_db(name, creator, model_file, class_names_file, color_config_file=None):
    """Save project information to database"""
    conn = sqlite3.connect('yolo_projects.db')
    cursor = conn.cursor()
    
    # Read model file
    model_bytes = model_file.read()
    
    # Read class names file
    class_names_content = class_names_file.read().decode('utf-8')
    
    # Read color config file if provided
    color_config_content = ""
    if color_config_file:
        color_config_content = color_config_file.read().decode('utf-8')
    
    # Save model to temporary file
    temp_model_path = f"models/{name}_{creator}.pt"
    os.makedirs("models", exist_ok=True)
    with open(temp_model_path, 'wb') as f:
        f.write(model_bytes)
    
    cursor.execute('''
        INSERT INTO projects (name, creator, model_path, class_names, color_config)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, creator, temp_model_path, class_names_content, color_config_content))
    
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_all_projects():
    """Get all projects from database"""
    conn = sqlite3.connect('yolo_projects.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
    projects = cursor.fetchall()
    conn.close()
    return projects

def save_image_to_db(project_id, original_image, processed_image, detection_results):
    """Save image and detection results to database"""
    conn = sqlite3.connect('yolo_projects.db')
    cursor = conn.cursor()
    
    # Convert images to bytes
    original_bytes = original_image
    processed_bytes = processed_image
    
    cursor.execute('''
        INSERT INTO images (project_id, original_image, processed_image, detection_results)
        VALUES (?, ?, ?, ?)
    ''', (project_id, original_bytes, processed_bytes, detection_results))
    
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_project_images(project_id):
    """Get all images for a specific project"""
    conn = sqlite3.connect('yolo_projects.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM images WHERE project_id = ? ORDER BY uploaded_at DESC', (project_id,))
    images = cursor.fetchall()
    conn.close()
    return images

def delete_image_from_db(image_id):
    """Delete a specific image from database"""
    conn = sqlite3.connect('yolo_projects.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM images WHERE id = ?', (image_id,))
    conn.commit()
    conn.close()
    return True

def parse_color_config(color_config_content):
    """Parse color configuration file and return color mapping"""
    color_map = {}
    if not color_config_content:
        return color_map
    
    try:
        lines = color_config_content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(':')
                if len(parts) >= 2:
                    class_name = parts[0].strip()
                    color = parts[1].strip()
                    color_map[class_name] = color
    except Exception as e:
        st.warning(f"Error parsing color config: {e}")
    
    return color_map

def get_default_colors():
    """Get default colors for bounding boxes"""
    return [
        "red", "blue", "green", "yellow", "purple", "orange", 
        "cyan", "magenta", "lime", "pink", "brown", "gray",
        "navy", "olive", "teal", "maroon", "fuchsia", "aqua"
    ]

def process_image_with_yolo(image, model_path, class_names, color_config_content=""):
    """Process image with YOLO model and return detection results"""
    if not YOLO_AVAILABLE:
        st.error("YOLO is not available. Please install the required system libraries first.")
        return image, []
    
    try:
        # Load YOLO model
        model = YOLO(model_path)
        
        # Perform detection
        results = model(image)
        
        # Get class names as list
        class_names_list = [name.strip() for name in class_names.split('\n') if name.strip()]
        
        # Parse color configuration
        color_map = parse_color_config(color_config_content)
        default_colors = get_default_colors()
        
        # Process results
        processed_image = image.copy()
        draw = ImageDraw.Draw(processed_image)
        
        # Try to load a font for larger text
        try:
            # Try to use a larger font if available
            font_size = 24  # 2x larger than default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        detection_data = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Get confidence and class
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    # Get class name
                    class_name = class_names_list[class_id] if class_id < len(class_names_list) else f"Class {class_id}"
                    
                    # Get color for this class
                    if class_name in color_map:
                        color = color_map[class_name]
                    else:
                        # Use default color based on class ID
                        color = default_colors[class_id % len(default_colors)]
                    
                    # Draw bounding box with thicker lines
                    draw.rectangle([x1, y1, x2, y2], outline=color, width=4)
                    
                    # Draw label with larger text
                    label = f"{class_name}: {confidence:.2f}"
                    
                    # Get text size for background
                    try:
                        bbox = draw.textbbox((0, 0), label, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                    except:
                        # Fallback if textbbox is not available
                        text_width = len(label) * 12
                        text_height = 20
                    
                    # Draw background rectangle for text
                    text_bg_y1 = max(0, y1 - text_height - 5)
                    text_bg_y2 = y1
                    draw.rectangle([x1, text_bg_y1, x1 + text_width + 10, text_bg_y2], fill=color)
                    
                    # Draw text
                    draw.text((x1 + 5, text_bg_y1 + 2), label, fill="white", font=font)
                    
                    detection_data.append({
                        'class_name': class_name,
                        'confidence': confidence,
                        'bbox': [x1, y1, x2, y2],
                        'color': color
                    })
        
        return processed_image, detection_data
        
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return image, []

def image_to_bytes(image):
    """Convert PIL image to bytes"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def bytes_to_image(image_bytes):
    """Convert bytes to PIL image"""
    return Image.open(io.BytesIO(image_bytes))

# Main app
def main():
    st.title("🔍 YOLO Object Detection App")
    st.markdown("---")
    
    # Check if YOLO is available
    if not YOLO_AVAILABLE:
        st.warning("⚠️ YOLO functionality is not available due to missing system dependencies.")
        show_installation_instructions()
        
        # Still allow users to view existing projects and images
        st.header("📁 View Existing Data")
        st.info("You can still view existing projects and images, but YOLO processing is disabled.")
        
        # Sidebar navigation (limited)
        page = st.sidebar.selectbox(
            "Navigation",
            ["View Images", "Project Management"]
        )
        
        if page == "View Images":
            st.header("View Uploaded Images")
            # ... existing view images code ...
            projects = get_all_projects()
            if not projects:
                st.warning("No projects found.")
                return
            
            project_options = {f"{p[1]} (by {p[2]})": p[0] for p in projects}
            selected_project_name = st.selectbox("Select Project", list(project_options.keys()))
            selected_project_id = project_options[selected_project_name]
            
            images = get_project_images(selected_project_id)
            if not images:
                st.info("No images found for this project.")
                return
            
            st.subheader(f"Images for {selected_project_name}")
            cols = st.columns(3)
            for idx, image_data in enumerate(images):
                col_idx = idx % 3
                with cols[col_idx]:
                    original_image = bytes_to_image(image_data[2])
                    st.image(original_image, caption=f"Image {image_data[0]}", use_column_width=True)
        
        elif page == "Project Management":
            st.header("Project Management")
            projects = get_all_projects()
            if not projects:
                st.info("No projects found.")
                return
            
            st.subheader("All Projects")
            for project in projects:
                with st.expander(f"{project[1]} (by {project[2]}) - Created: {project[5]}"):
                    st.write(f"**Project ID:** {project[0]}")
                    st.write(f"**Model:** {os.path.basename(project[3])}")
                    st.write(f"**Class Names:**")
                    class_names_preview = project[4][:100] + "..." if len(project[4]) > 100 else project[4]
                    st.code(class_names_preview)
                    
                    # Show color configuration if available
                    if len(project) > 5 and project[5]:
                        st.write(f"**Color Configuration:**")
                        color_config_preview = project[5][:100] + "..." if len(project[5]) > 100 else project[5]
                        st.code(color_config_preview)
                    else:
                        st.write("**Color Configuration:** Using default colors")
                    images = get_project_images(project[0])
                    st.metric("Images Processed", len(images))
        
        return
    
    # Sidebar navigation (full functionality when YOLO is available)
    page = st.sidebar.selectbox(
        "Navigation",
        ["Create Project", "Upload Images", "View Images", "Project Management"]
    )
    
    if page == "Create Project":
        st.header("Create New Project")
        
        with st.form("create_project_form"):
            project_name = st.text_input("Project Name", placeholder="Enter project name")
            creator_name = st.text_input("Creator Name", placeholder="Enter creator name")
            
            st.subheader("Upload YOLO Model")
            model_file = st.file_uploader(
                "Upload PyTorch YOLO Model (.pt file)",
                type=['pt'],
                help="Upload your custom-trained YOLO model in PyTorch format"
            )
            
            st.subheader("Upload Class Names")
            class_names_file = st.file_uploader(
                "Upload Class Names File (.txt)",
                type=['txt'],
                help="Upload a text file with class names (one per line)"
            )
            
            st.subheader("Upload Color Configuration (Optional)")
            color_config_file = st.file_uploader(
                "Upload Color Configuration File (.txt)",
                type=['txt'],
                help="Upload a text file with class colors (format: class_name:color, one per line)"
            )
            
            if color_config_file:
                st.info("**Color Configuration Format:**")
                st.code("person:red\ncar:blue\ndog:green\ncat:yellow")
                st.write("**Available colors:** red, blue, green, yellow, purple, orange, cyan, magenta, lime, pink, brown, gray, navy, olive, teal, maroon, fuchsia, aqua")
            
            submit_button = st.form_submit_button("Create Project")
            
            if submit_button:
                if project_name and creator_name and model_file and class_names_file:
                    try:
                        project_id = save_project_to_db(project_name, creator_name, model_file, class_names_file, color_config_file)
                        st.success(f"Project '{project_name}' created successfully!")
                        st.info(f"Project ID: {project_id}")
                    except Exception as e:
                        st.error(f"Error creating project: {str(e)}")
                else:
                    st.error("Please fill in all required fields and upload both model and class names files.")
    
    elif page == "Upload Images":
        st.header("Upload and Process Images")
        
        # Get all projects
        projects = get_all_projects()
        
        if not projects:
            st.warning("No projects found. Please create a project first.")
            return
        
        # Project selection
        project_options = {f"{p[1]} (by {p[2]})": p[0] for p in projects}
        selected_project_name = st.selectbox("Select Project", list(project_options.keys()))
        selected_project_id = project_options[selected_project_name]
        
        # Get project details
        selected_project = [p for p in projects if p[0] == selected_project_id][0]
        model_path = selected_project[3]
        class_names = selected_project[4]
        color_config = selected_project[5] if len(selected_project) > 5 else ""
        
        st.info(f"Selected Project: {selected_project[1]} | Model: {os.path.basename(model_path)}")
        
        # Show color configuration info
        if color_config:
            st.info("🎨 Custom color configuration loaded for this project")
        else:
            st.info("🎨 Using default colors for bounding boxes")
        
        # Image upload
        uploaded_files = st.file_uploader(
            "Upload Images",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            accept_multiple_files=True,
            help="Upload images to process with YOLO detection"
        )
        
        if uploaded_files:
            st.subheader("Processing Images...")
            
            for uploaded_file in uploaded_files:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    # Load image
                    image = Image.open(uploaded_file)
                    
                    # Process with YOLO
                    processed_image, detection_results = process_image_with_yolo(
                        image, model_path, class_names, color_config
                    )
                    
                    # Save to database
                    original_bytes = image_to_bytes(image)
                    processed_bytes = image_to_bytes(processed_image)
                    
                    save_image_to_db(
                        selected_project_id,
                        original_bytes,
                        processed_bytes,
                        str(detection_results)
                    )
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Original Image")
                        st.image(image, caption=uploaded_file.name, use_column_width=True)
                    
                    with col2:
                        st.subheader("Processed Image")
                        st.image(processed_image, caption=f"Detected {len(detection_results)} objects", use_column_width=True)
                    
                    # Show detection details
                    if detection_results:
                        st.subheader("Detection Results")
                        detection_df = pd.DataFrame(detection_results)
                        st.dataframe(detection_df)
                    
                    st.markdown("---")
    
    elif page == "View Images":
        st.header("View Uploaded Images")
        
        # Get all projects
        projects = get_all_projects()
        
        if not projects:
            st.warning("No projects found. Please create a project first.")
            return
        
        # Project selection
        project_options = {f"{p[1]} (by {p[2]})": p[0] for p in projects}
        selected_project_name = st.selectbox("Select Project", list(project_options.keys()))
        selected_project_id = project_options[selected_project_name]
        
        # Get images for selected project
        images = get_project_images(selected_project_id)
        
        if not images:
            st.info("No images found for this project. Upload some images first.")
            return
        
        st.subheader(f"Images for {selected_project_name}")
        
        # Add bulk delete functionality
        if images:
            st.write("**Bulk Actions:**")
            col_bulk1, col_bulk2 = st.columns([3, 1])
            
            with col_bulk1:
                # Create a list of image options for bulk delete
                image_options = [f"Image {img[0]} (Uploaded: {img[5]})" for img in images]
                selected_images_for_delete = st.multiselect(
                    "Select images to delete:",
                    options=image_options,
                    help="Select multiple images to delete them at once"
                )
            
            with col_bulk2:
                if selected_images_for_delete:
                    if st.button("🗑️ Delete Selected Images", type="primary"):
                        # Extract image IDs from selected options
                        image_ids_to_delete = []
                        for option in selected_images_for_delete:
                            image_id = int(option.split()[1])  # Extract ID from "Image X"
                            image_ids_to_delete.append(image_id)
                        
                        # Show confirmation
                        st.warning(f"⚠️ Are you sure you want to delete {len(image_ids_to_delete)} images?")
                        st.write("This action will permanently delete:")
                        st.write(f"• {len(image_ids_to_delete)} selected images")
                        st.write(f"• Original and processed images")
                        st.write(f"• Detection results")
                        st.write("**This action cannot be undone!**")
                        
                        col_bulk_confirm1, col_bulk_confirm2 = st.columns(2)
                        
                        with col_bulk_confirm1:
                            if st.button("✅ Yes, Delete Images", key="bulk_confirm_yes", type="primary"):
                                # Delete selected images
                                for image_id in image_ids_to_delete:
                                    delete_image_from_db(image_id)
                                st.success(f"Successfully deleted {len(image_ids_to_delete)} images!")
                                st.rerun()
                        
                        with col_bulk_confirm2:
                            if st.button("❌ Cancel", key="bulk_confirm_no"):
                                st.rerun()
        
        # Display images in a grid
        cols = st.columns(3)
        for idx, image_data in enumerate(images):
            col_idx = idx % 3
            
            with cols[col_idx]:
                # Convert bytes to image
                original_image = bytes_to_image(image_data[2])
                processed_image = bytes_to_image(image_data[3])
                
                # Display thumbnail
                st.image(original_image, caption=f"Image {image_data[0]}", use_column_width=True)
                
                # Button to view details
                if st.button(f"View Details - Image {image_data[0]}", key=f"view_{image_data[0]}"):
                    st.session_state.selected_image = image_data
                    st.session_state.show_details = True
        
        # Show detailed view
        if hasattr(st.session_state, 'show_details') and st.session_state.show_details:
            st.markdown("---")
            st.subheader("Image Details")
            
            selected_image = st.session_state.selected_image
            original_image = bytes_to_image(selected_image[2])
            processed_image = bytes_to_image(selected_image[3])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original Image")
                st.image(original_image, use_column_width=True)
            
            with col2:
                st.subheader("Processed Image with Detections")
                st.image(processed_image, use_column_width=True)
            
            # Show detection results
            if selected_image[4]:  # detection_results
                try:
                    detection_results = eval(selected_image[4])
                    if detection_results:
                        st.subheader("Detection Results")
                        detection_df = pd.DataFrame(detection_results)
                        st.dataframe(detection_df)
                except:
                    st.info("Detection results not available")
            
            # Action buttons
            col_close, col_delete = st.columns(2)
            
            with col_close:
                if st.button("Close Details"):
                    st.session_state.show_details = False
                    st.rerun()
            
            with col_delete:
                # Add confirmation for image deletion
                if f"confirm_delete_image_{selected_image[0]}" not in st.session_state:
                    st.session_state[f"confirm_delete_image_{selected_image[0]}"] = False
                
                if not st.session_state[f"confirm_delete_image_{selected_image[0]}"]:
                    if st.button("🗑️ Delete Image", key=f"delete_image_{selected_image[0]}"):
                        st.session_state[f"confirm_delete_image_{selected_image[0]}"] = True
                        st.rerun()
                else:
                    st.warning("⚠️ Are you sure you want to delete this image?")
                    st.write("This action will permanently delete:")
                    st.write(f"• Image ID: {selected_image[0]}")
                    st.write(f"• Original and processed images")
                    st.write(f"• Detection results")
                    st.write("**This action cannot be undone!**")
                    
                    col_confirm_img1, col_confirm_img2 = st.columns(2)
                    
                    with col_confirm_img1:
                        if st.button("✅ Yes, Delete Image", key=f"confirm_yes_img_{selected_image[0]}", type="primary"):
                            delete_image_from_db(selected_image[0])
                            st.success("Image deleted successfully!")
                            st.session_state[f"confirm_delete_image_{selected_image[0]}"] = False
                            st.session_state.show_details = False
                            st.rerun()
                    
                    with col_confirm_img2:
                        if st.button("❌ Cancel", key=f"confirm_no_img_{selected_image[0]}"):
                            st.session_state[f"confirm_delete_image_{selected_image[0]}"] = False
                            st.rerun()
    
    elif page == "Project Management":
        st.header("Project Management")
        
        # Get all projects
        projects = get_all_projects()
        
        if not projects:
            st.info("No projects found. Create your first project!")
            return
        
        st.subheader("All Projects")
        
        for project in projects:
            with st.expander(f"{project[1]} (by {project[2]}) - Created: {project[5]}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Project ID:** {project[0]}")
                    st.write(f"**Model:** {os.path.basename(project[3])}")
                    st.write(f"**Class Names:**")
                    class_names_preview = project[4][:100] + "..." if len(project[4]) > 100 else project[4]
                    st.code(class_names_preview)
                    
                    # Show color configuration if available
                    if len(project) > 5 and project[5]:
                        st.write(f"**Color Configuration:**")
                        color_config_preview = project[5][:100] + "..." if len(project[5]) > 100 else project[5]
                        st.code(color_config_preview)
                    else:
                        st.write("**Color Configuration:** Using default colors")
                
                with col2:
                    # Get image count for this project
                    images = get_project_images(project[0])
                    st.metric("Images Processed", len(images))
                    
                    # Add confirmation for project deletion
                    if f"confirm_delete_{project[0]}" not in st.session_state:
                        st.session_state[f"confirm_delete_{project[0]}"] = False
                    
                    if not st.session_state[f"confirm_delete_{project[0]}"]:
                        if st.button(f"Delete Project {project[0]}", key=f"delete_{project[0]}"):
                            st.session_state[f"confirm_delete_{project[0]}"] = True
                            st.rerun()
                    else:
                        st.warning(f"⚠️ Are you sure you want to delete project '{project[1]}'?")
                        st.write("This action will permanently delete:")
                        st.write(f"• Project: {project[1]}")
                        st.write(f"• {len(images)} processed images")
                        st.write(f"• Model file: {os.path.basename(project[3])}")
                        st.write("**This action cannot be undone!**")
                        
                        col_confirm1, col_confirm2 = st.columns(2)
                        
                        with col_confirm1:
                            if st.button("✅ Yes, Delete Project", key=f"confirm_yes_{project[0]}", type="primary"):
                                # Delete project and associated images
                                conn = sqlite3.connect('yolo_projects.db')
                                cursor = conn.cursor()
                                cursor.execute('DELETE FROM images WHERE project_id = ?', (project[0],))
                                cursor.execute('DELETE FROM projects WHERE id = ?', (project[0],))
                                conn.commit()
                                conn.close()
                                
                                # Remove model file
                                try:
                                    os.remove(project[3])
                                except:
                                    pass
                                
                                st.success(f"Project '{project[1]}' deleted successfully!")
                                st.session_state[f"confirm_delete_{project[0]}"] = False
                                st.rerun()
                        
                        with col_confirm2:
                            if st.button("❌ Cancel", key=f"confirm_no_{project[0]}"):
                                st.session_state[f"confirm_delete_{project[0]}"] = False
                                st.rerun()

if __name__ == "__main__":
    main()
