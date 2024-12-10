import tkinter as tk
from tkinter import simpledialog
from tkinter import font


class CustomDialog(simpledialog.Dialog):
    """
    A customizable dialog box for tkinter with options for font, colors, dimensions, and text.

    Parameters:
        parent (tk.Widget): The parent widget.
        title (str): The title of the dialog box.
        font_size (int): Font size for the text in the dialog.
        font_family (str): Font family for the text in the dialog.
        text_color (str): Color of the text.
        background_color (str): Background color of the dialog.
        button_color (str): Background color of the buttons.
        button_hover_color (str): Background color of the buttons when hovered.
        box_width (int): Width of the dialog box.
        box_height (int): Height of the dialog box.
        txt (str): Label text to display in the dialog box.

    Attributes:
        result (str): The user input from the dialog box.
    """

    def __init__(
        self,
        parent,
        title=None,
        font_size=14,
        font_family="Helvetica",
        text_color="black",
        background_color="white",
        button_color="lightblue",
        button_hover_color="blue",
        box_width=400,
        box_height=200,
        txt="",
    ):
        # Save customization settings
        self.font_size = font_size
        self.font_family = font_family
        self.text_color = text_color
        self.background_color = background_color
        self.button_color = button_color
        self.button_hover_color = button_hover_color
        self.box_width = box_width
        self.box_height = box_height
        self.txt = txt

        # Set the custom font
        self.custom_font = font.Font(family=self.font_family, size=self.font_size)

        super().__init__(parent, title)

    def body(self, master):
        """
        Create the body of the dialog box with custom label and entry.

        Args:
            master (tk.Widget): The parent widget.

        Returns:
            tk.Entry: The entry widget for user input.
        """
        # Set the background color for the master
        master.configure(bg=self.background_color)

        # Set dialog size and overall background color
        self.geometry(f"{self.box_width}x{self.box_height}")
        self.configure(bg=self.background_color)

        # Add a label with custom font and color
        self.label = tk.Label(
            master,
            text=self.txt,
            font=self.custom_font,
            fg=self.text_color,
            bg=self.background_color,
        )
        self.label.grid(row=0, column=0, padx=10, pady=10)

        # Add an entry widget with custom font
        self.entry = tk.Entry(master, font=self.custom_font, bg="white")
        self.entry.grid(row=0, column=1, padx=10, pady=10)

        # Bind Enter key to the OK button
        self.bind("<Return>", lambda event: self.ok())
        
        return self.entry

    def ok(self, event=None):
        """
        Trigger the OK button action.
        """
        self.unbind("<Return>")  # Unbind Enter key when dialog closes
        super().ok()

    
    def buttonbox(self):
        """
        Create and style the OK and Cancel buttons.
        """
        # Override the buttonbox to customize buttons
        box = tk.Frame(self, bg=self.background_color)
        box.pack()

        self.ok_button = tk.Button(
            box,
            text="OK",
            width=10,
            font=self.custom_font,
            bg=self.button_color,
            activebackground=self.button_hover_color,
            command=self.ok,
        )
        self.ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.cancel_button = tk.Button(
            box,
            text="Cancel",
            width=10,
            font=self.custom_font,
            bg=self.button_color,
            activebackground=self.button_hover_color,
            command=self.cancel,
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

    def apply(self):
        """
        Process the user input when OK is clicked.
        """
        self.result = self.entry.get()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Create a custom dialog with specific parameters
    dialog = CustomDialog(
        root,
        title="Time lost",
        font_size=12,
        font_family="Calibri",
        text_color="darkblue",
        background_color="lightblue",
        button_color="grey",
        button_hover_color="darkgrey",
        box_width=300,
        box_height=100,
        txt="Enter the time lost:",
    )
    print(f"User input: {dialog.result}")
