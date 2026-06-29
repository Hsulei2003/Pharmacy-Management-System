from database import db
from logic import get_status
import tkinter as tk
from tkinter import ttk, messagebox
from utils import clear
from datetime import datetime

def dashboard(main):
    clear(main)
    main.config(bg="#f8f9fa")

    # ခေါင်းစဉ်
    tk.Label(main, text="Pharmacy Dashboard (Batch System)", font=("Segoe UI", 24, "bold"), fg="#2c3e50", bg="#f8f9fa").pack(pady=15)

    # ===== TOP PANEL (STATUS COUNTERS) =====
    frame = tk.Frame(main, bg="#f8f9fa")
    frame.pack(pady=10)

    total_label = tk.Label(frame, text="Total Medicines\n0", bg="#34495e", fg="white", font=("Segoe UI", 12, "bold"), width=18, height=3, relief="flat")
    total_label.pack(side="left", padx=15)

    near_label = tk.Label(frame, text="Near Expiry\n0", bg="#d35400", fg="white", font=("Segoe UI", 12, "bold"), width=18, height=3, relief="flat")
    near_label.pack(side="left", padx=15)

    expired_label = tk.Label(frame, text="Expired\n0", bg="#e74c3c", fg="white", font=("Segoe UI", 12, "bold"), width=18, height=3, relief="flat")
    expired_label.pack(side="left", padx=15)

    # ===== MEDICINE CARDS PANELS (MAIN CONTAINER) =====
    panel_frame = tk.Frame(main, bg="#f8f9fa")
    panel_frame.pack(pady=15, fill="both", expand=True, padx=20)

    # 1. Expired Card Container (ဘယ်ဘက်ခြမ်း)
    exp_outer = tk.LabelFrame(panel_frame, text=" Expired Medicines ", font=("Segoe UI", 11, "bold"), fg="#c0392b", bg="white", relief="solid", bd=1)
    exp_outer.pack(side="left", fill="both", expand=True, padx=15)
    
    exp_canvas = tk.Canvas(exp_outer, width=320, height=200, bg="white", highlightthickness=0)
    exp_scroll = ttk.Scrollbar(exp_outer, orient="vertical", command=exp_canvas.yview)
    exp_scroll_frame = tk.Frame(exp_canvas, bg="white")
    
    exp_scroll_frame.bind("<Configure>", lambda e: exp_canvas.configure(scrollregion=exp_canvas.bbox("all")))
    exp_canvas.create_window((0, 0), window=exp_scroll_frame, anchor="nw", width=340)
    exp_canvas.configure(yscrollcommand=exp_scroll.set)
    
    exp_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    exp_scroll.pack(side="right", fill="y")

    # 2. Near Expiry Card Container (ညာဘက်ခြမ်း)
    near_outer = tk.LabelFrame(panel_frame, text=" Near Expiry Medicines (Within 7 Days) ", font=("Segoe UI", 11, "bold"), fg="#d35400", bg="white", relief="solid", bd=1)
    near_outer.pack(side="left", fill="both", expand=True, padx=15)
    
    near_canvas = tk.Canvas(near_outer, width=320, height=200, bg="white", highlightthickness=0)
    near_scroll = ttk.Scrollbar(near_outer, orient="vertical", command=near_canvas.yview)
    near_scroll_frame = tk.Frame(near_canvas, bg="white")
    
    near_scroll_frame.bind("<Configure>", lambda e: near_canvas.configure(scrollregion=near_canvas.bbox("all")))
    near_canvas.create_window((0, 0), window=near_scroll_frame, anchor="nw", width=340)
    near_canvas.configure(yscrollcommand=near_scroll.set)
    
    near_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    near_scroll.pack(side="right", fill="y")

    panel_frame.grid_columnconfigure(0, weight=1)
    panel_frame.grid_columnconfigure(1, weight=1)
    panel_frame.grid_rowconfigure(0, weight=1)

    # ===== QUICK SCAN SECTION =====
    scan_frame = tk.LabelFrame(main, text=" ⚡️ Quick Check Medicine ", font=("Segoe UI", 11, "bold"), fg="#2c3e50", bg="white", relief="solid", bd=1, padx=15, pady=10)
    scan_frame.pack(pady=15, fill="x", padx=35)

    tk.Label(scan_frame, text="Barcode:", font=("Segoe UI", 11), bg="white", fg="#34495e").pack(side="left", padx=5)

    scan_entry = tk.Entry(scan_frame, font=("Segoe UI", 11), width=25, relief="solid", bd=1)
    scan_entry.pack(side="left", padx=5, ipady=3)
    scan_entry.focus()

    # Quick Scan ရလဒ်ပြသမည့် Container Frame
    result_container = tk.Frame(scan_frame, bg="white")
    result_container.pack(side="right", padx=15, fill="x", expand=True)
    # အမှားခြစ် ❌ တစ်ခုတည်း သီးသန့်ကြီးပြရန် Label
    error_icon_label = tk.Label(result_container, text="", font=("Segoe UI", 20), fg="#c0392b", bg="white")
    error_icon_label.pack(side="left", padx=(0, 5))

    result_text = tk.Label(result_container, text="Scan a barcode to quick check status...", font=("Segoe UI", 10, "italic"), fg="gray", bg="white")
    result_text.pack(side="left", padx=5)

    # Status Badge အတွက် သီးသန့် Label 
    status_badge = tk.Label(result_container, text="", font=("Segoe UI", 10, "bold"), padx=8, pady=2, bg="white")
    status_badge.pack(side="left", padx=5)

    # --- 🛠️ ရှာဖွေစစ်ဆေးသည့် Batch Logic ပြင်ဆင်ချက် ---
    def scan(event=None, scanned_code=None):
        code = scanned_code if scanned_code else scan_entry.get().strip()
        
        error_icon_label.config(text="") 
        
        if not code:
            result_text.config(text="⚠️ Please enter or scan a barcode!", fg="#e67e22", font=("Segoe UI", 10, "bold"))
            status_badge.config(text="", bg="white")
            return

        try:
            conn = db()
            c = conn.cursor()
            # 🌟 Batch စနစ်အတွက် ဆေးရဲ့ စုစုပေါင်းအရေအတွက် (SUM) နဲ့ အစောဆုံးသက်တမ်းကုန်မယ့်ရက် (MIN) ကို တွက်ချက်ခြင်း
            c.execute("""
                SELECT m.name, m.barcode, m.category, SUM(b.qty), MIN(b.expiry) 
                FROM medicines m
                LEFT JOIN medicine_batches b ON m.id = b.medicine_id
                WHERE m.barcode = ?
                GROUP BY m.id
            """, (code,))
            data = c.fetchone()
            conn.close()

            if data and data[0] is not None:
                name, barcode, category, qty, expiry = data
                
                # အကယ်၍ အဝင် Batch လုံးဝမရှိသေးပါက အရေအတွက်ကို 0 ပေးပြီး သက်တမ်းကို No Date ဟု သတ်မှတ်မည်
                qty = qty if qty is  not None else 0
                expiry = expiry if expiry else "No Batch"
                
                status = get_status(expiry) if expiry != "No Batch" else "Normal"
                if qty == 0: status = "No Stock"

                display_name = name
                if len(display_name) > 12:
                    display_name = display_name[:10] + ".."

                
                result_text.config(
                    text=f"💊 {display_name}  |  Total Stock: {qty}  |  Nearest Expiry: {expiry}  |  Status: ", 
                    font=("Segoe UI", 11, "bold"),
                    fg="#2c3e50"
                )
                
                if status == "Expired":
                    status_badge.config(text=" Expired ", font=("Segoe UI", 10, "bold"), fg="#c0392b", bg="#fce4e4")
                elif status == "Near Expiry":
                    status_badge.config(text=" Near Expiry ", font=("Segoe UI", 10, "bold"), fg="#d35400", bg="#fef5e7")
                elif status == "No Stock":
                    status_badge.config(text=" Out of Stock ", font=("Segoe UI", 10, "bold"), fg="#7f8c8d", bg="#eaeded")
                else:
                    status_badge.config(text=" Normal ", font=("Segoe UI", 10, "bold"), fg="#1e7e34", bg="#d4edda")
            else:
                result_text.config(text="Medicine Not Found!", font=("Segoe UI", 11, "bold"), fg="#c0392b")
                error_icon_label.config(text="❌") 
                status_badge.config(text="", bg="white") 
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check medicine:\n{e}")

    scan_entry.bind("<Return>", scan)

    # --- Webcam ဖြင့် Quick Scan ဖတ်ရန် စနစ် ---
    def trigger_quick_scan():
        import cv2
        from scanner import BarcodeScanner
        
        quick_scan_btn.config(state="disabled")
        result_text.config(text="📷 Webcam Opening...", fg="#3498db")
        status_badge.config(text="", bg="white")
        
        scanner = BarcodeScanner()
        cap = cv2.VideoCapture(0)
        scanned_code = None

        window_name = "Quick Check Barcode (Press 'q' to Exit)"
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1) 
            res = scanner.scan_from_frame(frame)
            if res:
                import winsound
                winsound.Beep(2000, 150)
                scanned_code = res
                break
                
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except:
                break
                
        cap.release()
        cv2.destroyAllWindows()
        quick_scan_btn.config(state="normal")

        if scanned_code:
            scan_entry.delete(0, tk.END)
            scan_entry.insert(0, scanned_code)
            scan(scanned_code=scanned_code)
        else:
            result_text.config(text="⚠️ Scan cancelled.", fg="#e67e22", font=("Segoe UI", 10, "italic"))

    quick_scan_btn = tk.Button(
        scan_frame, 
        text="🔍 Scan", 
        font=("Segoe UI", 10, "bold"), 
        bg="#2ecc71", 
        fg="white", 
        relief="flat", 
        command=trigger_quick_scan,
        padx=12
    )
    quick_scan_btn.pack(side="left", padx=5)

    # ===== 🛠️ AUTO BACKGROUND SCAN & BATCH UI CARD GENERATOR =====
    def auto_scan():
        if not exp_scroll_frame.winfo_exists() or not near_scroll_frame.winfo_exists():
            return 
        try:
            conn = db()
            c = conn.cursor()
            
            # ၁။ စုစုပေါင်း ဆေးအမျိုးအစား အရေအတွက်ကို ရေတွက်ခြင်း
            c.execute("SELECT COUNT(*) FROM medicines")
            total = c.fetchone()[0] or 0
            
            # ၂။ Batch အားလုံးကို JOIN လုပ်ပြီး ဒေတာဆွဲထုတ်ခြင်း (စတော့ရှိတာတွေကိုပဲ စစ်ပါမယ်)
            c.execute("""
                SELECT m.name, m.barcode, b.batch_number, b.qty, b.expiry 
                FROM medicine_batches b
                JOIN medicines m ON b.medicine_id = m.id
                WHERE b.qty > 0
            """)
            batches = c.fetchall()
            conn.close()

            near = 0
            expired = 0

            # ဇယားဟောင်းများ ရှင်းထုတ်ခြင်း
            for widget in exp_scroll_frame.winfo_children():
                widget.destroy()
            for widget in near_scroll_frame.winfo_children():
                widget.destroy()

            today = datetime.today()
            for batch in batches:
                name, barcode, batch_no, qty, expiry = batch
                status = get_status(expiry)

                try:
                    exp_date = datetime.strptime(expiry, "%Y-%m-%d")
                except:
                    try:
                        exp_date = datetime.strptime(expiry, "%d/%m/%y")
                    except:
                        continue

                days = (exp_date - today).days + 1

                # (က) သက်တမ်းကုန်သွားသော ကတ်များ ထုတ်ပေးခြင်း
                if status == "Expired":
                    expired += 1
                    card = tk.Frame(exp_scroll_frame, bg="white", highlightbackground="#f5c6cb", highlightthickness=1, bd=0)
                    card.pack(fill="x", pady=6, padx=5, ipady=4)
                    
                    info_frame = tk.Frame(card, bg="white")
                    info_frame.pack(fill="x", padx=10, pady=5)
                    
                    tk.Label(info_frame, text=f"💊 {name}", font=("Segoe UI", 11, "bold"), fg="#2c3e50", bg="white").pack(side="left")
                    tk.Label(info_frame, text=" Expired ", font=("Segoe UI", 9, "bold"), fg="#c0392b", bg="#fce4e4", padx=6, pady=2).pack(side="right")

                    # Batch Number နှင့် အရေအတွက်ပါ တွဲပြပေးခြင်း
                    tk.Label(card, text=f"Barcode: {barcode}  |  Batch: {batch_no}  |  Qty: {qty}", font=("Segoe UI", 9), fg="#7f8c8d", bg="white", anchor="w").pack(fill="x", padx=10, pady=(0,5))

                # (ခ) သက်တမ်းကုန်ခါနီး ကတ်များ ထုတ်ပေးခြင်း
                elif status == "Near Expiry":
                    near += 1
                    card = tk.Frame(near_scroll_frame, bg="white", highlightbackground="#fed7a5", highlightthickness=1, bd=0)
                    card.pack(fill="x", pady=6, padx=5, ipady=4)
                    
                    info_frame = tk.Frame(card, bg="white")
                    info_frame.pack(fill="x", padx=10, pady=5)
                    
                    tk.Label(info_frame, text=f"⚠️ {name}", font=("Segoe UI", 11, "bold"), fg="#2c3e50", bg="white").pack(side="left")
                    tk.Label(info_frame, text=f" {days} days left ", font=("Segoe UI", 9, "bold"), fg="#d35400", bg="#fef5e7", padx=6, pady=2).pack(side="right")
                    
                    # Batch Number နှင့် အရေအတွက်ပါ တွဲပြပေးခြင်း
                    tk.Label(card, text=f"Barcode: {barcode}  |  Batch: {batch_no}  |  Qty: {qty}", font=("Segoe UI", 9), fg="#7f8c8d", bg="white", anchor="w").pack(fill="x", padx=10, pady=(0,5))

            if expired == 0:
                tk.Label(exp_scroll_frame, text="No expired medicine", font=("Segoe UI", 10, "italic"), fg="gray", bg="white").pack(pady=20)
            if near == 0:
                tk.Label(near_scroll_frame, text="No near expiry medicine", font=("Segoe UI", 10, "italic"), fg="gray", bg="white").pack(pady=20)

            # UI Status Counters များကို ကွက်တိ Update လုပ်ပေးခြင်း
            total_label.config(text=f"Total Medicines\n{total}")
            near_label.config(text=f"Near Expiry\n{near}")
            expired_label.config(text=f"Expired\n{expired}")

        except Exception as e:
            pass

        try:
            if exp_scroll_frame.winfo_exists() and near_scroll_frame.winfo_exists():
                main.after(30000, auto_scan)
        except:
            pass

    auto_scan()