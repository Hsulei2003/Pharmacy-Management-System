import sqlite3
from authentication.security import hash_password

def db():
    return sqlite3.connect("pharmacy.db", timeout=20)

def create_table():
    conn = db()
    c = conn.cursor()
    
    # 🌟 ၁။ Medicines Table (ဆေးအချက်အလက် ပုံသေဇယား)
    # ဒီနေရာမှာ ခဏခဏပြောင်းလဲမယ့် qty နဲ့ expiry ကို ဖြုတ်ပစ်လိုက်ပါပြီ။
    c.execute("""
    CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        barcode TEXT NOT NULL UNIQUE,
        category TEXT,
        supplier TEXT NOT NULL DEFAULT 'Unknown'
    )
    """)
    
    # 🌟 ၂။ Medicine Batches Table (ဆေးအဝင်အုပ်စု ဇယားသစ်)
    # ဆေးတစ်မျိုးချင်းစီရဲ့ အရေအတွက်နဲ့ သက်တမ်းကုန်ရက်တွေကို Batch လိုက် ခွဲသိမ်းမယ့်နေရာဖြစ်ပါတယ်။
    # medicines table ရဲ့ id နဲ့ ချိတ်ဆက်ဖို medicine_id (FOREIGN KEY) ကို သုံးထားပါတယ်ဗျာ။
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
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

        c.execute("""
        INSERT INTO audit_logs
        (
            user_id,
            username,
            role,
            action,
            module,
            description
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
            user_id,
            username,
            role,
            action,
            module,
            description
        ))

        conn.commit()
        conn.close()