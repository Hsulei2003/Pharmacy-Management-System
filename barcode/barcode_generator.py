import barcode
from barcode.writer import ImageWriter

def generate_barcode(code, filename):
    barcode_class = barcode.get_barcode_class('code128')
    
    # 🌟 [ရှည်ရှည်မျောမျော သေးသေးပြားပြား ဖြစ်စေမည့် အချိုးအစားအသစ်]
    render_options = {
        'module_width': 0.35,      # 👈 0.2 ကနေ 0.35 ကို တိုးလိုက်လို ဘေးဘက်ကို ရှည်ရှည်မျောမျော ဖြစ်သွားပါမယ်
        'module_height': 5.0,      # 👈 အမြင့်ကို 8.0 ကနေ 5.0 အထိ ထပ်လျှော့ချလိုက်လို အပြားလိုက် သေးသေးလေး ဖြစ်သွားပါမယ်
        'font_size': 7,            # အောက်က ဂဏန်းစာလုံးကို အချိုးကျအောင် သေးထားပါတယ်
        'text_distance': 2.5,      # မြင်းကြောင်းနဲ့ ဂဏန်းစာသား ကြားအကွာအဝေး
        'quiet_zone': 3.0,         # ဘယ်/ညာ ဘေးဘောင်လွတ်ခန့်ခွဲမှု
        'write_text': True         # ဂဏန်းစာသား ဆက်ပြထားမည်
    }
    
    # ပြင်ဆင်ထားတဲ့ Options တွေနဲ့အတူ ဘားကုဒ်ပုံကို Image အဖြစ် သိမ်းဆည်းခြင်း
    my_barcode = barcode_class(code, writer=ImageWriter())
    my_barcode.save(filename, options=render_options)