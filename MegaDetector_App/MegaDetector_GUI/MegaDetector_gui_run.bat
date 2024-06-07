@echo off
rem activate cameratraps environment
call "C:\ProgramData\mambaforge\Scripts\activate.bat" C:\Users\Public\Documents\cameratraps-detector

rem Set CUDA_VISIBLE_DEVICES to use GPU 0
set CUDA_VISIBLE_DEVICES=0

rem Run the Python script
python C:\Users\Public\Documents\MegaDetector_App\MegaDetector_GUI\MegaDetector_gui_sub4.py
