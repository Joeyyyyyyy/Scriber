"""
Contains classes required for converting regular text into RTF and vice-versa. 
"""

from docx import Document
import win32clipboard as wc
import ctypes
import re

class WordFormat():
    def __init__(self):
        super().__init__()
        
    def escape_special_characters(self, text: str) -> str:
        """Escapes special characters for RTF format with fallbacks.

        Args:
            text (str): The input text to escape.

        Returns:
            str: The text with special characters escaped for RTF compatibility.
        """
        replacements = {
            '\\': '\\\\',        # Escape backslashes
            '{': '\\{',          # Escape opening curly braces
            '}': '\\}',          # Escape closing curly braces
            '\n': r'\par ',      # Replace newline characters with RTF paragraph breaks
            "'": r"\'27",        # Escape straight single quotes
            '‘': r'\u8216 ?',    # Left single quotation mark with fallback
            '’': r'\u8217 ?',    # Right single quotation mark or apostrophe with fallback
            '“': r'\u8220 ?',    # Left double quotation mark with fallback
            '”': r'\u8221 ?',    # Right double quotation mark with fallback
            '-': r'\u8208 ?',    # Hyphen with fallback
            '–': r'\u8211 ?',    # En dash with fallback
            '—': r'\u8212 ?',    # Em dash with fallback
            '…': r'\u8230 ?',    # Ellipsis with fallback
            'é': r'\u233 ?',     # e acute
            'ü': r'\u252 ?',     # u umlaut
            'ñ': r'\u241 ?',     # n tilde
            '&': r'\u38 ?',      # Ampersand
            '%': r'\u37 ?',      # Percent sign
            '±': r'\u177 ?',     # Plus-minus sign
            '≤': r'\u8804 ?',    # Less-than-or-equal-to sign
            '≥': r'\u8805 ?',    # Greater-than-or-equal-to sign
            '\xa0': r'\~',       # Non-breaking space
            '$': r'\u36 ?',      # Dollar sign
            '€': r'\u8364 ?',    # Euro sign
            '£': r'\u163 ?',     # Pound sign
            '¥': r'\u165 ?',     # Yen sign
            '•': r'\u8226 ?',    # Bullet
            '§': r'\u167 ?',     # Section sign
            '¶': r'\u182 ?',     # Pilcrow
            '®': r'\u174 ?',     # Registered sign
            '™': r'\u8482 ?',    # Trademark sign
            '½': r'\u189 ?',     # One-half fraction
            '¼': r'\u188 ?',     # One-quarter fraction
            '¾': r'\u190 ?',     # Three-quarters fraction
            '×': r'\u215 ?',     # Multiplication sign
            '÷': r'\u247 ?',     # Division sign
        }
        for key, value in replacements.items():
            text = text.replace(key, value)
        return text
    
    def title_line(self, text: str) -> str:
        """Converts the first line of the text to uppercase and appends it back.

        Args:
            text (str): The input text.

        Returns:
            str: The text with the first line capitalized and formatted.
        """
        lines = text.splitlines()

        if lines:
            # Extract the first line and convert it to uppercase
            first_line = lines[0].upper()
            first_line.replace('\n',"")
            if("TIMESTAMPS," in first_line):
                first_line="+"+first_line+"+"
            # Rejoin the rest of the lines
            remaining_text = '\n'.join(lines[1:])
            # Append the capitalized first line to the original text
            return first_line + '\n' + remaining_text
        
        return text  # If no lines exist, return the original text

    def remove_empty_lines(self, text: str) -> str:
        """Removes empty lines from the input text.

        Args:
            text (str): The input text.

        Returns:
            str: The text without empty lines.
        """
        lines = text.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)
    
    def process_text(self, text: str, mode: int = 0) -> str:
        """Processes text for RTF formatting based on the mode specified.

        Args:
            text (str): The input text to process.
            mode (int): The processing mode (0 or 1) that determines formatting rules.

        Returns:
            str: The processed RTF text.
        """
        lines = text.split('\par')  # Split the string into lines
        ntext=""
        # Apply functions to each line and join them back
        if mode==0:
            for line in lines:
                line = line.replace('\u200b', '')
                line = line.replace('\u202f', '')
                line=self.format_asterisked_strings(line) 
                if("TIMESTAMPS," in line):
                    line=self.format_plus_strings(line)
                ntext+=line+'\par'
        else:
            for line in lines:
                line = line.replace('\u200b', '')
                line=line.replace('\u202f','')
                line=self.format_asterisked_strings(line) 
                line=self.format_italicized_strings(line) 
                line=self.format_bulletpoint_strings(line)
                ntext+=line+'\par '
        return ntext
    
    def format_bulletpoint_strings(self, doc):
        lines = doc.splitlines()
        bullet_pointed_lines = []

        for line in lines:
            stripped_line = line.strip()  # Strip once for efficiency
            
            # Check if line starts with '*' and there is a space after it
            if stripped_line.startswith('*'):
                if len(stripped_line) > 1 and stripped_line[1] == ' ':  # Ensure there's a space after '*'
                    bullet_pointed_lines.append("• " + stripped_line[2:].strip())  # Remove '*' and the space
                elif len(stripped_line) == 1:  # Handle case where line is just '*'
                    bullet_pointed_lines.append("•")
                else:
                    bullet_pointed_lines.append(stripped_line)  # Append the normal line
            else:
                bullet_pointed_lines.append(stripped_line)  # Append the normal line

        return '\n'.join(bullet_pointed_lines)
    
    def format_asterisked_strings(self,doc):
        """Format strings surrounded by asterisks as bold in RTF."""
        pattern = r'\*(.*?)\*'
        
        def replace(match):
            substring = match.group(1) 
            return r"{\b " + substring + "}"
        
        formatted_string = re.sub(pattern, replace, doc)
        return formatted_string
    
    def format_italicized_strings(self, doc):
        """Format strings surrounded by slashes as italic in RTF."""
        pattern = r'\_(.*?)\_'

        def replace(match):
            substring = match.group(1) 
            return r"{\i " + substring + "}"

        formatted_string = re.sub(pattern, replace, doc)
        return formatted_string
    
    def format_plus_strings(self,doc):
        """Format strings surrounded by asterisks as bold in RTF."""
        pattern = r'\+(.*?)\+'
        
        def replace(match):
            substring = match.group(1) 
            return r"{\ul " + substring + "}"
        
        formatted_string = re.sub(pattern, replace, doc)
        return formatted_string

    def generate_rtf_bold(self, text: str, mode: int = 0) -> str:
        """Generates RTF-formatted text with optional bold and formatting modes.

        Args:
            text (str): The input text to format.
            mode (int): Optional; 0 for processing Time Stamps, 1 for regular processing.

        Returns:
            str: The RTF formatted text.
        """
        if mode==0:
            text=self.remove_empty_lines(text)
            text=self.title_line(text)
        
        rtf_header = r"{\rtf1\ansi\ansicpg1252\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}}"
        rtf_footer = r"}"
        
        # Escape the input text
        escaped_text = self.escape_special_characters(text)
        rtf = self.process_text(escaped_text,mode)
        normal_text = r""  # Adjust as needed
        
        # Combine header, bolded text, normal text, and footer
        return rtf_header + rtf + normal_text + r"\par " + rtf_footer

    def copy_rtf_to_clipboard(self, rtf_data: str) -> None:
        """Copies the RTF-formatted data to the system clipboard.

        Args:
            rtf_data (str): The RTF data to copy.
        """
        CF_RTF = ctypes.windll.user32.RegisterClipboardFormatW("Rich Text Format")
        
        try:
            wc.OpenClipboard()
            wc.EmptyClipboard()
            # Set clipboard data as RTF
            wc.SetClipboardData(CF_RTF, rtf_data.encode('windows-1252'))
        finally:
            wc.CloseClipboard()

class WordExtractor():
    def __init__(self,filepath:str):
        super().__init__()
        self.filepath=filepath
        self.txtpath=self.convertor(self.driver(self.filepath))

    def is_numbered_list(self,paragraph):
        # Check if the paragraph has numbering properties
        numPr = paragraph._element.xpath('.//w:numPr')
        return len(numPr) > 0

    def count_trailing_whitespace(self,s):
        return len(s) - len(s.rstrip())
    
    def extract_text_from_word(self, file_path: str, output_txt_file: str) -> None:
        """Extracts text from a Word document and saves it to a text file.

        Args:
            file_path (str): The path to the Word document.
            output_txt_file (str): The output path for the extracted text file.
        """
        # Open the Word document
        doc = Document(file_path)

        list_number = 0  # Initialize a counter for numbered lists

        # Open the output text file in write mode
        with open(output_txt_file, 'w', encoding='utf-8') as txt_file:
            gap=""
            # Loop through each paragraph in the document
            for para in doc.paragraphs:
                # Detect if the paragraph is a heading
                if para.style.name.startswith('Heading'):
                    txt_file.write(gap)
                    gap=""
                    txt_file.write(f"*{para.text.strip()}*\n")
                    list_number=0
                    continue  # Move to the next paragraph after writing the heading
                
                # Detect numbered lists or bullet point lists by checking for numbering properties
                if self.is_numbered_list(para):
                    if gap!="" and list_number!=0:
                        gap=""
                    if list_number == 0:  # First item in a new numbered list
                        list_number = 1
                    else:
                        list_number += 1  # Increment the counter for each numbered list item
                    line = f'{list_number}. '
                    for run in para.runs:
                        text_to_add = run.text
                        whitecount=self.count_trailing_whitespace(text_to_add)
                        if run.bold and text_to_add.strip() != '':
                            text_to_add = f"*{text_to_add.strip()}*"+ ' '*whitecount  # Mark bold text with asterisks
                        if run.italic and text_to_add.strip() != '':
                            text_to_add = f"_{text_to_add.strip()}_"+ ' '*whitecount  # Mark italic text with underscores
                        line += text_to_add
                    txt_file.write(line + '\n')

                else:
                    backup_ln=list_number
                    #list_number=0 # Reset the counter when leaving a numbered list
                    # Ignore page breaks but preserve empty lines
                    if 'PAGE' in para._element.xml:
                        continue  # Skip page breaks only

                    # For empty paragraphs, simply add a blank line
                    if para.text.strip() == '':
                        gap+='\n'
                        continue  # Move to the next paragraph
                    
                    # list_number = 0  # Reset the counter when leaving a numbered list
                    # Loop through each run in the paragraph to identify bold and italic text
                    line = ""
                    for run in para.runs:
                        txt_file.write(gap)
                        gap=""
                        list_number=0
                        text_to_add = run.text
                        whitecount=self.count_trailing_whitespace(text_to_add)
                        if run.bold and text_to_add.strip() != '':
                            text_to_add = f"*{text_to_add.strip()}*"+ ' '*whitecount  # Mark bold text with asterisks
                        if run.italic and text_to_add.strip() != '':
                            text_to_add = f"_{text_to_add.strip()}_"+ ' '*whitecount  # Mark italic text with underscores
                        line += text_to_add
                    txt_file.write(line + '\n')

        print(f"Text has been extracted and saved to {output_txt_file}")
        

    def driver(self, filepath: str) -> str:
        """Processes a Word document and extracts text to a UTF-8 encoded text file.

        Args:
            filepath (str): The path to the Word document.

        Returns:
            str: Path to the extracted UTF-8 text file.
        """
        output_txt_path = self.filepath.replace('.docx','_utf8_backup.txt')
        self.extract_text_from_word(filepath,output_txt_path)
        return output_txt_path     
    
    def convertor(self, input_file: str) -> str:
        """Converts a UTF-8 text file to CP1252 encoding.

        Args:
            input_file (str): The path to the input UTF-8 text file.

        Returns:
            str: Path to the converted CP1252 text file.
        """
        with open(input_file, 'r', encoding='utf-8') as infile:
            # Read the file contents
            content = infile.read()

        output_file=input_file.replace('_utf8_backup.txt','.txt')
        
        # Open the output file in CP1252 encoding and write the content
        with open(output_file, 'w', encoding='cp1252', errors='replace') as outfile:
            # Write the content to the file in CP1252 encoding
            outfile.write(content)

        print("File conversion completed!")
        
        return(output_file)
    
    def getPath(self) -> str:
        """Retrieves the path to the converted text file.

        Returns:
            str: Path to the converted CP1252 text file.
        """
        return self.txtpath  

# Driver Function for testing purposes
if __name__ == "__main__":
    input_text = "hello\n\nHow are you my *dawg*\n\n*Joena\n&hehe\n*"
    wf= WordFormat()
    rtf_bold_text = wf.generate_rtf_bold(input_text)
    wf.copy_rtf_to_clipboard(rtf_bold_text)
    print("RTF bold text copied to clipboard. You can paste it into Word.")