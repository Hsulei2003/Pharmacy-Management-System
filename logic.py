from datetime import datetime, timedelta
# ---------- STATUS CHECK ----------
def get_status(expiry):
    try:
        exp = datetime.strptime(expiry, "%Y-%m-%d")
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

# 🌟 Supplier အသစ်သိမ်းရန် Function
def add_supplier_to_db(name, phone, email, address):
    from database import db
    try:
        conn = db()
        c = conn.cursor()
        c.execute("INSERT INTO suppliers (name, phone, email, address) VALUES (?, ?, ?, ?)", (name, phone, email, address))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False
    
    # 🌟 Supplier အားလုံးကို ဆွဲထုတ်ရန် (Add Supplier Page ဇယားအတွက်)
def get_suppliers_list_details():
    from database import db
    conn = db()
    c = conn.cursor()
    c.execute("SELECT id, name, phone, email, address FROM suppliers ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# 🌟 Supplier အားလုံးကို Dropdown Combobox အတွက် ဆွဲထုတ်ပေးမည့် Function
def get_all_suppliers():
    from database import db
    conn = db()
    c = conn.cursor()
    c.execute("SELECT name FROM suppliers ORDER BY name ASC")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# 🌟 Supplier ဖျက်ရန် Function
def delete_supplier_from_db(sup_id):
    from database import db
    try:
        conn = db()
        c = conn.cursor()
        c.execute("DELETE FROM suppliers WHERE id=?", (sup_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False
    
    # 🌟 ၅။ ဆေးဝါးအသစ် (သိုမဟုတ်) Batch အသစ် သိမ်းဆည်းရန် Function
# =====================================================================
def add_medicine_to_db(name, barcode, category, batch_number, qty, expiry, supplier):
    from database import db
    conn = db()
    c = conn.cursor()
    
    try:
        # အဆင့် (၁) - ရိုက်ထည့်လိုက်တဲ့ Barcode က medicines table ထဲမှာ ရှိပြီးသားလား အရင်စစ်မယ်
        c.execute("SELECT id FROM medicines WHERE barcode = ?", (barcode,))
        result = c.fetchone()
        
        if result:
            # ရှိပြီးသားဆိုရင် ဆေးရဲ့ id ကို ယူမယ်
            medicine_id = result[0]
            
            # ရှိပြီးသားဆေးဖြစ်တဲ့အတွက် နာမည်နဲ့ supplier တူရင် ထပ်မပြင်ချင်ပေမယ့် 
            # ပြောင်းလဲခဲ့ရင် အဆင်ပြေအောင် ဆေးအချက်အလက်ကို UPDATE လုပ်ပေးနိုင်ပါတယ် (Optional)
            c.execute(
                "UPDATE medicines SET name=?, category=?, supplier=? WHERE id=?",
                (name, category, supplier, medicine_id)
            )
        else:
            # မရှိသေးဘူးဆိုရင် ဆေးအသစ်အနေနဲ့ medicines table ထဲကို အရင် INSERT လုပ်မယ်
            c.execute(
                "INSERT INTO medicines (name, barcode, category, supplier) VALUES (?, ?, ?, ?)",
                (name, barcode, category, supplier)
            )
            # ခုနကမှ အသစ်ဝင်သွားတဲ့ ဆေးရဲ့ Auto-increment ID ကို လှမ်းယူခြင်း
            medicine_id = c.lastrowid
            
        # အဆင့် (၂) - ရလာတဲ့ medicine_id အောက်မှာ ဆေးအဝင်အုပ်စု (Batch) ကို ဆောက်ပြီး အရေအတွက်နဲ့ Expiry သွင်းမယ်
        c.execute(
            "INSERT INTO medicine_batches (medicine_id, batch_number, qty, expiry) VALUES (?, ?, ?, ?)",
            (medicine_id, batch_number, qty, expiry)
        )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Add Medicine Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# =====================================================================
# 🌟 ၆။ ဆေးစာရင်းဇယား (Medicine List) အတွက် ဒေတာထုတ်ပေးမည့် Function
# =====================================================================
def get_medicines_list_details():
    import datetime
    from database import db
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    conn = db()
    c = conn.cursor()
    
    # 🌟 ရှင်းလင်းချက် Query - 
    # ၁။ စတော့ခ်ရှိသေးသော ဘတ်ချ်များထဲမှ အစောဆုံး သက်တမ်းကုန်မည့်ရက် (Nearest Expiry) ကို တွက်သည်။
    # ၂။ အကယ်၍ စတော့ခ်အားလုံး 0 ဖြစ်နေပါက ရှိသမျှ ဘတ်ချ်ထဲမှ ရက်စွဲကို ယူပြီး Status ကို "No Stock" ဟု သတ်မှတ်သည်။
    c.execute("""
        SELECT 
            m.id, 
            m.name, 
            m.barcode, 
            m.category,
            COALESCE(SUM(b.qty), 0) as total_qty,
            -- စတော့ခ်ကျန်သေးတဲ့ ဘတ်ချ်တွေရဲ့ သက်တမ်းကို ဦးစားပေးယူမည်၊ မရှိရင် အားလုံးထဲက အစောဆုံးရက်ကိုယူမည်
            COALESCE(
                MIN(CASE WHEN b.qty > 0 THEN b.expiry END), 
                MIN(b.expiry)
            ) as nearest_expiry,
            m.supplier
        FROM medicines m
        LEFT JOIN medicine_batches b ON m.id = b.medicine_id
        GROUP BY m.id
        ORDER BY m.id DESC
    """)
    rows = c.fetchall()
    
    final_details = []
    for row in rows:
        med_id, name, barcode, category, total_qty, expiry, supplier = row
        
        # သက်တမ်းကုန်ရက် မရှိခဲ့လျှင် (ဘတ်ချ် လုံးဝမသွင်းရသေးလျှင်)
        if not expiry:
            expiry = "No Batch"
            status = "No Stock" if total_qty == 0 else "Normal"
        
        # 🌟 စတော့ခ် လုံးဝမရှိတော့လျှင် Status ကို "No Stock" ဟု တန်းသတ်မှတ်မည်
        elif total_qty == 0:
            status = "No Stock"
            
        else:
            # စတော့ခ်ရှိသေးလျှင် လက်ရှိရက်စွဲနှင့် နှိင်းယှဉ်၍ အမှန်တကယ် အရောင်ပြောင်းမည်
            exp_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
            today = datetime.date.today()
            
            if exp_date < today:
                status = "Expired"
            elif (exp_date - today).days <= 7: # ၃၀ ရက်အတွင်းဆိုလျှင်
                status = "Near Expiry"
            else:
                status = "Normal"
                
        final_details.append((med_id, name, barcode, category, total_qty, expiry, supplier, status))
        
    conn.close()
    return final_details


# =====================================================================
# 🌟 ၇။ ဆေးဝါးတစ်ခုလုံးကို ဖျက်ရန် Function (CASCADE ကြောင့် Batch တွေပါ အလိုအလျောက် ပျောက်သွားမည်)
# =====================================================================
def delete_medicine_from_db(med_id):
    from database import db
    try:
        conn = db()
        c = conn.cursor()
        c.execute("DELETE FROM medicines WHERE id=?", (med_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Delete Medicine Error: {e}")
        return False
