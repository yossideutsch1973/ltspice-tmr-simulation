import re; file_content = open("tmr_schematic_drawer.py", "r").read(); quotation_marks = re.findall("\"\"\"", file_content); print(f"Number of triple quotation marks: {len(quotation_marks)}")
