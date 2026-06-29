import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from database import db # မင်းရဲ့ ဒေတာဘေ့စ် ချိတ်ဆက်မှုဖိုင်
from utils import clear
from logic import get_status, get_all_categories, get_all_suppliers, get_medicines_list_details, delete_medicine_from_db

# =================================================================
# 🛠️ သက်တမ်းကုန်ဆေးများကို စတော့ခ် 0 ပြောင်းလဲပြီး ရှင်းထုတ်မည့် Logic
# =================================================================
def clear_expired_stock_update(refresh_callback):
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    confirm = messagebox.askyesno(
        "Confirm Action", 
        "Are you sure you want to set Qty to 0 for all expired medicine batches?"
    )
    if not confirm:
        return
        
    conn = None
    try:
        conn = db()
        c = conn.cursor()
        
        # 🌟 သက်တမ်းကုန်ပြီး စတော့ကျန်နေသေးသည့် Batch များကို Qty = 0 ပြောင်းလဲခြင်း
        c.execute("""
            UPDATE medicine_batches 
            SET qty = 0 
            WHERE expiry < ? AND qty > 0
        """, (current_date,))
        
        row_count = c.rowcount # ပြင်ဆင်လိုက်ရသော Batch အရေအတွက်ကို မှတ်သားခြင်း
        conn.commit()
        
        if row_count > 0:
            messagebox.showinfo("Success", f"Successfully cleared {row_count} expired batches (Set Qty to 0).")
            # 🔄 ဇယားကွက်ထဲတွင် စတော့ခ် 0 ဖြစ်သွားသည်ကို ချက်ချင်းမြင်ရအောင် ဇယားကို Refresh ပြန်လုပ်ခိုင်းခြင်း
            refresh_callback() 
        else:
            messagebox.showinfo("Info", "No expired active stock found to clear.")
            
    except Exception as e:
        messagebox.showerror("Database Error", f"Something went wrong while clearing stock:\n{e}")
    finally:
        # 🌟 သတိထားရန် - database locked အမှား ထပ်မတက်စေရန် connection ကို သေချာပြန်ပိတ်ခြင်း
        if conn:
            conn.close()

# ---------- MEDICINE LIST PAGE ----------
def list_page(main, focus_barcode=None):
    # ၁။ စာမျက်နှာအဟောင်းများကို အရင်ရှင်းထုတ်မည်
    clear(main)
    main.config(bg="#f8f9fa")

    # ခေါင်းစဉ်
    tk.Label(
        main, 
        text="💊 Medicine Stock Inventory (Batch System)", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=15)

    # 🌟 Search Frame
    search_frame = tk.Frame(main, bg="#f8f9fa")
    search_frame.pack(pady=5, fill="x", padx=20)

    # 🔍 (က) Name Search အပိုင်း
    tk.Label(search_frame, text="Search Name:", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#34495e").pack(side="left", padx=(5, 2))
    search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), width=20, relief="solid", bd=1)
    search_entry.pack(side="left", padx=5, ipady=3)
    
    # Name အတွက် သီးသန့် Search ခလုတ်
    def search_by_name():
        load(search_text=search_entry.get().strip(), search_type="name")

    tk.Button(search_frame, text="🔍 Search", font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", relief="flat", command=search_by_name).pack(side="left", padx=5)

    # separator လေးတစ်ခု ခြားပေးခြင်း
    tk.Label(search_frame, text=" | ", font=("Segoe UI", 11), bg="#f8f9fa", fg="#bdc3c7").pack(side="left", padx=10)

    # 💊 (ခ) Category Filter Dropdown အပိုင်း
    tk.Label(search_frame, text="Category:", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#34495e").pack(side="left", padx=(2, 2))
    
    db_categories = get_all_categories()
    if not db_categories:
        db_categories = ["⚪️ Tablet", "💊 Capsule", "🧪 Syrup", "💉 Injection", "🧴 Ointment", "📦 Other"]
    
    cat_options = ["✨ All Categories"] + db_categories
    
    cat_search_combo = ttk.Combobox(search_frame, values=cat_options, font=("Segoe UI", 11), state="readonly", width=18)
    cat_search_combo.current(0) 
    cat_search_combo.pack(side="left", padx=5, ipady=1)

    # ဇယား (Treeview) အတွက် Style ပြင်ဆင်ခြင်း
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Segoe UI", 11), rowheight=30, background="white")
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#2c3e50", foreground="white")
    
    # ရွေးချယ်ထားသော Row အား အရောင်သတ်မှတ်ခြင်း
    style.map("Treeview", background=[("selected", "#3498db")])

    # Table Container Frame
    table_frame = tk.Frame(main, bg="white", relief="solid", bd=1)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    scrollbar = ttk.Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")

    # 🌟 ကော်လံများတည်ဆောက်မှု (ID အား ရှေ့ဆုံးမှ ဝှက်၍ ထည့်သွင်းထားပါသည်)
    columns = ("id", "name", "barcode", "category", "qty", "expiry", "supplier", "status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set, style="Treeview")
    scrollbar.config(command=tree.yview)

    # ခေါင်းစဉ်များ သတ်မှတ်ခြင်း
    tree.heading("id", text="")
    tree.heading("name", text="Medicine Name")
    tree.heading("barcode", text="Barcode")
    tree.heading("category", text="Category")
    tree.heading("qty", text="Total Qty")
    tree.heading("expiry", text="Nearest Expiry")
    tree.heading("supplier", text="Supplier")
    tree.heading("status", text="Status")
        
    # ID အား လူမမြင်ရအောင် width=0, stretch=NO ပေးထားပြီး ကျန်ကော်လံများကို Mouse ဖြင့် ဆွဲဆန့်နိုင်အောင် ပြုလုပ်ထားပါသည်
    tree.column("id", width=0, minwidth=0, stretch=tk.NO)
    tree.column("name", width=180, anchor="w", stretch=True)
    tree.column("barcode", width=110, anchor="center", stretch=True)    
    tree.column("category", width=100, anchor="w", stretch=True) 
    tree.column("qty", width=80, anchor="center", stretch=True)       
    tree.column("expiry", width=110, anchor="center", stretch=True)       
    tree.column("supplier", width=120, anchor="w", stretch=True)   
    tree.column("status", width=110, anchor="center", stretch=True)   
    tree.pack(fill="both", expand=True)

    # 🌟 ဇယားထဲတွင် ဒေတာများကို ဆွဲထုတ်ပြသမည့် Load Function
    def load(search_text="", search_type="all"):
        for item in tree.get_children():
            tree.delete(item)

        # logic.py ထဲမှ စုပေါင်း JOIN ထားသော သန့်ရှင်းသည့် ဒေတာများကို လှမ်းယူခြင်း
        all_rows = get_medicines_list_details()
        
        # Treeview ထဲသို သက်ဆိုင်ရာ သက်တမ်းအလိုက် Сာသားအရောင်ဆိုးရန် Tag များ သတ်မှတ်ခြင်း
        tree.tag_configure("Expired", foreground="#e74c3c", font=("Segoe UI", 13, "bold"))      # စာသား အနီရောင်
        tree.tag_configure("Near Expiry", foreground="#e67e22", font=("Segoe UI", 13, "bold"))  # Сာသား လိမ္မော်ရောင်
        tree.tag_configure("Normal", foreground="#27ae60", font=("Segoe UI", 13, "bold"))                                     # Сာသား အစိမ်းရောင်
        tree.tag_configure("No Stock", foreground="#7f8c8d", background="#f2f2f2")             # ဇယား နောက်ခံ မီးခိုးရောင်

        target_item_id = None

        for row in all_rows:
            med_id, name, barcode, category, qty, expiry, supplier_val, status = row

            # --- 🔍 PYTHON SIDE FILTER (Name Search & Category Filter) ---
            if search_type == "name" and search_text:
                if not name.lower().startswith(search_text.lower()):
                    continue
            elif search_type == "category" and search_text and search_text != "✨ All Categories":
                if category != search_text:
                    continue

            # Treeview ထဲသို သိမ်းဆည်းထားသော အချက်အလက်များ သွတ်သွင်းခြင်း
            item_id = tree.insert(
                "", "end", 
                values=(med_id, name, barcode, category, qty, expiry, supplier_val, status), 
                tags=(status,)
            )
            # အသစ်သွင်းပြီး ပြန်လာပါက တန်းရွေးပေးထားရန်
            if focus_barcode and str(barcode) == str(focus_barcode):
                target_item_id = item_id
                
        if target_item_id:
            tree.selection_set(target_item_id)
            tree.focus(target_item_id)
            tree.see(target_item_id)

    def on_category_select(event):
        selected_cat = cat_search_combo.get()
        search_entry.delete(0, tk.END) 
        load(search_text=selected_cat, search_type="category")

    cat_search_combo.bind("<<ComboboxSelected>>", on_category_select)

    def reset_all():
        search_entry.delete(0, tk.END)
        cat_search_combo.current(0)
        load()

    tk.Button(search_frame, text="🔄 Show All", font=("Segoe UI", 10, "bold"), bg="#95a5a6", fg="white", relief="flat", command=reset_all).pack(side="left", padx=10)

# --------- EDIT WINDOW (အခြေခံဆေးအချက်အလက် ပြုပြင်ရန် ပေါ့ပ်အပ်) -----------
    def edit():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine from the list to edit!")
            return
        
        values = tree.item(selected, "values")
        med_id = values[0] # ID အား လှမ်းယူခြင်း
        
        edit_win = tk.Toplevel(main)
        edit_win.title("Edit Medicine Details")
        edit_win.geometry("380x280") # Qty နှင့် Expiry မပါတော့သဖြင့် အမြင့်ကို ညှိလိုက်ပါသည်
        edit_win.config(bg="#f8f9fa")
        edit_win.grab_set()

        lbl_style = {"bg": "#f8f9fa", "font": ("Segoe UI", 10, "bold"), "fg": "#34495e"}
        ent_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1}

        # Medicine Name
        tk.Label(edit_win, text="Medicine Name:", **lbl_style).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        name_entry = tk.Entry(edit_win, **ent_style, width=23)
        name_entry.insert(0, values[1])
        name_entry.grid(row=0, column=1, padx=15, pady=15)
        
        # Category
        tk.Label(edit_win, text="Category:", **lbl_style).grid(row=1, column=0, padx=15, pady=15, sticky="w")
        db_categories = get_all_categories()
        if not db_categories:
            db_categories = ["⚪️ Tablet", "💊 Capsule", "🧪 Syrup", "💉 Injection", "🧴 Ointment", "📦 Other"]

        cat_combo = ttk.Combobox(edit_win, values=db_categories, font=("Segoe UI", 11), state="readonly", width=21)
        cat_combo.set(values[3]) 
        cat_combo.grid(row=1, column=1, padx=15, pady=15)

        # Supplier Name
        tk.Label(edit_win, text="Supplier Name:", **lbl_style).grid(row=2, column=0, padx=15, pady=15, sticky="w")
        db_suppliers = get_all_suppliers()
        if not db_suppliers:
            db_suppliers = ["Default Supplier"]
            
        supplier_combo = ttk.Combobox(edit_win, values=db_suppliers, font=("Segoe UI", 11), state="readonly", width=21)
        supplier_combo.set(values[6]) 
        supplier_combo.grid(row=2, column=1, padx=15, pady=15)

        def update():
            name_val = name_entry.get().strip()
            cat_val = cat_combo.get().strip()
            supplier_val = supplier_combo.get().strip()

            if not name_val or not cat_val or not supplier_val:
                messagebox.showwarning("Error", "All fields are required!")
                return

            from database import db
            try:
                conn = db()
                c = conn.cursor()
                # 🌟 Medicines Table ထဲမှ အခြေခံအချက်အလက်ကို ပြင်ဆင်ခြင်း
                c.execute("""
                    UPDATE medicines 
                    SET name=?, category=?, supplier=?
                    WHERE id=?
                """, (name_val, cat_val, supplier_val, med_id))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Medicine details updated successfully!")
                load()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update medicine: {e}")

        tk.Button(
            edit_win, text="💾 Update Details", font=("Segoe UI", 11, "bold"), 
            bg="#2ecc71", fg="white", relief="flat", command=update, padx=20
        ).grid(row=3, column=0, columnspan=2, pady=20, ipady=4)

# --------- DELETE FUNCTION -----------
    def delete():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine from the list to delete!")
            return
            
        values = tree.item(selected, "values")
        med_id = values[0]
        med_name = values[1]
        
        # 🌟 CASCADE ကြောင့် Batch အားလုံးပါ တွဲပျက်သွားမည်ဖြစ်ကြောင်း အသိပေးချက်ထည့်ခြင်း
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete '{med_name}'?\n(This will automatically delete all its batch records!)"
        )
        if confirm:
            if delete_medicine_from_db(med_id):
                messagebox.showinfo("Deleted", f"'{med_name}' and its batch items deleted successfully!")
                load()
            else:
                messagebox.showerror("Error", "Failed to delete medicine from database.")

    # Action Buttons Frame
    btn_frame = tk.Frame(main, bg="#f8f9fa")
    btn_frame.pack(pady=15)

    # 🌟 အောက်က row=0 ထဲမှာ မင်းရဲ့ Edit နဲ့ Delete ခလုတ်တွေဘေးမှာ column=2 အနေနဲ့ စနစ်တကျ တိုးချဲ့ထည့်သွင်းပေးထားပါတယ်ဗျာ
    tk.Button(btn_frame, text="📝 Edit Details", font=("Segoe UI", 11, "bold"), bg="#f1c40f", fg="white", relief="flat", command=edit, padx=15, pady=5).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="🗑 Delete Medicine", font=("Segoe UI", 11, "bold"), bg="#e74c3c", fg="white", relief="flat", command=delete, padx=15, pady=5).grid(row=0, column=1, padx=10)
    
    # 🌟 (ထပ်တိုး) သက်တမ်းကုန်ဆေးများ ရှင်းထုတ်မည့် အနီရောင်ခလုတ်
    tk.Button(
        btn_frame, 
        text="🗑 Clear Expired Stock (Qty -> 0)", 
        font=("Segoe UI", 11, "bold"), 
        bg="#c0392b", # ပိုရင့်သော အနီရောင် Theme
        fg="white", 
        relief="flat", 
        cursor="hand2",
        padx=15, 
        pady=5,
        # load ဖန်ရှင်ကို callback အနေနဲ့ လှမ်းပေးလိုက်လို စတော့ခ် 0 ဖြစ်သွားတာ ချက်ချင်း ဇယားထဲမှာ မြင်ရမှာပါ
        command=lambda: clear_expired_stock_update(load) 
    ).grid(row=0, column=2, padx=10)

    # စာမျက်နှာစတင်ပွင့်သည်နှင့် ဒေတာများကို load လုပ်ခြင်း
    load()