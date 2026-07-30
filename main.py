import tkinter as tk
from database import create_table
from dashboard import dashboard
from add_medicine import add_page
from scan_sell import scan_page
from medicine_list import list_page
from add_category import add_category_page
from add_supplier import add_supplier_page
from account import account_page
from login import LoginWindow
from authentication.session import (logout as clear_session,get_current_user)
from user_management import user_management_page
from audit_log import audit_log_page

create_table()

def show_main_window(user_id):

    # ---------- MAIN WINDOW ----------
    root = tk.Tk()
    
    current_user = get_current_user()

    if current_user is None:
        root.destroy()
        return

    role = current_user["role"]

    root.title("Pharmacy Management System")
    root.geometry("1000x600")
    root.config(bg="#faf8f9")
    root.iconbitmap("app_icon.ico")
    
    # Maximize
    root.resizable(True, True) 

    def logout():

        current = get_current_user()

        if current:

            from database import log_action

            log_action(
                current["id"],
                current["username"],
                current["role"],
                "LOGOUT",
                "Authentication",
                "User logged out"
            )

        clear_session()

        root.destroy()

        login_app = LoginWindow(
            on_success=show_main_window
        )

        login_app.run()

    # Left Sidebar
    sidebar = tk.Frame(root, bg="#2c3e50", width=220)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # Right Main Content Area 
    main = tk.Frame(root, bg="#f8f9fa")
    main.pack(side="right", expand=True, fill="both")

    # ----- SIDEBAR STYLE & HEADER -----
    tk.Label(
        sidebar, 
        text="💊 PHARMACY", 
        font=("Segoe UI", 16, "bold"), 
        fg="#ecf0f1", 
        bg="#2c3e50", 
        pady=20
    ).pack()

    btn_style = {
        "font": ("Segoe UI", 11, "bold"),
        "fg": "#ecf0f1",
        "bg": "#34495e",
        "activebackground": "#1abc9c",
        "activeforeground": "white",
        "relief": "flat",
        "width": 20,
        "bd": 0,
        "cursor": "hand2"
    }

    # ---------- SIDEBAR BUTTONS ----------
    def create_sidebar_btn(icon, text_str, cmd):
        # btn background frame
        btn_frame = tk.Frame(sidebar, bg="#34495e", cursor="hand2")
        
        icon_lbl = tk.Label(btn_frame, text=icon, font=("Segoe UI", 12), fg="#ecf0f1", bg="#34495e", width=3, anchor="center")
        icon_lbl.pack(side="left", padx=(15, 0))
        
        text_lbl = tk.Label(btn_frame, text=text_str, font=("Segoe UI", 11, "bold"), fg="#ecf0f1", bg="#34495e", anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        # Event Bindings (ခလုတ်တစ်ခုလုံးရဲ့ ဘယ်နေရာကိုနှိပ်နှိပ် အလုပ်လုပ်စေရန်နှင့် Mouse တင်လျှင် အရောင်ပြောင်းရန်)
        for widget in (btn_frame, icon_lbl, text_lbl):
            widget.bind("<Button-1>", lambda e: cmd())
            widget.bind("<Enter>", lambda e, f=btn_frame, i=icon_lbl, t=text_lbl: [f.config(bg="#1abc9c"), i.config(bg="#1abc9c"), t.config(bg="#1abc9c")])
            widget.bind("<Leave>", lambda e, f=btn_frame, i=icon_lbl, t=text_lbl: [f.config(bg="#34495e"), i.config(bg="#34495e"), t.config(bg="#34495e")])
            
        return btn_frame
    
    # ----- Sidebar Buttons --------
    btn_dashboard = create_sidebar_btn("📊", "Dashboard", lambda: dashboard(main))
    btn_dashboard.pack(pady=8, fill="x", padx=10, ipady=6)

    btn_category = create_sidebar_btn("📦", "Category Setup", lambda: add_category_page(main))
    if role == "Admin":
        btn_category.pack(pady=8, fill="x", padx=10, ipady=6)

    btn_supplier = create_sidebar_btn("🏢", "Supplier Setup", lambda: add_supplier_page(main))
    if role == "Admin":
        btn_supplier.pack(pady=8, fill="x", padx=10, ipady=6)

    btn_add = create_sidebar_btn("➕", "Add Medicine", lambda: add_page(main))
    if role in ("Admin", "Staff"):
        btn_add.pack(pady=8, fill="x", padx=10, ipady=6)

    btn_list = create_sidebar_btn("📋", "Medicine List", lambda: list_page(main))
    if role in ("Admin", "Staff"):
        btn_list.pack(pady=8, fill="x", padx=10, ipady=6)

    btn_scan = create_sidebar_btn("🛍", "Scan & Sell", lambda: scan_page(main))
    btn_scan.pack(pady=8, fill="x", padx=10, ipady=6)

    btn_account = create_sidebar_btn("⚙️", "Account Settings", lambda: account_page(main, user_id))
    btn_account.pack(pady=8, fill="x", padx=10, ipady=6)

<<<<<<< HEAD
=======
    btn_user = create_sidebar_btn("👥","User Management",lambda: user_management_page(main))
    if role == "Admin":
        btn_user.pack(pady=8,fill="x",padx=10,ipady=6)

    btn_audit = create_sidebar_btn(
        "📜",
        "Audit Logs",
        lambda: audit_log_page(main)
    )

    if role == "Admin":
        btn_audit.pack(
            pady=8,
            fill="x",
            padx=10,
            ipady=6
        )

    # Sidebar ရဲ့ အောက်ခြေအဆုံးတွင် ပေါ်မည့် Log Out ခလုတ်လေး
>>>>>>> origin/king-receipt-update
    logout_btn = tk.Button(
        sidebar, 
        text="🚪 Log Out", 
        font=("Segoe UI", 11, "bold"), 
        bg="#c0392b", 
        fg="white", 
        relief="flat", 
        width=20, 
        bd=0, 
        cursor="hand2",
        activebackground="#e74c3c",
        activeforeground="white",
        command=logout
    )
    logout_btn.pack(pady=15, ipady=6, side="bottom")

    dashboard(main)

    root.mainloop()

if __name__ == "__main__":
    login_app = LoginWindow(on_success=show_main_window)
    login_app.run()