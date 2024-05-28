import wave
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import numpy as np

class ExtractWaveGUI:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap('logo.ico')  # Replace 'logo.ico' with the path to your icon file
        self.root.title("Steganographyx - Decode Wave Secret Message")
        self.af = ""

        self.create_widgets()

    def create_widgets(self):
        self.audio_label = tk.Label(self.root, text="Select Audio File:")
        self.audio_label.pack()

        self.audio_entry = tk.Entry(self.root, width=50)
        self.audio_entry.pack()

        self.audio_button = tk.Button(self.root, text="Browse", command=self.browse_audio)
        self.audio_button.pack()

        # Enable drag-and-drop for the audio entry
        self.audio_entry.drop_target_register(DND_FILES)
        self.audio_entry.dnd_bind('<<Drop>>', self.on_drop_audio)

        self.extract_button = tk.Button(self.root, text="Extract Message", command=self.extract_message)
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

    def decode_text_from_audio(self, audio_file_path):
        with wave.open(audio_file_path, "rb") as audio_file:
            frames = audio_file.readframes(-1)
            frames = np.frombuffer(frames, dtype=np.int16)
            binary_text = ""
            for frame in frames:
                binary_text += str(frame & 1)
            null_index = binary_text.find("00000000")
            if null_index != -1:
                binary_text = binary_text[:null_index]
            if len(binary_text) % 8 != 0:
                binary_text = binary_text[:-(len(binary_text) % 8)]
            decoded_text = ""
            for i in range(0, len(binary_text), 8):
                byte = binary_text[i:i + 8]
                decoded_text += chr(int(byte, 2))
        return decoded_text

    def extract_message(self):
        self.af = self.audio_entry.get()
        if self.af:
            try:
                message = self.decode_text_from_audio(self.af)
                self.message_text.delete(1.0, tk.END)
                self.message_text.insert(tk.END, message)
            except Exception as e:
                self.message_text.delete(1.0, tk.END)
                self.message_text.insert(tk.END, "Error: " + str(e))
        else:
            self.message_text.delete(1.0, tk.END)
            self.message_text.insert(tk.END, "Please select an audio file.")

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = ExtractWaveGUI(root)
    root.mainloop()
