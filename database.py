import sqlite3
from authentication.security import hash_password
from datetime import datetime

def db():
    return sqlite3.connect("pharmacy.db", timeout=20)

def create_table():
    conn = db()
    c = conn.cursor()
    
    # Medicines Table 
    # not including qty & expiry
    c.execute("""
    CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        barcode TEXT NOT NULL UNIQUE,
        category TEXT,
        supplier TEXT NOT NULL DEFAULT 'Unknown',
        unit_price INTEGER DEFAULT 0
    )
    """)
    
    # Medicine Batches Table 
    # ဆေးတစ်မျိုးချင်းစီရဲ့ အရေအတွက်နဲ့ သက်တမ်းကုန်ရက်တွေကို Batch လိုက် ခွဲသိမ်း
    # medicines table ရဲ့ id နဲ့ ချိတ်ဆက်ဖို medicine_id (FOREIGN KEY) ကို သုံးထား
    c.execute("""
    CREATE TABLE IF NOT EXISTS medicine_batches(
        batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        batch_number TEXT NOT NULL,
        qty INTEGER NOT NULL,
        expiry TEXT NOT NULL,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
    )
    """)
    
    # Login Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'Staff',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Audit Logs Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT NOT NULL,
        role TEXT NOT NULL,
        action TEXT NOT NULL,
        module TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Sales Header
    c.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT UNIQUE,
        cashier TEXT,
        sale_date TEXT,
        grand_total INTEGER
    )
    """)

    # Sales Items
    c.execute("""
    CREATE TABLE IF NOT EXISTS sale_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        medicine_id INTEGER,
        medicine_name TEXT,
        qty INTEGER,
        price INTEGER,
        subtotal INTEGER,
        FOREIGN KEY(sale_id) REFERENCES sales(id)
    )
    """)

    # Categories table
    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cat_name TEXT NOT NULL UNIQUE
    )
    """)
    
    # Suppliers Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        phone TEXT,
        email TEXT,
        address TEXT
    )
    """)

    # ===== Add unit_price column for old databases =====
    c.execute("PRAGMA table_info(medicines)")
    columns = [column[1] for column in c.fetchall()]

    if "unit_price" not in columns:
        c.execute("""
            ALTER TABLE medicines
            ADD COLUMN unit_price INTEGER NOT NULL DEFAULT 0
        """)
    
<<<<<<< HEAD
    # စမ်းသပ်ရန် အကောင့်တစ်ခု ကြိုထည့်ထားခြင်း
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (?, ?, ?)", (1, "admin", "admin123"))
=======
    admin_hash = hash_password("admin123")

    c.execute("""
    INSERT OR IGNORE INTO users
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
        "admin",
        admin_hash,
        "Admin"
    ))
>>>>>>> origin/king-receipt-update
    
    conn.commit()
    conn.close()

def log_action(
        user_id,
        username,
        role,
        action,
        module,
        description
    ):

        conn = db()
        c = conn.cursor()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
        INSERT INTO audit_logs
        (
            user_id,
            username,
            role,
            action,
            module,
            description,
            created_at
        )
        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """,
        (
            user_id,
            username,
            role,
            action,
            module,
            description,
            current_time
        ))

        conn.commit()
        conn.close()