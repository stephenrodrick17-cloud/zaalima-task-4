from ultralytics import YOLO
import torch
import os

def train_model():
    from ultralytics import settings
    # Set settings to local folders to avoid permission issues
    settings.update({
        'runs_dir': os.path.join(os.getcwd(), 'runs'),
        'datasets_dir': os.path.join(os.getcwd(), 'model', 'datasets'),
        'weights_dir': os.path.join(os.getcwd(), 'model', 'weights')
    })
    
    # Load a model
    model = YOLO('yolov8n.pt') 

    # Training configuration
    data_path = r"c:\Users\asus\Downloads\Road portfolio\infrastructure-damage-detection\model\datasets\combined_dataset\data.yaml"
    
    # Check if GPU is available
    device = 0 if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    # Start training with minimal resources to avoid memory errors
    results = model.train(
        data=data_path,
        epochs=50,  # Increased epochs for a full training run
        imgsz=320,  # Moderate image size for better accuracy
        batch=8,    # Moderate batch size
        workers=0,  # Disable multiprocessing
        device=device,
        project='runs/detect',
        name='infrastructure_damage',
        exist_ok=True,
        cache=False # Disable caching to save RAM
    )
    
    # Save the best model to a known location for the backend
    best_model_path = os.path.join('runs', 'detect', 'infrastructure_damage', 'weights', 'best.pt')
    target_path = r"c:\Users\asus\Downloads\Road portfolio\infrastructure-damage-detection\backend\app\services\best.pt"
    
    if os.path.exists(best_model_path):
        import shutil
        shutil.copy2(best_model_path, target_path)
        print(f"Training complete. Best weights saved to: {target_path}")
    else:
        print("Training failed or weights not found.")

if __name__ == "__main__":
    train_model()
