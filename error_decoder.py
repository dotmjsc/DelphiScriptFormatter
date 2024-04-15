import configparser
import os
import re
import chardet


def extract_error_messages(input_string):
    # Replace all '\r\n' with whitespace
    processed_string = input_string.replace('\r\n', ' ')

    # Split the string into parts based on the delimiters '[Info]' and '[Error]'
    parts = re.split(r'(\[Info\]|\[Error\])', processed_string)

    # Filter out empty strings and trim whitespace
    parts = [part.strip() for part in parts if part.strip()]

    # Filter parts to only include error messages
    error_messages = [parts[i+1] for i, part in enumerate(parts) if part == '[Error]']

    return error_messages


def extract_error_info(error_message):
    # Split the error message by the first occurrence of ": "
    filename_end = error_message.find(": ")
    file_info = error_message[:filename_end]
    rest = error_message[filename_end + 2:]

    # Initialize line number and char position as None
    line_number = None
    char_position = None

    # Extract line number and character position if available
    brace_start = rest.find("(")
    brace_end = rest.find(")")
    if brace_start != -1 and brace_end != -1:
        line_char_info = rest[brace_start + 1:brace_end]
        try:
            line_number, char_position = line_char_info.split(":")
            line_number = int(line_number.strip())
            char_position = int(char_position.strip())
        except:
            line_number = None
            char_position = None

    # Extract error message
    if brace_end != -1:
        error_msg = rest[brace_end + 1:].strip()
    else:
        error_msg = rest.strip()

    # Create a dictionary to store the extracted information
    error_info = {
        'file_name': file_info,
        'line_number': line_number,
        'char_position': char_position,
        'error_message': error_msg
    }

    return error_info

def find_single_prfscr_file(file_name):
    # Extract the path from the file name
    file_path = os.path.dirname(file_name)

    print(file_path)

    # List files with extension .PrjScr in the directory
    prfscr_files = [f for f in os.listdir(file_path) if f.upper().endswith('.PRJSCR')]

    # If there is only one .PrfScr file, return its complete path
    if len(prfscr_files) == 1:
        return os.path.join(file_path, prfscr_files[0])
    elif len(prfscr_files) == 0:
        print('No Project Files found to process!')
        return None
    else:
        print('Multiple Project Files found, not processing!')
        return None


def update_prfscr_file(file_path, error_info, offset):

    # check if a error in a line is found
    if file_path is not None and error_info['line_number'] is not None:

        # detect encoding
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']

        # Initialize configparser
        config = configparser.ConfigParser()

        # Read the existing file if it exists
        if os.path.exists(file_path):
            config.read(file_path, encoding=encoding)

        # Add or update [Generic_ScriptingSystemBreakpoints] section
        if not config.has_section('Generic_ScriptingSystemBreakpoints'):
            config.add_section('Generic_ScriptingSystemBreakpoints')

        # Check if the entry already exists
        for index in range(50):
            try:
                module_name_existing = config.get('Generic_ScriptingSystemBreakpoints', f'ModuleName{index}')
                condition_existing = config.get('Generic_ScriptingSystemBreakpoints', f'Condition{index}')
                line_existing = config.get('Generic_ScriptingSystemBreakpoints', f'Line{index}')
            except:
                module_name_existing = ""
                condition_existing = ""
                line_existing = ""

            if error_info['file_name'] == module_name_existing and str(error_info['line_number']) == line_existing and error_info['error_message'] == condition_existing:
                print('Do not make duplicate Error Breakpoint')
                return

        # Find the next available index
        index = 1
        while True:
            if f'ModuleName{index}' not in config['Generic_ScriptingSystemBreakpoints']:
                break
            index += 1

        # Add error info to the section
        config.set('Generic_ScriptingSystemBreakpoints', f'ModuleName{index}', error_info['file_name'])
        config.set('Generic_ScriptingSystemBreakpoints', f'Line{index}', str(error_info['line_number'] + offset))
        config.set('Generic_ScriptingSystemBreakpoints', f'Condition{index}', error_info['error_message'])
        config.set('Generic_ScriptingSystemBreakpoints', f'Enabled{index}', 'True')

        # Write the changes back to the file
        with open(file_path, 'w', encoding=encoding) as config_file:
            config.write(config_file, space_around_delimiters=False)

if __name__ == '__main__':
    test_error = b'[Info] C:/Users/viemar119/Desktop/WorkData/Python_Projects/AltiumDelphiFormatter/TEst.pas.wrk: Formatting file C:/Users/viemar119/Desktop/WorkData/Python_Projects/AltiumDelphiFormatter/TEst.pas.wrk\r\n[Error] C:/Users/viemar119/Desktop/WorkData/Python_Projects/AltiumDelphiFormatter/TEst.pas.wrk: (6:1) Exception TEParseError  Unexpected token, expected "BEGIN"\r\nNear vard\r\n[Info] C:/Users/viemar119/Desktop/WorkData/Python_Projects/AltiumDelphiFormatter/TEst.pas.wrk: Aborted due to error\r\n'

    error_lines = test_error.decode()
    error_lines_processed = extract_error_messages(error_lines)
    for line in error_lines_processed:
        print(line)
        error_info = extract_error_info(line)
        filename = error_info.get('file_name')
        project_file = find_single_prfscr_file(filename)
        update_prfscr_file(project_file, error_info, 0)

