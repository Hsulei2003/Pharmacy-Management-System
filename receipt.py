
import tkinter as tk
from tkinter import ttk, messagebox
from database import db

SHOP_NAME="Pharmacy Management System"

def show_receipt(invoice_no):
        conn = db()
        c = conn.cursor()

        c.execute("""
        SELECT
            invoice_no,
            cashier,
            sale_date,
            grand_total
        FROM sales
        WHERE invoice_no=?
        """, (invoice_no,))

        sale = c.fetchone()

        if not sale:
            conn.close()
            messagebox.showerror("Receipt", "Invoice not found.")
            return

        invoice_no, cashier, sale_date, grand_total = sale

        c.execute("""
        SELECT
            medicine_name,
            qty,
            price,
            subtotal
        FROM sale_items
        WHERE sale_id=(
            SELECT id
            FROM sales
            WHERE invoice_no=?
        )
        """, (invoice_no,))

        items = c.fetchall()

        conn.close()

        receipt_win = tk.Toplevel()
        receipt_win.title(f"Receipt - {invoice_no}")
        receipt_win.geometry("430x650")
        receipt_win.resizable(False, False)
        receipt_win.config(bg="white")
        receipt_win.grab_set() # Main window ကို ခဏ ပိတ်ထားမည်

        # Header Area
        tk.Label(receipt_win, text=SHOP_NAME, font=("Segoe UI",18,"bold"),bg="white", fg="#2c3e50").pack(pady=(15, 2))
        tk.Label(receipt_win, text="Official Cash Receipt", font=("Segoe UI", 10, "italic"), bg="white", fg="#7f8c8d").pack()
        tk.Label(receipt_win,text=f"Invoice : {invoice_no}",font=("Segoe UI",10),bg="white").pack()
        tk.Label(receipt_win,text=f"Cashier : {cashier}",font=("Segoe UI",9),bg="white").pack()
        tk.Label(receipt_win,text=f"Date : {sale_date}",font=("Segoe UI",9),bg="white").pack(pady=(5,10))
        tk.Label(receipt_win,text="---------------------------------------------",bg="white",fg="#7f8c8d").pack()

        tk.Frame(receipt_win, height=1, width=340, bg="#bdc3c7").pack() # Divider Line

        # Item List Table Frame
        list_frame = tk.Frame(receipt_win, bg="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Header Row
        tk.Label(list_frame, text="Item", font=("Segoe UI", 9, "bold"), bg="white", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(list_frame, text="Qty", font=("Segoe UI", 9, "bold"), bg="white", anchor="center").grid(row=0, column=1, padx=10)
        tk.Label(list_frame, text="Price", font=("Segoe UI", 9, "bold"), bg="white", anchor="e").grid(row=0, column=2, sticky="e")
        tk.Label(list_frame, text="Total", font=("Segoe UI", 9, "bold"), bg="white", anchor="e").grid(row=0, column=3, sticky="e")

        list_frame.columnconfigure(0, weight=2)
        list_frame.columnconfigure(3, weight=1)

        # Populate Cart Items
        row_idx = 1
        for item in items:
            # item = (barcode, name, qty, price, total, med_id)
            name = item[0]
            qty = item[1]
            price = f"{int(item[2]):,}"
            subtotal = f"{int(item[3]):,}"

            tk.Label(list_frame, text=name, font=("Segoe UI", 9), bg="white", anchor="w").grid(row=row_idx, column=0, sticky="w", pady=2)
            tk.Label(list_frame, text=str(qty), font=("Segoe UI", 9), bg="white").grid(row=row_idx, column=1, pady=2)
            tk.Label(list_frame, text=price, font=("Segoe UI", 9), bg="white", anchor="e").grid(row=row_idx, column=2, pady=2, padx=5)
            tk.Label(list_frame, text=subtotal, font=("Segoe UI", 9), bg="white", anchor="e").grid(row=row_idx, column=3, sticky="e", pady=2)
            row_idx += 1

        # Grand Total Frame
        tk.Frame(receipt_win, height=1, width=340, bg="#bdc3c7").pack()
        
        tot_frame = tk.Frame(receipt_win, bg="white")
        tot_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(receipt_win,text=f"Total Items : {len(items)}",font=("Segoe UI",9),bg="white").pack()
        tk.Label(tot_frame, text="Grand Total:", font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50").pack(side="left")
        tk.Label(tot_frame, text=f"{grand_total:,} Ks", font=("Segoe UI", 13, "bold"), bg="white", fg="#27ae60").pack(side="right")
        tk.Label(receipt_win,text="---------------------------------------------",bg="white",fg="#7f8c8d").pack()
        tk.Label(receipt_win, text="Thank you for shopping with us!", font=("Segoe UI", 9, "italic"), bg="white", fg="#7f8c8d").pack(pady=(0, 10))

        # --- Direct Print Action ---
        def print_action():
            messagebox.showinfo("Print", "Sending document to printer...")
            receipt_win.destroy()

        # Separate Print Button
        print_btn = tk.Button(
            receipt_win, text="🖨️ Print Receipt", font=("Segoe UI", 10, "bold"), 
            bg="#2980b9", fg="white", relief="flat", cursor="hand2", padx=20, pady=5,
            command=print_action
        )
        print_btn.pack(pady=(5,15),ipadx=20)
