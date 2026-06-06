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
        text="Scan & Sell Medicines", 
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

   # Row 2: Result Area (Grid စနစ်သုံးပြီး အလယ်တည့်တည့် ရောက်အောင် ညှိခြင်း)
    # =================================================================
    result_frame = tk.Frame(sell_card, bg="#f8f9fa", relief="solid", bd=1)
    sell_card.create_window(270, 210, window=result_frame, anchor="center", width=470, height=60)

    # 🌟 Frame တစ်ခုလုံးရဲ့ အလယ်မှာ ပေါ်စေဖို Grid Row/Column ကို Weight ပေးခြင်း
    result_frame.grid_columnconfigure(0, weight=1)
    result_frame.grid_columnconfigure(3, weight=1)
    result_frame.grid_rowconfigure(0, weight=1)

    # ၁။ ရှေ့က Icon ပြမည့် Label (font size ကို အချိုးကျအောင် ၁၄ လောက်ပဲ ထားပါမယ်)
    icon_label = tk.Label(
        result_frame, 
        text="🔍", 
        font=("Segoe UI", 14), 
        fg="#7f8c8d", 
        bg="#f8f9fa"
    )
    icon_label.grid(row=0, column=1, padx=(0, 8), sticky="nsew") 

    # ၂။ စာသားသီးသန့်ပြမည့် Label (anchor="center" ပြောင်းပြီး အလယ်ပိုလိုက်ပါတယ်)
    result = tk.Label(
        result_frame, 
        text="Please scan a medicine barcode...", 
        font=("Segoe UI", 11, "italic"), 
        fg="#7f8c8d", 
        bg="#f8f9fa",
        anchor="center" # 👈 ဘယ်ဘက်မကပ်တော့ဘဲ အလယ်မှာပဲ နေခိုင်းခြင်း
    )
    result.grid(row=0, column=2, padx=(0, 0), sticky="nsew")

    # Barcode သိမ်းရန် string ဆောက်ထားမည်
    scanned_barcode = tk.StringVar()

    # =================================================================
    # --- Scan စစ်ဆေးသည့် Logic (Database မှ ဒေတာဆွဲထုတ်ခြင်း) ---
    # =================================================================
    def check_barcode_data(code):
        if not code:
            return

        try:
            conn = db()
            c = conn.cursor()
            c.execute("SELECT name, barcode, qty, expiry FROM medicines WHERE barcode=?", (code,))
            data = c.fetchone()
            conn.close()
            
            if data:
                name, barcode, qty, expiry = data
                status = get_status(expiry)
                
                scanned_barcode.set(barcode)
                if qty <= 0:
                    text_color = "#e74c3c"       
                elif status == "Normal":
                    text_color = "#27ae60"       
                elif status == "Near Expiry":
                    text_color = "#e67e22"       
                else:
                    text_color = "#c0392b"       

                icon_label.config(text="💊", font=("Segoe UI", 11), fg=text_color)
                result.config(
                    text=f"{name}  |  Stock: {qty}  |  {status}",
                    font=("Segoe UI", 13, "bold"),
                    fg=text_color
                )

              # 🌟 [Expired သိုမဟုတ် Out of Stock ဖြစ်လျှင် မြည်မည့်အသံ]
                if status == "Expired" or qty <= 0:
                    import time
                    import threading
                    from pygame import mixer

                    def play_perfect_beeps():
                        mixer.init()
                        sound = mixer.Sound("warning.mp3") 
                        sound.play()
                    threading.Thread(target=play_perfect_beeps, daemon=True).start()

                    sell_btn.config(state="disabled", bg="#95a5a6")
                    if qty <= 0:
                        icon_label.config(text="❌", font=("Segoe UI", 20), fg="#c0392b")
                        result.config(text=f"{name} is Out of Stock!", font=("Segoe UI", 11, "bold"), fg="#c0392b", anchor="center")
                else:
                    sell_btn.config(state="normal", bg="#e74c3c") 
            else:
                scanned_barcode.set("")
                
                # 🌟 [ဆေးဝါးရှာမတွေ့ပါက မြည်မည့်အသံ]
                import threading
                from pygame import mixer

                def play_not_found_beeps():
                    mixer.init()
                    sound = mixer.Sound("error.mp3")
                    sound.play() 
                threading.Thread(target=play_not_found_beeps, daemon=True).start()
                
                icon_label.config(text="❌", font=("Segoe UI", 20), fg="#c0392b")
                result.config(text=" Medicine Not Found!", font=("Segoe UI", 11, "bold"), fg="#c0392b", anchor="center")
                sell_btn.config(state="disabled", bg="#95a5a6")
        except Exception as e:
            messagebox.showerror("Scan Error", f"Something went wrong while scanning:\n{e}")

    # Text Box ထဲ စာရိုက်ပြီး Enter ခေါက်လျှင် ချက်ချင်းစစ်ဆေးပေးမည့် စနစ်
    scan_entry.bind("<Return>", lambda e: check_barcode_data(scan_entry.get().strip()))

    # --- Webcam ဖွင့်ပြီး စကင်ဖတ်မည့် အစိတ်အပိုင်းသစ် ---
    def trigger_scan():
        import cv2
        from scanner import BarcodeScanner
        
        scan_btn.config(state="disabled")
        result.config(text="📷 Webcam Opening... Please wait.", fg="#3498db")
        scanner = BarcodeScanner()
        cap = cv2.VideoCapture(0)
        scanned_code = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1) 
            res = scanner.scan_from_frame(frame)
            if res:
                scanned_code = res
                break
                
            cv2.imshow("Scan Medicine Barcode (Press 'q' to Exit)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
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

    # --- အရောင်းသိမ်းဆည်းပြီး Stock လျှော့ချမည့် Logic ---
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
            conn = db()
            c = conn.cursor()
            c.execute("SELECT name, qty FROM medicines WHERE barcode=?", (code_to_sell,))
            row = c.fetchone()
            
            if not row:
                icon_label.config(text="❌", font=("Segoe UI", 24), fg="#c0392b")
                result.config(text="Medicine no longer exists!", font=("Segoe UI", 11, "bold"), fg="#c0392b")
                conn.close()
                sell_btn.config(state="disabled", bg="#95a5a6")
                return
            
            name, available_qty = row

            if available_qty >= sell_qty:
                new_qty = available_qty - sell_qty
                
                c.execute("UPDATE medicines SET qty=? WHERE barcode=?", (new_qty, code_to_sell))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", f"Successfully sold {sell_qty} {name}!\nRemaining Stock: {new_qty}")
                
                scan_entry.delete(0, tk.END)
                qty_entry.delete(0, tk.END)
                qty_entry.insert(0, "1")
                scanned_barcode.set("")
                
                icon_label.config(text="🔍", font=("Segoe UI", 11), fg="#7f8c8d")
                result.config(text="Transaction complete. Waiting for next scan...", font=("Segoe UI", 11, "italic"), fg="#7f8c8d")
                sell_btn.config(state="disabled", bg="#95a5a6")
            else:
                icon_label.config(text="❌", font=("Segoe UI", 20), fg="#c0392b")
                result.config(text=f"Not enough stock! Only {available_qty} items left.", font=("Segoe UI", 11, "bold"), fg="#c0392b")
                conn.close()
                
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
    sell_card.create_width = 395
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