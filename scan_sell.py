import tkinter as tk
from database import db, log_action
from authentication.session import get_current_user
from tkinter import ttk, messagebox
from logic import get_status
from utils import clear
from receipt import show_receipt

# ---------- SCAN + SELL (POS VERSION) ----------
def scan_page(main):
    clear(main)
    main.config(bg="#f8f9fa")

    tk.Label(
        main, 
        text="🛍 Point of Sale (POS) & Billing System", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=15)

    card_width = 540
    card_height = 630  # Cart ဆံ့အောင် Panel ကို အောက်သို ချဲ့ထားသည်

    sell_card = tk.Canvas(main, width=card_width, height=card_height, bg="#f8f9fa", highlightthickness=0)
    sell_card.pack(pady=5)

    def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    draw_rounded_rect(sell_card, 5, 5, card_width-5, card_height-5, radius=20, fill="white", outline="#e0e0e0", width=1)
    sell_card.create_text(35, 30, text="POS Cashier Panel", font=("Segoe UI", 12, "bold"), fill="#34495e", anchor="w")

    lbl_style = {"bg": "white", "font": ("Segoe UI", 11), "fg": "#34495e"}
    ent_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1}
    
    # Row 0: Barcode Input
    lbl_scan = tk.Label(sell_card, text="Scan Barcode", **lbl_style)
    sell_card.create_window(35, 75, window=lbl_scan, anchor="w")
    scan_entry = tk.Entry(sell_card, width=23, **ent_style)
    sell_card.create_window(165, 75, window=scan_entry, anchor="w")
    scan_entry.focus()

    # Row 1: Quantity Input
    lbl_qty = tk.Label(sell_card, text="Quantity to Add", **lbl_style)
    sell_card.create_window(35, 120, window=lbl_qty, anchor="w")
    qty_entry = tk.Entry(sell_card, width=23, **ent_style)
    qty_entry.insert(0, "1")
    sell_card.create_window(165, 120, window=qty_entry, anchor="w")

    # Row 2: Result Verification Area
    result_frame = tk.Frame(sell_card, bg="#f8f9fa", relief="solid", bd=1)
    sell_card.create_window(270, 185, window=result_frame, anchor="center", width=470, height=50)

    result_frame.grid_columnconfigure(0, weight=1)
    result_frame.grid_columnconfigure(3, weight=1)
    result_frame.grid_rowconfigure(0, weight=1)

    icon_label = tk.Label(result_frame, text="🔍", font=("Segoe UI", 12), fg="#7f8c8d", bg="#f8f9fa", anchor="center")
    icon_label.grid(row=0, column=1, padx=(10, 8), sticky="w") 

    result = tk.Label(
        result_frame, text="Waiting for barcode scan...", 
        font=("Segoe UI", 10, "italic"), fg="#7f8c8d", bg="#f8f9fa", anchor="w"
    )
    result.grid(row=0, column=2, sticky="w")

    # Local Variable Variables for temporary match
    current_med_data = {} 

    # --- Grand Total Update Function ---
    def update_grand_total():
        total = 0
        for item in cart_tree.get_children():
            total += int(cart_tree.item(item)['values'][4]) # Total Price က column index 4 မှာရှိသည်
        lbl_total.config(text=f"Grand Total: {total:,} Ks")

    # --- Barcode Verification Logic ---
    def check_barcode_data(code):
        if not code: return
        try:
            import datetime
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            conn = db()
            c = conn.cursor()
            
            # ဆေးဝါးအချက်အလက်နှင့် unit_price ကိုပါဆွဲထုတ်ခြင်း (မရှိလျှင် 0 ဟု ယူဆ)
            try:
                c.execute("SELECT id, name, barcode, unit_price FROM medicines WHERE barcode=?", (code,))
                med_info = c.fetchone()
            except:
                c.execute("SELECT id, name, barcode, 0 FROM medicines WHERE barcode=?", (code,))
                med_info = c.fetchone()
                
            if not med_info:
                current_med_data.clear()
                import threading
                from pygame import mixer
                def play_warning():
                    try:
                        mixer.init()
                        sound = mixer.Sound("error.mp3") 
                        sound.play()
                    except: pass
                threading.Thread(target=play_warning, daemon=True).start()

                icon_label.config(text="❌", fg="#c0392b")
                result.config(text=" Medicine Not Found!", font=("Segoe UI", 11, "bold"), fg="#c0392b")
                add_to_cart_btn.config(state="disabled", bg="#95a5a6")
                conn.close()
                return

            med_id, name, barcode, unit_price = med_info
            if unit_price is None: unit_price = 0

            # 🌟 [ပြင်ဆင်လိုက်သည်] သက်တမ်းမကုန်သေးဘဲ (expiry >= current_date) အမှန်တကယ်ရောင်းရမည့် Stock စုစုပေါင်းကိုပဲ တွက်ချက်ခြင်း
            c.execute("""
                SELECT SUM(qty) FROM medicine_batches 
                WHERE medicine_id = ? AND expiry >= ?
            """, (med_id, current_date))
            total_stock_row = c.fetchone()
            total_stock = total_stock_row[0] if total_stock_row and total_stock_row[0] is not None else 0

            # သက်တမ်းမကုန်သေးဘဲ stockကျန်ရှိသော Active အနီးစပ်ဆုံးရက်ကို တွက်ခြင်း
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
                
                # 🌟 ဒေတာဘေ့စ်ထဲမှ ဈေးနှုန်း format အမှားမတက်စေရန် ကော်မာသေချာဖြတ်ပြီး စာသားပုံစံ ပြင်ဆင်လိုက်ပါသည်
                formatted_price = f"{int(unit_price):,}" if str(unit_price).isdigit() else str(unit_price)

                # 🌟 လွဲမှားနေသော String Operator (|) ကို ဖယ်ရှားပြီး f-string တစ်ခုတည်းအဖြစ် စနစ်တကျ ပြောင်းလဲလိုက်ပါသည်
                result.config(
                    text=f"{name}  |  Available Stock: {total_stock}  |\nNearest Exp: {active_expiry}  |  Price: {formatted_price} Ks",
                    font=("Segoe UI", 11, "bold"),
                    fg=text_color,
                    justify="left"
                )
                
                # Add to Cart သုံးနိုင်ရန် လက်ရှိဆေးအချက်အလက်ကို သိမ်းဆည်းခြင်း
                current_med_data.update({
                    "id": med_id, "name": name, "barcode": barcode, 
                    "unit_price": int(unit_price) if str(unit_price).isdigit() else 0, 
                    "stock": total_stock
                })
                add_to_cart_btn.config(state="normal", bg="#3498db")
            else:
                import threading
                from pygame import mixer
                def play_warning():
                    try:
                        mixer.init()
                        sound = mixer.Sound("warning_short.mp3") 
                        sound.play()
                    except: pass
                threading.Thread(target=play_warning, daemon=True).start()

                icon_label.config(text="❌", font=("Segoe UI", 17), fg="#c0392b")
                
                if total_stock <= 0:
                    error_msg = f"{name} is Out of Stock!"
                else:
                    error_msg = f"{name} is Expired!"

                result.config(text=error_msg, font=("Segoe UI", 11, "bold"), fg="#c0392b", justify="center")
                add_to_cart_btn.config(state="disabled", bg="#95a5a6") 

            conn.close()
                
        except Exception as e:
            messagebox.showerror("Scan Error", f"Something went wrong while scanning:\n{e}")

    scan_entry.bind("<Return>", lambda e: check_barcode_data(scan_entry.get().strip()))
    def trigger_scan():
        import cv2
        from scanner import BarcodeScanner
        result.config(text="📷 Webcam Opening...", fg="#3498db")
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

        if scanned_code:
            scan_entry.delete(0, tk.END)
            scan_entry.insert(0, scanned_code)
            check_barcode_data(scanned_code)
        else:
            result.config(text="Scan cancelled.", fg="#e67e22")

    # --- Add To Cart Logic ---
    def add_to_cart():
        if not current_med_data: return
        qty_in = qty_entry.get().strip()
        if not qty_in.isdigit() or int(qty_in) <= 0:
            messagebox.showwarning("Warning", "Quantity must be a valid positive number!")
            return
        
        req_qty = int(qty_in)
        if req_qty > current_med_data["stock"]:
            messagebox.showerror("Stock Limit", f"Not enough stock! Only {current_med_data['stock']} items available.")
            return

        # Cart Treeview ထဲတွင် ရှိပြီးသားလား စစ်ဆေးခြင်း
        for item in cart_tree.get_children():
            values = cart_tree.item(item)['values']
            if str(values[0]) == str(current_med_data["barcode"]):
                new_qty = int(values[2]) + req_qty
                if new_qty > current_med_data["stock"]:
                    messagebox.showerror("Stock Limit", "Combined quantity exceeds available stock!")
                    return
                new_total = new_qty * int(values[3])
                cart_tree.item(item, values=(values[0], values[1], new_qty, values[3], new_total, current_med_data["id"]))
                update_grand_total()
                clear_inputs()
                return
            
        # Cart ထဲသို အသစ်ထည့်ခြင်း
        total_p = req_qty * current_med_data["unit_price"]
        cart_tree.insert("", "end", values=(
            current_med_data["barcode"], current_med_data["name"], 
            req_qty, current_med_data["unit_price"], total_p, current_med_data["id"]
        ))
        update_grand_total()
        clear_inputs()

    def clear_inputs():
        scan_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
        qty_entry.insert(0, "1")
        result.config(text="Waiting for next scan...", fg="#7f8c8d", font=("Segoe UI", 10, "italic"))
        icon_label.config(text="🔍", fg="#7f8c8d")
        add_to_cart_btn.config(state="disabled", bg="#95a5a6")
        current_med_data.clear()
        scan_entry.focus()

    # --- Cancel Selected Item ---
    def remove_item():
        selected = cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item from the cart to remove!")
            return
        cart_tree.delete(selected)
        update_grand_total()

    # --- Checkout / Checkout Done (FIFO Logic) ---
    def checkout():
        if not cart_tree.get_children():
            messagebox.showwarning("Warning", "Your shopping cart is empty!")
            return

        if not messagebox.askyesno("Confirm Sale", "Are you sure you want to complete this transaction?"):
            return

        try:
            import datetime
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            conn = db()
            c = conn.cursor()

            import datetime

            invoice_no = "INV" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            sale_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            grand_total = 0
            for item in cart_tree.get_children():
                grand_total += int(cart_tree.item(item)["values"][4])

            for item in cart_tree.get_children():
                vals = cart_tree.item(item)['values']
                med_id = vals[5]
                sell_qty = int(vals[2])
                
                # FIFO စနစ်အရ သက်တမ်းမကုန်သေးသော active batch များကို သက်တမ်းအလိုက် (expiry ASC) စီယူခြင်း
                # 🌟 Expiry ရက်စွဲကိုပါ UPDATE မှာ သုံးနိုင်အောင် SQL Query ထဲတွင် expiry ကိုပါ ဆွဲထုတ်ခိုင်းလိုက်ပါတယ်
                c.execute("""
                    SELECT qty, batch_number, expiry FROM medicine_batches 
                    WHERE medicine_id = ? AND qty > 0 AND expiry >= ?
                    ORDER BY expiry ASC
                """, (med_id, current_date))
                batches = c.fetchall()
                rem = sell_qty

                for batch in batches:
                    b_qty, b_no, b_exp = batch # 🌟 b_exp (expiry date) ကိုပါ variable ထဲ ထည့်ယူလိုက်ပါတယ်
                    if rem <= 0: break
                    
                    if b_qty >= rem:
                        # Batch နံပါတ် တူနေရင်တောင် Expiry ပါ ကိုက်ညီမှ နှုတ်ရန် AND expiry = ? ထည့်သွင်းထားပါတယ်
                        c.execute("""
                            UPDATE medicine_batches 
                            SET qty = qty - ? 
                            WHERE medicine_id = ? AND batch_number = ? AND expiry = ?
                        """, (rem, med_id, b_no, b_exp))
                        rem = 0
                    else:
                        rem -= b_qty
                        # 🌟 Batch နံပါတ် တူနေရင်တောင် Expiry ပါ ကိုက်ညီမှ 0 လုပ်ရန် AND expiry = ? ထည့်သွင်းထားပါတယ်
                        c.execute("""
                            UPDATE medicine_batches 
                            SET qty = 0 
                            WHERE medicine_id = ? AND batch_number = ? AND expiry = ?
                        """, (med_id, b_no, b_exp))

            # -----------------------------
            # Save Sale Header
            # -----------------------------
            user = get_current_user()

            cashier = user["username"] if user else "Unknown"

            c.execute("""
            INSERT INTO sales
            (
                invoice_no,
                cashier,
                sale_date,
                grand_total
            )
            VALUES
            (
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                invoice_no,
                cashier,
                sale_date,
                grand_total
            ))

            sale_id = c.lastrowid

            # -----------------------------
            # Save Sale Items
            # -----------------------------
            for item in cart_tree.get_children():

                vals = cart_tree.item(item)["values"]

                c.execute("""
                INSERT INTO sale_items
                (
                    sale_id,
                    medicine_id,
                    medicine_name,
                    qty,
                    price,
                    subtotal
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    sale_id,
                    vals[5],
                    vals[1],
                    vals[2],
                    vals[3],
                    vals[4]
                ))            

            conn.commit()
            user = get_current_user()

            if user:
                log_action(
                    user["id"],
                    user["username"],
                    user["role"],
                    "SELL",
                    "POS",
                    f"Invoice : {invoice_no}"
                )
            conn.close()

            show_receipt(invoice_no)

            # Reset Cart
            for item in cart_tree.get_children():
                cart_tree.delete(item)

            update_grand_total()
            clear_inputs()
            
            # Reset Cart
            for item in cart_tree.get_children(): cart_tree.delete(item)
            update_grand_total()
            clear_inputs()

        except Exception as e:
            messagebox.showerror("Database Error", f"Checkout failed:\n{e}")

    # BUTTONS PANEL
    scan_btn = tk.Button(sell_card, text="🔍 Scan", font=("Segoe UI", 10, "bold"), bg="#2ecc71", fg="white", relief="flat", command=trigger_scan, cursor="hand2", padx=8)
    sell_card.create_window(375, 75, window=scan_btn, anchor="w")

    add_to_cart_btn = tk.Button(sell_card, text="➕ Add to Cart", font=("Segoe UI", 10, "bold"), bg="#95a5a6", fg="white", relief="flat", state="disabled", command=add_to_cart, cursor="hand2", padx=8)
    sell_card.create_window(375, 120, window=add_to_cart_btn, anchor="w")

    # ===== DYNAMIC CART TREEVIEW PANEL =====
    tree_frame = tk.Frame(sell_card, bg="white")
    sell_card.create_window(270, 365, window=tree_frame, width=470, height=260)

    style = ttk.Style()
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    cart_tree = ttk.Treeview(tree_frame, columns=("barcode", "name", "qty", "price", "total", "med_id"), show="headings")
    cart_tree.heading("barcode", text="Barcode")
    cart_tree.heading("name", text="Medicine Name")
    cart_tree.heading("qty", text="Qty")
    cart_tree.heading("price", text="Price")
    cart_tree.heading("total", text="Total")
    
    cart_tree.column("barcode", width=85, anchor="center")
    cart_tree.column("name", width=155, anchor="w")
    cart_tree.column("qty", width=40, anchor="center")
    cart_tree.column("price", width=80, anchor="e")
    cart_tree.column("total", width=90, anchor="e")
    cart_tree.column("med_id", width=0, minwidth=0, stretch=tk.NO) # Hidden ID column
    # 🌟 Cart ထဲမှာ ဆေးအရမ်းများလာလျှင် အသုံးပြုရန် Scrollbar စနစ်
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=cart_tree.yview)
    cart_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y") # ညာဘက်ဘေးတွင် ကပ်ထားမည်
    cart_tree.pack(fill="both", expand=True)

    # ===== LOWER FOOTER CONTROLS =====
    lbl_total = tk.Label(sell_card, text="Grand Total: 0 Ks", font=("Segoe UI", 14, "bold"), fg="#2c3e50", bg="white")
    sell_card.create_window(35, 520, window=lbl_total, anchor="w")

    remove_btn = tk.Button(sell_card, text="❌ Cancel Item", font=("Segoe UI", 10, "bold"), bg="#e67e22", fg="white", relief="flat", command=remove_item, cursor="hand2", padx=10)
    sell_card.create_window(468, 520, window=remove_btn, anchor="e")

    checkout_btn = tk.Button(sell_card, text="🛍 Confirm Sell & Print Bill", font=("Segoe UI", 12, "bold"), bg="#2e7d32", fg="white", relief="flat", command=checkout, cursor="hand2", padx=40, pady=6)
    sell_card.create_window(270, 580, window=checkout_btn, anchor="center")