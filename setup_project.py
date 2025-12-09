import os

directories = [
    "src/core",
    "src/engine",
    "src/ui",
    "src/assets",
    "tests/core",
    "tests/engine",
    "tests/ui"
]

files = [
    "src/__init__.py",
    "src/core/__init__.py",
    "src/engine/__init__.py",
    "src/ui/__init__.py",
    "tests/__init__.py",
    "tests/core/__init__.py",
    "tests/engine/__init__.py",
    "tests/ui/__init__.py",
    "tests/conftest.py"
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

for file in files:
    with open(file, 'w') as f:
        pass # Create empty file
    print(f"Created file: {file}")

print("Project structure setup complete.")