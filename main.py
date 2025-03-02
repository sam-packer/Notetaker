import os
import re
from openai import OpenAI
import ollama
import config

client = OpenAI(
    api_key=config.api_key,
    base_url=config.base_url
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


# Remove <think></think> from DeepSeek when running locally
def remove_thinking(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# Turn the transcript into notes!
# Be careful modifying this prompt... If done improperly it can cause your token usage to skyrocket
def generate_summary(text):
    prompt = (
        f"""
        I will provide you with a transcript from a video that is part of a course. Your task is to summarize the transcript in a structured, article-style format with clear mini headings. The summary should be detailed enough to serve as a standalone resource for someone studying the course, but concise enough to avoid unnecessary repetition or filler. Do not create a title heading. A title is already created. Here’s how I’d like the summary to be structured:

        Introduction: Write a brief 2-3 sentence overview of what the video covers.
        Main Content: Break the transcript into logical sections and summarize each section under a mini heading. Use clear, descriptive headings that reflect the key points or subtopics discussed in the video.
        Key Takeaways: At the end, include a bullet-point list of the most important points or lessons from the video.
        
        For the tone, please use a professional, educational tone similar to a textbook or academic article. Avoid overly casual language.
        Please ensure the summary is well-organized, easy to follow, and captures the information of the video without omitting information.
        Here is the video transcript: \n\n{text}
        """
    )
    if config.mode == "openai":
        try:
            # Make the API call
            response = client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "system",
                           "content": "You are an assistant transcribing video transcripts into article form for students."},
                          {"role": "user", "content": prompt}],
                stream=False,
                # This should be changed based on the model you're using!!
                # DeepSeek I used temperature at 1.5 and no top_p
                # gpt-4o-mini I used temperature at 0.3 and top_p at 0.8
                temperature=1.5,
                # top_p=0.8,
            )
            summary = response.choices[0].message.content
            return summary
        except Exception as e:
            print(f"Error generating summary with OpenAI: {e}")
            return "Summary generation failed."
    elif config.mode == "ollama":
        try:
            response = ollama.chat(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            summary = response['message']['content']
            return remove_thinking(summary)
        except Exception as e:
            print(f"Error generating summary with Ollama: {e}")
            return "Summary generation failed."
    else:
        print("Unknown mode selected in config.")
        return "Summary generation failed."


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
    trimmed_text = "\n".join(line.rstrip() for line in summary.splitlines())

    # Save the summary to Markdown
    with open(md_full_path, "w", encoding="utf-8") as f:
        f.write(trimmed_text)

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
