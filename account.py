import tkinter as tk
from tkinter import messagebox
from database import db, log_action
from utils import clear
from authentication.security import (
    verify_password,
    hash_password,
    validate_password
)
from authentication.session import get_current_user

def account_page(main, user_id):
    clear(main)
    main.config(bg="#f8f9fa")

    tk.Label(
        main, 
        text="Account Settings", 
        font=("Segoe UI", 22, "bold"), 
        fg="#2c3e50", 
        bg="#f8f9fa"
    ).pack(pady=15)

    card_width = 540
    card_height = 420  
    account_card = tk.Canvas(main, width=card_width, height=card_height, bg="#f8f9fa", highlightthickness=0)
    account_card.pack(pady=10)

    def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    draw_rounded_rect(account_card, 5, 5, card_width-5, card_height-5, radius=20, fill="white", outline="#e0e0e0", width=1)
    account_card.create_text(35, 30, text="Secure Update Username & Password", font=("Segoe UI", 12, "bold"), fill="#34495e", anchor="w")

    lbl_style = {"bg": "white", "font": ("Segoe UI", 11), "fg": "#34495e"}
    ent_style = {"font": ("Segoe UI", 11), "relief": "solid", "bd": 1, "width": 25}

    # =====  INPUT FIELDS  =====
    
    #  Old Password 
    account_card.create_window(35, 80, window=tk.Label(account_card, text="Old Password", **lbl_style), anchor="w")
    old_pass_entry = tk.Entry(account_card, show="*", **ent_style)
    account_card.create_window(185, 80, window=old_pass_entry, anchor="w")

    #  New Username 
    account_card.create_window(35, 140, window=tk.Label(account_card, text="New Username", **lbl_style), anchor="w")
    user_entry = tk.Entry(account_card, **ent_style)
    account_card.create_window(185, 140, window=user_entry, anchor="w")

    #  New Password 
    account_card.create_window(35, 200, window=tk.Label(account_card, text="New Password", **lbl_style), anchor="w")
    pass_entry = tk.Entry(account_card, show="•", **ent_style)
    account_card.create_window(185, 200, window=pass_entry, anchor="w")

    #  Confirm New Password 
    account_card.create_window(35, 260, window=tk.Label(account_card, text="Confirm Password", **lbl_style), anchor="w")
    confirm_entry = tk.Entry(account_card, show="•", **ent_style)
    account_card.create_window(185, 260, window=confirm_entry, anchor="w")


    # =====  UPDATE BACKEND LOGIC (Check Old Password ) =====
    def update_account():
        old_pass = old_pass_entry.get().strip()
        new_user = user_entry.get().strip()
        new_pass = pass_entry.get().strip()
        conf_pass = confirm_entry.get().strip()

        if not old_pass or not new_user or not new_pass or not conf_pass:
            messagebox.showerror("Error", "All fields are required!")
            return

        if new_pass != conf_pass:
            messagebox.showerror("Error", "New passwords do not match!")
            return
        
        valid, message = validate_password(new_pass)

        if not valid:
            messagebox.showerror(
                "Weak Password",
                message
            )
            return

        try:
            current_user = get_current_user()

            if current_user is None:
                messagebox.showerror(
                    "Error",
                    "Please login again."
                )
                return

            user_id = current_user["id"]

            conn = db()
            c = conn.cursor()
            
<<<<<<< HEAD
            #လက်ရှိ user_id ရဲ့ Password ကို စစ်ဆေးပါတယ်
            c.execute("SELECT password FROM users WHERE id = ?", (user_id,))
=======
            # ဒေတာဘေ့စ်ထဲက လက်ရှိ (Admin ID: 1) ရဲ့ Password အဟောင်းကို လှမ်းယူစစ်ဆေးခြင်း
            c.execute("""
            SELECT password_hash
            FROM users
            WHERE id=?
            """, (user_id,))

>>>>>>> origin/king-receipt-update
            row = c.fetchone()
            
            if row is None:
                messagebox.showerror("Error", "User not found in database!")
                conn.close()
                return
                
<<<<<<< HEAD
            db_old_password = row[0]
            if old_pass != db_old_password:
                messagebox.showerror("Error", "Incorrect Old Password! Authorization failed.")
                conn.close()
                return
            
            # လက်ရှိ user_id နေရာမှာပဲ သွားပြီး UPDATE လုပ်တယ်
            c.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (new_user, new_pass, user_id))
=======
            password_hash = row[0]
            # 🌟 ရိုက်ထည့်လိုက်တဲ့ Old Password နဲ့ ဒေတာဘေ့စ်ထဲက Password ကိုက်ညီမှု ရှိမရှိ စစ်ဆေးခြင်း
            # (မှတ်ချက် - အကယ်၍ မိတ်ဆွေက login မှာ password ကို hash လုပ်သုံးထားရင် ဒီနေရာမှာလည်း old_pass ကို hash လုပ်ပြီးမှ တိုက်စစ်ပေးရပါမယ်ဗျာ)
            if not verify_password(
                old_pass,
                password_hash
            ):
                messagebox.showerror(
                    "Error",
                    "Incorrect Old Password!"
                )
                conn.close()
                return
            
            # အဟောင်းမှန်ကန်မှသာ အသစ်ကို UPDATE လုပ်ခွင့်ပေးမည်
            new_password_hash = hash_password(new_pass)

            c.execute("""
            UPDATE users
            SET
                username=?,
                password_hash=?
            WHERE id=?
            """,
            (
                new_user,
                new_password_hash,
                user_id
            ))
>>>>>>> origin/king-receipt-update
            conn.commit()
            conn.close()

            log_action(
                user_id,
                new_user,
                current_user["role"],
                "UPDATE",
                "Account",
                "Updated own account"
            )

            messagebox.showinfo("Success", "Account updated successfully!\nPlease use new credentials next time.")

            from authentication.session import login

            login({
                "id": user_id,
                "username": new_user,
                "role": current_user["role"]
            })
            
            old_pass_entry.delete(0, tk.END)
            user_entry.delete(0, tk.END)
            pass_entry.delete(0, tk.END)
            confirm_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update account:\n{e}")


    # =====  BUTTON =====
    update_btn = tk.Button(
        account_card, 
        text="💾 Update Account", 
        font=("Segoe UI", 11, "bold"), 
        bg="#3498db", 
        fg="white", 
        relief="flat", 
        command=update_account,
        cursor="hand2",
        padx=20,
        pady=5
    )
    account_card.create_window(270, 350, window=update_btn, anchor="center")