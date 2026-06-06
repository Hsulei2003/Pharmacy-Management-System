import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from utils import clear
from datetime import datetime
from tkcalendar import DateEntry 
from logic import get_all_categories

# ---------- ADD MEDICINE PAGE ----------
def add_page(main):
    clear(main)
    main.config(bg="#f8f9fa")

    # ခေါင်းစဉ်
    tk.Label(
        main, 
        text="➕ Add New Medicine", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=20)

    # ===== CANVAS PANEL PANEL ဆောက်ခြင်း =====
    card_width = 540
    card_height = 380  

    form_card = tk.Canvas(main, width=card_width, height=card_height, bg="#f8f9fa", highlightthickness=0)
    form_card.pack(pady=15)

    def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    draw_rounded_rect(form_card, 5, 5, card_width-5, card_height-5, radius=20, fill="white", outline="#e0e0e0", width=1)
    form_card.create_text(35, 30, text="Medicine Information", font=("Segoe UI", 12, "bold"), fill="#34495e", anchor="w")

    lbl_style = {"bg": "white", "font": ("Segoe UI", 11), "fg": "#2c3e50"}
    ent_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1}

    # ===== CONTROL များကို နေရာချခြင်း =====
    
    # Row 0: Medicine Name
    lbl_name = tk.Label(form_card, text="Medicine Name:", **lbl_style)
    form_card.create_window(35, 80, window=lbl_name, anchor="w")
    name_entry = tk.Entry(form_card, width=32, **ent_style)
    form_card.create_window(185, 80, window=name_entry, anchor="w")

    # Row 1: Barcode 
    lbl_bar = tk.Label(form_card, text="Barcode Number:", **lbl_style)
    form_card.create_window(35, 130, window=lbl_bar, anchor="w")
    barcode_entry = tk.Entry(form_card, width=32, **ent_style)
    form_card.create_window(185, 130, window=barcode_entry, anchor="w")

    # 🌟 [ဒီဇိုင်းအသစ်] Window အသစ်မဆောက်ဘဲ အောက်ခြေကနေ လှလှပပပေါ်ပြီး အလိုအလျောက် ပျောက်သွားမည့် အသံတိတ် Toast စနစ်
    def show_toast_success(message):
        toast = tk.Toplevel()
        toast.overrideredirect(True) # Window ဘောင်နဲ့ ခလုတ်တွေကို ဖျောက်ခြင်း
        toast.configure(bg="#2ecc71") # စိမ်းစိုပြီး လှပသော Success အရောင်
        
        # စာသား စတိုင်လ်
        lbl = tk.Label(toast, text=f"✓  {message}", font=("Segoe UI", 11, "bold"), fg="white", bg="#2ecc71", padx=20, pady=10)
        lbl.pack()
        
        # Main Window ရဲ့ အောက်ခြေအလယ်တည့်တည့်မှာ တွက်ချက်နေရာချခြင်း
        main.update_idletasks()
        x = main.winfo_rootx() + (main.winfo_width() // 2) - (toast.winfo_reqwidth() // 2)
        y = main.winfo_rooty() + main.winfo_height() - 70 # အောက်ခြေနားလေးတွင် ကပ်ပေါ်စေရန်
        toast.geometry(f"+{x}+{y}")
        
        # ၂ စက္ကန့် (2000ms) ပြည့်လျှင် အလိုအလျောက် ပြန်ပျောက်သွားစေခြင်း
        toast.after(2000, toast.destroy)

    # Webcam Scan Button
    def trigger_webcam_scan():
        import cv2
        from scanner import BarcodeScanner
        scan_btn.config(state="disabled")
        scanner = BarcodeScanner()
        cap = cv2.VideoCapture(0)
        scanned_result = None
        while True:
            ret, frame = cap.read()
            if not ret: break
            result = scanner.scan_from_frame(frame)
            if result:
                # 🔊 "တီ" ဟု အသံတစ်ချက်သာ မြည်စေခြင်း
                import winsound
                winsound.Beep(2000, 150) 
                
                scanned_result = result
                break
            cv2.imshow("Scan Barcode (Press 'q' to Exit)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        cap.release()
        cv2.destroyAllWindows()
        scan_btn.config(state="normal")
        
        if scanned_result:
            barcode_entry.delete(0, tk.END)
            barcode_entry.insert(0, scanned_result)
            # 🌟 Window ကြီးနဲ့ မကွယ်တော့ဘဲ အသံတိတ် Toast လေးပဲ အောက်ခြေမှာ ပေါ်စေခြင်း
            show_toast_success(f"Barcode '{scanned_result}' scanned successfully.")

    scan_btn = tk.Button(form_card, text="🔍 Scan", font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", relief="flat", command=trigger_webcam_scan, cursor="hand2", padx=8)
    form_card.create_window(450, 130, window=scan_btn, anchor="w")

    # # Row 2: Category
    lbl_cat = tk.Label(form_card, text="Category:", **lbl_style)
    form_card.create_window(35, 180, window=lbl_cat, anchor="w")
    
    cat_combo = ttk.Combobox(form_card, font=("Segoe UI", 11), width=30, state="readonly")
    
    # 🌟 [ဒီနေရာလေးကို အစားထိုးပြင်ဆင်တာပါ] 
    # Database ထဲက Category List ကို လှမ်းယူမယ်၊ မရှိသေးရင် အခြေခံဟာလေးတွေ ပြထားမယ်
    db_categories = get_all_categories()
    if not db_categories:
        db_categories = ["⚪️ Tablet", "💊 Capsule", "🧪 Syrup", "💉 Injection", "🧴 Ointment", "📦 Other"]
        
    cat_combo['values'] = db_categories
    
    # ပထမဆုံး Item ကို Default အနေနဲ့ ရွေးထားပေးခြင်း
    if db_categories:
        cat_combo.current(0)
        
    form_card.create_window(185, 180, window=cat_combo, anchor="w")

    # Row 3: Quantity
    lbl_qty = tk.Label(form_card, text="Quantity (Stock):", **lbl_style)
    form_card.create_window(35, 230, window=lbl_qty, anchor="w")
    qty_entry = tk.Entry(form_card, width=32, **ent_style)
    form_card.create_window(185, 230, window=qty_entry, anchor="w")

    # ===== Row 4: Expiry Date =====
    lbl_exp = tk.Label(form_card, text="Expiry Date:", **lbl_style)
    form_card.create_window(35, 280, window=lbl_exp, anchor="w")
    
    exp_entry = DateEntry(
        form_card, 
        width=30,                     
        font=("Segoe UI", 11), 
        background='#2c3e50',         
        foreground='white',           
        headersbackground='#34495e',
        date_pattern='yyyy-mm-dd'     
    )
    form_card.create_window(185, 280, window=exp_entry, anchor="w")

    # --------- SAVE TO DATABASE FUNCTION ---------
    def save_medicine():
        name = name_entry.get().strip()
        barcode = barcode_entry.get().strip()
        category = cat_combo.get()
        qty = qty_entry.get().strip()
        expiry = exp_entry.get().strip() 

        if not name or not barcode or not qty or not expiry:
            messagebox.showwarning("Warning", "Please fill all required fields!")
            return

        if not qty.isdigit():
            messagebox.showwarning("Invalid Quantity", "Quantity must be a valid positive number!")
            return
            
        qty_int = int(qty)
        if qty_int <= 0:
            messagebox.showwarning("Invalid Quantity", "Quantity must be greater than 0!")
            return

        try:
            conn = db()
            c = conn.cursor()
            c.execute(
                "INSERT INTO medicines (name, barcode, category, qty, expiry) VALUES (?, ?, ?, ?, ?)",
                (name, barcode, category, qty_int, expiry)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"'{name}' added successfully to inventory!")
            
            from medicine_list import list_page   
            list_page(main, focus_barcode=barcode) 
            return 

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine. Barcode might be duplicate!\n({e})")

    # Row 5: Add Button
    add_btn = tk.Button(
        form_card, 
        text="➕ Add Medicine", 
        font=("Segoe UI", 11, "bold"), 
        bg="#2e7d32", 
        fg="white", 
        relief="flat",
        command=save_medicine,
        cursor="hand2",
        padx=25,
        pady=5
    )
    form_card.create_window(270, 340, window=add_btn, anchor="center")