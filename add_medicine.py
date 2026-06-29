import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import db # 🌟 ဒေတာဘေ့စ် ချိတ်ဆက်မှု
from utils import clear

# 🌟 Logic နှင့် အခြား စာမျက်နှာ (List Page) ကို လှမ်းယူခြင်း
from logic import get_all_categories, get_all_suppliers
from medicine_list import list_page # 🌟 ဒေတာသိမ်းပြီးရင် List Page ကို တန်းကူးဖို လှမ်းခေါ်ခြင်း

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
    lbl_name = tk.Label(form_card, text="Medicine Name *:", **lbl_style)
    form_card.create_window(35, 75, window=lbl_name, anchor="w")
    name_entry = tk.Entry(form_card, width=32, **ent_style)
    form_card.create_window(185, 75, window=name_entry, anchor="w")

    # Row 1: Barcode 
    lbl_bar = tk.Label(form_card, text="Barcode Number *:", **lbl_style)
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
            
        cap.release() 
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
    lbl_qty = tk.Label(form_card, text="Quantity (Stock) *:", **lbl_style)
    form_card.create_window(35, 275, window=lbl_qty, anchor="w")
    qty_entry = tk.Entry(form_card, width=32, **ent_style)
    qty_entry.insert(0, "0") 
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
    lbl_exp = tk.Label(form_card, text="Expiry Date *:", **lbl_style)
    form_card.create_window(35, 375, window=lbl_exp, anchor="w") 
    
    date_container = tk.Frame(form_card, bg="white", highlightbackground="#a0a0a0", highlightcolor="#2c3e50", highlightthickness=1)
    form_card.create_window(185, 375, window=date_container, width=262, height=28, anchor="w") 
    
    exp_entry = tk.Entry(date_container, font=("Segoe UI", 11), bg="white", bd=0, relief="flat")
    exp_entry.pack(side="left", fill="x", expand=True, padx=(5, 2))
    
    # 📅 ပြက္ခဒိန်ကို ဘောင်ပါရှိပြီး ခလုတ်ဘေးတင် ကွက်တိပေါ်စေမည့် Function
    def pick_date():
        top = tk.Toplevel(main)
        top.title("Select Expiry Date")
        top.resizable(False, False)
        top.attributes("-topmost", True) # အမြဲတမ်းအပေါ်ဆုံးမှာ ရှိနေစေရန်

        # 📅 ခလုတ်ရဲ့ Screen ပေါ်က တည်နေရာကို ယူခြင်း
        btn_x = cal_btn.winfo_rootx()
        btn_y = cal_btn.winfo_rooty()
        btn_width = cal_btn.winfo_width()

        # 🌟 ပြက္ခဒိန် အရွယ်အစား သတ်မှတ်ခြင်း
        popup_width = 270
        popup_height = 250

        # 🌟 📅 ခလုတ်ရဲ့ ညာဘက်ဘေးတင် ကွက်တိ ကပ်ပေါ်စေရန် တွက်ချက်ခြင်း
        # ခလုတ်ရဲ့ X တည်နေရာ + ခလုတ်အကျယ် + ၅ ပစ်ဆယ်လ် (ဘေးကပ်လျက် ပေါ်လာပါလိမ့်မယ်)
        popup_x = btn_x + btn_width + 5
        popup_y = btn_y - 10 # ခေါင်းစဉ်ဘောင်ပါလို အနည်းငယ် အပေါ်ပြန်တင်ပေးထားခြင်း

        top.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

        # 📅 Calendar Widget ထည့်သွင်းခြင်း
        from tkcalendar import Calendar
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd', locale='en_US')
        cal.pack(padx=5, pady=5, fill="both", expand=True)
        
        # ရွေးချယ်မှုစနစ်
        def set_date():
            exp_entry.delete(0, tk.END)
            exp_entry.insert(0, cal.get_date())
            top.destroy()
            
        tk.Button(
            top, text="✔️ Select Date", command=set_date, 
            bg="#2c3e50", fg="white", font=("Segoe UI", 9, "bold"), 
            padx=10, pady=2, relief="flat", cursor="hand2"
        ).pack(pady=3)

    cal_btn = tk.Button(
        date_container, text="📅", font=("Segoe UI", 11), bg="white", fg="#34495e", 
        relief="flat", command=pick_date, cursor="hand2", bd=0, activebackground="white"
    )
    cal_btn.pack(side="right", padx=(0, 5))
    
    # --------- SAVE TO DATABASE FUNCTION ---------
    def save_medicine():
        name_val = name_entry.get().strip()
        barcode_val = barcode_entry.get().strip()
        qty_input = qty_entry.get().strip()
        expiry_val = exp_entry.get().strip() 
        batch_val = batch_entry.get().strip()
        cat_val = cat_combo.get().strip()
        supplier_val = supplier_combo.get().strip()

        if not name_val or not barcode_val or not batch_val or not qty_input or not expiry_val:
            messagebox.showwarning("Warning", "All required fields (*) must be filled!")
            return
        
        # 🟢 Barcode စည်းကမ်းသတ်မှတ်ခြင်း (အင်္ဂလိပ်စာလုံး၊ ဂဏန်း နှင့် - သာ ခွင့်ပြုမည်)
        # spaces တွေ၊ မြန်မာစာတွေ၊ အခြား symbols တွေ မှားရိုက်ရင် တားဆီးရန်
        import re
        if not re.match("^[A-Za-z0-9_-]+$", barcode_val):
            messagebox.showerror(
                "Invalid Barcode", 
                "Barcode must contain English letters, numbers, or dashes (-) only!\nNo spaces or special characters allowed."
            )
            return

        if not qty_input.isdigit():
            messagebox.showerror("Error", "Quantity must be a valid number!")
            return
        qty_val = int(qty_input)

        try:
            conn = db()
            c = conn.cursor()

            # 🔍 ၁။ Barcode ရှိပြီးသားလား အရင်စစ်မည်
            c.execute("SELECT id, name FROM medicines WHERE barcode = ?", (barcode_val,))
            existing_med = c.fetchone()

            if existing_med:
                med_id, existing_name = existing_med
                
                # ⚠️ ၂။ Barcode တူပေမယ့် နာမည် မတူရင် တားဆီးခြင်း
                if existing_name.lower() != name_val.lower():
                    messagebox.showerror(
                        "Barcode Clash Error", 
                        f"This Barcode ({barcode_val}) is already registered to another medicine: '{existing_name}'.\n\n"
                        f"You cannot assign the same barcode to '{name_val}'!"
                    )
                    conn.close()
                    return 
                    
                else:
                    # 👍 ၃။ Barcode ရော နာမည်ရော တူရင် - Batch သစ်ပဲ သွင်းမည်
                    c.execute("""
                        INSERT INTO medicine_batches (medicine_id, batch_number, qty, expiry)
                        VALUES (?, ?, ?, ?)
                    """, (med_id, batch_val, qty_val, expiry_val))
                    conn.commit()
                    messagebox.showinfo("Success", f"New batch ({batch_val}) added for existing medicine '{name_val}'.")

            else:
                # ✨ ၄။ Barcode အသစ်ဆိုလျှင် ဆေးအသစ်ရော၊ Batch အသစ်ရော သွင်းမည်
                c.execute("""
                    INSERT INTO medicines (name, barcode, category, supplier)
                    VALUES (?, ?, ?, ?)
                """, (name_val, barcode_val, cat_val, supplier_val))
                
                new_med_id = c.lastrowid 
                
                c.execute("""
                    INSERT INTO medicine_batches (medicine_id, batch_number, qty, expiry)
                    VALUES (?, ?, ?, ?)
                """, (new_med_id, batch_val, qty_val, expiry_val))
                conn.commit()
                messagebox.showinfo("Success", f"Successfully added new medicine '{name_val}'!")

            conn.close()
            
            # 🌟 ၅။ [အောင်မြင်စွာ သိမ်းပြီးပါက Medicine List Сာမျက်နှာသို တန်းကူးသွားစေရန် လှမ်းခေါ်ခြင်း]
            list_page(main, focus_barcode=barcode_val)
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save medicine:\n{e}")

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