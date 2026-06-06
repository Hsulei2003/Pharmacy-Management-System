import sqlite3

def db():
    return sqlite3.connect("pharmacy.db", timeout=20)

def create_table():
    conn = db()
    c = conn.cursor()
    
    # ဆေးဝါးစာရင်း Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        barcode TEXT UNIQUE,
        category TEXT,
        qty INTEGER,
        expiry TEXT
    )
    """)
    
    # Login အတွက် Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    
    # စမ်းသပ်ရန် အကောင့်တစ်ခု ကြိုထည့်ထားခြင်း (ရှိပြီးသားဆိုရင် ထပ်မထည့်ပါ)
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
    
    conn.commit()
    conn.close()