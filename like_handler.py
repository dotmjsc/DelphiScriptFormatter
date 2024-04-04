import re

def like_processing_content_preprocess(content):
    content_modified = []

    for line in content:
        # Split the line into the part to be processed and the part to be ignored (comment)
        parts = line.split("//", 1)
        process_part = parts[0]  # Part to be processed
        comment_part = "//" + parts[1] if len(parts) > 1 else ""  # Comment part with slashes

        # Mockup function to process the part to be processed
        processed_part, reverse_info = process_like_statements(process_part)

        if reverse_info != "":
            content_modified.append(reverse_info)

        # Reassemble both parts into a single line
        modified_line = processed_part + comment_part
        content_modified.append(modified_line)

    return content_modified

def like_processing_content_restore(content_modified):
    restored_content = []
    processing_info_found = False
    leading_whitespace = ""
    processing_info = ""

    for line in content_modified:
        if line.strip().startswith("// LIKEPROCESSING_INFO:"):
            # Found a line containing 'LIKEPROCESSING_INFO'
            processing_info_found = True
            # Extract leading whitespace from the current line
            leading_whitespace = line[:len(line) - len(line.lstrip())]
            processing_info = line.strip()[len("// LIKEPROCESSING_INFO:"):].split(",")
            continue

        if processing_info_found:
            # Restore the original content
            original_line = revert_like_statements(line, processing_info)
            # Add leading whitespace back to the original line
            restored_content.append(leading_whitespace + original_line)
            processing_info_found = False
        else:
            restored_content.append(line)

    return restored_content

def revert_like_statements(line, processing_info):
    restored_line = line
    equals_positions = [i for i, char in enumerate(restored_line) if char == '=']
    offset = 0

    for equals_to_skip in processing_info:
        equals_to_skip = int(equals_to_skip)

        # Ensure the equals_to_skip is within the range of equals positions
        if 0 <= equals_to_skip < len(equals_positions):
            replacement_index = equals_positions[equals_to_skip]
            restored_line = restored_line[:replacement_index + offset] + 'like' + restored_line[replacement_index + 1 + offset:]
            # like as 3 chars more than = so advance
            offset = offset + 3

    return restored_line

def process_like_statements(part):
    # Regular expression pattern to find all occurrences of 'like' (case insensitive)
    pattern = r'\blike\b'

    # Find all occurrences of 'like' (case insensitive) and replace them with '='
    processed_part = re.sub(pattern, '=', part, flags=re.IGNORECASE)

    # Initialize the reverse info
    reverse_info = ""

    found_likes = 0

    # If 'like' processing occurred
    if re.search(pattern, part, flags=re.IGNORECASE):
        # Create a string to facilitate reverse replacement
        # This string will be a comment with slashes starting with 'LIKEPROCESSING_INFO'
        # Each 'like' replacement is indicated by the number of '=' to be skipped
        # So that the reverse function knows where a '=' should be replaced by a 'like'
        reverse_info = "// LIKEPROCESSING_INFO: "
        like_positions = [m.start() for m in re.finditer(pattern, part, flags=re.IGNORECASE)]
        for pos in like_positions:
            # Count the number of '=' to skip
            equals_to_skip = part.count('=', 0, pos)
            reverse_info += str(equals_to_skip + found_likes) + ","
            # each processed like makes a extra skip for restoring
            found_likes = found_likes + 1
        # Remove the last comma

        reverse_info = reverse_info[:-1]

        # make a full comment line if like is found
        if found_likes > 0:
            reverse_info = reverse_info + '\n'

    # Return both the processed part and the reverse info
    return processed_part, reverse_info

if __name__ == '__main__':
    import chardet
    def detect_encoding(file_path):
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']


    filename = "test_like_handling.pas"

    # Example usage:
    source_encoding = detect_encoding(filename)

    # Modify the file content
    with open(filename, 'r', encoding=source_encoding, errors='ignore') as original_file:
        content = original_file.readlines()

    for line in content:
        print(repr(line))

    content_modified = like_processing_content_preprocess(content)
    for line in content_modified:
        print(repr(line))

    restored_content = like_processing_content_restore(content_modified)
    for line in restored_content:
        print(repr(line))
