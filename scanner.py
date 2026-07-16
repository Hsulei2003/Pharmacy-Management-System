import cv2
import zxingcpp

class BarcodeScanner:
    def __init__(self):
        pass

    def scan_from_frame(self, frame):
        
        if frame is None:
            return None
            
        results = zxingcpp.read_barcodes(frame)
        
        for result in results:
            if result.text:
                return result.text.strip()
                
        return None