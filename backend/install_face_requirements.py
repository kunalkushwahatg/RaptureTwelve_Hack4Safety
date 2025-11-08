"""
Setup and Install Requirements for Face Embedding Population
"""

import subprocess
import sys

def install_packages():
    """Install required packages for face embedding extraction"""
    
    packages = [
        'opencv-python',
        'insightface', 
        'onnxruntime',  # Use onnxruntime-gpu if you have CUDA GPU
        'qdrant-client',
        'numpy'
    ]
    
    print("="*60)
    print("INSTALLING FACE RECOGNITION REQUIREMENTS")
    print("="*60)
    print()
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully\n")
        except Exception as e:
            print(f"✗ Failed to install {package}: {e}\n")
    
    print("="*60)
    print("Installation complete!")
    print("="*60)
    print()
    print("Now you can run: python populate_qdrant_images.py")
    print()

if __name__ == "__main__":
    install_packages()
