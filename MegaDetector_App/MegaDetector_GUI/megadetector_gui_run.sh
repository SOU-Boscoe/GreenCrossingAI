#!/bin/bash
# activate cameratraps environment
source /shared/land_bridge/miniforge3/bin/activate cameratraps-detector

# Set CUDA_VISIBLE_DEVICES to use GPU 1
export CUDA_VISIBLE_DEVICES=1

# Run the Python script
CUDA_VISIBLE_DEVICES=1 python /shared/land_bridge/MegaDetector_App/MegaDetector_GUI/megadetector_gui_sub.py

