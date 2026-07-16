import tkinter as tk
from tkinter import ttk, messagebox
from authentication.security import hash_password
from utils import clear
from database import db, log_action
from authentication.session import get_current_user


def user_management_page(main):

    clear(main)
    main.config(bg="#f8f9fa")

    # ================= TITLE =================
    tk.Label(
        main,
        text="User Management",
        font=("Segoe UI", 22, "bold"),
        fg="#2c3e50",
        bg="#f8f9fa"
    ).pack(pady=15)

    container = tk.Frame(main, bg="#f8f9fa")
    container.pack(fill="both", expand=True, padx=20, pady=10)

    left_frame = tk.Frame(container, bg="#f8f9fa")
    left_frame.pack(side="left", fill="y", padx=(0,20))
    left_frame.config(width=470)
    left_frame.pack_propagate(False)

    right_frame = tk.Frame(container, bg="#f8f9fa")
    right_frame.pack(side="left", fill="both", expand=True, padx=(25,0))

    # ================= CARD =================

    card_width = 440
    card_height = 340

    card = tk.Canvas(
        left_frame,
        width=card_width,
        height=card_height,
        bg="#f8f9fa",
        highlightthickness=0
    )

    card.pack(padx=15,pady=10)
    def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):

        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]

        canvas.create_polygon(
            points,
            smooth=True,
            fill="white",
            outline="#dddddd",
            width=1
        )

    draw_rounded_rect(
        card,
        5,
        5,
        card_width-5,
        card_height-5,
        20
    )

    card.create_text(
        30,
        30,
        text="Create New User",
        anchor="w",
        font=("Segoe UI", 12, "bold"),
        fill="#34495e"
    )

    lbl_style = {
        "bg": "white",
        "font": ("Segoe UI", 11),
        "fg": "#34495e"
    }

    entry_style = {
        "font": ("Segoe UI", 11),
        "relief": "solid",
        "bd": 1,
        "width": 30
    }

    # Username

    card.create_window(
        35,
        80,
        window=tk.Label(card, text="Username", **lbl_style),
        anchor="w"
    )

    username_entry = tk.Entry(card, **entry_style)

    card.create_window(
        160,
        80,
        window=username_entry,
        anchor="w"
    )

    # Password

    card.create_window(
        35,
        140,
        window=tk.Label(card, text="Password", **lbl_style),
        anchor="w"
    )

    password_entry = tk.Entry(
        card,
        show="*",
        **entry_style
    )

    card.create_window(
        160,
        140,
        window=password_entry,
        anchor="w"
    )

    card.create_window(
        35,
        200,
        window=tk.Label(card, text="Role", **lbl_style),
        anchor="w"
    )

    role_combo = ttk.Combobox(
        card,
        values=["Admin", "Staff"],
        state="readonly",
        width=26
    )

    role_combo.current(1)

    card.create_window(
        160,
        200,
        window=role_combo,
        anchor="w"
    )

    # ================= FUNCTION =================

    def create_user():

        username = username_entry.get().strip()
        password = password_entry.get().strip()
        role = role_combo.get()

        if username == "" or password == "":

            messagebox.showerror(
                "Error",
                "Please fill all fields."
            )
            return
        
        password_hash = hash_password(password)

        try:

            conn = db()
            c = conn.cursor()

            c.execute(
                "SELECT id FROM users WHERE username=?",
                (username,)
            )

            if c.fetchone():
                messagebox.showerror(
                    "Error",
                    "Username already exists."
                )
                conn.close()
                return

            c.execute("""
            INSERT INTO users
            (
                username,
                password_hash,
                role
            )
            VALUES
            (
                ?,
                ?,
                ?
            )
            """,
            (
            username,
            password_hash,
            role
            ))

            conn.commit()
            conn.close()

            current = get_current_user()

            log_action(
                current["id"],
                current["username"],
                current["role"],
                "CREATE",
                "User Management",
                f"Created user : {username}"
            )

            messagebox.showinfo(
                "Success",
                "User created successfully."
            )

            load_users()

            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            role_combo.current(1)

            # load_users()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

    # ================= BUTTON =================

    create_btn = tk.Button(
        card,
        text="➕ Create User",
        font=("Segoe UI", 11, "bold"),
        bg="#2ecc71",
        fg="white",
        relief="flat",
        padx=20,
        pady=5,
        cursor="hand2",
        command=create_user
    )

    card.create_window(
        220,
        295,
        window=create_btn
    )

   # ================= SEARCH =================

    search_frame = tk.Frame(right_frame, bg="#f8f9fa")
    search_frame.pack(fill="x", pady=(0,10))

    tk.Label(
        search_frame,
        text="🔍 Search User",
        bg="#f8f9fa",
        font=("Segoe UI", 11, "bold")
    ).pack(side="left")

    search_entry = tk.Entry(
        search_frame,
        font=("Segoe UI", 11),
        width=25
    )

    search_entry.pack(side="left", padx=10)
    def search_user(event=None):

        load_users(
            search_entry.get().strip()
        )

    search_entry.bind(
        "<KeyRelease>",
        search_user
    )

    list_frame = tk.Frame(right_frame, bg="#f8f9fa")
    list_frame.pack(fill="both", expand=True, pady=10)

    # ================= USER CARD AREA =================

    list_canvas = tk.Canvas(
        list_frame,
        bg="#f8f9fa",
        highlightthickness=0
    )

    scroll_frame = tk.Frame(
        list_canvas,
        bg="#f8f9fa"
    )

    scroll_frame.bind(
        "<Configure>",
        lambda e: list_canvas.configure(
            scrollregion=list_canvas.bbox("all")
        )
    )

    list_canvas.create_window(
        (0,0),
        window=scroll_frame,
        anchor="nw"
    )

    list_canvas.pack(
        fill="both",
        expand=True
    )

    cards_frame = tk.Frame(
        scroll_frame,
        bg="#f8f9fa"
    )

    cards_frame.pack(
        fill="both",
        expand=True
    )

    def edit_user(user_id):

        conn = db()
        c = conn.cursor()

        c.execute("""
            SELECT username, role
            FROM users
            WHERE id=?
        """, (user_id,))

        user = c.fetchone()
        conn.close()

        if not user:
            return

        username, role = user

        win = tk.Toplevel(main)
        win.title("Edit User")
        win.geometry("350x220")
        win.transient(main)
        win.grab_set()
        win.focus_force()
        win.resizable(False, False)

        tk.Label(
            win,
            text="Username"
        ).pack(pady=(20,5))

        username_edit = tk.Entry(
            win,
            width=30
        )

        username_edit.pack()

        username_edit.insert(
            0,
            username
        )

        tk.Label(
            win,
            text="Role"
        ).pack(pady=(15,5))

        role_edit = ttk.Combobox(
            win,
            values=["Admin","Staff"],
            state="readonly"
        )

        role_edit.pack()

        role_edit.set(role)
        if role == "Admin":
            role_edit.config(state="disabled")

        def save():

            new_username = username_edit.get().strip()
            new_role = role_edit.get()

            conn = db()
            c = conn.cursor()

            c.execute("""
            SELECT id
            FROM users
            WHERE username=?
            AND id!=?
            """,
            (
                new_username,
                user_id
            ))

            if c.fetchone():
                messagebox.showerror(
                    "Error",
                    "Username already exists."
                )
                conn.close()
                return
            
            if role == "Admin":
                new_role = "Admin"

            c.execute("""
                UPDATE users
                SET username=?,
                    role=?
                WHERE id=?
            """,
            (
                new_username,
                new_role,
                user_id
            ))

            conn.commit()
            conn.close()

            current = get_current_user()

            log_action(
                current["id"],
                current["username"],
                current["role"],
                "UPDATE",
                "User Management",
                f"Updated user : {new_username}"
            )

            load_users()

            win.destroy()

            messagebox.showinfo(
                "Success",
                "User updated successfully."
            )

        tk.Button(
                win,
                text="Save",
                bg="#2ecc71",
                fg="white",
                width=15,
                command=save
            ).pack(pady=20)   
        
    def delete_user(user_id):

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this user?"
        ):
            return

        conn = db()
        c = conn.cursor()

        # User အချက်အလက်ယူ
        c.execute("""
            SELECT username, role
            FROM users
            WHERE id=?
        """, (user_id,))

        user = c.fetchone()

        if not user:
            conn.close()
            return

        username, role = user

        current = get_current_user()

        if current["id"] == user_id:
            conn.close()

            messagebox.showwarning(
                "Warning",
                "You cannot delete your own account."
            )
            return

        if role == "Admin":
            conn.close()

            messagebox.showwarning(
                "Warning",
                "Admin account cannot be deleted."
            )
            return
        
        c.execute(
            "DELETE FROM users WHERE id=?",
            (user_id,)
        )

        conn.commit()
        conn.close()

        current = get_current_user()

        log_action(
            current["id"],
            current["username"],
            current["role"],
            "DELETE",
            "User Management",
            f"Deleted user : {username}"
        )

        load_users()

        messagebox.showinfo(
            "Success",
            "User deleted successfully."
        )

    def load_users(keyword=""):

        # Card အဟောင်းတွေဖျက်
        for widget in cards_frame.winfo_children():
            widget.destroy()

        # Header ကို ပြန်ဆောက်
        header = tk.Frame(cards_frame, bg="#34495e")
        header.pack(fill="x")

        tk.Label(header, text="Username",
                bg="#34495e", fg="white",
                width=25, anchor="w").pack(side="left", padx=10, pady=8)

        tk.Label(header, text="Role",
                bg="#34495e", fg="white",
                width=12).pack(side="left")

        tk.Label(header, text="Action",
                bg="#34495e", fg="white",
                width=22).pack(side="right", padx=10)

        conn = db()
        c = conn.cursor()

        c.execute("""
            SELECT id, username, role
            FROM users
            WHERE username LIKE ?
            ORDER BY id DESC
        """, (f"%{keyword}%",))

        users = c.fetchall()
        conn.close()

        for user in users:

            user_id, username, role = user

            row = tk.Frame(
                cards_frame,
                bg="white"
            )

            row.pack(
                fill="x",
                pady=1
            )

            tk.Label(
                row,
                text=username,
                bg="white",
                width=24,
                anchor="w",
                font=("Segoe UI", 10)
            ).pack(
                side="left",
                padx=10,
                pady=10
            )

            tk.Label(
                row,
                text=role,
                bg="white",
                width=12
            ).pack(side="left")

            action = tk.Frame(
                row,
                bg="white"
            )

            action.pack(
                side="right",
                padx=10,
                pady=5
            )

            edit_btn = tk.Button(
                action,
                text="Edit",
                bg="#3498db",
                fg="white",
                width=7,
                cursor="hand2",
                command=lambda uid=user_id: edit_user(uid)
            )

            edit_btn.pack(
                side="left",
                padx=3
            )

            if role != "Admin":

                delete_btn = tk.Button(
                    action,
                    text="Delete",
                    bg="#e74c3c",
                    fg="white",
                    width=7,
                    cursor="hand2",
                    command=lambda uid=user_id: delete_user(uid)
                )

                delete_btn.pack(
                    side="left",
                    padx=3
                ) 
    load_users()