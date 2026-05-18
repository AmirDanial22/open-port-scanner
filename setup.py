# setup.py - Auto-install dependencies
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("Installing required packages...")

required = [
    "Flask==2.3.3",
    "Flask-SQLAlchemy==3.0.5", 
    "python-dotenv==1.0.0"
]

for package in required:
    try:
        install(package)
        print(f"✓ Installed: {package}")
    except:
        print(f"✗ Failed to install: {package}")

print("\n✅ Setup complete! Run: python app.py")