import tkinter as tk
from tkinter import messagebox
from barcode_generator import generate_barcode
import random

def generate():
    name = name_entry.get().strip()

    if not name:
        messagebox.showerror("Error", "Enter medicine name")
        return

    code = str(random.randint(100000, 999999))

    generate_barcode(code, code)

    barcode_label.config(text=f"Barcode: {code}")
    messagebox.showinfo("Success", "Barcode Generated!")

# UI
root = tk.Tk()
root.title("Generate Barcode")

tk.Label(root, text="Medicine Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Button(root, text="Generate Barcode", command=generate).pack(pady=10)

barcode_label = tk.Label(root, text="")
barcode_label.pack()

root.mainloop()