import wave
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import numpy as np


class ExtractWaveGUI:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap(
            "logo.ico"
        )  # Replace 'logo.ico' with the path to your icon file
        self.root.title("Steganographyx - Decode Wave Secret Message")
        self.af = ""
        self.lsb_count = tk.IntVar(value=1)

        self.create_widgets()

    def create_widgets(self):
        self.audio_label = tk.Label(self.root, text="Select Audio File:")
        self.audio_label.pack()

        self.audio_entry = tk.Entry(self.root, width=50)
        self.audio_entry.pack()

        self.audio_button = tk.Button(
            self.root, text="Browse", command=self.browse_audio
        )
        self.audio_button.pack()

        # Enable drag-and-drop for the audio entry
        self.audio_entry.drop_target_register(DND_FILES)
        self.audio_entry.dnd_bind("<<Drop>>", self.on_drop_audio)

        self.lsb_label = tk.Label(self.root, text="Select number of LSBs:")
        self.lsb_label.pack()

        self.lsb_dropdown = ttk.Combobox(
            self.root, textvariable=self.lsb_count, values=list(range(1, 9))
        )
        self.lsb_dropdown.pack()

        self.extract_button = tk.Button(
            self.root, text="Extract Message", command=self.extract_message
        )
        self.extract_button.pack()

        self.message_label = tk.Label(self.root, text="Extracted Message:")
        self.message_label.pack()

        self.message_text = tk.Text(self.root, height=20, width=40)
        self.message_text.pack()

    def browse_audio(self):
        self.af = filedialog.askopenfilename(filetypes=[("Wave Audio Files", "*.wav")])
        self.audio_entry.delete(0, tk.END)
        self.audio_entry.insert(0, self.af)

    def on_drop_audio(self, event):
        self.af = event.data
        self.audio_entry.delete(0, tk.END)
        self.audio_entry.insert(0, self.af)

    def decode_text_from_audio(self, audio_file_path, lsb_count):
        with wave.open(audio_file_path, "rb") as audio_file:
            frames = audio_file.readframes(-1)
            frames = np.frombuffer(frames, dtype=np.int16)

            binary_text = ""
            for frame in frames:
            # Extract the specified number of LSBs from each frame
                for i in range(lsb_count):
                    binary_text += str((frame >> i) & 1)

        # Handle incomplete byte at the end if not divisible by 8
            if len(binary_text) % 8 != 0:
                binary_text = binary_text[:-(len(binary_text) % 8)]

            decoded_text = ""
            i = 0
            while i < len(binary_text):
                byte = binary_text[i:i+8]
                if byte == "00000000":  # Stop if null terminator is found
                    break
                decoded_text += chr(int(byte, 2))
                i += 8

            return decoded_text


        
    def extract_message(self):
        self.af = self.audio_entry.get()
        lsb_count = self.lsb_count.get()
        if self.af:
            try:
                message = self.decode_text_from_audio(self.af, lsb_count)
                self.message_text.delete(1.0, tk.END)
                self.message_text.insert(tk.END, message)
            except Exception as e:
                self.message_text.delete(1.0, tk.END)
                self.message_text.insert(tk.END, "Error: " + str(e))
        else:
            self.message_text.delete(1.0, tk.END)
            self.message_text.insert(tk.END, "Please select an audio file.")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ExtractWaveGUI(root)
    root.mainloop()
