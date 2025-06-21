#!/usr/bin/env python3
"""
Example script to demonstrate YOLO Streamlit app usage
This script creates sample data for testing the application
"""

import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_sample_class_names():
    """Create a sample class names file"""
    class_names = """person
car
dog
cat
bicycle
motorcycle
bus
truck
bird
horse
sheep
cow
elephant
bear
zebra
giraffe
backpack
umbrella
handbag
tie
suitcase
frisbee
skis
snowboard
sports ball
kite
baseball bat
baseball glove
skateboard
surfboard
tennis racket
bottle
wine glass
cup
fork
knife
spoon
bowl
banana
apple
sandwich
orange
broccoli
carrot
hot dog
pizza
donut
cake
chair
couch
potted plant
bed
dining table
toilet
tv
laptop
mouse
remote
keyboard
cell phone
microwave
oven
toaster
sink
refrigerator
book
clock
vase
scissors
teddy bear
hair drier
toothbrush"""
    
    with open('sample_classes.txt', 'w') as f:
        f.write(class_names)
    
    print("Created sample_classes.txt with 80 COCO class names")
    return 'sample_classes.txt'

def create_sample_image(width=640, height=480):
    """Create a sample image with some geometric shapes"""
    # Create a white background
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw some rectangles (simulating objects)
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    
    for i in range(5):
        x1 = np.random.randint(50, width-100)
        y1 = np.random.randint(50, height-100)
        x2 = x1 + np.random.randint(50, 150)
        y2 = y1 + np.random.randint(50, 150)
        
        color = colors[i % len(colors)]
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='black', width=2)
        
        # Add some text
        draw.text((x1+5, y1+5), f"Object {i+1}", fill='white')
    
    # Add some circles
    for i in range(3):
        x = np.random.randint(100, width-100)
        y = np.random.randint(100, height-100)
        radius = np.random.randint(20, 50)
        
        color = colors[(i+5) % len(colors)]
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                    fill=color, outline='black', width=2)
        draw.text((x-10, y-10), f"Circle {i+1}", fill='white')
    
    return image

def create_sample_images():
    """Create multiple sample images for testing"""
    os.makedirs('sample_images', exist_ok=True)
    
    for i in range(5):
        image = create_sample_image()
        filename = f'sample_images/sample_image_{i+1}.jpg'
        image.save(filename, 'JPEG', quality=95)
        print(f"Created {filename}")
    
    print("Created 5 sample images in sample_images/ directory")

def download_sample_yolo_model():
    """Instructions for downloading a sample YOLO model"""
    print("\n" + "="*60)
    print("SAMPLE YOLO MODEL DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print("To get a sample YOLO model for testing:")
    print()
    print("1. Visit: https://github.com/ultralytics/yolov5/releases")
    print("2. Download yolov5s.pt (small model, ~14MB)")
    print("3. Or download yolov5n.pt (nano model, ~6MB)")
    print("4. Place the .pt file in your project directory")
    print()
    print("Alternative: Use the ultralytics library to download automatically:")
    print("```python")
    print("from ultralytics import YOLO")
    print("model = YOLO('yolov5s.pt')  # This will download automatically")
    print("```")
    print("="*60)

def main():
    """Main function to set up sample data"""
    print("Setting up sample data for YOLO Streamlit app...")
    print()
    
    # Create sample class names file
    class_file = create_sample_class_names()
    print(f"✓ Class names file: {class_file}")
    
    # Create sample images
    create_sample_images()
    print("✓ Sample images created")
    
    # Provide instructions for YOLO model
    download_sample_yolo_model()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Download a YOLO model (.pt file) as described above")
    print("2. Run the Streamlit app: streamlit run yolo_test_app.py")
    print("3. Create a project using:")
    print("   - Project name: 'Sample Project'")
    print("   - Creator name: 'Your Name'")
    print("   - Model file: your downloaded .pt file")
    print("   - Class names: sample_classes.txt")
    print("4. Upload images from sample_images/ directory")
    print("5. View results in the app!")
    print("="*60)

if __name__ == "__main__":
    main() 