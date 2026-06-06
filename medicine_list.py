import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from logic import get_status
from utils import clear
from logic import get_all_categories

# ---------- MEDICINE LIST PAGE ----------
def list_page(main, focus_barcode=None):
    # ၁။ Сာမျက်နှာအဟောင်းများကို အရင်ရှင်းထုတ်မည်
    clear(main)
    main.config(bg="#f8f9fa")

    # ခေါင်းစဉ်
    tk.Label(
        main, 
        text="💊 Medicine Inventory List", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=15)

    # Search Frame (ရှာဖွေရန်နေရာ)
    search_frame = tk.Frame(main, bg="#f8f9fa")
    search_frame.pack(pady=5, fill="x", padx=20)

    search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), width=30, relief="solid", bd=1)
    search_entry.pack(side="left", padx=5, ipady=3)

    # ဇယား (Treeview) အတွက် Style ပြင်ဆင်ခြင်း
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background="white")
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#34495e", foreground="white")
    style.map("Treeview", background=[("selected", "#1abc9c")]) # ရွေးလိုက်ရင် ပြာစိမ်းရောင်ပြောင်းမည်

    # Table Container Frame
    table_frame = tk.Frame(main)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Scrollbar ထည့်သွင်းခြင်း
    scrollbar = ttk.Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")

    # Treeview ဇယားဆောက်ခြင်း
    columns = ("name", "barcode", "category", "qty", "expiry", "status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    scrollbar.config(command=tree.yview)

    # Column ခေါင်းစဉ်များနှင့် အကျယ် သတ်မှတ်ခြင်း
    headers = {
        "name": "Medicine Name", "barcode": "Barcode", "category": "Category",
        "qty": "Quantity", "expiry": "Expiry Date", "status": "Status"
    }
    for col, text in headers.items():
        tree.heading(col, text=text, anchor="center")
        
    tree.column("name", width=160, anchor="w")        
    tree.column("barcode", width=110, anchor="center")    
    tree.column("category", width=100, anchor="center") 
    tree.column("qty", width=90, anchor="center")       
    tree.column("expiry", width=110, anchor="center")       
    tree.column("status", width=110, anchor="center")   
    
    tree.pack(fill="both", expand=True)

    # ဒေတာများကို သက်ဆိုင်ရာ အရောင်များနှင့်ပြသပေးမည့် Load Function
    def load(search_text=""):
        for item in tree.get_children():
            tree.delete(item)

        conn = db()
        c = conn.cursor()
        
        if search_text:
            c.execute("""
                SELECT name, barcode, category, qty, expiry 
                FROM medicines 
                WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ? 
                ORDER BY rowid DESC
            """, (f"{search_text.lower()}%", f"{search_text.lower()}%"))
        else:
            c.execute("SELECT name, barcode, category, qty, expiry FROM medicines ORDER BY rowid DESC")
            
        rows = c.fetchall()
        conn.close()

        tree.tag_configure("Expired", foreground="#e74c3c", font=("Segoe UI", 12, "bold"))
        tree.tag_configure("Near Expiry", foreground="#d35400", font=("Segoe UI", 12, "bold"))
        tree.tag_configure("Normal", foreground="#1e7e34", font=("Segoe UI", 12, "bold"))

        target_item_id = None

        for row in rows:
            name, barcode, category, qty, expiry = row
            status = get_status(expiry)

            if status == "Expired":
                tag = "Expired"
            elif status == "Near Expiry":
                tag = "Near Expiry"
            else:
                tag = "Normal"

            item_id = tree.insert("", "end", values=(name, barcode, category, qty, expiry, status), tags=(tag,))
            
            if focus_barcode and str(barcode) == str(focus_barcode):
                target_item_id = item_id
                if target_item_id:
                    tree.selection_set(target_item_id)
                    tree.focus(target_item_id)
                    tree.see(target_item_id)

    # Search Buttons
    tk.Button(search_frame, text="🔍 Search", font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", relief="flat", command=lambda: load(search_entry.get().strip())).pack(side="left", padx=5)
    tk.Button(search_frame, text="🔄 Show All", font=("Segoe UI", 10, "bold"), bg="#95a5a6", fg="white", relief="flat", command=lambda: [search_entry.delete(0, tk.END), load()]).pack(side="left", padx=5)

    # --------- EDIT WINDOW (ပြုပြင်ရန် ပေါ့ပ်အပ်) -----------
    def edit():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine from the list to edit!")
            return
        
        values = tree.item(selected, "values")
        
        # Window အသစ် ဆောက်ခြင်း
        edit_win = tk.Toplevel(main)
        edit_win.title("Edit Medicine")
        edit_win.geometry("380x320")
        edit_win.config(bg="#f8f9fa")
        edit_win.grab_set()

        # Form UI Style
        lbl_style = {"bg": "#f8f9fa", "font": ("Segoe UI", 10, "bold"), "fg": "#34495e"}
        ent_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1}

        tk.Label(edit_win, text="Medicine Name:", **lbl_style).grid(row=0, column=0, padx=15, pady=12, sticky="w")
        name_entry = tk.Entry(edit_win, **ent_style)
        name_entry.insert(0, values[0])
        name_entry.grid(row=0, column=1, padx=15, pady=12)

        # # ⭐️ (ပြင်ဆင်ချက်) Category ကို ရိုက်ထည့်ခိုင်းမည့်အစား Dropdown (Combobox) ပြောင်းလဲခြင်း
        tk.Label(edit_win, text="Category:", **lbl_style).grid(row=1, column=0, padx=15, pady=12, sticky="w")
        
        # 🌟 [ဒီနေရာလေးကို အစားထိုးပြင်ဆင်တာပါ]
        # Database ထဲက အသစ်ထည့်ထားသမျှ Category List ကို လှမ်းယူခြင်း
        db_categories = get_all_categories()
        
        # အကယ်၍ database ထဲမှာ ဘာမှမရှိသေးရင် Backup အနေနဲ့ ဒါလေးတွေပြပေးထားမယ်
        if not db_categories:
            db_categories = ["⚪️ Tablet", "💊 Capsule", "🧪 Syrup", "💉 Injection", "🧴 Ointment", "📦 Other"]

        # values နေရာမှာ ပုံသေ list အစား db_categories ကို ထည့်ပေးလိုက်ပါတယ်
        cat_combo = ttk.Combobox(edit_win, values=db_categories, font=("Segoe UI", 11), state="readonly")
        cat_combo.set(values[2]) # နဂိုမူလ database ထဲက တန်ဖိုးကို အလိုအလျောက် ရွေးပေးထားခြင်း
        cat_combo.grid(row=1, column=1, padx=15, pady=12)

        tk.Label(edit_win, text="Quantity:", **lbl_style).grid(row=2, column=0, padx=15, pady=12, sticky="w")
        qty_entry = tk.Entry(edit_win, **ent_style)
        qty_entry.insert(0, values[3])
        qty_entry.grid(row=2, column=1, padx=15, pady=12)

        tk.Label(edit_win, text="Expiry Date:", **lbl_style).grid(row=3, column=0, padx=15, pady=12, sticky="w")
        exp_entry = tk.Entry(edit_win, **ent_style)
        exp_entry.insert(0, values[4])
        exp_entry.grid(row=3, column=1, padx=15, pady=12)

        def update():
            # သတ်မှတ်ချက်များ စစ်ဆေးခြင်း
            if not name_entry.get().strip() or not cat_combo.get().strip() or not qty_entry.get().strip() or not exp_entry.get().strip():
                messagebox.showwarning("Error", "All fields are required!")
                return
                
            conn = db()
            c = conn.cursor()
            c.execute("""
                UPDATE medicines 
                SET name=?, category=?, qty=?, expiry=?
                WHERE barcode=?
            """, (name_entry.get().strip(), cat_combo.get().strip(), qty_entry.get().strip(), exp_entry.get().strip(), values[1]))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Medicine updated successfully!")
            load()
            edit_win.destroy()

        # Update Button
        tk.Button(
            edit_win, text="💾 Update Now", font=("Segoe UI", 11, "bold"), 
            bg="#2ecc71", fg="white", relief="flat", command=update, padx=20
        ).grid(row=4, column=0, columnspan=2, pady=20, ipady=4)

        # --------- DELETE FUNCTION -----------
    def delete():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine from the list to delete!")
            return
            
        values = tree.item(selected, "values")
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{values[0]}'?")
        if confirm:
            conn = db()
            c = conn.cursor()
            c.execute("DELETE FROM medicines WHERE barcode=?", (values[1],))
            conn.commit()
            conn.close()
            load()
            messagebox.showinfo("Deleted", "Medicine deleted successfully!")

    # Action Buttons Frame
    btn_frame = tk.Frame(main, bg="#f8f9fa")
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="📝 Edit Selected", font=("Segoe UI", 11, "bold"), bg="#f1c40f", fg="white", relief="flat", command=edit, padx=15, pady=5).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="🗑 Delete Selected", font=("Segoe UI", 11, "bold"), bg="#e74c3c", fg="white", relief="flat", command=delete, padx=15, pady=5).grid(row=0, column=1, padx=10)

    load()