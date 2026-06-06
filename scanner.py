import cv2
import zxingcpp

class BarcodeScanner:
    def __init__(self):
        pass

    def scan_from_frame(self, frame):
        """
        ကင်မရာ Frame ထဲကနေ Barcode ကို အင်မတန်မြန်ဆန်စွာ ရှာဖွေဖတ်ပေးမည့် function
        """
        if frame is None:
            return None
            
        # ဓာတ်ပုံထဲကနေ barcode ရှိမရှိ ချက်ချင်းရှာဖွေခြင်း
        results = zxingcpp.read_barcodes(frame)
        
        # အကယ်၍ barcode မိခဲ့ရင် ဒေတာကို return ပြန်ပေးမည်
        for result in results:
            if result.text:
                return result.text.strip()
                
        return None