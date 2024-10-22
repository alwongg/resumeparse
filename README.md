# ResumeParse

**ResumeParse** is a command-line tool designed to help recruiters efficiently rename and filter a list of resumes using OpenAI for parsing and text recognition. This tool extracts key information from resumes, checks against a target school list, and renames the files accordingly.

## Requirements

You can install all dependencies using:

```
pip install -r requirements.txt
```

## Environment Setup
You need to provide your OpenAI API key in a .env file. Create a .env file in your project root directory with the following content:
```
OPENAI_API_KEY=your_openai_api_key
```

## Usage
Prepare Your Folders:

Place all unprocessed resumes inside a folder named unprocessed_resumes.
Create a file named target_school_list.txt and add your list of target schools in Simplified Chinese.
Run the Script: Open a terminal, navigate to the ResumeParse directory, and run the following command:
```
python ResumeParse.py
```

## Output:

The script will automatically process all resumes in the unprocessed_resumes folder and output the renamed files to a folder named processed_resumes.
If any errors occur, those resumes will be renamed with "ERROR" as a prefix.

## How It Works
1. Text Extraction: The tool extracts text from resumes in .pdf, .docx, and .doc formats using various techniques, such as MuPDF, python-docx, docx2txt, and OCR.
2. Content Parsing: The extracted text is sent to OpenAI's model, which identifies and extracts key information like education level, name, major, graduation year, and attended schools.
3. School Matching: The tool compares the extracted school names with the list in target_school_list.txt to determine if there’s a match.
4. Renaming: The resumes are renamed based on extracted information and match status, and the files are moved to the processed_resumes folder.
