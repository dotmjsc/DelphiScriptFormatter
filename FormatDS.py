import tkinter as tk
from tkinter import filedialog
import configparser
import shutil
import os
import subprocess
import sys
import chardet

from error_decoder import extract_error_messages, extract_error_info, find_single_prjscr_file, update_prjscr_file
from like_handler import like_processing_content_restore, like_processing_content_preprocess


class FileProcessorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("DelphiScript Formatter 0.6")

        # Set minimum window size
        self.master.minsize(width=400, height=150)

        self.file_path = None
        self.config_file_path = None
        self.rev_config_file_path = None

        # Initialize checkbox variables
        self.comma_handler_var = tk.BooleanVar()
        self.delimiter_handler_var = tk.BooleanVar()
        self.like_handler_var = tk.BooleanVar()
        self.generate_bak_var = tk.BooleanVar()
        self.keep_work_var = tk.BooleanVar()

        self.file_path_label = tk.Label(self.master, text="File Path:")
        self.file_path_label.pack(padx=10, pady=(5, 0), anchor=tk.W)

        self.config_label_text = tk.StringVar()
        self.config_label_text.set("Config File: Default")
        self.file_path_label_cfg = tk.Label(self.master, textvariable=self.config_label_text)
        self.file_path_label_cfg.pack(padx=10, pady=(0, 5), anchor=tk.W)

        # Checkbox for Function declaration format comma handler
        self.comma_handler_var = tk.BooleanVar()
        self.comma_handler_checkbox = tk.Checkbutton(self.master, text="Function declaration format comma handler",
                                                     variable=self.comma_handler_var,
                                                     command=self.update_config_file)
        self.comma_handler_checkbox.pack(padx=10, pady=(5, 0), anchor=tk.W)

        # Checkbox for Change declaration delimiters to semicolons
        self.delimiter_handler_var = tk.BooleanVar()
        self.delimiter_handler_checkbox = tk.Checkbutton(self.master,
                                                         text="Change declaration delimiters to semicolons",
                                                         variable=self.delimiter_handler_var,
                                                         command=self.update_config_file,
                                                         state=tk.DISABLED)
        self.delimiter_handler_checkbox.pack(padx=10, pady=(0, 5), anchor=tk.W)

        self.like_handler_var = tk.BooleanVar()
        self.like_handler_checkbox = tk.Checkbutton(self.master,
                                                    text="Preprocess \'like\' operator",
                                                    variable=self.like_handler_var,
                                                    command=self.update_config_file)
        self.like_handler_checkbox.pack(padx=10, pady=(0, 5), anchor=tk.W)

        self.generate_bak_var = tk.BooleanVar()
        self.generate_bak_checkbox = tk.Checkbutton(self.master,
                                                    text="Make backup (.bak) file",
                                                    variable=self.generate_bak_var,
                                                    command=self.update_config_file)
        self.generate_bak_checkbox.pack(padx=10, pady=(5, 0), anchor=tk.W)

        self.keep_work_var = tk.BooleanVar()
        self.keep_work_checkbox = tk.Checkbutton(self.master,
                                                 text="Keep work (.wrk) file",
                                                 variable=self.keep_work_var,
                                                 command=self.update_config_file)
        self.keep_work_checkbox.pack(padx=10, pady=(0, 5), anchor=tk.W)

        self.generate_breakpoints_var = tk.BooleanVar()
        self.generate_breakpoints_checkbox = tk.Checkbutton(self.master,
                                                 text="Generate Breakpoints for Errors (to Altium .PrjScr File)",
                                                 variable=self.generate_breakpoints_var,
                                                 command=self.update_config_file)
        self.generate_breakpoints_checkbox.pack(padx=10, pady=(0, 5), anchor=tk.W)

        self.open_button = tk.Button(self.master, text="Open", command=self.open_file, width=15, height=2)
        self.open_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.process_button = tk.Button(self.master, text="Process", command=self.process_file, width=15, height=2,
                                        state=tk.DISABLED)
        self.process_button.pack(side=tk.RIGHT, padx=10, pady=5)

        self.load_config_button = tk.Button(self.master, text="Load Config", command=self.load_config, width=15,
                                            height=2)
        self.load_config_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Load setting states from config file
        self.load_settings()

    def load_settings(self):
        config = configparser.ConfigParser()
        try:
            config.read('DSF_settings.ini')
            self.comma_handler_var.set(config.getboolean('Settings', 'comma_handler'))
            self.delimiter_handler_var.set(config.getboolean('Settings', 'delimiter_handler'))
            self.like_handler_var.set(config.getboolean('Settings', 'like_handler'))
            self.generate_bak_var.set(config.getboolean('Settings', 'generate_bak'))
            self.keep_work_var.set(config.getboolean('Settings', 'keep_work_file'))
            self.generate_breakpoints_var.set(config.getboolean('Settings', 'generate_breakpoints'))
            self.update_checkbox_states()
        except configparser.Error:
            # If there's any issue reading the config file, all checkboxes will be set to default (False)
            pass

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'comma_handler': self.comma_handler_var.get(),
            'delimiter_handler': self.delimiter_handler_var.get(),
            'like_handler': self.like_handler_var.get(),
            'generate_bak': self.generate_bak_var.get(),
            'keep_work_file': self.keep_work_var.get(),
            'generate_breakpoints': self.generate_breakpoints_var.get()
        }
        with open('DSF_settings.ini', 'w') as configfile:
            config.write(configfile)

    def update_config_file(self):
        self.save_settings()
        self.update_checkbox_states()

    def update_checkbox_states(self):
        if not self.comma_handler_var.get():
            self.delimiter_handler_var.set(False)
            self.delimiter_handler_checkbox.config(state=tk.DISABLED)
        else:
            self.delimiter_handler_checkbox.config(state=tk.NORMAL)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pascal files", "*.pas")])
        if file_path:
            self.file_path_label.config(text="File Path: " + file_path)
            self.file_path = file_path
            self.process_button.config(state=tk.NORMAL)
        else:
            self.file_path_label.config(text="File Path:")
            self.file_path = None
            self.process_button.config(state=tk.DISABLED)

    def load_config(self):
        config_file_path = filedialog.askopenfilename(filetypes=[("Config files", "*.cfg")])
        if config_file_path:
            self.config_label_text.set("Config File: " + config_file_path)
            self.config_file_path = config_file_path

            # Check and modify the key in the config file if needed
            if self.check_and_modify_config():
                self.config_label_text.set("Config File: " + self.rev_config_file_path)
                self.config_file_path = self.rev_config_file_path
                print("Key 'JediCodeFormatSettings' renamed to 'CodeFormatSettings'. Using revised config file.")
            else:
                print("Using the provided config file.")
        else:
            self.config_label_text.set("Config File: Default")
            self.config_file_path = None

    def check_and_modify_config(self):
        if self.config_file_path and self.config_file_path.endswith('.cfg'):

            with open(self.config_file_path, 'rb') as config_file:
                config_content = config_file.read()

            # Check if JediCodeFormatSettings is present
            if b'JediCodeFormatSettings' in config_content:
                # Replace JediCodeFormatSettings with CodeFormatSettings
                modified_content = config_content.replace(b'JediCodeFormatSettings', b'CodeFormatSettings')

                # Save the modified content to a new file with _rev in the name
                self.rev_config_file_path = self.config_file_path.replace('.cfg', '_rev.cfg')

                with open(self.rev_config_file_path, 'wb') as rev_config_file:
                    rev_config_file.write(modified_content)

                return True

        return False

    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']

    def convert_declaration_format(self, line: str, to_script: bool):
        old_char = ','
        new_char = ';'
        # Direction setting
        if to_script:
            old_char = ';'
            new_char = ','
        # Check if the line starts with "procedure" or "function"
        if line.strip().startswith(('procedure', 'function')):
            # Find the position of the opening and closing parentheses
            start_index = line.find('(')
            end_index = line.find(')')

            # If both opening and closing parentheses are found
            if start_index != -1 and end_index != -1:
                # Replace commas with semicolons within the parentheses
                line = line[:start_index + 1] + line[start_index + 1:end_index].replace(old_char, new_char) + line[
                                                                                                              end_index:]

        return line


    def process_filename(self, file_name):
        # Replace forward slashes with backslashes
        file_name = file_name.replace('/', '\\')

        # Check if the file name has .wrk as extension and remove it
        if file_name.endswith('.wrk'):
            file_name = file_name[:-4]

        return file_name

    def process_file(self):

        # This is set when a formatting error is found
        format_error = False

        # Make a backup copy with .bak extension
        bak_file_path = self.file_path + ".bak"
        if self.generate_bak_var:
            shutil.copy2(self.file_path, bak_file_path)

        # Detect source file encoding
        source_encoding = self.detect_encoding(self.file_path)

        # Modify the file content
        with open(self.file_path, 'r', encoding=source_encoding, errors='ignore') as original_file:
            content = original_file.readlines()

        # Process declaration formatting
        if self.comma_handler_var.get():
            for i, line in enumerate(content):
                content[i] = self.convert_declaration_format(line, False)

        if self.like_handler_var.get():
            content = like_processing_content_preprocess(content)

        modified_content = "unit Test;\ninterface\nimplementation\n\n" + ''.join(content) + "\nend."

        with open(self.file_path + ".wrk", 'w', encoding=source_encoding) as new_file:
            new_file.write(modified_content)

        # Run pascal-format.exe with optional config file
        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        pascal_format_path = os.path.join(script_dir, "pascal-format.exe")

        command = [pascal_format_path]

        if self.rev_config_file_path:
            command.extend(["-config=" + self.rev_config_file_path])
        elif self.config_file_path:
            command.extend(["-config=" + self.config_file_path])

        command.extend([self.file_path + ".wrk"])

        print(command)

        try:
            subprocess.check_output(command)
        except subprocess.CalledProcessError as e:

            format_error = True

            # Read output from JCF
            output = e.output

            # Decode Bytes to str
            error_lines = output.decode()

            print(error_lines)

            # if breakpoints should be generated:
            if self.generate_breakpoints_var:

                # extract error messages from output: [Error] Message
                error_lines_processed = extract_error_messages(error_lines)

                for line in error_lines_processed:
                    error_info = extract_error_info(line)
                    filename = error_info.get('file_name')
                    project_file = find_single_prjscr_file(filename)

                    # Replace forward slashes with backslashes
                    file_name_sanitized = filename.replace('/', '\\')

                    # Check if the file name has .wrk as extension and remove it
                    if file_name_sanitized.endswith('.wrk'):
                        file_name_sanitized = file_name_sanitized[:-4]

                    error_info['file_name'] = file_name_sanitized

                    update_prjscr_file(project_file, error_info, -5)

        # only proceed if formatting was successful
        if not format_error:

            # Detect formatted file encoding
            formatted_encoding = self.detect_encoding(self.file_path + ".wrk")

            # After command completion, remove the added lines
            with open(self.file_path + ".wrk", 'r', encoding=formatted_encoding) as processed_file:
                lines = processed_file.readlines()

                # Process declaration formatting
                if self.comma_handler_var.get() and not self.delimiter_handler_var.get():
                    for i, line in enumerate(lines):
                        lines[i] = self.convert_declaration_format(line, True)

                lines_to_write = [line for line in lines if
                                  line.strip() not in ("unit Test;", "interface", "implementation", "end.")]

            # restore likes on the content if necessary
            if self.like_handler_var.get():
                lines_to_write = like_processing_content_restore(lines_to_write)

            # Remove newlines from the beginning
            while lines_to_write and lines_to_write[0] == "\n":
                lines_to_write.pop(0)

            # Remove newlines from the end
            while lines_to_write and lines_to_write[-1] == "\n":
                lines_to_write.pop()

            # Save the modified content back to the original .pas file without the added lines
            with open(self.file_path, 'w', encoding=source_encoding) as original_file:
                original_file.writelines(lines_to_write)

        # Delete the work file
        if not self.keep_work_var:
            os.remove(self.file_path + ".wrk")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorGUI(root)
    root.mainloop()
