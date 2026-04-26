import os
import sys
import subprocess

def install_requirements():
    req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
    if os.path.exists(req_file):
        print(f"Installing requirements for ComfyUI-Pitonisa from {req_file}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
    else:
        print("requirements.txt not found for ComfyUI-Pitonisa")

if __name__ == "__main__":
    install_requirements()
