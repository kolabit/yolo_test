#!/usr/bin/env python3
"""
Validation Tool for YOLO Streamlit App, according to the project requirements
This tool helps validate class names and colors files, and images before uploading
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field, validator, ValidationError
import re
from PIL import Image

# Pydantic validation models (same as in main app)
class ClassColorEntry(BaseModel):
    """Model for a single class-color entry"""
    class_name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    
    @validator('class_name')
    def validate_class_name(cls, v):
        if not v.strip():
            raise ValueError('Class name cannot be empty')
        # Remove any special characters that might cause issues
        v = re.sub(r'[^\w\s-]', '', v.strip())
        if not v:
            raise ValueError('Class name must contain valid characters')
        return v
    
    @validator('color')
    def validate_color(cls, v):
        if v is None:
            return v
        valid_colors = {
            'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 
            'magenta', 'lime', 'pink', 'brown', 'gray', 'navy', 'olive', 
            'teal', 'maroon', 'fuchsia', 'aqua'
        }
        if v.lower() not in valid_colors:
            raise ValueError(f'Invalid color: {v}. Valid colors are: {", ".join(valid_colors)}')
        return v.lower()

class ClassColorConfig(BaseModel):
    """Model for the entire class-color configuration file"""
    entries: List[ClassColorEntry] = Field(..., min_items=1, max_items=1000)
    
    @validator('entries')
    def validate_unique_class_names(cls, v):
        class_names = [entry.class_name for entry in v]
        duplicates = [name for name in set(class_names) if class_names.count(name) > 1]
        if duplicates:
            raise ValueError(f'Duplicate class names found: {", ".join(duplicates)}')
        return v

class ImageValidation(BaseModel):
    """Model for image validation"""
    file_name: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0, le=50*1024*1024)  # Max 50MB
    file_type: str = Field(..., regex=r'\.(jpg|jpeg|png|bmp)$')
    image_width: int = Field(..., gt=0, le=10000)  # Max 10000px width
    image_height: int = Field(..., gt=0, le=10000)  # Max 10000px height
    
    @validator('file_name')
    def validate_file_name(cls, v):
        if not v.strip():
            raise ValueError('File name cannot be empty')
        # Check for potentially dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in v for char in dangerous_chars):
            raise ValueError(f'File name contains invalid characters: {dangerous_chars}')
        return v.strip()
    
    @validator('file_type')
    def validate_file_type(cls, v):
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        if v.lower() not in valid_extensions:
            raise ValueError(f'Invalid file type: {v}. Valid types are: {", ".join(valid_extensions)}')
        return v.lower()

def validate_class_color_file(file_path: str) -> tuple[bool, str, Optional[ClassColorConfig]]:
    """Validate the class-color configuration file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the content
        lines = content.strip().split('\n')
        entries = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                if ':' in line:
                    # Format: class_name:color
                    parts = line.split(':', 1)
                    class_name = parts[0].strip()
                    color = parts[1].strip()
                    entries.append(ClassColorEntry(class_name=class_name, color=color))
                else:
                    # Format: class_name (no color)
                    class_name = line
                    entries.append(ClassColorEntry(class_name=class_name, color=None))
        
        if not entries:
            return False, "No valid class entries found in file", None
        
        # Validate the entire configuration
        config = ClassColorConfig(entries=entries)
        return True, f"Valid configuration with {len(entries)} classes", config
        
    except FileNotFoundError:
        return False, f"File not found: {file_path}", None
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            if error['type'] == 'value_error':
                error_messages.append(error['msg'])
            else:
                error_messages.append(f"{error['loc'][0]}: {error['msg']}")
        return False, f"Validation errors: {'; '.join(error_messages)}", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None

def validate_image_file(file_path: str) -> tuple[bool, str, Optional[ImageValidation]]:
    """Validate image file"""
    try:
        # Check file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}", None
        
        # Get file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Try to open and validate image
        try:
            with Image.open(file_path) as image:
                width, height = image.size
                
                # Create validation model
                validation = ImageValidation(
                    file_name=file_name,
                    file_size=file_size,
                    file_type=file_ext,
                    image_width=width,
                    image_height=height
                )
                
                return True, f"Valid image: {width}x{height}, {file_size/1024/1024:.1f}MB", validation
                
        except Exception as img_error:
            return False, f"Invalid image format: {str(img_error)}", None
            
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            error_messages.append(f"{error['loc'][0]}: {error['msg']}")
        return False, f"Validation errors: {'; '.join(error_messages)}", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None

def validate_directory_images(directory_path: str) -> tuple[List[str], List[tuple[str, str]]]:
    """Validate all images in a directory"""
    valid_images = []
    invalid_images = []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    try:
        for file_path in Path(directory_path).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                is_valid, message, validation = validate_image_file(str(file_path))
                if is_valid:
                    valid_images.append(str(file_path))
                else:
                    invalid_images.append((str(file_path), message))
    except Exception as e:
        print(f"Error scanning directory: {e}")
    
    return valid_images, invalid_images

def main():
    """Main validation tool function"""
    print("🔍 YOLO Streamlit App - Validation Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python validation_tool.py class_file <file_path>")
        print("  python validation_tool.py image <file_path>")
        print("  python validation_tool.py directory <directory_path>")
        print()
        print("Examples:")
        print("  python validation_tool.py class_file sample_classes_with_colors.txt")
        print("  python validation_tool.py image sample_images/image1.jpg")
        print("  python validation_tool.py directory sample_images/")
        return
    
    command = sys.argv[1].lower()
    
    if command == "class_file":
        if len(sys.argv) < 3:
            print("❌ Please provide a file path")
            return
        
        file_path = sys.argv[2]
        print(f"🔍 Validating class file: {file_path}")
        
        is_valid, message, config = validate_class_color_file(file_path)
        
        if is_valid:
            print(f"✅ {message}")
            print(f"📊 Total Classes: {len(config.entries)}")
            print(f"🎨 Classes with Custom Colors: {len([e for e in config.entries if e.color])}")
            print(f"⚪ Classes with Default Colors: {len([e for e in config.entries if not e.color])}")
            
            print("\n📋 Class Details:")
            for i, entry in enumerate(config.entries):
                color_info = f" (Color: {entry.color})" if entry.color else " (Default color)"
                print(f"  {i+1:3d}. {entry.class_name}{color_info}")
        else:
            print(f"❌ {message}")
    
    elif command == "image":
        if len(sys.argv) < 3:
            print("❌ Please provide an image file path")
            return
        
        file_path = sys.argv[2]
        print(f"🔍 Validating image: {file_path}")
        
        is_valid, message, validation = validate_image_file(file_path)
        
        if is_valid:
            print(f"✅ {message}")
            print(f"📊 File: {validation.file_name}")
            print(f"📏 Dimensions: {validation.image_width}x{validation.image_height}")
            print(f"💾 Size: {validation.file_size/1024/1024:.1f}MB")
            print(f"📁 Type: {validation.file_type}")
        else:
            print(f"❌ {message}")
    
    elif command == "directory":
        if len(sys.argv) < 3:
            print("❌ Please provide a directory path")
            return
        
        directory_path = sys.argv[2]
        print(f"🔍 Validating images in directory: {directory_path}")
        
        valid_images, invalid_images = validate_directory_images(directory_path)
        
        print(f"✅ Valid Images: {len(valid_images)}")
        print(f"❌ Invalid Images: {len(invalid_images)}")
        
        if valid_images:
            print("\n📋 Valid Images:")
            for i, img_path in enumerate(valid_images[:10]):  # Show first 10
                print(f"  {i+1:3d}. {os.path.basename(img_path)}")
            if len(valid_images) > 10:
                print(f"     ... and {len(valid_images) - 10} more")
        
        if invalid_images:
            print("\n❌ Invalid Images:")
            for img_path, error in invalid_images[:10]:  # Show first 10
                print(f"  • {os.path.basename(img_path)}: {error}")
            if len(invalid_images) > 10:
                print(f"     ... and {len(invalid_images) - 10} more")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: class_file, image, directory")

if __name__ == "__main__":
    main() 