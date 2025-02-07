# Notetaker

This converts transcripts from Coursera into notes automatically!

## How does it work?

Use a tool such as [coursera-helper](https://github.com/csyezheng/coursera-helper) to first download the actual course from Coursera. This will download *everything* from the videos to the actual transcripts. We're interested in the English transcripts for each video as that's what we'll use to convert into notes. We can call the OpenAI API and feed in the transcript to summarize it. This turns it into much easier to read bullet points. I use Obsidian for notes, so it converts it into Obsidian and moves it into my Obsidian Vault.

I recommend using the gpt-4o-mini model. It's cheap enough and works well. Converting 118 files only costed me 15 cents. That's the content from three courses. Keep in mind, the way you prompt ChatGPT can cause **significant** charges to incur.
