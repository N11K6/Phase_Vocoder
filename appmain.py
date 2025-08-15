#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhaseVox Tkinter App:
    A simple GUI application to use the Phase Vocoder for time stretching or
    pitch shifting an audio file, with playback and saving options.

@author: nk
"""
# Dependencies:
import tkinter as tk
from tkinter import filedialog, messagebox
import soundfile as sf
import pygame  # For playback
import threading # To run processing without freezing the GUI
import os
import tempfile
from phasevox import PhaseVox
#%%
# --- Tkinter Application ---
class PhaseVoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phase Vocoder")
        self.root.geometry("500x400")

        self.audio_file_path = None
        self.original_audio = None
        self.original_sr = None
        self.processed_audio = None
        self.processed_sr = None
        self.Q = tk.DoubleVar(value=1.0)
        self.mode = tk.StringVar(value='time')

        # Initialize pygame mixer for playback
        pygame.mixer.init()

        self.create_widgets()

    def create_widgets(self):
        # --- File Selection ---
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)

        tk.Label(file_frame, text="Audio File:").pack(side=tk.LEFT)
        self.file_label = tk.Label(file_frame, text="No file selected", width=40, anchor='w')
        self.file_label.pack(side=tk.LEFT, padx=(5, 0))
        tk.Button(file_frame, text="Browse", command=self.load_file).pack(side=tk.LEFT, padx=(5, 0))

        # --- Playback Original ---
        play_orig_frame = tk.Frame(self.root)
        play_orig_frame.pack(pady=5)
        tk.Button(play_orig_frame, text="Play Original", command=self.play_original, state='disabled', width=15).pack()
        self.play_orig_button = play_orig_frame.winfo_children()[0] # Store button reference

        # --- Mode Selection ---
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=10)

        tk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Time Stretch", variable=self.mode, value='time').pack(side=tk.LEFT, padx=(10, 0))
        tk.Radiobutton(mode_frame, text="Pitch Shift", variable=self.mode, value='pitch').pack(side=tk.LEFT, padx=(10, 0))

        # --- Q Factor Slider ---
        q_frame = tk.Frame(self.root)
        q_frame.pack(pady=10)

        tk.Label(q_frame, text="Factor (Q):").pack(side=tk.LEFT)
        self.q_label = tk.Label(q_frame, text=f"{self.Q.get():.2f}", width=5)
        self.q_label.pack(side=tk.LEFT, padx=(5, 0))
        self.q_slider = tk.Scale(q_frame, from_=0.1, to=3.0, resolution=0.01, orient=tk.HORIZONTAL, variable=self.Q, command=self.update_q_label)
        self.q_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # --- Process Button ---
        self.process_button = tk.Button(self.root, text="Process Audio", command=self.start_processing, state='disabled', bg='lightblue')
        self.process_button.pack(pady=10)

        # --- Playback Processed ---
        play_proc_frame = tk.Frame(self.root)
        play_proc_frame.pack(pady=5)
        tk.Button(play_proc_frame, text="Play Processed", command=self.play_processed, state='disabled', width=15).pack()
        self.play_proc_button = play_proc_frame.winfo_children()[0] # Store button reference

        # --- Save Button ---
        self.save_button = tk.Button(self.root, text="Save Processed File", command=self.save_file, state='disabled', bg='lightgreen')
        self.save_button.pack(pady=10)

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_q_label(self, value):
        self.q_label.config(text=f"{float(value):.2f}")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an audio file",
            filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.ogg *.aiff")]
        )
        if file_path:
            self.audio_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=filename)
            self.status_var.set(f"Loaded: {filename}")
            self.play_orig_button.config(state='normal')
            self.process_button.config(state='normal')
            # Clear previous processed audio
            self.processed_audio = None
            self.processed_sr = None
            self.play_proc_button.config(state='disabled')
            self.save_button.config(state='disabled')

    def play_original(self):
        if self.audio_file_path:
            # Stop any currently playing sound
            pygame.mixer.music.stop()
            # Load and play the original file directly
            try:
                pygame.mixer.music.load(self.audio_file_path)
                pygame.mixer.music.play()
                self.status_var.set("Playing original audio...")
                # Optional: Disable button while playing (requires threading for proper check)
            except Exception as e:
                messagebox.showerror("Playback Error", f"Could not play original file:\n{e}")
                self.status_var.set("Playback error (original)")

    def start_processing(self):
        if not self.audio_file_path:
            messagebox.showwarning("No File", "Please select an audio file first.")
            return

        # Disable buttons during processing
        self.process_button.config(state='disabled', text="Processing...", bg='lightcoral')
        self.play_orig_button.config(state='disabled')
        self.play_proc_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.status_var.set("Processing audio... Please wait.")
        self.root.update() # Force UI update

        # Run processing in a separate thread to prevent freezing
        processing_thread = threading.Thread(target=self.process_audio)
        processing_thread.start()

    def process_audio(self):
        try:
            Q_val = self.Q.get()
            mode_val = self.mode.get()
            # Call the PhaseVox function
            self.processed_audio, self.processed_sr = PhaseVox(self.audio_file_path, Q_val, mode_val)
            self.root.after(0, self.on_processing_complete, True)
        except Exception as e:
            # Schedule error message on main thread
            self.root.after(0, self.on_processing_complete, False, str(e))

    def on_processing_complete(self, success, error_msg=None):
        self.process_button.config(state='normal', text="Process Audio", bg='lightblue')
        self.play_orig_button.config(state='normal')
        
        if success:
            self.status_var.set("Processing complete!")
            self.play_proc_button.config(state='normal')
            self.save_button.config(state='normal')
        else:
            self.status_var.set("Processing failed!")
            messagebox.showerror("Processing Error", f"An error occurred:\n{error_msg}")

    def play_processed(self):
        if self.processed_audio is not None and self.processed_sr is not None:
            pygame.mixer.music.stop() # Stop any current playback
            
            # Save processed audio to a temporary file for pygame playback
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
                    temp_filename = tmpfile.name
                # soundfile requires_subtype for float32, librosa load handles it
                sf.write(temp_filename, self.processed_audio, self.processed_sr, subtype='FLOAT') 
                
                pygame.mixer.music.load(temp_filename)
                pygame.mixer.music.play()
                self.status_var.set("Playing processed audio...")
                # Optional: Clean up temp file after playback (tricky with pygame). 
                # A better way might be to manage a single temp file path and overwrite/clean on exit.
                # For simplicity here, we'll rely on OS temp cleanup eventually.
                # Or, clean it up after a delay (requires more threading/event handling).
                
            except Exception as e:
                messagebox.showerror("Playback Error", f"Could not play processed file:\n{e}")
                self.status_var.set("Playback error (processed)")
        else:
            messagebox.showwarning("No Processed Audio", "Please process the audio first.")

    def save_file(self):
         if self.processed_audio is not None and self.processed_sr is not None:
            default_name = f"PhaseVox_out_{self.mode.get()}_{self.Q.get():.2f}.wav"
            file_path = filedialog.asksaveasfilename(
                title="Save processed audio",
                defaultextension=".wav",
                initialfile=default_name,
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    sf.write(file_path, self.processed_audio, self.processed_sr)
                    self.status_var.set(f"Saved: {os.path.basename(file_path)}")
                    messagebox.showinfo("Saved", f"File saved successfully:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Could not save file:\n{e}")
                    self.status_var.set("Save failed")
         else:
            messagebox.showwarning("No Processed Audio", "Please process the audio first.")
#%%
if __name__ == "__main__":
    root = tk.Tk()
    app = PhaseVoxApp(root)
    root.mainloop()
