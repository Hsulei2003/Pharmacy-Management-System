import barcode
from barcode.writer import ImageWriter

def generate_barcode(code, filename):
    barcode_class = barcode.get_barcode_class('code128')
    
    render_options = {
        'module_width': 0.35,     
        'module_height': 5.0,      
        'font_size': 7,           
        'text_distance': 2.5,      
        'quiet_zone': 3.0,        
        'write_text': True         
    }
    
    my_barcode = barcode_class(code, writer=ImageWriter())
    my_barcode.save(filename, options=render_options)