import tkinter as tk
from tkinter import ttk
from utils import clear
from database import db

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
    
    search_frame = tk.Frame(main,bg="#f8f9fa")
    search_frame.pack(fill="x",padx=20)

    tk.Label(
        search_frame,
        text="Search",
        bg="#f8f9fa"
    ).pack(side="left")

    search_entry = tk.Entry(
        search_frame,
        width=30
    )

    search_entry.pack(side="left",padx=10)

    tk.Label(
        search_frame,
        text="Action",
        bg="#f8f9fa"
    ).pack(side="left", padx=(20,5))

    action_combo = ttk.Combobox(
        search_frame,
        values=[
            "Important",
            "All",
            "LOGIN",
            "LOGOUT",
            "CREATE",
            "UPDATE",
            "DELETE"
        ],
        state="readonly",
        width=15
    )

    action_combo.current(0)

    action_combo.pack(side="left")

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

    def load_logs(keyword="", action_filter="Important"):

        tree.delete(*tree.get_children())

        conn = db()
        c = conn.cursor()

        if action_filter == "Important":

            c.execute("""
            SELECT
                created_at,
                username,
                role,
                action,
                module,
                description
            FROM audit_logs
            WHERE username LIKE ?
            AND action IN
            (
                'CREATE',
                'UPDATE',
                'DELETE'
            )
            ORDER BY id DESC
            LIMIT 100
            """,(f"%{keyword}%",))

        elif action_filter == "All":

            c.execute("""
            SELECT
                created_at,
                username,
                role,
                action,
                module,
                description
            FROM audit_logs
            WHERE username LIKE ?
            ORDER BY id DESC
            LIMIT 100
            """,(f"%{keyword}%",))

        else:

            c.execute("""
            SELECT
                created_at,
                username,
                role,
                action,
                module,
                description
            FROM audit_logs
            WHERE username LIKE ?
            AND action=?
            ORDER BY id DESC
            LIMIT 100
            """,
            (
                f"%{keyword}%",
                action_filter
            ))

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

        for row in rows:

            created_at, username, role, action, module, description = row

            tree.insert(
                "",
                tk.END,
                values=row,
                tags=(action,)
            )
    
    def search(event=None):

        load_logs(
            search_entry.get().strip(),
            action_combo.get()
        )

    search_entry.bind(
        "<KeyRelease>",
        search
    )

    action_combo.bind(
        "<<ComboboxSelected>>",
        lambda e: load_logs(
            search_entry.get().strip(),
            action_combo.get()
        )
    )

    load_logs(
        "",
        "Important"
    )

    def auto_refresh():

        # Widget တွေရှိသေးလား စစ်
        if (
            not search_entry.winfo_exists()
            or not action_combo.winfo_exists()
            or not tree.winfo_exists()
        ):
            return
        
        if (
            not main.winfo_exists()
            or not search_entry.winfo_exists()
            or not action_combo.winfo_exists()
            or not tree.winfo_exists()
        ):
            return

        load_logs(
            search_entry.get().strip(),
            action_combo.get()
        )

        main.after(
            5000,
            auto_refresh
        )

    main.after(
        5000,
        auto_refresh
    )