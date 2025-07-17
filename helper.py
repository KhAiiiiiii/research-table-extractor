import re
from tkinter import filedialog

def open_file_dialog():
    file_path = filedialog.askopenfilename(title="Select a file",
                                           filetypes=[("Images", ["*.png", "*.jpg", "*.jpeg"])])
    if file_path:
        return file_path
    
def is_comma_separated_number(s):
    pattern = r'^[+-]?\d{1,3}(,\d{3})+(\.\d+)?$'
    return bool(re.fullmatch(pattern, s))

def is_percentage_string(s):
    pattern = r'^[+-]?((\d{1,3}(,\d{3})*|\d+)(\.\d+)?|\.\d+)\s*%\s*$'
    return bool(re.fullmatch(pattern, s))

def strip_comma_thousands(number_str):
    return re.sub(r'(?<=\d),(?=\d)', '', number_str)

def convert_percentage_to_decimal(percent_str):
    if percent_str.strip().endswith("%") and len(percent_str.strip()) > 1:
        number_part = percent_str[:-1].strip()
        try:
            return float(number_part) / 100.0
        except ValueError:
            return percent_str