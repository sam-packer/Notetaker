import os
import re
from openai import OpenAI

import config

client = OpenAI(
    api_key=config.api_key
)


# Cleans up text and random returns
def clean_text(text):
    text = text.strip()
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    return text


# Formats the title from "01_document.en.txt" to "1. Document"
def format_title(filename):
    filename = filename.replace(".en.txt", "")  # Remove the language suffix
    match = re.match(r"(\d+)_([a-zA-Z0-9\-]+)", filename)  # Extract number and title
    if match:
        number = str(int(match.group(1)))  # Convert "01" -> "1"
        title = match.group(2).replace("-", " ").title()  # Convert to Title Case
        return f"{number}. {title}"  # Format as "1. Title"
    return filename.title()  # Fallback (if no number is found)


# Turn the transcript into notes!
# Be careful modifying this prompt... If done improperly it can cause your token usage to skyrocket
def generate_summary(text):
    prompt = (
        "Summarize the following text for a student's notes. "
        "Include key details but keep it structured and readable. "
        "Use a mix of bullet points and short paragraphs where needed. "
        "Highlight important definitions, concepts, and takeaways:\n\n"
        f"{text}"
    )

    # Make the API call
    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[{"role": "system", "content": "You are an assistant summarizing text for students."},
                  {"role": "user", "content": prompt}],
        stream=False
    )
    summary = response.choices[0].message.content
    return summary


# Process the text file, convert it to .md file, move it to Obsidian folder
def process_txt_to_md(txt_file):
    relative_path = os.path.relpath(txt_file, config.BASE_FOLDER)  # Get relative path from base
    relative_dir, file_name = os.path.split(relative_path)  # Split into folder + file
    base_name = file_name.replace(".en.txt", "")  # Remove language suffix
    formatted_title = format_title(base_name)  # Convert filename into readable title
    md_relative_path = os.path.join(relative_dir, f"{formatted_title}.md")  # Replace .txt with .md
    md_full_path = os.path.join(config.OBSIDIAN_VAULT, md_relative_path)  # Get full destination path

    # Ensure the directory structure is replicated in Obsidian Vault
    os.makedirs(os.path.dirname(md_full_path), exist_ok=True)

    with open(txt_file, "r", encoding="utf-8") as f:
        text = f.read()

    text = clean_text(text)  # Fix broken line breaks
    summary = generate_summary(text)  # Call the API to generate the summary

    # Save the summary to Markdown
    with open(md_full_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Saved summary to {md_full_path}")


# Process all subfolders within the base folder
def process_folder_recursive(base_folder):
    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".en.txt"):
                full_path = os.path.join(root, file)
                process_txt_to_md(full_path)


### Entrypoint
if __name__ == "__main__":
    process_folder_recursive(config.BASE_FOLDER)
