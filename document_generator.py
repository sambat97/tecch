from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime, timedelta
import random
import io
import requests
import textwrap
import os

# =====================================================
# KONFIGURASI FONT OTOMATIS (ROBOTO)
# =====================================================

# URL Font Open Source (Roboto) agar hasil pasti rapi di semua OS
FONT_URL_REGULAR = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
FONT_URL_BOLD = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"

# Cache untuk menyimpan font di memori agar tidak download berulang kali
FONT_CACHE = {}

def get_font(size, bold=False):
    """
    Mendapatkan font yang pasti bagus (Roboto).
    Urutan prioritas:
    1. Cek Cache Memori.
    2. Download Roboto dari URL (jika belum ada).
    3. Cari font sistem (Arial/Helvetica).
    4. Default (terburuk).
    """
    key = (size, bold)
    
    # 1. Cek Cache
    if key in FONT_CACHE:
        return FONT_CACHE[key]

    # 2. Coba Download/Load Roboto
    try:
        url = FONT_URL_BOLD if bold else FONT_URL_REGULAR
        
        # Cek jika kita punya internet/bisa akses URL
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            font_bytes = io.BytesIO(resp.content)
            font = ImageFont.truetype(font_bytes, size)
            FONT_CACHE[key] = font
            return font
    except Exception as e:
        # Jika gagal download (misal offline), lanjut ke fallback sistem
        pass

    # 3. Fallback ke Font Sistem (Windows/Linux/Mac)
    system_fonts = []
    if bold:
        system_fonts = ["arialbd.ttf", "Arial Bold", "Arial-Bold.ttf", "DejaVuSans-Bold.ttf", "Helvetica-Bold"]
    else:
        system_fonts = ["arial.ttf", "Arial", "Arial.ttf", "DejaVuSans.ttf", "Helvetica"]

    for name in system_fonts:
        try:
            font = ImageFont.truetype(name, size)
            FONT_CACHE[key] = font
            return font
        except OSError:
            continue
    
    # 4. Pilihan Terakhir (Default PIL - Jelek tapi jalan)
    print(f"⚠️ Warning: Menggunakan font default untuk ukuran {size}")
    return ImageFont.load_default()

def get_fonts_collection():
    """Koleksi font dengan hierarki ukuran yang rapi"""
    return {
        "huge": get_font(60, bold=True),      # Nama Sekolah
        "title": get_font(48, bold=True),     # Judul Utama
        "heading": get_font(38, bold=True),   # Header Seksi
        "subheading": get_font(30, bold=True),# Sub-header
        "large": get_font(26, bold=False),    # Teks Penting
        "normal": get_font(22, bold=False),   # Teks Biasa
        "small": get_font(18, bold=False),    # Teks Kecil
        "tiny": get_font(14, bold=False)      # Footer/Fine print
    }

def fetch_photo(url, target_size=(280, 360)):
    """Ambil foto dari URL dan resize dengan rapi"""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        # Menggunakan LANCZOS untuk hasil resize tajam
        img = ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        return img
    except Exception as e:
        print(f"⚠️ Gagal mengambil foto: {e}")
        return None

# =====================================================
# 1. FACULTY ID CARD (Generator)
# =====================================================

def generate_faculty_id(
    teacher_name, 
    teacher_email, 
    school_name, 
    photo_url="https://github.com/oranglemah/ngebot/raw/main/foto.jpg"
):
    W, H = 1200, 768
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    fonts = get_fonts_collection()

    # Warna Corporate
    primary_color = "#1e3a8a"  # Deep Blue
    accent_color = "#fbbf24"   # Gold
    text_dark = "#111827"
    text_light = "#6b7280"

    # --- Header ---
    header_h = 200
    draw.rectangle([(0, 0), (W, header_h)], fill=primary_color)
    draw.rectangle([(0, header_h), (W, header_h + 12)], fill=accent_color)

    # Logo Placeholder
    logo_size = 140
    logo_x, logo_y = 50, 30
    draw.ellipse(
        [(logo_x, logo_y), (logo_x + logo_size, logo_y + logo_size)], 
        fill="white", outline=accent_color, width=4
    )
    draw.text((logo_x + logo_size/2, logo_y + logo_size/2), "EDU", fill=primary_color, font=fonts["heading"], anchor="mm")

    # Nama Sekolah (Auto-resize jika kepanjangan)
    text_x = logo_x + logo_size + 40
    school_font = fonts["huge"]
    if len(school_name) > 25: 
        school_font = get_font(45, bold=True) # Kecilkan font jika nama panjang
        
    draw.text((text_x, 75), school_name.upper(), fill="white", font=school_font, anchor="lm")
    draw.text((text_x, 140), "FACULTY IDENTIFICATION CARD", fill="#e0e7ff", font=fonts["subheading"], anchor="lm")

    # --- Foto ---
    photo_w, photo_h = 280, 360
    photo_x = 60
    photo_y = header_h + 50
    
    # Border foto
    border = 6
    draw.rectangle(
        [(photo_x - border, photo_y - border), (photo_x + photo_w + border, photo_y + photo_h + border)],
        fill=primary_color
    )
    
    photo = fetch_photo(photo_url, target_size=(photo_w, photo_h))
    if photo:
        img.paste(photo, (photo_x, photo_y))
    else:
        # Placeholder jika foto gagal
        draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], fill="#e5e7eb")
        draw.text((photo_x + photo_w/2, photo_y + photo_h/2), "NO PHOTO", fill="#9ca3af", font=fonts["heading"], anchor="mm")

    # --- Info Guru ---
    info_x = photo_x + photo_w + 80
    current_y = header_h + 60

    emp_id = f"FAC-{random.randint(100000, 999999)}"
    dept = random.choice(["Mathematics", "Science & Tech", "Language Arts", "Social Studies", "Special Ed."])

    def draw_field(label, value, y, value_font=fonts["title"]):
        draw.text((info_x, y), label.upper(), fill=text_light, font=fonts["small"])
        draw.text((info_x, y + 25), value, fill=text_dark, font=value_font)
        draw.line([(info_x, y + 85), (W - 60, y + 85)], fill="#e5e7eb", width=2)
        return y + 105

    current_y = draw_field("FULL NAME", teacher_name, current_y, fonts["huge"])
    current_y = draw_field("EMPLOYEE ID", emp_id, current_y, fonts["title"])
    current_y = draw_field("DEPARTMENT", dept, current_y, fonts["heading"])

    # Badge Status
    badge_y = current_y + 10
    draw.rectangle([(info_x, badge_y), (info_x + 280, badge_y + 60)], fill=accent_color, outline=None)
    draw.text((info_x + 140, badge_y + 30), "ACTIVE FACULTY", fill="white", font=fonts["heading"], anchor="mm")

    # --- Tanggal & Footer ---
    bottom_y = H - 100
    draw.rectangle([(0, bottom_y - 20), (W, H)], fill="#f3f4f6")
    
    now = datetime.now()
    issue_year = now.year if now.month >= 8 else now.year - 1
    valid_until = datetime(issue_year + 1, 7, 31)
    
    draw.text((80, bottom_y + 25), f"ISSUED: {datetime.now().strftime('%B %d, %Y').upper()}", fill=text_dark, font=fonts["normal"])
    draw.text((W - 80, bottom_y + 25), f"EXPIRES: {valid_until.strftime('%B %d, %Y').upper()}", fill="#dc2626", font=fonts["heading"], anchor="rm")
    
    return img, emp_id, dept

# =====================================================
# 2. PAY STUB (Generator)
# =====================================================

def generate_pay_stub(teacher_name, teacher_email, school_name, emp_id, department):
    W, H = 900, 1200
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    fonts = get_fonts_collection()

    margin = 50
    primary_color = "#1e3a8a"
    bg_light = "#f9fafb"

    # --- Header ---
    draw.text((W/2, 60), school_name, fill=primary_color, font=fonts["heading"], anchor="mm")
    draw.text((W/2, 100), "OFFICIAL PAYROLL STATEMENT", fill="#6b7280", font=fonts["normal"], anchor="mm")
    
    # Garis pemisah
    draw.line([(margin, 130), (W-margin, 130)], fill=primary_color, width=3)
    
    # --- Kotak Info ---
    box_y = 160
    box_h = 220
    draw.rectangle([(margin, box_y), (W-margin, box_y + box_h)], outline="#e5e7eb", width=2)
    
    # Kolom Kiri
    col1_x = margin + 30
    info_start_y = box_y + 30
    
    draw.text((col1_x, info_start_y), "EMPLOYEE NAME", fill="#9ca3af", font=fonts["tiny"])
    draw.text((col1_x, info_start_y + 20), teacher_name, fill="black", font=fonts["large"])
    
    draw.text((col1_x, info_start_y + 70), "EMPLOYEE ID", fill="#9ca3af", font=fonts["tiny"])
    draw.text((col1_x, info_start_y + 90), emp_id, fill="black", font=fonts["normal"])

    draw.text((col1_x, info_start_y + 140), "DEPARTMENT", fill="#9ca3af", font=fonts["tiny"])
    draw.text((col1_x, info_start_y + 160), department, fill="black", font=fonts["normal"])

    # Kolom Kanan (Tanggal)
    col2_x = W/2 + 30
    pay_date = datetime.now() - timedelta(days=random.randint(5, 25)) # Recent date
    
    draw.text((col2_x, info_start_y), "PAY DATE", fill="#9ca3af", font=fonts["tiny"])
    draw.text((col2_x, info_start_y + 20), pay_date.strftime("%m/%d/%Y"), fill="black", font=fonts["large"])
    
    draw.text((col2_x, info_start_y + 70), "PAY PERIOD", fill="#9ca3af", font=fonts["tiny"])
    period_start = pay_date - timedelta(days=14)
    draw.text((col2_x, info_start_y + 90), f"{period_start.strftime('%m/%d')} - {pay_date.strftime('%m/%d/%Y')}", fill="black", font=fonts["normal"])

    # --- Tabel Gaji ---
    table_y = 450
    # Header Tabel
    draw.rectangle([(margin, table_y), (W-margin, table_y + 40)], fill=primary_color)
    draw.text((margin + 20, table_y + 10), "DESCRIPTION", fill="white", font=fonts["small"])
    draw.text((W - margin - 20, table_y + 10), "AMOUNT", fill="white", font=fonts["small"], anchor="ra")

    row_y = table_y + 60
    base_salary = random.randint(2900, 3800)
    items = [("Regular Salary", base_salary)]
    if random.choice([True, False]): items.append(("Coaching Stipend", 350))
    
    gross = 0
    for desc, amt in items:
        draw.text((margin + 20, row_y), desc, fill="black", font=fonts["normal"])
        draw.text((W - margin - 20, row_y), f"{amt:,.2f}", fill="black", font=fonts["normal"], anchor="ra")
        gross += amt
        row_y += 40
    
    # Total Gross
    draw.line([(margin, row_y), (W-margin, row_y)], fill="#e5e7eb", width=2)
    row_y += 20
    draw.text((margin + 20, row_y), "GROSS PAY", fill=primary_color, font=fonts["heading"])
    draw.text((W - margin - 20, row_y), f"{gross:,.2f}", fill=primary_color, font=fonts["heading"], anchor="ra")

    # --- Potongan (Deductions) ---
    row_y += 80
    draw.rectangle([(margin, row_y), (W-margin, row_y + 40)], fill="#dc2626")
    draw.text((margin + 20, row_y + 10), "TAXES & DEDUCTIONS", fill="white", font=fonts["small"])
    
    row_y += 60
    deductions = [
        ("Federal Tax", gross * 0.11),
        ("State Tax", gross * 0.04),
        ("FICA/Medicare", gross * 0.0765),
        ("Retirement (403b)", gross * 0.05)
    ]
    
    total_deduct = 0
    for desc, amt in deductions:
        draw.text((margin + 20, row_y), desc, fill="#4b5563", font=fonts["normal"])
        draw.text((W - margin - 20, row_y), f"({amt:,.2f})", fill="#dc2626", font=fonts["normal"], anchor="ra")
        total_deduct += amt
        row_y += 40
        
    # --- Net Pay ---
    net_pay = gross - total_deduct
    final_y = row_y + 40
    draw.rectangle([(margin, final_y), (W-margin, final_y + 80)], fill=primary_color)
    draw.text((margin + 30, final_y + 25), "NET PAY", fill="white", font=fonts["title"])
    draw.text((W - margin - 30, final_y + 25), f"${net_pay:,.2f}", fill="white", font=fonts["title"], anchor="ra")

    return img

# =====================================================
# 3. EMPLOYMENT LETTER (Generator)
# =====================================================

def generate_employment_letter(teacher_name, teacher_email, school_name, emp_id, department):
    W, H = 900, 1200
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    fonts = get_fonts_collection()
    
    margin = 90
    primary_color = "#1e3a8a"

    # --- Letterhead ---
    draw.text((W/2, 70), school_name.upper(), fill=primary_color, font=fonts["heading"], anchor="mm")
    draw.text((W/2, 115), "OFFICE OF HUMAN RESOURCES", fill="#6b7280", font=fonts["small"], anchor="mm")
    draw.text((W/2, 145), "123 Education Blvd, District Office Building", fill="#9ca3af", font=fonts["tiny"], anchor="mm")
    draw.line([(margin, 170), (W-margin, 170)], fill=primary_color, width=3)

    # --- Konten ---
    current_y = 220
    draw.text((margin, current_y), datetime.now().strftime("%B %d, %Y"), fill="black", font=fonts["normal"])
    
    current_y += 80
    draw.text((margin, current_y), "To Whom It May Concern:", fill="black", font=fonts["normal"])
    
    current_y += 60
    draw.text((W/2, current_y), "RE: VERIFICATION OF EMPLOYMENT", fill="black", font=fonts["heading"], anchor="mm")
    draw.line([(margin + 100, current_y + 25), (W - margin - 100, current_y + 25)], fill="black", width=1)

    # Body Paragraphs
    current_y += 80
    start_year = datetime.now().year - random.randint(1, 8)
    
    text_body = (
        f"This letter serves to confirm that {teacher_name} is currently employed with "
        f"{school_name} as a full-time Teacher in the {department} Department.\n\n"
        f"Mr./Ms. {teacher_name.split()[-1]} has been employed with our district since August {start_year} "
        f"and holds the Employee ID {emp_id}. The employee is in good standing.\n\n"
        "If you require any further information regarding this employment verification, "
        "please do not hesitate to contact our Human Resources department directly."
    )
    
    # Text Wrapping yang rapi
    lines = textwrap.wrap(text_body, width=70) # Adjust width sesuai font size
    
    for line in lines:
        if line == "": 
            current_y += 30 # Spasi antar paragraf
        else:
            draw.text((margin, current_y), line, fill="#374151", font=fonts["normal"])
            current_y += 35 # Line height

    # --- Kotak Ringkasan ---
    current_y += 50
    box_pad = 20
    draw.rectangle([(margin, current_y), (W-margin, current_y + 160)], outline=primary_color, width=1)
    
    details_y = current_y + box_pad + 10
    labels = [("Name:", teacher_name), ("Position:", "Full-Time Faculty"), ("Status:", "Active")]
    
    for label, val in labels:
        draw.text((margin + 30, details_y), label, fill="#6b7280", font=fonts["small"])
        draw.text((margin + 200, details_y), val, fill="black", font=fonts["large"])
        details_y += 45

    # --- Tanda Tangan ---
    sig_y = H - 250
    draw.text((margin, sig_y), "Sincerely,", fill="black", font=fonts["normal"])
    
    # Garis TTD
    draw.line([(margin, sig_y + 80), (margin + 300, sig_y + 80)], fill="black", width=2)
    
    hr_name = "Patricia Williams"
    draw.text((margin, sig_y + 95), hr_name, fill="black", font=fonts["heading"])
    draw.text((margin, sig_y + 130), "Director of Human Resources", fill="#6b7280", font=fonts["small"])
    draw.text((margin, sig_y + 155), f"hr@{school_name.split()[0].lower()}.edu", fill=primary_color, font=fonts["tiny"])

    return img
