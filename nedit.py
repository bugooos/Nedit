#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, messagebox, font

class Nedit:
    def __init__(self, filename):
        self.filename = filename
        self.root = tk.Tk()
        self.root.title(f"Nedit - {filename}")
        
        # Configure main window background
        self.root.configure(bg='#1E1E1E')

        # Set a modern monospace font
        self.custom_font = font.Font(family="Consolas", size=12)

        # Create the text area
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=self.custom_font)
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Text area styling
        self.text_area.config(bg='#2D2D2D', fg='#FFFFFF', insertbackground='white', 
                             selectbackground='#3E3E3E', selectforeground='#FFFFFF')

        # Initialize undo/redo stacks
        self.undo_stack = []
        self.redo_stack = []
        
        # Load file content
        self.original_text = ""
        self.load_file(filename)

        # Create filter entries and buttons
        self.create_buttons()

        # Create status bar
        self.create_status_bar()

        # Bind events
        self.text_area.bind('<KeyRelease>', self.update_cursor_position)

        self.root.mainloop()

    def create_buttons(self):
        # Frame for filter entries and buttons
        control_frame = tk.Frame(self.root, bg='#1E1E1E')
        control_frame.pack(fill='x', padx=10, pady=(0, 10))

        # Filter entry with label
        filter_label = tk.Label(control_frame, text="Filter:", bg='#1E1E1E', fg='#FFFFFF')
        filter_label.pack(side='left', padx=(0, 5))

        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(control_frame, bg='#2D2D2D', fg='#FFFFFF', 
                                     insertbackground='white', textvariable=self.filter_var)
        self.filter_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.filter_entry.bind('<Return>', self.apply_filter)

        # Negative filter entry with label
        negative_filter_label = tk.Label(control_frame, text="Negative Filter:", bg='#1E1E1E', fg='#FFFFFF')
        negative_filter_label.pack(side='left', padx=(0, 5))

        self.negative_filter_var = tk.StringVar()
        self.negative_filter_entry = tk.Entry(control_frame, bg='#2D2D2D', fg='#FFFFFF', 
                                              insertbackground='white', textvariable=self.negative_filter_var)
        self.negative_filter_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.negative_filter_entry.bind('<Return>', self.apply_negative_filter)

        # Buttons with modern styling
        button_frame = tk.Frame(control_frame, bg='#1E1E1E')
        button_frame.pack(side='left', padx=(10, 0))

        self.create_button(button_frame, "Undo", self.undo)
        self.create_button(button_frame, "Redo", self.redo)
        self.create_button(button_frame, "Reset", self.reset_filter)
        self.create_button(button_frame, "Save", self.save_file)

    def create_button(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command, bg='#3E3E3E', fg='#FFFFFF', 
                           activebackground='#4E4E4E', activeforeground='#FFFFFF', 
                           relief='flat', bd=0, padx=10, pady=5)
        button.pack(side='left', padx=5)
        return button

    def create_status_bar(self):
        # Status bar at the bottom
        status_bar = tk.Frame(self.root, bg='#1E1E1E', height=20)
        status_bar.pack(fill='x', side='bottom', pady=(0, 10), padx=10)

        self.cursor_label = tk.Label(status_bar, text="Cursor Position: 0", bg='#1E1E1E', fg='#FFFFFF')
        self.cursor_label.pack(side='left')

    def load_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.original_text = file.read()
                self.text_area.insert(tk.END, self.original_text)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File '{filename}' not found. Starting with an empty file.")
            self.original_text = ""
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.original_text = ""

    def apply_filter(self, event):
        filter_text = self.filter_var.get()
        if filter_text:
            self.undo_stack.append(self.text_area.get("1.0", tk.END))
            self.redo_stack.clear()
            self.filter_content(filter_text)

    def filter_content(self, filter_text):
        content = self.text_area.get("1.0", tk.END).splitlines()
        filter_text = filter_text.lower()
        filtered_lines = [line for line in content if filter_text in line.lower()]
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, "\n".join(filtered_lines))

    def apply_negative_filter(self, event):
        negative_filter_text = self.negative_filter_var.get()
        if negative_filter_text:
            self.undo_stack.append(self.text_area.get("1.0", tk.END))
            self.redo_stack.clear()
            self.negative_filter_content(negative_filter_text)

    def negative_filter_content(self, negative_filter_text):
        content = self.text_area.get("1.0", tk.END).splitlines()
        negative_filter_text = negative_filter_text.lower()
        filtered_lines = [line for line in content if negative_filter_text not in line.lower()]
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, "\n".join(filtered_lines))

    def undo(self):
        if self.undo_stack:
            last_content = self.undo_stack.pop()
            self.redo_stack.append(self.text_area.get("1.0", tk.END))
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, last_content)

    def redo(self):
        if self.redo_stack:
            last_redone = self.redo_stack.pop()
            self.undo_stack.append(self.text_area.get("1.0", tk.END))
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, last_redone)

    def reset_filter(self):
        # Save the current content to undo stack
        self.undo_stack.append(self.text_area.get("1.0", tk.END))
        self.redo_stack.clear()
        # Clear the text area
        self.text_area.delete("1.0", tk.END)
        # Load the original content of the currently opened file
        self.text_area.insert(tk.END, self.original_text)

    def save_file(self):
        current_content = self.text_area.get("1.0", tk.END)
        try:
            with open(self.filename, 'w') as file:
                file.write(current_content)
            messagebox.showinfo("Success", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def update_cursor_position(self, event):
        position = self.text_area.index(tk.INSERT)
        self.cursor_label.config(text=f"Cursor Position: {position}")

if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else "your_file.txt"
    Nedit(filename)