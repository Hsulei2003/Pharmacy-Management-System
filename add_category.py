import tkinter as tk
from tkinter import ttk, messagebox
from database import db
import sqlite3
from utils import clear

def add_category_page(main):
    clear(main)
    main.config(bg="#f8f9fa")

    tk.Label(
        main, 
        text="📁 Category Setup", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=15)

    # Main Container Frame
    main_container = tk.Frame(main, bg="#f8f9fa")
    main_container.pack(fill="both", expand=True, padx=20, pady=10)

    # Left Panel: ADD CATEGORY FORM
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

    # Right Panel: CATEGORY LIST
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

    # Treeview Style
    cat_style = ttk.Style()
    cat_style.theme_use("clam")
    cat_style.configure("Cat.Treeview", font=("Segoe UI", 12), rowheight=30, background="white")
    cat_style.configure("Cat.Treeview.Heading", font=("Segoe UI", 13, "bold"), background="#34495e", foreground="white")
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
    tree.column("name", width=260, anchor="center")
    tree.pack(fill="both", expand=True)


    # LOGIC FUNCTIONS
    
    # Executing Categories From Database Function
    def load_categories():
        for item in tree.get_children():
            tree.delete(item)
        
        conn = None
        try:
            conn = db()
            c = conn.cursor()
            c.execute("SELECT cat_name FROM categories ORDER BY cat_name ASC")
            rows = c.fetchall()
            for idx, row in enumerate(rows, 1):
                tree.insert("", "end", values=(idx, row[0]))
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")
        finally:
            if conn:
                conn.close() 

    # Add New Category Function
    def save_category():
        cat_name = cat_entry.get().strip().capitalize()
        if not cat_name:
            messagebox.showwarning("Warning", "Please enter a category name!")
            return

        conn = None
        try:
            conn = db()
            c = conn.cursor()
            c.execute("INSERT INTO categories (cat_name) VALUES (?)", (cat_name,))
            conn.commit()
            
            messagebox.showinfo("Success", f"'{cat_name}' added successfully!")
            cat_entry.delete(0, tk.END)
            load_categories()
            
        except sqlite3.IntegrityError:  # နာမည်တူရှိနေခဲ့ရင်
            messagebox.showerror("Error", "This category already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            if conn:
                conn.close() 

    # Deleting Chosen Category From Treeview Function
    def delete_category():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category from the list to delete!")
            return
            
        values = tree.item(selected, "values")
        cat_name_to_delete = values[1]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Category '{cat_name_to_delete}'?\n(This might affect medicines under this category.)")
        
        if confirm:
            conn = None
            try:
                conn = db()
                c = conn.cursor()
                c.execute("DELETE FROM categories WHERE cat_name=?", (cat_name_to_delete,))
                conn.commit()
                messagebox.showinfo("Deleted", f"Category '{cat_name_to_delete}' deleted successfully!")
                load_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {e}")
            finally:
                if conn:
                    conn.close()

    
    # Right Delete Selected Button
    tk.Button(
        right_panel, 
        text="🗑 Delete Selected Category", 
        font=("Segoe UI", 11, "bold"), 
        bg="#e74c3c", 
        fg="white", 
        relief="flat",
        command=delete_category
    ).pack(side="bottom", anchor="center", padx=15, pady=(5, 15), ipady=3)

    # Left Add Category Button
    tk.Button(
        left_panel, 
        text="➕ Add Category", 
        font=("Segoe UI", 11, "bold"), 
        bg="#2ecc71", 
        fg="white", 
        relief="flat",
        command=save_category
    ).pack(fill="x", padx=20, pady=20, ipady=4)

    # pageပွင့်တာနဲ့ ညာဘက်ဇယားထဲ ဒေတာအလိုအလျောက်ဖြည့်
    load_categories()