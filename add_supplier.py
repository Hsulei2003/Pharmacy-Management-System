import tkinter as tk
from tkinter import ttk, messagebox
import re  
from utils import clear

def add_supplier_page(main):
    # Circular Import မဖြစ်စေရန် Local Import သုံးထားပါသည်
    from logic import add_supplier_to_db, get_suppliers_list_details, delete_supplier_from_db

    clear(main)
    main.config(bg="#f8f9fa")

    # ခေါင်းစဉ်
    tk.Label(
        main, text="🏢 Supplier Management Setup", font=("Segoe UI", 20, "bold"), fg="#2c3e50", bg="#f8f9fa"
    ).pack(pady=15)

    # ဘယ်/ညာ ခွဲရန် Main Frame
    content_frame = tk.Frame(main, bg="#f8f9fa")
    content_frame.pack(fill="both", expand=True, padx=15, pady=5)

    # ==================== (ဘယ်ဘက်ခြမ်း) ADD SUPPLIER FORM ====================
    left_frame = tk.LabelFrame(
        content_frame, text="Add New Supplier", font=("Segoe UI", 11, "bold"), 
        bg="white", fg="#34495e", relief="solid", bd=1, padx=15, pady=15, width=320      
    )
    left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))

    lbl_style = {"bg": "white", "font": ("Segoe UI", 10, "bold"), "fg": "#2c3e50"}
    ent_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1}

    tk.Label(left_frame, text="Supplier Name *:", **lbl_style).pack(anchor="w", pady=(5, 2))
    name_entry = tk.Entry(left_frame, **ent_style, width=28)
    name_entry.pack(anchor="w", pady=(0, 10), ipady=3)

    tk.Label(left_frame, text="Phone Number *:", **lbl_style).pack(anchor="w", pady=(5, 2))
    phone_entry = tk.Entry(left_frame, **ent_style, width=28)
    phone_entry.pack(anchor="w", pady=(0, 10), ipady=3)

    tk.Label(left_frame, text="Email Address:", **lbl_style).pack(anchor="w", pady=(5, 2))
    email_entry = tk.Entry(left_frame, **ent_style, width=28)
    email_entry.pack(anchor="w", pady=(0, 10), ipady=3)

    tk.Label(left_frame, text="Address:", **lbl_style).pack(anchor="w", pady=(5, 2))
    address_entry = tk.Entry(left_frame, **ent_style, width=28)
    address_entry.pack(anchor="w", pady=(0, 15), ipady=3)

    # ==================== (ညာဘက်ခြမ်း) SUPPLIER LIST ====================
    right_frame = tk.LabelFrame(
        content_frame, text="Suppliers List", font=("Segoe UI", 11, "bold"), 
        bg="white", fg="#34495e", relief="solid", bd=1, padx=10, pady=10
    )
    right_frame.pack(side="right", fill="both", expand=True)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Segoe UI", 12), rowheight=28, background="white")
    style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#34495e", foreground="white")

    tree_scroll = ttk.Scrollbar(right_frame)
    tree_scroll.pack(side="right", fill="y")

    columns = ("id", "name", "phone", "email", "address")
    tree = ttk.Treeview(right_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set, style="Treeview")
    tree_scroll.config(command=tree.yview)

    tree.heading("id", text=" ")
    tree.heading("name", text="Supplier Name")
    tree.heading("phone", text="Phone")
    tree.heading("email", text="Email")
    tree.heading("address", text="Address")

    tree.column("id", width=0, minwidth= 0, stretch=tk.NO)
    tree.column("name", width=180, anchor="w", stretch=True)
    tree.column("phone", width=120, anchor="center", stretch=True)
    tree.column("email", width=120, anchor="w", stretch=True)
    tree.column("address", width=120, anchor="w", stretch=True)
    tree.pack(fill="both", expand=True, pady=(0, 10))

    # 🔄 🌟 [အစီအစဉ်ပြင်ဆင်ချက်] LOAD SUPPLIERS FUNCTION ကို ထိပ်ဆုံးသို ရွှေ့ထားပါသည်
    # ဤနေရာတွင် ထားမှသာ အောက်က Save, Edit, Delete ထဲက လှမ်းခေါ်ရင် Python က သိမှာဖြစ်ပါတယ်
    def load_suppliers():
        for item in tree.get_children():
            tree.delete(item)
        try:
            rows = get_suppliers_list_details()
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            print(f"Load Suppliers Error: {e}")

            # Format စစ်ဆေးသည့် Functions များ
    def is_valid_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def is_valid_phone(phone):
        cleaned_phone = re.sub(r'[\s\s-]', '', phone)
        phone_pattern = r'^(\+959|09|959)\d{7,10}$'
        return re.match(phone_pattern, cleaned_phone) is not None

    # Save function
    def save():
        name = name_entry.get().strip()
        phone = phone_entry.get().strip()
        email = email_entry.get().strip()
        address = address_entry.get().strip()

        if not name or not phone:
            messagebox.showwarning("Warning", "Supplier Name and Phone Number are required!")
            return

        if not is_valid_phone(phone):
            messagebox.showwarning("Invalid Phone", "Please enter a valid Phone Number!\nExample: 09123456789")
            return

        if email and not is_valid_email(email):
            messagebox.showwarning("Invalid Email", "Please enter a valid Email Address!\nExample: supplier@email.com")
            return

        cleaned_phone = re.sub(r'[\s\s-]', '', phone)

        if add_supplier_to_db(name, cleaned_phone, email, address):
            messagebox.showinfo("Success", "Supplier added successfully!")
            name_entry.delete(0, tk.END)
            phone_entry.delete(0, tk.END)
            email_entry.delete(0, tk.END)
            address_entry.delete(0, tk.END)
            load_suppliers()  # ယခုအခါ အထက်တွင် ရှိနေသဖြင့် ခေါ်၍ရသွားပါပြီ
        else:
            messagebox.showerror("Error", "Failed to add supplier. Name might already exist or Database table error!")

    # Add Button 
    tk.Button(
        left_frame, text="➕ Save Supplier", font=("Segoe UI", 11, "bold"), bg="#27ae60", fg="white", relief="flat", command=save, cursor="hand2", padx=15, pady=4
    ).pack(anchor="center", pady=5)


    # ==================== 🛠️ EDIT & DELETE BUTTONS AREA ====================
    # ညာဘက် List Table ရဲ့ အောက်ခြေ အလယ်တည့်တည့်မှာ ကပ်ထားရန် Frame
    action_btn_frame = tk.Frame(right_frame, bg="white")
    action_btn_frame.pack(anchor="center", pady=10) 

    # ၁။ Edit function
    def edit_supplier():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier from the list to edit!")
            return
        
        values = tree.item(selected, "values")
        sup_id = values[0]
        sup_name = values[1]
        sup_phone = values[2]
        sup_email = values[3]
        sup_address = values[4]

        # Edit Window Pop-up
        edit_win = tk.Toplevel()
        edit_win.title("📝 Edit Supplier")
        edit_win.geometry("360x420")
        edit_win.config(bg="#f8f9fa")
        edit_win.resizable(False, False)
        edit_win.grab_set() 

        tk.Label(edit_win, text="📝 Edit Supplier Details", font=("Segoe UI", 14, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=15)
        
        form_frame = tk.Frame(edit_win, bg="#f8f9fa")
        form_frame.pack(padx=20, fill="both", expand=True)

        lbl_m_style = {"bg": "#f8f9fa", "font": ("Segoe UI", 10, "bold"), "fg": "#2c3e50"}
        ent_m_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1}

        # Name
        tk.Label(form_frame, text="Supplier Name *:", **lbl_m_style).pack(anchor="w", pady=(5, 2))
        e_name_entry = tk.Entry(form_frame, **ent_m_style, width=32)
        e_name_entry.insert(0, sup_name)
        e_name_entry.pack(anchor="w", pady=(0, 10), ipady=2)

        # Phone
        tk.Label(form_frame, text="Phone Number *:", **lbl_m_style).pack(anchor="w", pady=(5, 2))
        e_phone_entry = tk.Entry(form_frame, **ent_m_style, width=32)
        e_phone_entry.insert(0, sup_phone)
        e_phone_entry.pack(anchor="w", pady=(0, 10), ipady=2)

        # Email
        tk.Label(form_frame, text="Email Address:", **lbl_m_style).pack(anchor="w", pady=(5, 2))
        e_email_entry = tk.Entry(form_frame, **ent_m_style, width=32)
        e_email_entry.insert(0, sup_email)
        e_email_entry.pack(anchor="w", pady=(0, 10), ipady=2)

        # Address
        tk.Label(form_frame, text="Address:", **lbl_m_style).pack(anchor="w", pady=(5, 2))
        e_address_entry = tk.Entry(form_frame, **ent_m_style, width=32)
        e_address_entry.insert(0, sup_address)
        e_address_entry.pack(anchor="w", pady=(0, 15), ipady=2)

        # Update Save function
        def update_supplier_save():
            u_name = e_name_entry.get().strip()
            u_phone = e_phone_entry.get().strip()
            u_email = e_email_entry.get().strip()
            u_address = e_address_entry.get().strip()

            if not u_name or not u_phone:
                messagebox.showwarning("Warning", "Supplier Name and Phone Number are required!", parent=edit_win)
                return

            if not is_valid_phone(u_phone):
                messagebox.showwarning("Invalid Phone", "Please enter a valid Phone Number!", parent=edit_win)
                return

            if u_email and not is_valid_email(u_email):
                messagebox.showwarning("Invalid Email", "Please enter a valid Email Address!", parent=edit_win)
                return

            u_cleaned_phone = re.sub(r'[\s\s-]', '', u_phone)

            # Database Update လုပ်ခြင်း
            from database import db
            try:
                with db() as conn:
                    c = conn.cursor()
                    c.execute(
                        "UPDATE suppliers SET name=?, phone=?, email=?, address=? WHERE id=?",
                        (u_name, u_cleaned_phone, u_email, u_address, sup_id)
                    )
                    conn.commit()
                messagebox.showinfo("Success", "Supplier updated successfully!")
                edit_win.destroy()
                load_suppliers() 
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update supplier: {e}", parent=edit_win)

        # Update Button
        tk.Button(
            form_frame, text="💾 Update Supplier", font=("Segoe UI", 11, "bold"), 
            bg="#2ecc71", fg="white", relief="flat", command=update_supplier_save, cursor="hand2", padx=15, pady=4
        ).pack(anchor="center", pady=10)

    # 📝 Edit Button (ဘယ်ဘက်ကပ်လျက်)
    tk.Button(
        action_btn_frame, text="📝 Edit Selected", font=("Segoe UI", 10, "bold"), 
        bg="#f1c40f", fg="white", relief="flat", command=edit_supplier, cursor="hand2", padx=15, pady=5
    ).pack(side="left", padx=10)


    # ၂။ Delete function
    def delete_supplier():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier from the list to delete!")
            return
        
        values = tree.item(selected, "values")
        sup_id = values[0]
        sup_name = values[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete supplier '{sup_name}'?"):
            if delete_supplier_from_db(sup_id):
                messagebox.showinfo("Deleted", "Supplier deleted successfully!")
                load_suppliers()
            else:
                messagebox.showerror("Error", "Failed to delete supplier.")

    # 🗑 Delete Button (ညာဘက်ကပ်လျက်)
    tk.Button(
        action_btn_frame, text="🗑 Delete Selected", font=("Segoe UI", 10, "bold"), 
        bg="#e74c3c", fg="white", relief="flat", command=delete_supplier, cursor="hand2", padx=15, pady=5
    ).pack(side="left", padx=10)

    # စာမျက်နှာစဖွင့်ချင်း ဇယားထဲ ဒေတာတင်ရန်
    load_suppliers()