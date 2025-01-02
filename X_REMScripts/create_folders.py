import os

# Define the base directory
base_dir = r"C:\Users\robmo\OneDrive\Documents\evidenceai_test"

# Define the folder structure
folders = [
    "chatGPT/prompts",
    "chatGPT/algorithms",
    "chatGPT/zapier_triggers",
    "chatGPT/outputs"
]

# Create the folders
for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Created: {folder_path}")

print("Folder structure created successfully!")
