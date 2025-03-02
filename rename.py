import os
import re
import config

# Formats the directories to be more readable
def format_title(name):
    match = re.match(r"(\d+)_([a-zA-Z0-9\-]+)", name)  # Extract number and title
    if match:
        number = str(int(match.group(1)))  # Convert "03" -> "3"
        title = match.group(2).replace("-", " ").title()  # Replace hyphens and capitalize words
        return f"{number}. {title}"  # Format as "3. Title"
    return name.replace("-", " ").title()  # Fallback for non-numbered folders


# Renames folders to follow the 'Course <#> / Module <#> / Section <#>' format
def rename_folders(base_folder, level):
    for root, dirs, _ in os.walk(base_folder, topdown=False):  # Process deepest folders first
        for folder_name in dirs:
            folder_path = os.path.join(root, folder_name)

            # Get relative path from base
            relative_path = os.path.relpath(folder_path, base_folder)
            folder_parts = relative_path.split(os.sep)  # Split into individual folders

            if len(folder_parts) < level + 1:  # Skip if folder depth is not enough
                continue

            formatted_parts = folder_parts[:]  # Copy the original path
            formatted_parts[level] = format_title(folder_parts[level])  # Format only the specific level

            # Apply structure rules (only modify the required level)
            if level == 0 and not formatted_parts[level].startswith("Course "):
                formatted_parts[level] = f"Course {formatted_parts[level]}"
            elif level == 1 and not formatted_parts[level].startswith("Module "):
                formatted_parts[level] = f"Module {formatted_parts[level]}"
            elif level == 2 and not formatted_parts[level].startswith("Section "):
                formatted_parts[level] = f"Section {formatted_parts[level]}"

            new_folder_path = os.path.join(base_folder, *formatted_parts)

            # Only rename if the folder name actually changes
            if folder_path != new_folder_path:
                try:
                    os.rename(folder_path, new_folder_path)
                    print(f"Renamed (Level {level}): '{folder_path}' → '{new_folder_path}'")
                except FileNotFoundError:
                    pass
                except OSError as e:
                    print(f"Error renaming '{folder_path}': {e}")


# Make 3 passes to rename the folders bottom to top
def rename_all_folders(base_folder):
    rename_folders(base_folder, 2)  # Pass 1: Rename Section folders first
    rename_folders(base_folder, 1)  # Pass 2: Rename Module folders after Sections
    rename_folders(base_folder, 0)  # Pass 3: Rename Course folders last


### Entrypoint
if __name__ == "__main__":
    rename_all_folders(config.OBSIDIAN_VAULT)
