import tkinter as tk
from tkinter import ttk, messagebox
from utils import clear
from datetime import datetime

# 🌟 Logic ထဲမှ လိုအပ်သော Functions များကို လှမ်းယူခြင်း
from logic import get_all_categories, get_all_suppliers, add_medicine_to_db

# ---------- ADD MEDICINE PAGE ----------
def add_page(main):
    clear(main)
    main.config(bg="#f8f9fa")

    # ခေါင်းစဉ်
    tk.Label(
        main, 
        text="🏢 Add Medicine (Batch Setup)", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=15)

    # ===== CANVAS PANEL ဆောက်ခြင်း =====
    card_width = 540
    card_height = 480  

    form_card = tk.Canvas(main, width=card_width, height=card_height, bg="#f8f9fa", highlightthickness=0)
    form_card.pack(pady=10)

    def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    draw_rounded_rect(form_card, 5, 5, card_width-5, card_height-5, radius=20, fill="white", outline="#e0e0e0", width=1)
    form_card.create_text(35, 30, text="Medicine & Batch Information", font=("Segoe UI", 12, "bold"), fill="#34495e", anchor="w")

    lbl_style = {"bg": "white", "font": ("Segoe UI", 11), "fg": "#2c3e50"}
    ent_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1}

    # ===== CONTROL များကို နေရာချခြင်း =====
    
    # Row 0: Medicine Name
    lbl_name = tk.Label(form_card, text="Medicine Name:", **lbl_style)
    form_card.create_window(35, 75, window=lbl_name, anchor="w")
    name_entry = tk.Entry(form_card, width=32, **ent_style)
    form_card.create_window(185, 75, window=name_entry, anchor="w")

    # Row 1: Barcode 
    lbl_bar = tk.Label(form_card, text="Barcode Number:", **lbl_style)
    form_card.create_window(35, 125, window=lbl_bar, anchor="w")
    barcode_entry = tk.Entry(form_card, width=32, **ent_style)
    form_card.create_window(185, 125, window=barcode_entry, anchor="w")

    # Toast Success စနစ်
    def show_toast_success(message):
        toast = tk.Toplevel()
        toast.overrideredirect(True) 
        toast.configure(bg="#2ecc71") 
        
        lbl = tk.Label(toast, text=f"✓  {message}", font=("Segoe UI", 11, "bold"), fg="white", bg="#2ecc71", padx=20, pady=10)
        lbl.pack()
        
        main.update_idletasks()
        x = main.winfo_rootx() + (main.winfo_width() // 2) - (toast.winfo_reqwidth() // 2)
        y = main.winfo_rooty() + main.winfo_height() - 70 
        toast.geometry(f"+{x}+{y}")
        
        toast.after(2000, toast.destroy)

    # Webcam Scan Button Function
    def trigger_webcam_scan():
        import cv2
        from scanner import BarcodeScanner
        
        scan_btn.config(state="disabled")
        scanner = BarcodeScanner()
        cap = cv2.VideoCapture(0)
        scanned_result = None
        window_name = "Quick Check Barcode (Press 'q' to Exit)"

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1) 
            result = scanner.scan_from_frame(frame)
            if result:
                import winsound
                winsound.Beep(2000, 150) 
                scanned_result = result
                break
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break
            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1: break
            except: break
            
        cap.release() # 🛠 Indentation တည့်ပေးလိုက်ပါတယ်

        cv2.destroyAllWindows()
        scan_btn.config(state="normal")
        
        if scanned_result:
            barcode_entry.delete(0, tk.END)
            barcode_entry.insert(0, scanned_result)
            show_toast_success(f"Barcode '{scanned_result}' scanned successfully.")

    # Scan Button
    scan_btn = tk.Button(
        form_card, text="🔍 Scan", font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", 
        relief="flat", command=trigger_webcam_scan, cursor="hand2", padx=8
    )
    form_card.create_window(450, 125, window=scan_btn, anchor="w")

    # Row 2: Category
    lbl_cat = tk.Label(form_card, text="Category:", **lbl_style)
    form_card.create_window(35, 175, window=lbl_cat, anchor="w")
    
    cat_combo = ttk.Combobox(form_card, font=("Segoe UI", 11), width=30, state="readonly")
    db_categories = get_all_categories()
    if not db_categories:
        db_categories = ["⚪️ Tablet", "💊 Capsule", "🧪 Syrup", "💉 Injection", "🧴 Ointment", "📦 Other"]
    cat_combo['values'] = db_categories
    if db_categories:
        cat_combo.current(0)
    form_card.create_window(185, 175, window=cat_combo, anchor="w")

    # Row 2.5: Batch Number
    lbl_batch = tk.Label(form_card, text="Batch Number *:", **lbl_style)
    form_card.create_window(35, 225, window=lbl_batch, anchor="w")
    batch_entry = tk.Entry(form_card, width=32, **ent_style)
    batch_entry.insert(0, "BATCH-" + datetime.now().strftime("%Y%m%d"))  
    form_card.create_window(185, 225, window=batch_entry, anchor="w")

    # Row 3: Quantity 
    lbl_qty = tk.Label(form_card, text="Quantity (Stock):", **lbl_style)
    form_card.create_window(35, 275, window=lbl_qty, anchor="w")
    qty_entry = tk.Entry(form_card, width=32, **ent_style)
    form_card.create_window(185, 275, window=qty_entry, anchor="w")

    # Row 3.5: Supplier Dropdown 
    lbl_supplier = tk.Label(form_card, text="Supplier Name:", **lbl_style)
    form_card.create_window(35, 325, window=lbl_supplier, anchor="w") 
    
    supplier_combo = ttk.Combobox(form_card, font=("Segoe UI", 11), width=30, state="readonly")
    db_suppliers = get_all_suppliers()
    if not db_suppliers:
        db_suppliers = ["Default Supplier"]
    supplier_combo['values'] = db_suppliers
    supplier_combo.current(0)
    form_card.create_window(185, 325, window=supplier_combo, anchor="w")

    # ===== Row 4: Expiry Date =====
    lbl_exp = tk.Label(form_card, text="Expiry Date:", **lbl_style)
    form_card.create_window(35, 375, window=lbl_exp, anchor="w") 
    
    date_container = tk.Frame(form_card, bg="white", highlightbackground="#a0a0a0", highlightcolor="#2c3e50", highlightthickness=1)
    form_card.create_window(185, 375, window=date_container, width=262, height=28, anchor="w") 
    
    # 🌟 (ပြင်ဆင်ချက်) exp_entry ကို pick_date() ရဲ့ အပြင်ဘက်ကို ထုတ်ပေးလိုက်လို ပုံမှန်အတိုင်း ပေါ်လာပါပြီ
    exp_entry = tk.Entry(date_container, font=("Segoe UI", 11), bg="white", bd=0, relief="flat")
    exp_entry.pack(side="left", fill="x", expand=True, padx=(5, 2))
    
    # ပြက္ခဒိန် Pop-up ဝင်းဒိုး ဖွင့်မည့် Function
    def pick_date():
        top = tk.Toplevel(main)
        top.title("Select Expiry Date")
        top.resizable(False, False)
        x = main.winfo_rootx() + 200
        y = main.winfo_rooty() + 250
        top.geometry(f"+{x}+{y}")
        
        from tkcalendar import Calendar
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        
        def set_date():
            exp_entry.delete(0, tk.END)
            exp_entry.insert(0, cal.get_date())
            top.destroy()
            
        tk.Button(top, text="Select Date", command=set_date, bg="#2c3e50", fg="white", font=("Segoe UI", 10, "bold"), padx=10).pack(pady=5)

    # 🌟 (ပြင်ဆင်ချက်) cal_btn ကို pick_date() ရဲ့ အပြင်ဘက်ကို ထုတ်ပြီး pack လုပ်ပေးလိုက်ပါတယ်
    cal_btn = tk.Button(
        date_container, text="📅", font=("Segoe UI", 11), bg="white", fg="#34495e", 
        relief="flat", command=pick_date, cursor="hand2", bd=0, activebackground="white"
    )
    cal_btn.pack(side="right", padx=(0, 5))
    
    # --------- SAVE TO DATABASE FUNCTION ---------
    def save_medicine():
        name = name_entry.get().strip()
        barcode = barcode_entry.get().strip()
        category = cat_combo.get()
        batch_number = batch_entry.get().strip() 
        qty = qty_entry.get().strip()
        supplier_val = supplier_combo.get() 
        expiry = exp_entry.get().strip()

        if not name or not barcode or not batch_number or not qty or not supplier_val or not expiry:
            messagebox.showwarning("Warning", "Please fill all required fields!")
            return
        
        if not qty.isdigit():
            messagebox.showwarning("Invalid Quantity", "Quantity must be a valid positive number!")
            return
            
        qty_int = int(qty)

        if add_medicine_to_db(name, barcode, category, batch_number, qty_int, expiry, supplier_val):
            messagebox.showinfo("Success", f"'{name}' (Batch: {batch_number}) added successfully to inventory!")
            
            from medicine_list import list_page   
            list_page(main, focus_barcode=barcode) 
        else:
            messagebox.showerror("Error", "Failed to add medicine batch. Database configuration error!")

    # Row 5: Add Button
    add_btn = tk.Button(
        form_card, 
        text="➕ Add Medicine & Batch", 
        font=("Segoe UI", 11, "bold"), 
        bg="#2e7d32", 
        fg="white",
        relief="flat",
        command=save_medicine,
        cursor="hand2",
        padx=25,
        pady=5
    )
    form_card.create_window(270, 445, window=add_btn, anchor="center")