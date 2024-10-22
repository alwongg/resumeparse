import os
import json
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from openai import OpenAI
from docx import Document  # For .docx files
from docx2txt import process as docx2txt_process  # To extract text from docx
from PIL import Image  # To handle images for OCR from screenshots
from pdf2image import convert_from_path
from pytesseract import image_to_string
from dotenv import load_dotenv  # Ensure this is imported correctly
import re

import platform
import subprocess

# Load environment variables
load_dotenv()

import platform
import subprocess

def extract_text_from_file(file):
    file_extension = os.path.splitext(file)[1]
    text_content = ""

    # Handle PDF files using MuPDF
    if file_extension == ".pdf":
        try:
            pdf_document = fitz.open(file)
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text_content += page.get_text()

            # If MuPDF fails to extract any text, fallback to OCR
            if len(text_content.strip()) == 0:
                raise ValueError("No text extracted using MuPDF, falling back to OCR...")

        except Exception as e:
            print(f"MuPDF error: {e}")
            print("Falling back to OCR...")
            images = convert_from_path(file)
            for image in images:
                text_content += pytesseract.image_to_string(image)

    # Handle .docx files using python-docx and fallback to docx2txt
    elif file_extension == ".docx":
        try:
            # First try python-docx
            doc = Document(file)
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"

            # If python-docx fails to extract any text, fallback to docx2txt
            if not text_content.strip():
                print("No text extracted using python-docx, falling back to docx2txt...")
                text_content = docx2txt_process(file)

                if not text_content.strip():
                    raise ValueError("No text extracted using docx2txt either, falling back to OCR...")

        except Exception as e:
            print(f"docx2txt error: {e}")
            print("Falling back to OCR for .docx file...")

            # Convert the document to images and apply OCR
            try:
                doc_images = convert_from_path(file)
                for image in doc_images:
                    text_content += pytesseract.image_to_string(image)

                if not text_content.strip():
                    raise ValueError("OCR failed to extract text from the .docx file.")
            except Exception as e:
                print(f"OCR fallback for .docx failed: {e}")
                text_content = ""  # Set empty to indicate failure

    # Handle .doc files using antiword on Linux/Mac
    elif file_extension == ".doc":
        if platform.system() in ["Linux", "Darwin"]:  # Linux or Mac
            try:
                result = subprocess.run(["antiword", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                text_content = result.stdout.decode('utf-8')
                if result.returncode != 0:
                    raise Exception(f"antiword error: {result.stderr.decode('utf-8')}")
            except Exception as e:
                print(f"Error processing .doc file: {e}")
                text_content = ""  # Ensure it's not sent empty to OpenAI
        else:
            # If on Windows or other platform without antiword
            print(f"Warning: .doc file processing is not supported on this platform. Skipping file: {file}")
            text_content = ""

    return text_content



def parse_content(text_content, target_school_list):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Format target_school_list for OpenAI prompt
    school_list_str = ', '.join(target_school_list)

    system_message = (
        "You are a professional-grade resume parser. "
        "You will be provided with text content extracted from a resume file. "
        "Your task is to return clean, accurate JSON formatted data with the following keys: "
        "- 'education_level' (highest level of education: Bachelor's, Master's, or PhD)\n"
        "- 'name' (full name of the candidate)\n"
        "- 'major' (in Simplified Chinese)\n"
        "- 'grad_year' (graduation year)\n"
        "- 'phd_school' (in Simplified Chinese only)\n"
        "- 'master_school' (in Simplified Chinese only)\n"
        "- 'bachelor_school' (in Simplified Chinese only)\n"
        "If not applicable, fill the fields with 'NA'."
    )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text_content}
        ]
    )

    # Extract and parse the message content from OpenAI response
    raw_response = completion.choices[0].message.content
    print(f"\nOpenAI response: {raw_response}")

    # Clean the response content by removing any backticks, "json" tags, or extra characters
    cleaned_content = re.sub(r"```json|```", "", raw_response).strip()
    # Remove trailing commas before closing braces/brackets
    cleaned_content = re.sub(r",\s*([\}\]])", r"\1", cleaned_content)

    try:
        # Attempt to parse cleaned content as JSON
        parsed_info = json.loads(cleaned_content)

        # Function to remove text in parentheses
        def clean_school_name(school_name):
            return re.sub(r"\s*\(.*?\)", "", school_name).strip()
        
        # Normalize extracted school names before matching
        parsed_info['phd_school'] = parsed_info.get('phd_school', 'NA')
        parsed_info['master_school'] = parsed_info.get('master_school', 'NA')
        parsed_info['bachelor_school'] = parsed_info.get('bachelor_school', 'NA')

        # Perform match locally, set match status to NA if school is NA
        if parsed_info['phd_school'] == 'NA':
            parsed_info['phd_match_status'] = 'NA'
        else:
            parsed_info['phd_match_status'] = "Match 💚" if parsed_info['phd_school'] in target_school_list else "Not Match 💔"
        print(f"\nPhD School: {parsed_info['phd_school']}, Match Status: {parsed_info['phd_match_status']}")

        if parsed_info['master_school'] == 'NA':
            parsed_info['master_match_status'] = 'NA'
        else:
            parsed_info['master_match_status'] = "Match 💚" if parsed_info['master_school'] in target_school_list else "Not Match 💔"
        print(f"Master's School: {parsed_info['master_school']}, Match Status: {parsed_info['master_match_status']}")

        if parsed_info['bachelor_school'] == 'NA':
            parsed_info['bachelor_match_status'] = 'NA'
        else:
            parsed_info['bachelor_match_status'] = "Match 💚" if parsed_info['bachelor_school'] in target_school_list else "Not Match 💔"
        print(f"Bachelor's School: {parsed_info['bachelor_school']}, Match Status: {parsed_info['bachelor_match_status']}")

        return parsed_info

    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        print(f"Cleaned response: {cleaned_content}")
        raise ValueError(f"Error parsing OpenAI response: {e}")


# Function to sanitize filename components
def sanitize_filename_component(component):
    if component is None:
        component = 'Unknown'  # Default value if None
    elif isinstance(component, int):
        component = str(component)  # Convert integers to strings
    return str(component).replace('/', '_').replace('\\', '_').replace(':', '_').strip()

def generate_filename(parsed_info):
    # Handle missing or empty fields with default values, using sanitization
    name = sanitize_filename_component(parsed_info.get('name', 'Unknown Name').strip())
    major = sanitize_filename_component(parsed_info.get('major', 'Unknown Major').strip())
    grad_year = sanitize_filename_component(parsed_info.get('grad_year', 'Unknown Year'))

    # Determine the school based on the highest education level
    if parsed_info.get('education_level') == "PhD":
        school = sanitize_filename_component(parsed_info.get('phd_school', 'Unknown School').strip())
    elif parsed_info.get('education_level') == "Master's":
        school = sanitize_filename_component(parsed_info.get('master_school', 'Unknown School').strip())
    else:
        school = sanitize_filename_component(parsed_info.get('bachelor_school', 'Unknown School').strip())

    # Logic to determine if the final match status should be "Match" or "Not Match"
    phd_match_status = parsed_info.get('phd_match_status', 'NA')
    master_match_status = parsed_info.get('master_match_status', 'NA')
    bachelor_match_status = parsed_info.get('bachelor_match_status', 'NA')

    # Determine if all non-NA match statuses are "Match"
    applicable_matches = [
        phd_match_status if phd_match_status != 'NA' else None,
        master_match_status if master_match_status != 'NA' else None,
        bachelor_match_status if bachelor_match_status != 'NA' else None
    ]
    
    # Filter out None values (for schools that are NA) and check if all remaining statuses are "Match"
    applicable_matches = [status for status in applicable_matches if status is not None]
    final_match_status = "Match" if all(status == "Match 💚" for status in applicable_matches) else "Not Match"

    # Convert education level to Simplified Chinese
    education_level = parsed_info.get('education_level', '本科').strip()
    if education_level == "Bachelor's":
        education_level = "本科"
    elif education_level == "Master's":
        education_level = "硕士"
    elif education_level == "PhD":
        education_level = "博士"
    
    # Determine if it's 实习 (intern) or 全职 (full-time)
    job_type = '实习' if grad_year.isdigit() and int(grad_year) > 2024 else '全职'

    # Construct the filename
    filename = f"{final_match_status}-{job_type}-{education_level}-{school}-{grad_year}-{major}-{name}"
    return filename
