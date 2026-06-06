from datetime import datetime, timedelta
# ---------- STATUS CHECK ----------
def get_status(expiry):
    try:
        exp = datetime.strptime(expiry, "%Y-%m-%d")
    except:
        try:
            exp = datetime.strptime(expiry, "%d/%m/%y")
        except:
            return "Invalid"

    today = datetime.today()

    if exp < today:
        return "Expired"
    elif exp <= today + timedelta(days=7):
        return "Near Expiry"
    else:
        return "Normal"
    
def get_all_categories():
    from database import db
    conn = db()
    c = conn.cursor()
    # Database ထဲက category နာမည်တွေကို ဆွဲထုတ်ခြင်း
    c.execute("SELECT cat_name FROM categories ORDER BY cat_name ASC")
    rows = c.fetchall()
    conn.close()
    
    # ရလာတဲ့ ဒေတာတွေကို list ပုံစံပြောင်းပစ်ခြင်း (ဥပမာ- ["💊 Capsule", "⚪️ Tablet"])
    return [row[0] for row in rows]
