import os
import re
import config


# Formats the directories to be more readable
def format_title(name):
    match = re.match(r"(\d+)_([a-zA-Z0-9\-]+)", name)  # Extract number and title
    if match:
        number = str(int(match.group(1)))  # Convert "02" -> "2"
        title = match.group(2).replace("-", " ").title()  # Replace hyphens and capitalize words
        return f"{number}. {title}"  # Format as "2. Title"
    return name.replace("-", " ").title()  # Fallback for non-numbered folders


# Recursively reformat all folders in the base folder
def rename_folders(base_folder):
    for root, dirs, _ in os.walk(base_folder, topdown=False):
        for folder_name in dirs:
            folder_path = os.path.join(root, folder_name)
            formatted_name = format_title(folder_name)  # Format the folder name
            new_folder_path = os.path.join(root, formatted_name)

            if folder_path != new_folder_path:  # Rename only if the name has changed
                try:
                    os.rename(folder_path, new_folder_path)
                    print(f"Renamed: '{folder_path}' → '{new_folder_path}'")
                except Exception as e:
                    print(f"Error renaming '{folder_path}': {e}")
            else:
                print(f"Skipped (already formatted): '{folder_path}'")


### Entrypoint
if __name__ == "__main__":
    rename_folders(config.OBSIDIAN_VAULT)
