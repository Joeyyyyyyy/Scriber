"""
Developer Notes:
##(1.1.0) Updated format of the heading
##(1.1.0) Updated formatting of timestamps
##(1.1.0) Added exit confirmation to the File menu
##(1.2.0) Added auto-save feature
##(1.3.0) Enhanced readability by adding asterisks to the heading and timestamps
##(1.4.0) Implemented a backup save function
##(1.5.0) Added dropdown menu for start time input
##(1.6.0) Integrated sequence tag reference and mention dropdown menus
##(2.0.0) Redesigned the entire user interface
##(2.0.1) Fixed issue with file open operation error
##(2.1.0) Added keyboard shortcut (Ctrl+S) for saving
##(2.2.0) Introduced a File dropdown menu for file operations
##(2.2.0) Changed start time input to a button
##(2.2.1) Resolved issue with dropdown menu name settings
##(2.3.0) Secured the backup process
##(2.3.1) Removed colon from timestamps for consistency
##(2.4.0) Added word checker for American English words which can be toggled by keyboard shortcut (Ctrl+W)
##(2.4.0) Fixed extra space after timestamps
##(2.4.1) Added right-click context menu for text operations
##(2.5.0) Added Pause-Resume button for tracking lost time
##(2.6.0) Created a manual time difference changer
##(3.0.0) Added display toggle for time elapsed
##(3.1.0) Added Start Time indicator on the button
##(3.2.0) Added RTF converter to export to MS Word
##(3.3.0) Added basic proofreader
##(3.4.0) Added event report generation feature
##(3.4.0) Improved backup save reliability
##(3.4.1) Fixed Word format glitch
##(3.4.1) Enhanced auto-save in the open function
##(3.5.0) Added modes in WordFormat class
##(3.5.0) Added shortcut CTRL+Q for Word formatting
##(3.5.1) Added more words in the american words list and removed comments
##(3.6.0) Report Generator mentions the no. of the breakout room
##(3.6.1) Report Generator always adds a 5min Introductions at #1 by default
##(3.6.1) Report Generator also has a Shares section.
##(3.6.1) Added more words to american words dataset
##(3.7.1) Added more words to american words dataset and made minor tweaks in report
##(3.7.1) Added the docx extraction feature
##(3.7.1) Made the Open File feature more secure
##(3.7.2) Added Object deletion for memory optimization
"""

import tkinter as tk
import pyperclip
from tkinter import filedialog, messagebox, simpledialog,Menu
import time
from datetime import datetime, timedelta
import os
import customtkinter as ctk
from deps.awlist import american_words
from deps.format import WordFormat, WordExtractor
from deps.proofreader import WhatsAppChecker
import tkinter.font as tkFont
from deps.ReportGenerator import ReportGenerator as rg

# Initialize customtkinter
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (default), "dark-blue", "green"

# Create the main application window
class ChScriber(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Scriber")
        self.geometry("800x600")

        # Create a custom toolbar
        self.toolbar = ctk.CTkFrame(self, height=40, fg_color="#2b2b2b")
        self.toolbar.pack(side="top", fill="x")
        
        # Set the icon using an .ico file
        #try:
         #   self.iconbitmap("build/logo.ico")
        #except Exception as e:
         #   print(str(e))
        
        # Initializing start time
        self.s_hour = 14
        self.s_minute = 30
        self.s_second = 0
        self.time_difference_str = None
        self.showhourmin = True
        
        # File Dropdown menu
        self.functions=["Open","Save","Word Checker","Time Lost","Proofread","Export to Word","Import from Word","Generate Report","Display Time Elapsed (Active)"]
        self.file_menu = ctk.CTkOptionMenu(self.toolbar, values=self.functions, command=lambda f=self.functions: self.handlefunctions(f))
        self.file_menu.pack(side="left", padx=10, pady=5)
        self.file_menu.set("File")

        # Add start time button
        self.start_time_button = ctk.CTkButton(self.toolbar, text=("Start  "+str(self.s_hour)+":"+str(self.s_minute)), command=self.insert_timestamp, fg_color="#3e3e3e")#, text_color="green",hover_color="#42b0ff")
        self.start_time_button.pack(side="left", padx=10, pady=5)
        
        # Create a dropdown for sample tags
        self.tags = ["Interaction","Recording Ends", "Short Break", "Music", "Main Teaching", "Exercise", "Live Demonstration", "Breakout Rooms Instructions", "Story", "Screen Share", "Share", "Question"]
        self.tags_menu = ctk.CTkOptionMenu(self.toolbar, values=self.tags, command=lambda  t=self.tags: self.insert_tag(t))
        self.tags_menu.pack(side="left", padx=10, pady=5)
        self.tags_menu.set("Tags")
        
        # Create a dropdown for mentions
        self.mentions=["(Trainer: )","(Delegate: )","(Trainer: , Delegate: )","(Trainer: Dr Rangana)","(Trainer: Dr Rangana, Delegate: )","(Room Population: , Duration: )"]        
        self.mentions_menu = ctk.CTkOptionMenu(self.toolbar, values=self.mentions, command=lambda m=self.mentions: self.insert_mention(m))
        self.mentions_menu.pack(side="left", padx=10, pady=5)
        self.mentions_menu.set("Mentions")

        # Create the text area
        self.text_area = ctk.CTkTextbox(self, wrap=tk.WORD, font=("Helvetica", 14), undo=True)
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)

        # Default text insertion
        self.insert_default_text()
        
        #Binding ctrl-s shortcut to save
        self.bind('<Control-s>', lambda event: self.save_file())
        
        #Binding ctrl-w shortcut to word-checker
        self.bind('<Control-w>', lambda event: self.check_spelling())
        
        # Binding ctrl-q shortcut to format mode 1 and preventing further default actions
        self.bind('<Control-q>', lambda event: self.gformatter())

        # Bind the keypress event for brackets replacement
        self.text_area.bind("<KeyRelease>", self.replace_brackets_with_time)

        # Bind the window close (X) button to the on_closing function
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


        # Global file path variable to store the currently opened file
        self.file_path = None
        
        # Toggle highlight variable
        self.spell_checked = False  # Tracks whether spelling check is on or off
        
        # Create the context menu
        menu_font = tkFont.Font(family="Arial", size=9)
        self.context_menu = Menu(self, tearoff=0, bg="#424242", fg="#F5F5F5", activebackground="#229799", activeforeground="#F5F5F5", font=menu_font)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)

        # Bind right-click to show the context menu
        self.text_area.bind("<Button-3>", self.show_context_menu)
        
        # Create Pause-Resume button
        self.pause_button = ctk.CTkButton(self.toolbar, text="Pause", command=self.pause_resume,fg_color="#362222", hover_color="#CF0000")
        self.pause_button.pack(side="left", padx=10, pady=5)
        
        # Prompt menu
        self.prompts=["Refine english","Clean Transcript"]
        self.prompts_menu= ctk.CTkOptionMenu(self.toolbar, values=self.prompts, command=lambda m=self.mentions: self.copy_prompt(m))
        self.prompts_menu.pack(side="left", padx=10, pady=5)
        self.prompts_menu.set("AI Prompts")
        
        # Pause-Resume Time variables
        self.pause_time= None
        self.time_lost= None

    # Proofreading function to check incorrect formatting and
    def proofread(self):
        try:
            wc= WhatsAppChecker()
            text=self.text_area.get("1.0", "end-1c")
            formatobject=wc.ensure_asterisks_with_tracking(text)
            mistakes=formatobject.mistakes
            repetitions=wc.find_duplicate_timestamps(text)
            
            del wc # Deleting objects after they are used
            
            changes=formatobject.changes_count+ len(repetitions)
            
            if mistakes==[] and repetitions==[]:
                messagebox.showinfo("Proofreading Results", "Everything seems alright :)")
            elif mistakes!=[] and repetitions==[]:
                emessage=str(changes)+" mistake(s) detected!\n\n"+"These timestamps have incorrect formatting: "+str(mistakes)
                messagebox.showinfo("Proofreading Results",emessage)
            elif mistakes==[] and repetitions!=[]:
                emessage=str(changes)+" mistake(s) detected!\n\n"+"These timestamps are repeated: "+str(repetitions)
                messagebox.showinfo("Proofreading Results",emessage)
            else:
                emessage=str(changes)+" mistakes detected!\n\n"+"These timestamps have incorrect formatting: "+str(mistakes)+"\n\nThese timestamps are repeated: "+str(repetitions)
                messagebox.showinfo("Proofreading Results",emessage)
        except Exception as e:
            print_statement=str(e)+" has occurred. Unable to proofread the file :("
            messagebox.showerror("Exception Ocurred", print_statement)
        #newtext= formatobject.modified_string   
        # Delete all text in the text area
        #self.text_area.delete("1.0", "end")
        
        # Insert the new text into the text area
        #self.text_area.insert("1.0", newtext)

    
    def copy_word_format(self):
        try:
            text=self.text_area.get("1.0", "end-1c")
            formatter= WordFormat()
            rtf_bold_text = formatter.generate_rtf_bold(text,mode=0) # Converts text to RTF 
            formatter.copy_rtf_to_clipboard(rtf_bold_text) # Copies RTF text with boldened timestamps into clipboard
            
            del formatter # deleting the object after it is used
            
            asterisk_count = text.count('*')
            if asterisk_count%2 == 0 :
                messagebox.showinfo("Copy", "Word Format for Timestamps Copied to Clipboard!")
            else:
                messagebox.showinfo("Error in Copying", "Odd number of asterisks detected. Please check your formatting!")
            
        except Exception as e:
            print_statement=str(e)+" has occurred. Unable to copy the file :("
            messagebox.showerror("Exception Ocurred", print_statement)
            
    def gformatter(self):
        try:
            text=self.text_area.get("1.0", "end-1c")
            formatter= WordFormat()
            rtf_bold_text = formatter.generate_rtf_bold(text,mode=1) # Converts text to RTF 
            formatter.copy_rtf_to_clipboard(rtf_bold_text) # Copies RTF text with boldened timestamps into clipboard
            
            del formatter # deleting the object after it is used
            
            messagebox.showinfo("Copy", "Word Format Copied to Clipboard!")            
        except Exception as e:
            print_statement=str(e)+" has occurred. Unable to copy the file :("
            messagebox.showerror("Exception Ocurred", print_statement)
            
    
    def pause_resume(self):
        if self.pause_button.cget("text") == "Pause":
            # Change button text to "Resume"
            self.pause_button.configure(text="Resume",fg_color="green", hover_color="#1E5128")  
            self.pause_time=datetime.now()
            self.pause_time=self.pause_time.replace(second=0,microsecond=0)
            self.hourmin()
            if self.showhourmin:
                breaktext = time.strftime(f"*%I:%M %p* ({self.time_difference_str})").lower()+" Recording pauses.\n"
            else:
                breaktext = time.strftime(f"*%I:%M %p*").lower()+" Recording pauses.\n"
            self.text_area.insert(tk.END,breaktext)
            self.text_area.mark_set(tk.INSERT, tk.END)
            self.auto_save_file()

        else:
            # Change button text to "Pause"
            self.pause_button.configure(text="Pause",fg_color="#362222", hover_color="#CF0000")
            
            resume_time=datetime.now()
            resume_time=resume_time.replace(second=0,microsecond=0)
            time_lost=resume_time-self.pause_time 
            if(self.time_lost==None):
                self.time_lost=time_lost
            else:
                self.time_lost=time_lost+self.time_lost
                
            self.hourmin()
            if self.showhourmin:
                breaktext = time.strftime(f"*%I:%M %p* ({self.time_difference_str})").lower()+" Recording resumes.\n"
            else:
                breaktext = time.strftime(f"*%I:%M %p*").lower()+" Recording resumes.\n"                
            self.text_area.insert(tk.END,breaktext)
            self.text_area.mark_set(tk.INSERT, tk.END)
            self.pause_time=None
            
            self.auto_save_file()


    def copy_text(self):
        # Copy selected text to the clipboard
        self.text_area.event_generate("<Control-c>")

    def cut_text(self):
        # Cut selected text to the clipboard
        self.text_area.event_generate("<Control-x>")


    def paste_text(self):
        # Paste text from the clipboard
        self.text_area.event_generate("<Control-v>")

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
        
    # Function to toggle spelling check and highlight American English words
    def check_spelling(self):
        try:
            if self.spell_checked:
                # Remove all highlights if already checked
                self.text_area.tag_remove("highlight", "1.0", "end")
                self.spell_checked = False  # Update the state
                current_options = list(self.file_menu.cget("values"))
                current_options[current_options.index("Word Checker (Active)")] = "Word Checker"
                self.file_menu.configure(values=current_options)

            else:
                current_options = list(self.file_menu.cget("values"))
                current_options[current_options.index("Word Checker")] = "Word Checker (Active)"
                self.file_menu.configure(values=current_options)
                # Highlight the American words if not checked
                for american_word in american_words:
                    start_pos = "1.0"
                    while True:
                        start_pos = self.text_area.search(american_word, start_pos, stopindex="end", nocase=True)
                        if not start_pos:
                            break
                        end_pos = f"{start_pos}+{len(american_word)}c"
                        self.text_area.tag_add("highlight", start_pos, end_pos)
                        start_pos = end_pos

                self.text_area.tag_config("highlight", background="yellow", foreground="black")
                self.spell_checked = True  # Update the state
        except Exception as e:
            print_statement=str(e)+" has occurred. Unable to SpellCheck the file :("
            messagebox.showerror("Exception Ocurred", print_statement)    
            
            
    def set_hourmin(self):
        if self.showhourmin:
            current_options = list(self.file_menu.cget("values"))
            current_options[current_options.index("Display Time Elapsed (Active)")] = "Display Time Elapsed (Inactive)"
            self.file_menu.configure(values=current_options)
            self.showhourmin=False
        else:
            current_options = list(self.file_menu.cget("values"))
            current_options[current_options.index("Display Time Elapsed (Inactive)")] = "Display Time Elapsed (Active)"
            self.file_menu.configure(values=current_options)
            self.showhourmin=True

    
    def copy_prompt(self, name):
        self.prompts_menu.set("AI Prompts")
        prompt1="Refine the grammar and punctuations but do not change the wordings, terminology and format:"
        prompt2="Combine all the back to back dialogs said by the same person into a single dialog, correcting the grammatical errors and mistakes made by transcript AI. the output should be in the form of a conversation:"
        if name=="Refine english":
            prompt=prompt1
        else:
            prompt=prompt2
        pyperclip.copy(prompt)
        
    
    def insert_mention(self, word):
        self.mentions_menu.set("Mentions")
        self.text_area.insert(tk.INSERT, word)
        
    def insert_tag(self, word):
        self.tags_menu.set("Tags")
        word=word+": "
        self.text_area.insert(tk.INSERT, word)
        
    # Handling File Menu Functions
    def handlefunctions(self,functions):
        self.file_menu.set("File")
        if functions == "Open":
            self.open_file()
        elif functions == "Save":
            self.save_file()
        elif functions == "Word Checker" or functions == "Word Checker (Active)":
            self.check_spelling()
        elif functions== "Time Lost":
            self.set_timelost()
        elif functions=="Display Time Elapsed (Active)" or functions== "Display Time Elapsed (Inactive)":
            self.set_hourmin()
        elif functions== "Export to Word":
            self.copy_word_format()
        elif functions== "Proofread":
            self.proofread()
        elif functions== "Generate Report":
            self.report()
        elif functions== "Import from Word":
            self.extract_docx_text()
        else:
            print("Error")
    
    def extract_docx_text(self):
        try:
            file_path = filedialog.askopenfilename(defaultextension=".docx", 
                                            filetypes=[("Word Document", "*.docx"), 
                                                        ("All files", "*.*")])
            we=WordExtractor(file_path)
            path=we.getPath()
            del we                  # Deleting the object after it is used.
            self.open_file(path)
        except Exception as e:
            messagebox.showerror("Exception Occurred",str(e))
        
    def report(self):
        try:
            ed= rg(self.text_area.get("1.0", "end-1c"))
            output=ed.extract_and_copy()
            ed.fullReport()
            
            del ed # deleting the object after it is used
            messagebox.showinfo("Event Report","Event Report copied to clipboard :)")
        except Exception as e:
            messagebox.showerror("Exception Occurred",str(e))
           
    def insert_timestamp(self, value=None):
        timestamp = simpledialog.askstring("Input", "Enter time in HH:MM format (24-hour):")
        if timestamp:
            try:
                valid_time = datetime.strptime(timestamp, "%H:%M")
                self.s_hour = valid_time.hour
                self.s_minute = valid_time.minute
                #self.sttime = f"{(self.s_hour % 12) or 12}:{self.s_minute:02d} {'pm' if self.s_hour >= 12 else 'am'}"
                formatted_time = f"{self.s_hour:02}:{self.s_minute:02}"
                self.start_time_button.configure(text=("Start  "+formatted_time))
            except ValueError:
                messagebox.showerror("Invalid format", "Please enter a valid time in HH:MM format.")
                
    def set_timelost(self, value=None):
        dialog="Current time lost is : "+str(self.time_lost) +"\nEnter time lost in MINUTES : "
        lost=None
        if self.pause_time==None:
            lost = simpledialog.askstring("Input", dialog)
        else:
            messagebox.showerror("Warning","Manipulating time lost value when paused might cause errors.")
        if lost:
            try:
            # Convert the string `lost` to an integer (number of minutes)
                minutes_lost = int(lost)
                
                # Create a timedelta object representing the lost minutes
                lostmin = timedelta(minutes=minutes_lost)
                
                # Optionally, print or return the timedelta object
                self.time_lost=lostmin
            
            except ValueError:
                messagebox.showerror("Invalid input","Please enter a valid number of minutes.")

    def hourmin(self):
        current_time = datetime.now()
        current_time=current_time.replace(second=0, microsecond=0)
        given_time = current_time.replace(hour=self.s_hour, minute=self.s_minute, second=0, microsecond=0)
        if(self.time_lost!=None):
            time_difference = current_time - given_time - self.time_lost
        else:
            time_difference = current_time - given_time
        total_seconds = int(time_difference.total_seconds())
        hours_diff = abs(total_seconds // 3600)
        minutes_diff = abs((total_seconds % 3600) // 60)
        if hours_diff == 0:
            self.time_difference_str = f"{minutes_diff:02}min"
        else:
            self.time_difference_str = f"{hours_diff:02}hr{minutes_diff:02}min"

    def get_day_suffix(self, day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    def insert_default_text(self):
        current_time = time.localtime()
        day = current_time.tm_mday
        month = time.strftime("%B", current_time)
        year = current_time.tm_year
        day_with_suffix = str(day) + self.get_day_suffix(day)
        formatted_date = f"{day_with_suffix} {month} {year}"
        default_text = (
            f"*Timestamps, Event_Name, {formatted_date}*\n\n"
            "*02:30 pm* (00min) Recording Starts: Session begins. Dance energiser. "
            "Music: Song_Name by Artists_Name. Dr Rangana warmly welcomes all the delegates."
        )
        self.text_area.insert(tk.END, default_text)

    def on_closing(self):
        response = messagebox.askyesnocancel("Exit", "Are you sure that you want to exit?")
        if response:
            if self.file_path is None:
                pass
            else:
                self.auto_save_file()
            self.quit()

    def open_file(self,path=None):
        try:
            backup_file_path=self.file_path
            backup_text=self.text_area.get(1.0, tk.END)
            
            if self.file_path is None:
                pass
            else:
                self.auto_save_file()
            if path==None:
                self.file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            else:
                self.file_path = path
            if self.file_path:
                with open(self.file_path, "r") as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, file.read())
                self.title(f"Scriber - {self.file_path}")
            else:
                self.file_path=None
        except Exception as e:
                self.file_path=backup_file_path
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END,backup_text)
                print_statement=str(e)+"\nUnable to open the file."
                messagebox.showerror("Exception Ocurred", print_statement)

    def auto_save_file(self):
        if self.file_path is None:
            self.save_as_file()
        else:
            try:
                with open(self.file_path, "w") as file:
                    file.write(self.text_area.get(1.0, tk.END))
            except:
                pass

    def save_file(self):
        if self.file_path is None:
            self.save_as_file()
        else:
            try:
                with open(self.file_path, "w") as file:
                    file.write(self.text_area.get(1.0, tk.END))
                messagebox.showinfo("Save", "File Saved Successfully!")
            except Exception as e:
                print_statement=str(e)+" has occurred. Unable to save the file."
                messagebox.showerror("Exception Ocurred", print_statement)

    def save_as_file(self):
        try:
            self.file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if self.file_path:
                with open(self.file_path, "w") as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.title(f"Scriber - {self.file_path}")
                messagebox.showinfo("Save As", "File Saved Successfully!")
            else:
            # Backup process
                backup_directory = "C:/backup_directory"  # Specify your backup directory path here
                time_with_milliseconds = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
                backup_filename = time_with_milliseconds+".txt"
                backup_file_path = os.path.join(backup_directory, backup_filename)
                self.file_path = backup_file_path
                # Ensure the backup directory exists
                os.makedirs(backup_directory, exist_ok=True)
                
                # Save the backup file
                with open(backup_file_path, "w") as backup_file:
                    backup_file.write(self.text_area.get(1.0, tk.END))
                
                messagebox.showinfo("Backup", f"File has been created and will be saved at backup location: {backup_file_path}")
        except Exception as e:
                self.file_path=None
                print_statement=str(e)+" has occurred. Unable to save the file."
                messagebox.showerror("Exception Ocurred", print_statement)


    def replace_brackets_with_time(self, event=None):
        current_view = self.text_area.yview()
        start_idx = self.text_area.search("()", "1.0", tk.END)
        if start_idx:
            self.auto_save_file()
            end_idx = f"{start_idx}+2c"
            if self.showhourmin :
                if(self.pause_time==None or self.time_difference_str==None):
                    self.hourmin()
                current_time = time.strftime(f"*%I:%M %p* ({self.time_difference_str}) ").lower()
            else:
                current_time = time.strftime(f"*%I:%M %p*").lower()
            current_time=current_time.strip()+" "
            self.text_area.delete(start_idx, end_idx)
            self.text_area.insert(start_idx, current_time)
            new_cursor_position = f"{start_idx}+{len(current_time)}c"
            self.text_area.mark_set(tk.INSERT, new_cursor_position)
        self.text_area.yview_moveto(current_view[0])


# Run the application
if __name__ == "__main__":
    app = ChScriber()
    app.mainloop()
    
# type: ignore #Rough Estimate for Optimal Performance:
#Small Files (1KB to 100KB, about 1,000–10,000 words): The app should perform optimally without noticeable lag or issues. This range covers most short texts, notes, or articles, and you'll likely not encounter performance issues.

#Medium Files (100KB to 1MB, about 10,000–100,000 words): Performance will still be decent, but you may start to notice slight lag, particularly when opening, saving, or performing large operations (like text replacement or scroll updates). It's still usable for standard-sized documents or code files.

#Large Files (1MB to 5MB, about 100,000–500,000 words): Performance degradation becomes more noticeable as you approach the higher end of this range. Typing may become slower, the interface may feel less responsive, and operations like replacing text or saving might take a bit longer. Tkinter's Text widget isn't designed for such large files, so responsiveness will likely drop.

#Very Large Files (5MB+ or 500,000+ words): Handling very large files (such as novels, large codebases, or data dumps) may cause significant lag, freezing, or crashes due to the Tkinter Text widget's limitations and Python's single-threaded nature. You may face memory issues, and the app might become unusable for typing, scrolling, or large text manipulation tasks.

#Written by Joel Joseph Justin 2024