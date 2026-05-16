#!/usr/bin/env python
"""
YOLOv8 Training Runner
Prepares dataset and trains model
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "model"
DATASET_DIR = MODEL_DIR / "datasets" / "combined_dataset"
MODELS_DIR = MODEL_DIR / "trained_models"

def ensure_directories():
    """Ensure all required directories exist"""
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"✓ Directories ready")

def install_requirements():
    """Install required packages"""
    logger.info("Installing required packages...")
    
    packages = [
        "ultralytics",
        "opencv-python",
        "numpy",
        "scikit-learn",
        "pyyaml"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])
            logger.info(f"✓ {package}")
        except subprocess.CalledProcessError:
            logger.error(f"Failed to install {package}")
            return False
    
    return True

def prepare_dataset():
    """Run dataset preparation script"""
    logger.info("\n" + "="*60)
    logger.info("STEP 1: PREPARING DATASET")
    logger.info("="*60)
    
    prepare_script = MODEL_DIR / "prepare_dataset.py"
    
    try:
        subprocess.run([sys.executable, str(prepare_script)], check=True)
        logger.info("✓ Dataset preparation complete")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Dataset preparation failed: {e}")
        return False

def train_model():
    """Train YOLOv8 model"""
    logger.info("\n" + "="*60)
    logger.info("STEP 2: TRAINING YOLOV8 MODEL")
    logger.info("="*60)
    
    try:
        from ultralytics import YOLO
        
        # Prepare data config
        data_yaml = str(DATASET_DIR / "data.yaml")
        
        if not os.path.exists(data_yaml):
            logger.error(f"data.yaml not found at {data_yaml}")
            return False

        # Find the latest training run to resume
        latest_run = None
        run_dirs = sorted(MODELS_DIR.glob("infrastructure_damage_gpu*"), key=os.path.getmtime, reverse=True)
        for run_dir in run_dirs:
            last_pt = run_dir / "weights" / "last.pt"
            if last_pt.exists():
                latest_run = last_pt
                break
        
        if latest_run:
            logger.info(f"Resuming training from: {latest_run}")
            model = YOLO(str(latest_run))
            resume = True
        else:
            logger.info("Loading YOLOv8 base model for new training...")
            model = YOLO('yolov8m.pt')
            resume = False
        
        logger.info(f"Training with data config: {data_yaml}")
        
        # Train model
        logger.info("\nStarting training on GPU... (optimized for 4GB VRAM)")
        results = model.train(
            data=data_yaml,
            epochs=100,
            imgsz=384,
            batch=8,
            patience=20,
            device=0,
            project=str(MODELS_DIR),
            name='infrastructure_damage_gpu',
            save=True,
            cache=False,
            augment=True,
            mosaic=0.5,
            workers=1,
            close_mosaic=10,
            amp=True,
            optimizer='SGD',
            resume=resume
        )
        
        logger.info("✓ Model training complete")
        
        # Save best model
        best_model_path = MODELS_DIR / "infrastructure_damage" / "weights" / "best.pt"
        if best_model_path.exists():
            logger.info(f"✓ Best model saved: {best_model_path}")
            
            # Copy to standard location
            final_model = MODEL_DIR / "trained_models" / "best.pt"
            import shutil
            shutil.copy2(best_model_path, final_model)
            logger.info(f"✓ Copied to: {final_model}")
        
        return True
    
    except ImportError:
        logger.error("ultralytics not installed. Please install: pip install ultralytics")
        return False
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return False

def validate_model():
    """Validate trained model"""
    logger.info("\n" + "="*60)
    logger.info("STEP 3: VALIDATING MODEL")
    logger.info("="*60)
    
    try:
        from ultralytics import YOLO
        
        model_path = MODEL_DIR / "trained_models" / "best.pt"
        
        if not model_path.exists():
            logger.error(f"Model not found at {model_path}")
            return False
        
        logger.info(f"Loading model: {model_path}")
        model = YOLO(str(model_path))
        
        # Validate
        data_yaml = str(DATASET_DIR / "data.yaml")
        logger.info("Running validation...")
        
        metrics = model.val(data=data_yaml)
        
        logger.info("\n✓ Validation Results:")
        logger.info(f"  mAP50: {metrics.box.map50:.3f}")
        logger.info(f"  mAP50-95: {metrics.box.map:.3f}")
        
        return True
    
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False

def test_inference():
    """Test model with sample images"""
    logger.info("\n" + "="*60)
    logger.info("STEP 4: TESTING INFERENCE")
    logger.info("="*60)
    
    try:
        from ultralytics import YOLO
        import cv2
        
        model_path = MODEL_DIR / "trained_models" / "best.pt"
        
        if not model_path.exists():
            logger.error(f"Model not found at {model_path}")
            return False
        
        model = YOLO(str(model_path))
        
        # Get test images
        test_dir = DATASET_DIR / "images" / "test"
        test_images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
        
        if not test_images:
            logger.warning("No test images found")
            return True
        
        logger.info(f"Testing with {min(5, len(test_images))} sample images...")
        
        for img_path in test_images[:5]:
            results = model.predict(source=str(img_path), conf=0.25)
            
            if results[0].boxes is not None:
                num_detections = len(results[0].boxes)
                logger.info(f"  {img_path.name}: {num_detections} detections")
            else:
                logger.info(f"  {img_path.name}: no detections")
        
        logger.info("✓ Inference tests complete")
        return True
    
    except Exception as e:
        logger.error(f"Inference testing failed: {e}")
        return False

def main():
    """Main training pipeline"""
    logger.info("\n" + "="*60)
    logger.info("INFRASTRUCTURE DAMAGE DETECTION - TRAINING PIPELINE")
    logger.info("="*60)
    
    # Step 1: Setup
    ensure_directories()
    
    # Step 2: Install dependencies
    if not install_requirements():
        logger.error("Failed to install dependencies")
        return False
    
    # Step 3: Prepare dataset
    if not prepare_dataset():
        logger.error("Dataset preparation failed")
        return False
    
    # Step 4: Train model
    if not train_model():
        logger.error("Model training failed")
        return False
    
    # Step 5: Validate model
    if not validate_model():
        logger.warning("Model validation had issues, but continuing...")
    
    # Step 6: Test inference
    if not test_inference():
        logger.warning("Inference testing had issues, but training may still be successful")
    
    logger.info("\n" + "="*60)
    logger.info("✓ TRAINING PIPELINE COMPLETE!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("1. Review training results in: model/trained_models/infrastructure_damage/")
    logger.info("2. Update config/settings.py with new MODEL_PATH")
    logger.info("3. Test the backend API with actual detections")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
