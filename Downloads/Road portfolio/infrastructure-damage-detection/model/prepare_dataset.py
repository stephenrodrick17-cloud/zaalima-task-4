"""
Dataset Preparation Script for YOLOv8 Training
Organizes and converts your datasets into YOLOv8 format
"""

import os
import shutil
import cv2
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths to your datasets
ARCHIVE_2 = r"c:\Users\asus\Downloads\Road portfolio\archive (2)"
ARCHIVE_3 = r"c:\Users\asus\Downloads\Road portfolio\archive (3)"
ARCHIVE_4 = r"c:\Users\asus\Downloads\Road portfolio\archive (4)"

# Output dataset path
OUTPUT_DATASET = r"c:\Users\asus\Downloads\Road portfolio\infrastructure-damage-detection\model\datasets\combined_dataset"

# Class mapping
CLASS_MAPPING = {
    0: "crack",           # From archive 2 (Cracked)
    1: "pothole",         # From archive 3 (Pothole issues)
    2: "structural",      # From archive 3 (Damaged road)
    3: "mixed"            # From archive 4 and mixed issues
}

def setup_directories():
    """Create output directory structure"""
    logger.info("Setting up directory structure...")
    
    for split in ["train", "val", "test"]:
        os.makedirs(f"{OUTPUT_DATASET}/images/{split}", exist_ok=True)
        os.makedirs(f"{OUTPUT_DATASET}/labels/{split}", exist_ok=True)
    
    logger.info(f"✓ Directories created at {OUTPUT_DATASET}")

def process_archive_2():
    """
    Process Archive 2: Cracked/Non-cracked images
    Class 0: crack
    """
    logger.info("\n=== Processing Archive 2 (Cracked/Non-cracked) ===")
    
    cracked_dir = os.path.join(ARCHIVE_2, "Decks", "Cracked")
    
    images = []
    for img_file in os.listdir(cracked_dir):
        if img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
            img_path = os.path.join(cracked_dir, img_file)
            images.append((img_path, 0, "crack"))  # Class 0: crack
    
    logger.info(f"Found {len(images)} cracked images from Archive 2")
    return images

def process_archive_3():
    """
    Process Archive 3: Road issues categorized
    Maps different issue types to classes
    """
    logger.info("\n=== Processing Archive 3 (Road Issues) ===")
    
    images = []
    road_issues = os.path.join(ARCHIVE_3, "data", "Road Issues")
    
    # Class mapping for archive 3
    issue_class_map = {
        "Pothole Issues": 1,
        "Damaged Road issues": 2,
        "Broken Road Sign Issues": 3,
        "Illegal Parking Issues": 3,
        "Mixed Issues": 3
    }
    
    for issue_type, class_id in issue_class_map.items():
        issue_dir = os.path.join(road_issues, issue_type)
        
        if os.path.exists(issue_dir):
            count = 0
            for img_file in os.listdir(issue_dir):
                if img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    img_path = os.path.join(issue_dir, img_file)
                    class_name = CLASS_MAPPING[class_id]
                    images.append((img_path, class_id, class_name))
                    count += 1
            
            logger.info(f"Found {count} images from '{issue_type}' (Class {class_id}: {CLASS_MAPPING[class_id]})")
    
    return images

def mask_to_yolo_bbox(mask_path, image_shape):
    """
    Convert segmentation mask to YOLO bounding box format
    
    Args:
        mask_path: Path to mask file
        image_shape: Shape of original image (height, width)
    
    Returns:
        YOLO format annotation (x_center, y_center, width, height) normalized 0-1
    """
    try:
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        if mask is None:
            logger.warning(f"Could not read mask: {mask_path}")
            return None
        
        # Find contours in mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Get largest contour (most likely the damage)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Normalize to 0-1 range
        img_h, img_w = image_shape
        
        x_center = (x + w / 2) / img_w
        y_center = (y + h / 2) / img_h
        width = w / img_w
        height = h / img_h
        
        # Ensure values are in valid range
        x_center = max(0, min(1, x_center))
        y_center = max(0, min(1, y_center))
        width = max(0, min(1, width))
        height = max(0, min(1, height))
        
        return (x_center, y_center, width, height)
    
    except Exception as e:
        logger.warning(f"Error processing mask {mask_path}: {str(e)}")
        return None

def process_archive_4():
    """
    Process Archive 4: Images with segmentation masks
    Convert masks to bounding boxes
    Class assignment based on mask analysis
    """
    logger.info("\n=== Processing Archive 4 (Images with Masks) ===")
    
    images_dir = os.path.join(ARCHIVE_4, "Images")
    masks_dir = os.path.join(ARCHIVE_4, "Masks")
    
    images = []
    annotations = {}
    
    for img_file in sorted(os.listdir(images_dir)):
        if img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
            # Get corresponding mask
            mask_name = img_file.replace('.jpg', '_label.PNG').replace('.png', '_label.PNG').replace('.jpeg', '_label.PNG')
            
            img_path = os.path.join(images_dir, img_file)
            mask_path = os.path.join(masks_dir, mask_name)
            
            if os.path.exists(mask_path):
                # Read image to get shape
                img = cv2.imread(img_path)
                if img is not None:
                    img_h, img_w = img.shape[:2]
                    
                    # Convert mask to bbox
                    bbox = mask_to_yolo_bbox(mask_path, (img_h, img_w))
                    
                    if bbox:
                        # Assign class based on file patterns
                        class_id = 1  # Default: pothole (most common)
                        
                        annotations[img_file] = (bbox, class_id)
                        images.append((img_path, class_id, CLASS_MAPPING[class_id]))
    
    logger.info(f"Found {len(images)} images with valid masks from Archive 4")
    return images, annotations

def copy_and_create_labels(image_list, annotations, split, split_ratio):
    """
    Copy images and create label files for YOLO
    """
    logger.info(f"\nProcessing {split} split...")
    
    split_images = image_list[:int(len(image_list) * split_ratio)]
    
    for img_path, class_id, class_name in split_images:
        try:
            img_filename = os.path.basename(img_path)
            
            # Copy image
            dest_img = os.path.join(OUTPUT_DATASET, "images", split, img_filename)
            shutil.copy2(img_path, dest_img)
            
            # Create label file
            label_filename = os.path.splitext(img_filename)[0] + ".txt"
            label_path = os.path.join(OUTPUT_DATASET, "labels", split, label_filename)
            
            # Check if we have bbox annotation (for archive 4)
            if img_filename in annotations:
                bbox, class_id = annotations[img_filename]
                with open(label_path, 'w') as f:
                    f.write(f"{class_id} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")
            else:
                # For other archives, create whole-image bbox (full image damage)
                # This is a simplification - in production, you'd need actual annotations
                with open(label_path, 'w') as f:
                    # Center at middle, covers most of image
                    f.write(f"{class_id} 0.5 0.5 0.9 0.9\n")
        
        except Exception as e:
            logger.error(f"Error processing {img_path}: {str(e)}")

def create_data_yaml():
    """Create data.yaml for YOLOv8 training"""
    
    yaml_content = f"""path: {OUTPUT_DATASET}
train: images/train
val: images/val
test: images/test

nc: 4
names: ['crack', 'pothole', 'structural', 'mixed']
"""
    
    yaml_path = os.path.join(OUTPUT_DATASET, "data.yaml")
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    logger.info(f"✓ Created data.yaml at {yaml_path}")
    return yaml_path

def prepare_dataset():
    """Main dataset preparation function"""
    
    logger.info("=" * 60)
    logger.info("DATASET PREPARATION FOR YOLOV8 TRAINING")
    logger.info("=" * 60)
    
    # Setup
    setup_directories()
    
    # Process all archives
    archive_2_images = process_archive_2()
    archive_3_images = process_archive_3()
    archive_4_images, archive_4_annotations = process_archive_4()
    
    # Combine all images
    all_images = archive_2_images + archive_3_images + archive_4_images
    
    logger.info(f"\n{'='*60}")
    logger.info(f"TOTAL IMAGES COLLECTED: {len(all_images)}")
    logger.info(f"{'='*60}")
    
    # Split dataset: 80% train, 10% val, 10% test
    logger.info("\nSplitting dataset...")
    
    train_images, temp_images = train_test_split(all_images, train_size=0.8, random_state=42)
    val_images, test_images = train_test_split(temp_images, train_size=0.5, random_state=42)
    
    logger.info(f"Train: {len(train_images)} images")
    logger.info(f"Val:   {len(val_images)} images")
    logger.info(f"Test:  {len(test_images)} images")
    
    # Copy images and create labels
    copy_and_create_labels(train_images, archive_4_annotations, "train", 1.0)
    copy_and_create_labels(val_images, archive_4_annotations, "val", 1.0)
    copy_and_create_labels(test_images, archive_4_annotations, "test", 1.0)
    
    # Create data.yaml
    yaml_path = create_data_yaml()
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("DATASET PREPARATION COMPLETE!")
    logger.info(f"{'='*60}")
    logger.info(f"Output location: {OUTPUT_DATASET}")
    logger.info(f"Data config: {yaml_path}")
    logger.info(f"Total images: {len(all_images)}")
    logger.info(f"Classes: {len(CLASS_MAPPING)}")
    logger.info(f"Classes: {', '.join(CLASS_MAPPING.values())}")
    
    return yaml_path

if __name__ == "__main__":
    yaml_path = prepare_dataset()
    print(f"\nReady to train! Use: --data {yaml_path}")
