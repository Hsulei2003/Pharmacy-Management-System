import tkinter as tk
from tkinter import messagebox
from database import db

class LoginWindow:
    def __init__(self, on_success):
        self.on_success = on_success
        
        self.root = tk.Tk()
        self.root.title("Pharmacy System - Login")
        self.root.geometry("450x400") 
        self.root.config(bg="#f8f9fa")
        self.root.resizable(False, False)
        
        # Screen ရဲ့ အလယ်တည့်တည့်မှာ Window ပွင့်စေရန်
        self.root.eval('tk::PlaceWindow . center')

        # Main Container Frame (ဘေးပတ်ပတ်လည် နေရာလွတ်ချန်ရန်)
        main_frame = tk.Frame(self.root, bg="#f8f9fa", padx=40, pady=30)
        main_frame.pack(fill="both", expand=True)

        # Header Title
        tk.Label(
            main_frame, 
            text="🔐 LOGIN SYSTEM", 
            font=("Segoe UI", 18, "bold"), 
            fg="#2c3e50", 
            bg="#f8f9fa"
        ).pack(pady=(0, 25))

        # Username Field
        tk.Label(main_frame, text="Username", font=("Segoe UI", 10, "bold"), fg="#7f8c8d", bg="#f8f9fa").pack(anchor="w")
        self.username_entry = tk.Entry(
            main_frame, 
            font=("Segoe UI", 12), 
            bd=1, 
            relief="solid",
            bg="white",
            highlightthickness=0
        )
        self.username_entry.pack(fill="x", pady=(5, 15), ipady=6) # ipady က entry ဗူးကို ပိုမိုအမြင့်ကြီးစေပါတယ်
        self.username_entry.focus()

        # Password Field
        tk.Label(main_frame, text="Password", font=("Segoe UI", 10, "bold"), fg="#7f8c8d", bg="#f8f9fa").pack(anchor="w")
        self.password_entry = tk.Entry(
            main_frame, 
            font=("Segoe UI", 12), 
            bd=1, 
            relief="solid",
            bg="white",
            show="•",
            highlightthickness=0
        )
        self.password_entry.pack(fill="x", pady=(5, 25), ipady=6)

        # Login Button
        self.login_btn = tk.Button(
            main_frame, 
            text="LOGIN", 
            font=("Segoe UI", 11, "bold"), 
            bg="#1abc9c", 
            fg="white", 
            activebackground="#16a085",
            activeforeground="white",
            bd=0, 
            relief="flat",
            command=self.check_login,
            cursor="hand2"
        )
        self.login_btn.pack(fill="x", ipady=8)

        # Enter ခလုတ်နှိပ်ရင်လည်း Login ဝင်လို့ရအောင် ချိတ်ဆက်ခြင်း
        self.root.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Warning", "Please fill Username and Password.")
            return

        try:
            conn = db()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = c.fetchone()
            conn.close()

            if user:
                self.root.destroy()
                self.on_success()
            else:
                messagebox.showerror("Error", "Incorrect Username or Password!")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    def run(self):
        self.root.mainloop()