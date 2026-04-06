from tkinter import messagebox

def set_reminder(text):
    messagebox.showinfo(
        "Reminder",
        f"Reminder saved:\n{text}"
    )
