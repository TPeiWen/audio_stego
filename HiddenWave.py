import os
import wave
import threading
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import make_chunks

class HiddenWaveGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganographyx - Encode Message in Wave Audio")

        self.root.iconbitmap('logo.ico')  # Replace 'logo.ico' with the path to your icon file

        self.af = ""
        self.string = ""
        self.output = ""

        self.audio_thread = None
        self.playing = False
        self.pause_flag = threading.Event()

        self.lsb_count = tk.IntVar(value=1)  # Default to using 1 LSB

        self.create_widgets()

    def create_widgets(self):
        self.logo_label = tk.Label(self.root)
        self.logo_label.pack()
        self.display_logo()

        self.audio_label = tk.Label(self.root, text="Select Audio File:")
        self.audio_label.pack()

        self.audio_entry = tk.Entry(self.root)
        self.audio_entry.pack()

        self.audio_button = tk.Button(self.root, text="Browse", command=self.browse_audio)
        self.audio_button.pack()

        self.audio_entry.drop_target_register(DND_FILES)
        self.audio_entry.dnd_bind('<<Drop>>', self.on_drop_audio)

        self.output_label = tk.Label(self.root, text="Your Output file path and name:")
        self.output_label.pack()

        self.output_entry = tk.Entry(self.root)
        self.output_entry.pack()

        self.output_button = tk.Button(self.root, text="Browse Output", command=self.browse_output)
        self.output_button.pack()

        self.output_entry.drop_target_register(DND_FILES)
        self.output_entry.dnd_bind('<<Drop>>', self.on_drop_output)

        self.message_label = tk.Label(self.root, text="Enter your Secret Message:")
        self.message_label.pack()

        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack()

        self.lsb_label = tk.Label(self.root, text="Select number of LSBs:")
        self.lsb_label.pack()

        self.lsb_dropdown = ttk.Combobox(self.root, textvariable=self.lsb_count, values=list(range(1, 9)))
        self.lsb_dropdown.pack()

        self.hide_button = tk.Button(self.root, text="Hide Message", command=self.hide_message)
        self.hide_button.pack()

        self.play_original_button = tk.Button(self.root, text="Play Original Audio", command=lambda: self.play_audio(self.af))
        self.play_original_button.pack()

        self.pause_original_button = tk.Button(self.root, text="Pause Original Audio", command=self.pause_audio)
        self.pause_original_button.pack()

        self.play_decoded_button = tk.Button(self.root, text="Play Decoded Audio", command=lambda: self.play_audio(self.output), state=tk.DISABLED)
        self.play_decoded_button.pack()

        self.pause_decoded_button = tk.Button(self.root, text="Pause Decoded Audio", command=self.pause_audio, state=tk.DISABLED)
        self.pause_decoded_button.pack()

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

    def browse_audio(self):
        self.af = filedialog.askopenfilename(filetypes=[("Wave Audio Files", "*.wav")])
        if self.af and self.check_file_size(self.af):
            self.audio_entry.delete(0, tk.END)
            self.audio_entry.insert(0, self.af)
        else:
            messagebox.showerror("File Size Error", "The selected file exceeds the maximum size of 1 GB.")

    def browse_output(self):
        self.output = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Wave Audio Files", "*.wav")])
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, self.output)

    def on_drop_audio(self, event):
        self.af = event.data
        if self.af and self.check_file_size(self.af):
            self.audio_entry.delete(0, tk.END)
            self.audio_entry.insert(0, self.af)
        else:
            messagebox.showerror("File Size Error", "The selected file exceeds the maximum size of 1 GB.")

    def on_drop_output(self, event):
        self.output = event.data
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, self.output)

    def hide_message(self):
        self.af = self.audio_entry.get()
        self.string = self.message_entry.get()
        self.output = self.output_entry.get()

        if not self.af or not self.string or not self.output:
            self.status_label.config(text="Please fill in all fields.")
            return

        try:
            self.encode_text_in_audio(self.string, self.af, self.output, self.lsb_count.get())
            self.status_label.config(text="Message hidden successfully.")
            self.play_decoded_button.config(state=tk.NORMAL)
            self.pause_decoded_button.config(state=tk.NORMAL)
        except Exception as e:
            self.status_label.config(text="Error: " + str(e))
            self.play_decoded_button.config(state=tk.DISABLED)
            self.pause_decoded_button.config(state=tk.DISABLED)

    def encode_text_in_audio(self, text, audio_file_path, output_file_path, lsb_count):
        with wave.open(audio_file_path, "rb") as audio_file:
            frames = audio_file.readframes(-1)
            frames = np.frombuffer(frames, dtype=np.int16)
            binary_text = "".join(format(ord(char), "08b") for char in text)
            binary_text += "00000000"  # Null character to indicate end of the message
            text_index = 0
            encoded_frames = frames.copy()

            for i in range(len(encoded_frames)):
                for bit in range(lsb_count):
                    if text_index < len(binary_text):
                        encoded_frames[i] = (encoded_frames[i] & ~(1 << bit)) | (int(binary_text[text_index]) << bit)
                        text_index += 1
                    else:
                        break

        with wave.open(output_file_path, "wb") as encoded_audio_file:
            encoded_audio_file.setparams(audio_file.getparams())
            encoded_audio_file.writeframes(encoded_frames.tobytes())

    def play_audio(self, file_path):
        if file_path:
            try:
                audio = AudioSegment.from_wav(file_path)
                self.audio_thread = threading.Thread(target=self.play_audio_thread, args=(audio,))
                self.playing = True
                self.pause_flag.clear()
                self.audio_thread.start()
            except Exception as e:
                self.status_label.config(text="Error playing audio: " + str(e))

    def play_audio_thread(self, audio):
        chunk_size = 1000  # 1 second chunks
        for chunk in make_chunks(audio, chunk_size):
            if not self.playing:
                break
            if self.pause_flag.is_set():
                self.pause_flag.wait()
            play(chunk)

    def pause_audio(self):
        if self.playing:
            self.pause_flag.set()
            self.playing = False
        else:
            self.pause_flag.clear()
            self.playing = True
            self.audio_thread = threading.Thread(target=self.resume_audio)
            self.audio_thread.start()

    def resume_audio(self):
        if self.playing:
            self.pause_flag.clear()

    def display_logo(self):
        # Load and display the logo image
        logo_image = Image.open("logo.png")
        logo_image = logo_image.resize((200, 156), Image.LANCZOS)
        logo_image = ImageTk.PhotoImage(logo_image)
        self.logo_label.config(image=logo_image)
        self.logo_label.image = logo_image

    def check_file_size(self, file_path):
        max_size = 1 * 1024 * 1024 * 1024  # 1 GB in bytes
        return os.path.getsize(file_path) <= max_size

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = HiddenWaveGUI(root)
    root.mainloop()
