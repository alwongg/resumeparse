# ResumeParse Project Documentation

## Overview

The ResumeParse project is a command-line tool designed to process resumes by extracting key information from files, interacting with OpenAI to parse the content, and renaming the files based on the extracted details. The main functionality revolves around handling files, extracting relevant content, and ensuring that the filenames reflect the parsed information.

The project uses multiple technologies, including PyMuPDF (for PDF text extraction), PyTesseract (for Optical Character Recognition), OpenAI API for text parsing, and Python's shutil and os libraries for file manipulation. The tool was designed to interact dynamically with a target school list, providing a way to assess whether the candidate’s educational institutions match the provided list of target schools.

## Project Structure

- **ResumeParse.py**: The main script that handles argument parsing, file processing, and interactions with helper functions. It handles the workflow from file extraction to renaming based on the parsed content.
- **utilities.py**: Contains utility functions for extracting text, interacting with OpenAI, parsing the content, and generating file names.

## Workflow Overview

### File Processing:

It processes files with `.pdf`, `.docx`, or `.doc` extensions from the source directory and attempts to extract text from them.

- **PDF Files**: Uses PyMuPDF to extract text. If that fails, it falls back to OCR using PyTesseract.
- **DOCX Files**: Attempts extraction using `python-docx` and falls back to `docx2txt` and OCR if necessary.
- **DOC Files**: Uses antiword on Linux/Mac systems or skips the file on unsupported platforms like Windows.

### OpenAI Interaction:

- **Text Parsing**: Once the text is extracted from the file, it is passed to OpenAI’s GPT-3.5-turbo model via the `parse_content()` function in `utilities.py`.
- **Prompt Engineering**: The system message in the OpenAI prompt is carefully constructed to ensure the model returns specific structured data. This includes extracting the education level, candidate’s name, major, graduation year, and school names.
- **JSON Parsing**: The response from OpenAI is received as text and then cleaned, formatted, and parsed as JSON. This parsed information is used to determine the appropriate filename based on the educational background.

### Target School Matching:

If a target school list is provided, the tool checks whether the extracted school names match the schools in the list. A match status is appended to the parsed information, such as "Match 💚" for matching schools or "Not Match 💔" for non-matching schools.

### File Renaming:

Based on the parsed information, the tool generates a new filename that includes details like the candidate’s name, education level, graduation year, major, and school match status. The file is then copied to the output directory with the new filename.

## Key Features and Functionality

### File Handling and Error Management:

The `process_file()` function ensures that errors in text extraction or parsing do not crash the program. If an error occurs, the file is renamed with a prefix of `ERROR`, and processing continues.

### OpenAI Interaction:

The `parse_content()` function interacts with OpenAI’s GPT-3.5-turbo to parse resumes and extract the required information in JSON format. The prompt is designed to ensure accurate extraction of fields like education level, name, major, graduation year, and school names.

#### Example of the system prompt:

You are a professional-grade resume parser. You will be provided with text content extracted from a resume file. Your task is to return clean, accurate JSON formatted data with the following keys:

- 'education_level' (highest level of education: Bachelor's, Master's, or PhD)
- 'name' (full name of the candidate)
- 'major' (in Simplified Chinese)
- 'grad_year' (graduation year)
- 'phd_school', 'master_school', 'bachelor_school' (in Simplified Chinese only)

### File Renaming:

The `generate_filename()` function in `utilities.py` uses the parsed information to generate a descriptive filename. The filename includes:

- **Match Status**: Whether the candidate’s school matches a target school from the provided list.
- **Job Type**: Identifies if the candidate is applying for an internship (实习) or full-time (全职) position based on the graduation year.
- **Education Level**: Converts the education level to Simplified Chinese.

#### Final Filename Example:

Not Match-实习-硕士-清华大学-2023-计算机科学-王伟.pdf

## Challenges and Lessons Learned

### OpenAI Response Challenges:

OpenAI’s responses weren’t always in the expected JSON format, requiring additional cleaning and reformatting. I used regular expressions to clean unnecessary characters like backticks and extraneous JSON code blocks.
Choosing between which model to use required some experimenting because of usage cost. GPT-3.5-turbo turned out to be the most cost efficient and accurate model to use in case hundreds of resumes needed to be processed at a time.
Target school list was initially sent to OpenAI to process the match status but the results were very inconsistent, whether the problem was because of language requirements in Chinese or the school's response was making a literal comparison with the list.
Some fields would be populated as empty strings and therefore, filling the field with "NA" made processing the file a lot easier.

### Handling Multilingual Data:

- **Chinese vs English**: The system required proper handling of school names in both Simplified Chinese and English. OpenAI would sometimes return extra information in parentheses (e.g., English translations), which had to be removed using regex patterns.
- **Normalization of School Names**: To ensure proper matching between target school names and extracted names, I removed parenthesis-enclosed text and cleaning whitespace.

### Error Management:

I implemented robust error handling in `process_file()` to manage issues like empty files, text extraction errors, or parsing failures. Any file that encountered an error was saved with an "ERROR" prefix in the filename.

### Fallback Mechanisms:

I built fallback mechanisms for each step of text extraction. For example, if PyMuPDF failed to extract text from a PDF, the system would fall back to OCR. Similarly, if `python-docx` failed to process a `.docx` file, it would use `docx2txt` or OCR as a backup.

### Iterative Improvements:

Throughout the project, I iterated on how to handle edge cases in the input files, whether it was dealing with corrupted files or optimizing the OpenAI request to return cleaner JSON outputs. This iterative process helped ensure the tool could process a variety of resumes.

## Conclusion

In the ResumeParse Project, I built a professional-grade resume parsing tool that uses OpenAI’s GPT-3.5-turbo for parsing text content extracted from resumes. This project allowed me to explore:

- File handling and text extraction using multiple libraries.
- Interacting with OpenAI’s API to create dynamic and professional prompts for parsing structured data.
- Building robust error handling mechanisms and fallback strategies for handling complex file types.

This project has provided deep insights into building tools that automate document processing workflows while interacting with AI models. The flexibility and extensibility of the tool also make it suitable for real-world applications in resume management and recruitment.
``` 

This should now be properly formatted for Markdown. You can copy and paste this directly into your GitHub README or documentation file.
