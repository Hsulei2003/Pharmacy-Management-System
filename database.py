import sqlite3

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
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
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
    
    # စမ်းသပ်ရန် အကောင့်တစ်ခု ကြိုထည့်ထားခြင်း
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (?, ?, ?)", (1, "admin", "admin123"))
    
    conn.commit()
    conn.close()