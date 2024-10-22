from utilities import extract_text_from_file, parse_content, generate_filename
import os
import shutil

def handle_file_error(file, output_dir, error_message, file_num, total_files):
    error_filename = f"ERROR - {os.path.basename(file)}"
    error_filepath = os.path.join(output_dir, error_filename)
    shutil.copyfile(file, error_filepath)  # Ensure file is copied to the output directory
    return False, f"Error {file_num}/{total_files} encountered an issue: {error_message} ❌"

def process_file(file, output_dir, target_school_list, file_num, total_files):
    print(f'-------------------------------------------------------------------------------------\nProcessing file: {file}...')

    # Extract text from file
    try:
        text_content = extract_text_from_file(file)
        if not text_content.strip():  # Check if text content is empty or just whitespace
            return handle_file_error(file, output_dir, "No text extracted from the resume.", file_num, total_files)
    except Exception as e:
        return handle_file_error(file, output_dir, f"Error extracting text: {e}", file_num, total_files)

    print('Waiting for response from OpenAI...')

    try:
        # Pass the target_school_list to the parse_content function
        parsed_info = parse_content(text_content, target_school_list)
        if not parsed_info:  # Check if parsed_info is empty or null
            return handle_file_error(file, output_dir, "Parsed content is empty. The resume might lack required information.", file_num, total_files)
    except Exception as e:
        return handle_file_error(file, output_dir, f"Error with OpenAI response: {e}", file_num, total_files)

    # Get the original file extension
    file_extension = os.path.splitext(file)[1]

    # Generate the new filename
    try:
        filename = f"{generate_filename(parsed_info)}{file_extension}"
        print(f"\nNew filename: {filename}")
        
        # Copy the file to the output directory with the new name
        shutil.copyfile(file, os.path.join(output_dir, filename))
        return True, f"Done {file_num}/{total_files} with no problems ✅"
    except Exception as e:
        return handle_file_error(file, output_dir, f"Error renaming file: {e}", file_num, total_files)

def main():
    source_dir = 'unprocessed_resumes'
    output_dir = 'processed_resumes'
    target_list_file = 'target_school_list.txt'

    # Check if the source directory exists, stop the program if it doesn't
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    # Ensure the output directory exists, create it if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Check if the target list file exists
    if not os.path.exists(target_list_file):
        print(f"Error: Target list file '{target_list_file}' does not exist.")
        return

    # Read target school list
    with open(target_list_file, 'r', encoding='utf-8') as f:
        target_school_list = [x.strip() for x in f.readlines()]

    # Get all files with the following extensions: PDF, DOCX, DOC
    files = [file for file in os.listdir(source_dir) if file.endswith((".pdf", ".docx", ".doc"))]
    total_files = len(files)
    successfully_processed_count = 0  # Files renamed and created successfully
    error_files_count = 0  # Files that encountered errors and renamed with "ERROR - name"

    # Print initial message with number of resumes
    print(f"\nHello, I'm ResumeParse. I will now process {total_files} resumes for you.")
    print()

    # Process each file
    for file_num, file in enumerate(files, 1):
        file_path = os.path.join(source_dir, file)
        success, result = process_file(file_path, output_dir, target_school_list, file_num, total_files)
        print(result)
        
        # Increment counters based on outcome
        if success:
            successfully_processed_count += 1  # Increment count for successfully processed files
        else:
            error_files_count += 1  # Increment count for error files

    # Final message after all files are processed
    print(f"ResumeParse renamed and created {successfully_processed_count} resumes for you 🥳")
    print(f"{error_files_count} resume(s) were renamed with 'ERROR' due to issues 😡\n")

if __name__ == "__main__":
    main()
