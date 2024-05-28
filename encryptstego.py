# Import necessary libraries
from tkinter import *
from ctypes import windll
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import subprocess
import HiddenWave
import ExWave
import os

# Define global variables to track child window states
encode_opened = False
decode_opened = False
help_opened = False
windows = True  # Set to 'False' for non-Windows environments
file_path = " "  # Store the path of the selected image

def encode_audio():
    try:
        subprocess.run(["python", "HiddenWave.py"])
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def decode_audio():
    try:
        subprocess.run(["python", "ExWave.py"])
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to handle closing of help window
def close_help_window(help_window):
    global help_opened
    help_window.destroy()
    help_opened = False

# Function to handle closing of decoding window
def close_decode_window(decode_window):
    global decode_opened
    decode_window.destroy()
    decode_opened = False

# Create the main window
window = Tk()
window.title("Steganographyx")
window.geometry('500x500')
window.resizable(False, False)
if windows:
    windll.shcore.SetProcessDpiAwareness(1)

# Load the logo image
logo = Image.open("icon.png")
logo = logo.resize((250, 250), Image.LANCZOS)
logo = ImageTk.PhotoImage(logo)
window.iconphoto(True, logo)

# Display the logo on the window
image_label = Label(window, image=logo, height=250, width=250)
image_label.pack(pady=20)

# Display the title label on the window
title_label = Label(window, text="Steganographyx")
title_label.config(font=("Open Sans", 32))
title_label.pack()

encode_audio_btn = Button(window, text="Encode Audio", height=2, width=15, bg="#0066CC", fg="white", cursor="hand2", borderwidth=0, command=encode_audio)
encode_audio_btn.config(font=("Open Sans", 15, "bold"))
encode_audio_btn.pack(side=LEFT, padx=10)

decode_audio_btn = Button(window, text="Decode Audio", height=2, width=15, bg="#FF6600", fg="white", cursor="hand2", borderwidth=0, command=decode_audio)
decode_audio_btn.config(font=("Open Sans", 15, "bold"))
decode_audio_btn.pack(side=RIGHT, padx=10)

# Start the main loop
window.mainloop()
