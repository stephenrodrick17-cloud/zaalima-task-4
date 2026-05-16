import sys
import time

def log(m):
    print(m)
    sys.stdout.flush()

log("Step 1: os/sys")
import os
log("Step 2: torch")
import torch
log("Step 3: cv2")
import cv2
log("Step 4: ultralytics")
from ultralytics import YOLO
log("Step 5: Load model")
model = YOLO("yolov8n.pt")
log("ALL OK")
