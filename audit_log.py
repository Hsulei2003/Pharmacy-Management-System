import tkinter as tk
from tkinter import ttk
from utils import clear
from database import db
from receipt import show_receipt

def audit_log_page(main):

    clear(main)
    main.config(bg="#f8f9fa")

    tk.Label(
    main,
    text="Audit Logs",
    font=("Segoe UI",22,"bold"),
    bg="#f8f9fa",
    fg="#2c3e50"
).pack(pady=15)

    filter_frame = tk.Frame(main, bg="#f8f9fa")
    filter_frame.pack(fill="x", padx=20, pady=(0,10))

    tk.Label(
        filter_frame,
        text="Action :",
        bg="#f8f9fa",
        font=("Segoe UI",10)
    ).pack(side="left")

    action_combo = ttk.Combobox(
        filter_frame,
        values=[
            "Important",
            "All",
            "LOGIN",
            "LOGOUT",
            "CREATE",
            "UPDATE",
            "DELETE",
            "SELL"
        ],
        state="readonly",
        width=15
    )

    action_combo.current(0)
    action_combo.pack(side="left", padx=10)

    table_frame = tk.Frame(main)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )

    style = ttk.Style()

    style.theme_use("clam")

    style.configure(
        "Treeview",
        font=("Segoe UI", 11),
        rowheight=30,
        background="white"
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 11, "bold"),
        background="#2c3e50",
        foreground="white"
    )

    style.map(
        "Treeview",
        background=[("selected", "#3498db")]
    )

    columns = (
        "ID",
        "Date",
        "Username",
        "Role",
        "Action",
        "Module",
        "Description"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Treeview"
    )

    for col in columns:
        tree.heading(col, text=col)

    tree.heading("ID", text="")
    tree.column("ID", width=0, minwidth=0, stretch=False)
    tree.column("Date", width=170)
    tree.column("Username", width=120)
    tree.column("Role", width=80)
    tree.column("Action", width=100)
    tree.column("Module", width=140)
    tree.column("Description", width=350)

    scroll = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scroll.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scroll.pack(
        side="right",
        fill="y"
    )

    def load_logs(action_filter="Important"):

        tree.delete(*tree.get_children())

        conn = db()
        c = conn.cursor()

        if action_filter == "Important":

            c.execute("""
            SELECT
                id,
                created_at,
                username,
                role,
                action,
                module,
                description
            FROM audit_logs
            WHERE action IN
            (
                'CREATE',
                'UPDATE',
                'DELETE',
                'SELL'
            )
            ORDER BY id DESC
            LIMIT 100
            """)

        elif action_filter == "All":

            c.execute("""
            SELECT
                id,
                created_at,
                username,
                role,
                action,
                module,
                description
            FROM audit_logs
            ORDER BY id DESC
            LIMIT 100
            """)

        else:

            c.execute("""
            SELECT
                id,
                created_at,
                username,
                role,
                action,
                module,
                description
            FROM audit_logs
            WHERE action=?
            ORDER BY id DESC
            LIMIT 100
            """, (action_filter,))

        rows = c.fetchall()

        if not rows:

            tree.insert(
                "",
                tk.END,
                values=(
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "No audit logs found."
                )
            )

            conn.close()
            return

        conn.close()

        tree.tag_configure("LOGIN", foreground="#3498db")
        tree.tag_configure("LOGOUT", foreground="#7f8c8d")
        tree.tag_configure("CREATE", foreground="#27ae60")
        tree.tag_configure("UPDATE", foreground="#f39c12")
        tree.tag_configure("DELETE", foreground="#e74c3c")
        tree.tag_configure("SELL", foreground="#8e44ad")

        for row in rows:

            id,created_at, username, role, action, module, description = row

            tree.insert(
                "",
                tk.END,
                values=row,
                tags=(action,)
            )

    def open_receipt(event):

        selected = tree.selection()

        if not selected:
            return

        values = tree.item(selected[0])["values"]

        action = values[4]

        if action != "SELL":
            return

        description = values[6]

        if "Invoice :" not in description:
            return

        invoice_no = description.replace(
            "Invoice :",
            ""
        ).strip()

        show_receipt(invoice_no)

    tree.bind("<Double-1>",open_receipt)
    action_combo.bind("<<ComboboxSelected>>",lambda e: load_logs(action_combo.get()))
    load_logs("Important")

    def auto_refresh():

        # Widget တွေရှိသေးလား စစ်
        if (
             not tree.winfo_exists()
        ):
            return
        
        if (
            not main.winfo_exists()
            or not tree.winfo_exists()
        ):
            return

        load_logs(action_combo.get())

        main.after(
            5000,
            auto_refresh
        )

    main.after(
        5000,
        auto_refresh
    )