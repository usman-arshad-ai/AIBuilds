import os
from dotenv import load_dotenv 
#have dotenv file configured with API Key
from scraper import fetch_website_contents
from IPython.display import Markdown, display
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

def fetch_website_contents(url: str, timeout: int = 10) -> str:
    """
    Fetches and returns cleaned text content from a webpage.
    
    Args:
        url (str): Website URL
        timeout (int): Request timeout in seconds
    
    Returns:
        str: Extracted page text or error message
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts, styles, nav junk
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        # Clean up whitespace
        cleaned_text = "\n".join(
            line.strip() for line in text.splitlines() if line.strip()
        )

        return cleaned_text

    except requests.exceptions.RequestException as e:
        return f"Error fetching {url}: {e}"
import subprocess
from pathlib import Path

def read_file_contents(file_path: str) -> str:
    """
    Reads text from a local PDF using pdftotext (brew-installed).
    No pip dependencies.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")

    try:
        result = subprocess.run(
            ["pdftotext", str(path), "-"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to read PDF: {e.stderr}")

file_path = input("Enter the full path to your PDF: ").strip()

res = read_file_contents(file_path)
print(res[:2000])

# Define our system prompt - you can experiment with this later, changing the last sentence to 'Respond in markdown in Spanish."

system_prompt = """
You are a honest career couch that will help take a look at a resume and evaluate it. You will summarize the resume and provide a rating based on the resume content. The user is trying to become an AI PM. Give him advice on how to get the job, and changes he should make. 
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""
# Define our user prompt

user_prompt_prefix = """
Here is my resume: let me know what you think.
"""

# See how this function creates exactly the format above

def messages_for(resume):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + resume}
    ]

# Try this out, and then try for a few more websites

messages_for(res)

# And now: call the OpenAI API. You will get very familiar with this!
import subprocess
from pathlib import Path
import openai

def pdf_to_text_pdftotext(pdf_path: str) -> str:
    pdf_path = str(Path(pdf_path).expanduser())
    # - layout-ish output can be nicer for resumes; remove -layout if you prefer
    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],  # "-" outputs to stdout
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {result.stderr.strip()}")
    return result.stdout

def summarize_pdf(pdf_path: str):
    pdf_text = pdf_to_text_pdftotext(pdf_path)
    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages_for(pdf_text)  # assuming messages_for expects raw text
    )
    return response.choices[0].message.content

