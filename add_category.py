import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from utils import clear

def add_category_page(main):
    # ၁။ စာမျက်နှာဟောင်းများကို ဖယ်ရှားခြင်း
    clear(main)
    main.config(bg="#f8f9fa")

    # ဒေတာဘေ့စ်ထဲမှာ categories table မရှိသေးရင် ဆောက်ရန်
    conn = db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_name TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

    # ขေါင်းစဉ်ကြီး
    tk.Label(
        main, 
        text="📁 Category Management", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=15)

    # 🌟 [ပင်မ Container Frame] - ဘယ်/ညာ Panel နှစ်ခုကို ကပ်ထားမည့် နေရာ
    main_container = tk.Frame(main, bg="#f8f9fa")
    main_container.pack(fill="both", expand=True, padx=20, pady=10)

    # =================================================================
    # 👈 ဘယ်ဘက် Panel: ADD CATEGORY FORM
    # =================================================================
    left_panel = tk.LabelFrame(
        main_container, 
        text="Add New Category", 
        font=("Segoe UI", 12, "bold"),
        fg="#2c3e50", 
        bg="white", 
        relief="solid", 
        bd=1
    )
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

    tk.Label(
        left_panel, 
        text="Category Name:", 
        font=("Segoe UI", 11, "bold"), 
        fg="#34495e", 
        bg="white"
    ).pack(anchor="w", padx=20, pady=(30, 5))

    cat_entry = tk.Entry(left_panel, font=("Segoe UI", 12), relief="solid", bd=1)
    cat_entry.pack(fill="x", padx=20, pady=5, ipady=4)

    # =================================================================
    # 👉 ညာဘက် Panel: CATEGORY LIST
    # =================================================================
    right_panel = tk.LabelFrame(
        main_container, 
        text="Existing Categories", 
        font=("Segoe UI", 12, "bold"),
        fg="#2c3e50", 
        bg="white", 
        relief="solid", 
        bd=1
    )
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)

    # Table Container Frame
    tree_frame = tk.Frame(right_panel, bg="white")
    tree_frame.pack(fill="both", expand=True, padx=15, pady=(15, 5))

    scrollbar = ttk.Scrollbar(tree_frame)
    scrollbar.pack(side="right", fill="y")

    # Treeview Style မြှင့်တင်ထားခြင်း
    cat_style = ttk.Style()
    cat_style.theme_use("clam")
    cat_style.configure("Cat.Treeview", font=("Segoe UI", 10), rowheight=28, background="white")
    cat_style.configure("Cat.Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#34495e", foreground="white")
    cat_style.map("Cat.Treeview", background=[("selected", "#1abc9c")])

    tree = ttk.Treeview(
        tree_frame, 
        columns=("id", "name"), 
        show="headings", 
        style="Cat.Treeview", 
        yscrollcommand=scrollbar.set
    )
    scrollbar.config(command=tree.yview)

    tree.heading("id", text="No.", anchor="center")
    tree.heading("name", text="Category Name", anchor="center")
    tree.column("id", width=80, anchor="center")
    tree.column("name", width=260, anchor="w")
    tree.pack(fill="both", expand=True)


    # =================================================================
    # ⚙️ LOGIC FUNCTIONS (ခလုတ်တွေမခေါ်ခင် ကြိုတင်ကြေညာထားခြင်း)
    # =================================================================
    
    # 🔄 Database ထဲက Category များကို ဆွဲထုတ်ပြသမည့် Function
    def load_categories():
        for item in tree.get_children():
            tree.delete(item)
        
        conn = db()
        c = conn.cursor()
        c.execute("SELECT cat_name FROM categories ORDER BY cat_name ASC")
        rows = c.fetchall()
        conn.close()

        for idx, row in enumerate(rows, 1):
            tree.insert("", "end", values=(idx, row[0]))
            # 💾 Category အသစ်ထည့်မည့် လုပ်ဆောင်ချက်
    def save_category():
        cat_name = cat_entry.get().strip()
        if not cat_name:
            messagebox.showwarning("Warning", "Please enter a category name!")
            return

        try:
            conn = db()
            c = conn.cursor()
            c.execute("INSERT INTO categories (cat_name) VALUES (?)", (cat_name,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"'{cat_name}' added successfully!")
            cat_entry.delete(0, tk.END)
            load_categories()
            
        except db.IntegrityError:  # sqlite3 သိုမဟုတ် db error စစ်ဆေးခြင်း
            messagebox.showerror("Error", "This category already exists!")

    # 🗑 Treeview ထဲက ရွေးထားတဲ့ Category ကို ဖျက်မည့် Function
    def delete_category():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category from the list to delete!")
            return
            
        values = tree.item(selected, "values")
        cat_name_to_delete = values[1]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Category '{cat_name_to_delete}'?\n(This might affect medicines under this category.)")
        
        if confirm:
            conn = db()
            c = conn.cursor()
            c.execute("DELETE FROM categories WHERE cat_name=?", (cat_name_to_delete,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Deleted", f"Category '{cat_name_to_delete}' deleted successfully!")
            load_categories()


    # =================================================================
    # 🔘 BUTTONS CREATION (Function များအောက်သို ရွှေ့လိုက်သဖြင့် Error မတက်တော့ပါ)
    # =================================================================
    
    # ➕ ညာဘက်ခြမ်းအတွက် Delete Selected Button
    tk.Button(
        right_panel, 
        text="🗑 Delete Selected Category", 
        font=("Segoe UI", 11, "bold"), 
        bg="#e74c3c", 
        fg="white", 
        relief="flat",
        command=delete_category
    ).pack(side="bottom", anchor="center", padx=15, pady=(5, 15), ipady=3)

    # ➕ ဘယ်ဘက်ခြမ်းအတွက် Add Category Button
    tk.Button(
        left_panel, 
        text="➕ Add Category", 
        font=("Segoe UI", 11, "bold"), 
        bg="#2ecc71", 
        fg="white", 
        relief="flat",
        command=save_category
    ).pack(fill="x", padx=20, pady=20, ipady=4)

    # စာမျက်နှာပွင့်လာတာနဲ့ ညာဘက်ဇယားထဲ ဒေတာအလိုအလျောက်ဖြည့်ရန်
    load_categories()