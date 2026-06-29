import tkinter as tk
from database import db
from tkinter import ttk, messagebox
from logic import get_status
from utils import clear

# ---------- SCAN + SELL ----------
def scan_page(main):
    clear(main)
    main.config(bg="#f8f9fa")

    # ခေါင်းစဉ်
    tk.Label(
        main, 
        text="Scan & Sell Medicines (Batch System)", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=15)

    # ===== ၁။ CANVAS ဖြင့် ထောင့်ကွေး PANEL ဆောက်ခြင်း =====
    card_width = 540
    card_height = 360  

    sell_card = tk.Canvas(main, width=card_width, height=card_height, bg="#f8f9fa", highlightthickness=0)
    sell_card.pack(pady=10)

    # ထောင့်ကွေးစတုဂံဆွဲသည့် Function
    def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    # ကတ်ပြားနောက်ခံအဖြူရောင်ကို ထောင့်ကွေး (Radius=20) ဖြင့် ဆွဲခြင်း
    draw_rounded_rect(sell_card, 5, 5, card_width-5, card_height-5, radius=20, fill="white", outline="#e0e0e0", width=1)

    # Panel ခေါင်းစဉ်စာသား
    sell_card.create_text(35, 30, text="Transaction Panel", font=("Segoe UI", 12, "bold"), fill="#34495e", anchor="w")

    # Styles
    lbl_style = {"bg": "white", "font": ("Segoe UI", 11), "fg": "#34495e"}
    ent_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1}

    # ===== ၂။ CONTROL များကို CANVAS ပေါ်တွင် နေရာချခြင်း =====
    
    # Row 0: Barcode Input
    lbl_scan = tk.Label(sell_card, text="Scan Barcode", **lbl_style)
    sell_card.create_window(35, 80, window=lbl_scan, anchor="w")
    
    scan_entry = tk.Entry(sell_card, width=25, **ent_style)
    sell_card.create_window(175, 80, window=scan_entry, anchor="w")
    scan_entry.focus()

    # Row 1: Quantity Input
    lbl_qty = tk.Label(sell_card, text="Quantity to Sell", **lbl_style)
    sell_card.create_window(35, 130, window=lbl_qty, anchor="w")
    
    qty_entry = tk.Entry(sell_card, width=25, **ent_style)
    qty_entry.insert(0, "1")
    sell_card.create_window(175, 130, window=qty_entry, anchor="w")

    # Row 2: Result Area
    result_frame = tk.Frame(sell_card, bg="#f8f9fa", relief="solid", bd=1)
    sell_card.create_window(270, 210, window=result_frame, anchor="center", width=470, height=60)

    result_frame.grid_columnconfigure(0, weight=1)
    result_frame.grid_columnconfigure(3, weight=1)
    result_frame.grid_rowconfigure(0, weight=1)

    icon_label = tk.Label(result_frame, text="🔍", font=("Segoe UI", 13), fg="#7f8c8d", bg="#f8f9fa", anchor="center")
    icon_label.grid(row=0, column=1, padx=(0, 8), sticky="nsew") 

    result = tk.Label(
        result_frame, 
        text="Please scan a medicine barcode...", 
        font=("Segoe UI", 11, "italic"), 
        fg="#7f8c8d", 
        bg="#f8f9fa",
        anchor="w",
        justify= "left"
    )
    result.grid(row=0, column=2, padx=(0, 0), sticky="nsew")

    # Barcode သိမ်းရန် string ဆောက်ထားမည်
    scanned_barcode = tk.StringVar()

    # =================================================================
    # --- 🛠 Scan စစ်ဆေးသည့် Logic (စတော့ပြတ်/သက်တမ်းကုန် သတ်သတ်စီပြသခြင်း) ---
    # =================================================================
    def check_barcode_data(code):
        if not code:
            return

        try:
            import datetime
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            
            conn = db()
            c = conn.cursor()
            
            # ၁။ ဆေးအချက်အလက် ရှိမရှိ အရင်ရှာခြင်း
            c.execute("SELECT id, name, barcode FROM medicines WHERE barcode=?", (code,))
            med_info = c.fetchone()
            
            if not med_info:
                scanned_barcode.set("")
                
                # 🌟 ဤနေရာတွင် ဆေးဝါးရှာမတွေ့ပါက သတိပေးသံမြည်အောင် ကုဒ်ထည့်သွင်းခြင်း
                import threading
                from pygame import mixer
                def play_warning():
                    try:
                        mixer.init()
                        sound = mixer.Sound("error.mp3") # 👈 မိတ်ဆွေသုံးထားတဲ့ အသံဖိုင်နာမည်ထည့်ရန်
                        sound.play()
                    except: pass
                threading.Thread(target=play_warning, daemon=True).start()

                icon_label.config(text="❌", font=("Segoe UI", 20), fg="#c0392b")
                result.config(text=" Medicine Not Found!", font=("Segoe UI", 11, "bold"), fg="#c0392b", anchor="center")
                sell_btn.config(state="disabled", bg="#95a5a6")
                conn.close()
                return

            med_id, name, barcode = med_info
            scanned_barcode.set(barcode)

            # ၂။ ရှိသမျှ Batch အားလုံး၏ စတော့စုစုပေါင်းကို တွက်ခြင်း
            c.execute("SELECT SUM(qty) FROM medicine_batches WHERE medicine_id = ?", (med_id,))
            total_stock_row = c.fetchone()
            total_stock = total_stock_row[0] if total_stock_row and total_stock_row[0] is not None else 0

            # ၃။ သက်တမ်းမကုန်သေးဘဲ စတော့ကျန်ရှိသော Active အနီးစပ်ဆုံးရက်ကို တွက်ခြင်း
            c.execute("""
                SELECT MIN(expiry) FROM medicine_batches 
                WHERE medicine_id = ? AND qty > 0 AND expiry >= ?
            """, (med_id, current_date))
            active_expiry_row = c.fetchone()
            active_expiry = active_expiry_row[0] if active_expiry_row and active_expiry_row[0] is not None else None

            # UI ပေါ်တွင် ရလဒ် ထုတ်ပြခြင်း
            if active_expiry:
                status = get_status(active_expiry) 
                text_color = "#27ae60" if status == "Normal" else "#e67e22"       

                icon_label.config(text=" ", font=("Segoe UI", 13), fg=text_color)
                
                # display_name = name
                # if len(display_name) > 18:
                #     display_name = display_name[:15] + "..."
                    
                result.config(
                    text=f"{name}  |  Available Stock: {total_stock}  |\n  Nearest Exp: {active_expiry}",
                    font=("Segoe UI", 12, "bold"),
                    fg=text_color,
                    justify="center"
                )
                sell_btn.config(state="normal", bg="#e74c3c") # အရောင်းခလုတ်ဖွင့်မည်
                
            else:
                # Active Stock မရှိပါက (စတော့ပြတ်တာလား သိုမဟုတ် သက်တမ်းကုန်တာလား သပ်သတ်စီ ခွဲပြမည်)
                import threading
                from pygame import mixer
                def play_warning():
                    try:
                        mixer.init()
                        sound = mixer.Sound("warning_short.mp3") 
                        sound.play()
                    except: pass
                threading.Thread(target=play_warning, daemon=True).start()

                icon_label.config(text="❌", font=("Segoe UI", 20), fg="#c0392b")
                
                if total_stock <= 0:
                    error_msg = f"{name} is Out of Stock!"
                else:
                    error_msg = f"{name} is Expired!"

                result.config(text=error_msg, font=("Segoe UI", 11, "bold"), fg="#c0392b", justify="center")
                sell_btn.config(state="disabled", bg="#95a5a6") 

            conn.close()
                
        except Exception as e:
            messagebox.showerror("Scan Error", f"Something went wrong while scanning:\n{e}")

    # Text Box ထဲ စာရိုက်ပြီး Enter ခေါက်လျှင် စစ်ဆေးပေးမည့် စနစ်
    scan_entry.bind("<Return>", lambda e: check_barcode_data(scan_entry.get().strip()))

    # --- Webcam ဖွင့်ပြီး စကင်ဖတ်မည့် အစိတ်အပိုင်း ---
    def trigger_scan():
        import cv2
        from scanner import BarcodeScanner
        
        scan_btn.config(state="disabled")
        result.config(text="📷 Webcam Opening... Please wait.", fg="#3498db")
        scanner = BarcodeScanner()
        cap = cv2.VideoCapture(0)
        scanned_code = None
        window_name = "Quick Check Barcode (Press 'q' to Exit)"
        while True:
            ret, frame = cap.read()
            if not ret: break
                
            frame = cv2.flip(frame, 1) 
            res = scanner.scan_from_frame(frame)
            if res:
                scanned_code = res
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

        if scanned_code:
            scan_entry.delete(0, tk.END)
            scan_entry.insert(0, scanned_code)
            check_barcode_data(scanned_code)
        else:
            icon_label.config(text="❌", font=("Segoe UI", 24), fg="#e67e22")
            result.config(text="Scan cancelled or no barcode detected.", font=("Segoe UI", 11, "bold"), fg="#e67e22")

    # =================================================================
    # --- 🛠 အရောင်းသိမ်းဆည်းပြီး FIFO စနစ်ဖြင့် စတော့လျှော့ချမည့် Logic ---
    # =================================================================
    def sell():
        code_to_sell = scanned_barcode.get()
        if not code_to_sell:
            icon_label.config(text="❌", font=("Segoe UI", 24), fg="#e67e22")
            result.config(text="Please scan a medicine first!", font=("Segoe UI", 11, "bold"), fg="#e67e22")
            return
            
        qty_input = qty_entry.get().strip()
        if not qty_input.isdigit():
            icon_label.config(text="❌", font=("Segoe UI", 24), fg="#c0392b")
            result.config(text="Invalid quantity! Numbers only.", font=("Segoe UI", 11, "bold"), fg="#c0392b")
            return
            
        sell_qty = int(qty_input)
        if sell_qty <= 0:
            icon_label.config(text="❌", font=("Segoe UI", 24), fg="#c0392b")
            result.config(text="Quantity must be greater than 0!", font=("Segoe UI", 11, "bold"), fg="#c0392b")
            return

        try:
            import datetime
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            
            conn = db()
            c = conn.cursor()
            
            # ၁။ ဆေး၏ သက်တမ်းမကုန်သေးသော (Active) စတော့ကျန်ရှိမှုကို စစ်ဆေးခြင်း
            c.execute("""
                SELECT m.id, m.name, SUM(b.qty) 
                FROM medicines m
                JOIN medicine_batches b ON m.id = b.medicine_id
                WHERE m.barcode = ? AND b.qty > 0 AND b.expiry >= ?
                GROUP BY m.id
            """, (code_to_sell, current_date))
            row = c.fetchone()
            
            if not row:
                icon_label.config(text="❌", font=("Segoe UI", 24), fg="#c0392b")
                result.config(text="No active stock available to sell!", font=("Segoe UI", 11, "bold"), fg="#c0392b")
                conn.close()
                return
            
            med_id, name, total_available = row

            if total_available < sell_qty:
                icon_label.config(text="❌", font=("Segoe UI", 20), fg="#c0392b")
                result.config(text=f"Not enough active stock! Only {total_available} items left.", font=("Segoe UI", 11, "bold"), fg="#c0392b")
                conn.close()
                return

            # ၂။ 🌟 FIFO (First Expired, First Out) အရောင်းစနစ် - သက်တမ်းမကုန်သေးသော ဘတ်ချ်များကိုသာ နှုတ်မည်
            c.execute("""
                SELECT qty, batch_number FROM medicine_batches 
                WHERE medicine_id = ? AND qty > 0 AND expiry >= ?
                ORDER BY expiry ASC
            """, (med_id, current_date))
            batches = c.fetchall()
            remaining_to_sell = sell_qty
            
            for batch in batches:
                batch_qty, batch_no = batch
                if remaining_to_sell <= 0: break
                
                if batch_qty >= remaining_to_sell:
                    new_batch_qty = batch_qty - remaining_to_sell
                    c.execute("""
                        UPDATE medicine_batches 
                        SET qty = ? 
                        WHERE medicine_id = ? AND batch_number = ?
                    """, (new_batch_qty, med_id, batch_no))
                    remaining_to_sell = 0
                else:
                    remaining_to_sell -= batch_qty
                    c.execute("""
                        UPDATE medicine_batches 
                        SET qty = 0 
                        WHERE medicine_id = ? AND batch_number = ?
                    """, (med_id, batch_no))

            conn.commit()
            conn.close()
            
            # အောင်မြင်ကြောင်း ပြသခြင်း
            messagebox.showinfo("Success", f"Successfully sold {sell_qty} {name}!\nStock deducted from oldest active batch.")
            
            # UI ပြန်လည်ရှင်းလင်းခြင်း
            scan_entry.delete(0, tk.END)
            qty_entry.delete(0, tk.END)
            qty_entry.insert(0, "1")
            scanned_barcode.set("")
            
            icon_label.config(text="🔍", font=("Segoe UI", 11), fg="#7f8c8d")
            result.config(text="Transaction complete. Waiting for next scan...", font=("Segoe UI", 11, "italic"), fg="#7f8c8d")
            sell_btn.config(state="disabled", bg="#95a5a6")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update stock in database:\n{e}")

    # Scan Button ကို နေရာချခြင်း
    scan_btn = tk.Button(
        sell_card, 
        text="🔍 Scan", 
        font=("Segoe UI", 10, "bold"), 
        bg="#2ecc71", 
        fg="white", 
        relief="flat", 
        command=trigger_scan, 
        cursor="hand2",
        padx=12
    )
    sell_card.create_window(395, 80, window=scan_btn, anchor="w")
    
    # Sell Button ကို နေရာချခြင်း
    sell_btn = tk.Button(
        sell_card, 
        text="🛍 Sell Now", 
        font=("Segoe UI", 11, "bold"), 
        bg="#95a5a6", 
        fg="white", 
        relief="flat", 
        state="disabled",
        cursor="hand2",
        command=sell, 
        padx=35,
        pady=5
    )
    sell_card.create_window(270, 310, window=sell_btn, anchor="center")