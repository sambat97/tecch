from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime, timedelta
import random
import io
import requests
import textwrap

# =====================================================
# UTILITAS GAMBAR & FONT
# =====================================================

def image_to_bytes(image, format="PNG"):
    """
    Mengubah PIL Image menjadi BytesIO agar bisa dikirim ke Telegram
    atau diupload ke API tanpa harus save ke harddisk.
    """
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)
    img_byte_arr.seek(0)
    return img_byte_arr

def get_font(size, bold=False):
    """Mencari font yang tersedia di sistem (Windows/Linux)."""
    font_names = []
    if bold:
        font_names = ["arialbd.ttf", "Arial-Bold.ttf", "DejaVuSans-Bold.ttf", 
                      "Roboto-Bold.ttf", "OpenSans-Bold.ttf"]
    else:
        font_names = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", 
                      "Roboto-Regular.ttf", "OpenSans-Regular.ttf"]

    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()

def get_fonts_collection():
    """Collection of fonts with better sizing for readability"""
    return {
        "huge": get_font(60, bold=True),      # School name
        "title": get_font(48, bold=True),     # Main titles
        "heading": get_font(40, bold=True),   # Section headers
        "subheading": get_font(32, bold=True),# Sub-headers
        "large": get_font(28, bold=False),    # Important text
        "normal": get_font(24, bold=False),   # Regular text
        "small": get_font(20, bold=False),    # Small text
        "tiny": get_font(16, bold=False)      # Fine print
    }

def fetch_photo(url, target_size=(280, 360)):
    """Fetch and resize photo from URL"""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        img = ImageOps.fit(img, target_size, method=Image.LANCZOS, centering=(0.5, 0.5))
        return img
    except Exception as e:
        print(f"⚠️ Failed to fetch photo: {e}")
        return None

# =====================================================
# 1. FACULTY ID CARD - SheerID Compliant
# =====================================================

def generate_faculty_id(
    teacher_name, 
    teacher_email, 
    school_name, 
    photo_url="https://github.com/oranglemah/ngebot/raw/main/foto.jpg"
):
    """
    Generate K12 Faculty ID Card - SheerID Verification Ready

    CRITICAL FIELDS (SheerID Requirements):
    - First and Last Name (clearly visible)
    - School Name (exact match)
    - Current Date/Valid Date (current academic year)
    - Photo
    - Employee ID
    - Position/Department

    Output: Tuple (ImageObject, employee_id_string, department_string)
    """
    W, H = 1200, 768
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    fonts = get_fonts_collection()

    # Professional color scheme
    primary_color = "#1e3a8a"  # Deep Blue
    accent_color = "#fbbf24"   # Gold/Amber
    text_dark = "#1f2937"
    text_light = "#6b7280"

    # ========== HEADER SECTION ==========
    header_h = 200
    draw.rectangle([(0, 0), (W, header_h)], fill=primary_color)
    draw.rectangle([(0, header_h), (W, header_h + 10)], fill=accent_color)

    # School logo placeholder
    logo_size = 140
    logo_x, logo_y = 50, 30
    draw.ellipse(
        [(logo_x, logo_y), (logo_x + logo_size, logo_y + logo_size)], 
        fill="white", 
        outline=accent_color, 
        width=4
    )
    draw.text(
        (logo_x + logo_size/2, logo_y + logo_size/2), 
        "EDU", 
        fill=primary_color, 
        font=fonts["heading"], 
        anchor="mm"
    )

    # School name - CRITICAL for SheerID
    text_x = logo_x + logo_size + 40
    draw.text(
        (text_x, 70), 
        school_name.upper(), 
        fill="white", 
        font=fonts["huge"]
    )
    draw.text(
        (text_x, 135), 
        "FACULTY IDENTIFICATION CARD", 
        fill="#e0e7ff", 
        font=fonts["subheading"]
    )

    # ========== PHOTO SECTION ==========
    photo_w, photo_h = 280, 360
    photo_x = 60
    photo_y = header_h + 50

    # Photo border
    border_padding = 8
    draw.rectangle(
        [
            (photo_x - border_padding, photo_y - border_padding),
            (photo_x + photo_w + border_padding, photo_y + photo_h + border_padding)
        ],
        fill=primary_color
    )

    # Fetch and place photo
    photo = fetch_photo(photo_url, target_size=(photo_w, photo_h))
    if photo:
        img.paste(photo, (photo_x, photo_y))
    else:
        draw.rectangle(
            [(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], 
            fill="#e5e7eb"
        )
        draw.text(
            (photo_x + photo_w/2, photo_y + photo_h/2), 
            "PHOTO", 
            fill="#9ca3af", 
            font=fonts["heading"], 
            anchor="mm"
        )

    # ========== INFORMATION SECTION ==========
    info_x = photo_x + photo_w + 80
    current_y = header_h + 60

    # Generate employee ID and department
    emp_id = f"FAC-{random.randint(100000, 999999)}"
    departments = [
        "Mathematics",
        "Science & Technology", 
        "English Language Arts",
        "Social Studies",
        "Special Education"
    ]
    dept = random.choice(departments)

    def draw_info_field(label, value, y_pos, value_font=None):
        """Draw field with label and value"""
        if value_font is None:
            value_font = fonts["title"]

        # Label
        draw.text((info_x, y_pos), label.upper(), fill=text_light, font=fonts["small"])

        # Value - BOLD and LARGE for readability
        draw.text(
            (info_x, y_pos + 35), 
            value, 
            fill=text_dark, 
            font=value_font
        )

        # Separator line
        line_y = y_pos + 100
        draw.line(
            [(info_x, line_y), (W - 80, line_y)], 
            fill="#e5e7eb", 
            width=2
        )

        return y_pos + 120

    # NAME - MOST CRITICAL FIELD
    current_y = draw_info_field("FULL NAME", teacher_name, current_y, fonts["huge"])

    # EMPLOYEE ID
    current_y = draw_info_field("EMPLOYEE ID", emp_id, current_y, fonts["title"])

    # DEPARTMENT/POSITION
    current_y = draw_info_field("DEPARTMENT", dept, current_y, fonts["heading"])

    # ========== STATUS BADGE ==========
    badge_y = current_y + 20
    badge_w, badge_h = 280, 80
    draw.rectangle(
        [(info_x, badge_y), (info_x + badge_w, badge_y + badge_h)],
        fill=accent_color
    )
    draw.text(
        (info_x + badge_w/2, badge_y + badge_h/2),
        "FACULTY STAFF",
        fill="white",
        font=fonts["heading"],
        anchor="mm"
    )

    # ========== DATES SECTION - CRITICAL for SheerID ==========
    bottom_y = H - 120

    # Background for dates
    draw.rectangle(
        [(0, bottom_y - 20), (W, H)],
        fill="#f3f4f6"
    )

    # Issue date (within current academic year)
    current_date = datetime.now()
    # Academic year typically starts in August/September
    if current_date.month >= 8:
        academic_year_start = datetime(current_date.year, 8, 1)
    else:
        academic_year_start = datetime(current_date.year - 1, 8, 1)

    # Issue date between academic year start and now
    days_since_start = (current_date - academic_year_start).days
    issue_date = academic_year_start + timedelta(days=random.randint(0, days_since_start))

    # Valid until end of academic year
    if current_date.month >= 8:
        valid_until = datetime(current_date.year + 1, 7, 31)
    else:
        valid_until = datetime(current_date.year, 7, 31)

    # Draw issue date
    draw.text(
        (80, bottom_y + 10),
        "ISSUED:",
        fill=text_light,
        font=fonts["small"]
    )
    draw.text(
        (80, bottom_y + 45),
        issue_date.strftime("%B %d, %Y").upper(),
        fill=text_dark,
        font=fonts["large"]
    )

    # Draw valid until
    draw.text(
        (W - 420, bottom_y + 10),
        "VALID UNTIL:",
        fill=text_light,
        font=fonts["small"]
    )
    draw.text(
        (W - 420, bottom_y + 45),
        valid_until.strftime("%B %d, %Y").upper(),
        fill="#dc2626",
        font=fonts["large"]
    )

    # Academic year indicator
    academic_year_str = f"{academic_year_start.year}-{valid_until.year}"
    draw.text(
        (W/2, bottom_y + 30),
        f"ACADEMIC YEAR {academic_year_str}",
        fill=primary_color,
        font=fonts["heading"],
        anchor="mm"
    )

    print(f"✅ Generated Faculty ID for {teacher_name}")
    print(f"   Employee ID: {emp_id}")
    print(f"   Department: {dept}")
    print(f"   Issue Date: {issue_date.strftime('%m/%d/%Y')}")
    print(f"   Valid Until: {valid_until.strftime('%m/%d/%Y')}")

    return img, emp_id, dept


# =====================================================
# 2. PAY STUB - SheerID Compliant
# =====================================================

def generate_pay_stub(
    teacher_name, 
    teacher_email, 
    school_name, 
    emp_id, 
    department
):
    """
    Generate K12 Teacher Pay Stub - SheerID Verification Ready

    CRITICAL REQUIREMENTS (SheerID):
    - Employee Name (clearly visible)
    - School/District Name
    - Pay Date (within last 90 days - CRITICAL!)
    - Employee ID
    - Payment details

    Output: ImageObject
    """
    W, H = 900, 1200
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    fonts = get_fonts_collection()

    margin = 60
    primary_color = "#1e3a8a"
    text_dark = "#1f2937"
    text_light = "#6b7280"
    bg_light = "#f3f4f6"

    # ========== HEADER SECTION ==========
    # School/District name - CRITICAL
    draw.text(
        (W/2, 60), 
        school_name, 
        fill=primary_color, 
        font=fonts["huge"], 
        anchor="mm"
    )
    draw.text(
        (W/2, 115), 
        "PAYROLL DEPARTMENT", 
        fill=text_light, 
        font=fonts["normal"], 
        anchor="mm"
    )

    # Address line
    addresses = [
        "1234 Education Drive, Suite 100",
        "5678 Learning Boulevard",
        "999 School District Plaza"
    ]
    draw.text(
        (W/2, 150), 
        random.choice(addresses), 
        fill=text_light, 
        font=fonts["small"], 
        anchor="mm"
    )

    # Title line
    draw.line([(margin, 190), (W-margin, 190)], fill=primary_color, width=3)
    draw.text(
        (W/2, 230), 
        "EMPLOYEE EARNINGS STATEMENT", 
        fill=primary_color, 
        font=fonts["title"], 
        anchor="mm"
    )
    draw.line([(margin, 270), (W-margin, 270)], fill=primary_color, width=1)

    # ========== EMPLOYEE INFO BOX ==========
    box_top = 310
    box_height = 240
    draw.rectangle(
        [(margin, box_top), (W-margin, box_top + box_height)], 
        outline=primary_color, 
        width=2
    )

    # Split into two columns
    col1_x = margin + 30
    col2_x = W/2 + 30
    info_y = box_top + 30

    # Left column
    draw.text((col1_x, info_y), "EMPLOYEE NAME:", fill=text_light, font=fonts["small"])
    draw.text(
        (col1_x, info_y + 30), 
        teacher_name, 
        fill=text_dark, 
        font=fonts["heading"]
    )

    draw.text((col1_x, info_y + 90), "EMPLOYEE ID:", fill=text_light, font=fonts["small"])
    draw.text(
        (col1_x, info_y + 120), 
        emp_id, 
        fill=text_dark, 
        font=fonts["large"]
    )

    draw.text((col1_x, info_y + 170), "DEPARTMENT:", fill=text_light, font=fonts["small"])
    draw.text(
        (col1_x, info_y + 200), 
        department, 
        fill=text_dark, 
        font=fonts["normal"]
    )

    # Right column - DATES (CRITICAL for SheerID - must be within 90 days!)
    current_date = datetime.now()
    # Pay date is recent (within last 90 days)
    days_ago = random.randint(7, 75)  # Keep it reasonably recent
    pay_date = current_date - timedelta(days=days_ago)

    # Pay period end = pay date
    pay_period_end = pay_date
    # Pay period start = 2 weeks before (bi-weekly pay)
    pay_period_start = pay_period_end - timedelta(days=14)

    draw.text((col2_x, info_y), "PAY DATE:", fill=text_light, font=fonts["small"])
    draw.text(
        (col2_x, info_y + 30), 
        pay_date.strftime("%m/%d/%Y"), 
        fill=text_dark, 
        font=fonts["heading"]
    )

    draw.text((col2_x, info_y + 90), "PAY PERIOD:", fill=text_light, font=fonts["small"])
    draw.text(
        (col2_x, info_y + 120), 
        f"{pay_period_start.strftime('%m/%d')} - {pay_period_end.strftime('%m/%d/%Y')}", 
        fill=text_dark, 
        font=fonts["large"]
    )

    draw.text((col2_x, info_y + 170), "EMAIL:", fill=text_light, font=fonts["small"])
    # Wrap email if too long
    if len(teacher_email) > 25:
        email_display = teacher_email[:22] + "..."
    else:
        email_display = teacher_email
    draw.text(
        (col2_x, info_y + 200), 
        email_display, 
        fill=text_dark, 
        font=fonts["small"]
    )

    # ========== EARNINGS TABLE ==========
    table_y = 600

    # Table header
    draw.rectangle(
        [(margin, table_y), (W-margin, table_y + 50)], 
        fill=primary_color
    )
    draw.text(
        (margin + 30, table_y + 15), 
        "EARNINGS DESCRIPTION", 
        fill="white", 
        font=fonts["subheading"]
    )
    draw.text(
        (W - margin - 30, table_y + 15), 
        "AMOUNT ($)", 
        fill="white", 
        font=fonts["subheading"], 
        anchor="ra"
    )

    # Earnings rows
    row_y = table_y + 70
    row_height = 45

    # Calculate realistic teacher salary
    # Bi-weekly gross pay for K12 teacher
    base_salary = random.randint(2800, 3800)  # Bi-weekly
    stipend = random.choice([0, 200, 350])  # Optional stipend

    earnings_items = [
        ("Regular Salary - Bi-Weekly", base_salary),
    ]

    if stipend > 0:
        earnings_items.append(("Department Stipend", stipend))

    gross_pay = 0
    for i, (description, amount) in enumerate(earnings_items):
        # Alternate row background
        if i % 2 == 0:
            draw.rectangle(
                [(margin, row_y), (W-margin, row_y + row_height)],
                fill=bg_light
            )

        draw.text(
            (margin + 30, row_y + 10), 
            description, 
            fill=text_dark, 
            font=fonts["normal"]
        )
        draw.text(
            (W - margin - 30, row_y + 10), 
            f"{amount:,.2f}", 
            fill=text_dark, 
            font=fonts["normal"], 
            anchor="ra"
        )

        gross_pay += amount
        row_y += row_height

    # Gross pay total
    row_y += 15
    draw.line([(margin, row_y), (W-margin, row_y)], fill=primary_color, width=2)
    row_y += 20

    draw.rectangle(
        [(margin, row_y), (W-margin, row_y + 60)],
        fill=bg_light
    )
    draw.text(
        (margin + 30, row_y + 15), 
        "GROSS PAY", 
        fill=text_dark, 
        font=fonts["heading"]
    )
    draw.text(
        (W - margin - 30, row_y + 15), 
        f"{gross_pay:,.2f}", 
        fill=text_dark, 
        font=fonts["heading"], 
        anchor="ra"
    )

    # ========== DEDUCTIONS TABLE ==========
    row_y += 100

    draw.rectangle(
        [(margin, row_y), (W-margin, row_y + 50)], 
        fill="#dc2626"  # Red for deductions
    )
    draw.text(
        (margin + 30, row_y + 15), 
        "DEDUCTIONS & TAXES", 
        fill="white", 
        font=fonts["subheading"]
    )

    # Deduction rows
    row_y += 70

    deductions = [
        ("Federal Income Tax", gross_pay * 0.12),
        ("State Income Tax", gross_pay * 0.05),
        ("Social Security (FICA)", gross_pay * 0.062),
        ("Medicare", gross_pay * 0.0145),
        ("Retirement Contribution", gross_pay * 0.05),
    ]

    total_deductions = 0
    for i, (description, amount) in enumerate(deductions):
        if i % 2 == 0:
            draw.rectangle(
                [(margin, row_y), (W-margin, row_y + row_height)],
                fill=bg_light
            )

        draw.text(
            (margin + 30, row_y + 10), 
            description, 
            fill=text_dark, 
            font=fonts["normal"]
        )
        draw.text(
            (W - margin - 30, row_y + 10), 
            f"({amount:,.2f})", 
            fill="#dc2626", 
            font=fonts["normal"], 
            anchor="ra"
        )

        total_deductions += amount
        row_y += row_height

    # Net pay (final)
    net_pay = gross_pay - total_deductions

    row_y += 40
    draw.rectangle(
        [(margin, row_y), (W-margin, row_y + 90)],
        fill=primary_color
    )
    draw.text(
        (margin + 40, row_y + 20), 
        "NET PAY", 
        fill="white", 
        font=fonts["title"]
    )
    draw.text(
        (W - margin - 40, row_y + 25), 
        f"${net_pay:,.2f}", 
        fill="white", 
        font=fonts["huge"], 
        anchor="ra"
    )

    print(f"✅ Generated Pay Stub for {teacher_name}")
    print(f"   Pay Date: {pay_date.strftime('%m/%d/%Y')} (within 90 days)")
    print(f"   Gross Pay: ${gross_pay:,.2f}")
    print(f"   Net Pay: ${net_pay:,.2f}")

    return img


# =====================================================
# 3. EMPLOYMENT VERIFICATION LETTER - SheerID Compliant
# =====================================================

def generate_employment_letter(
    teacher_name, 
    teacher_email, 
    school_name, 
    emp_id, 
    department
):
    """
    Generate Official Employment Verification Letter - SheerID Ready

    CRITICAL REQUIREMENTS (SheerID):
    - Official letterhead with school name
    - Employee full name
    - Current employment status
    - Position/Title
    - Date (current/recent)
    - Signature (authorized person)

    Output: ImageObject
    """
    W, H = 900, 1200
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    fonts = get_fonts_collection()

    margin = 80
    primary_color = "#1e3a8a"
    text_dark = "#1f2937"
    text_light = "#6b7280"

    # ========== LETTERHEAD ==========
    # School name - PROMINENT
    draw.text(
        (W/2, 70), 
        school_name, 
        fill=primary_color, 
        font=fonts["huge"], 
        anchor="mm"
    )

    # Department/Office
    draw.text(
        (W/2, 130), 
        "OFFICE OF HUMAN RESOURCES", 
        fill=text_light, 
        font=fonts["subheading"], 
        anchor="mm"
    )

    # Address
    addresses = [
        "1234 Education Avenue • District Office Building",
        "5678 Learning Drive • Administrative Center",
        "999 School District Road • HR Department"
    ]
    draw.text(
        (W/2, 165), 
        random.choice(addresses), 
        fill=text_light, 
        font=fonts["small"], 
        anchor="mm"
    )

    # Letterhead separator
    draw.line([(margin, 200), (W-margin, 200)], fill=primary_color, width=3)

    # ========== DATE ==========
    letter_date = datetime.now()
    y = 250
    draw.text(
        (margin, y), 
        letter_date.strftime("%B %d, %Y"), 
        fill=text_dark, 
        font=fonts["normal"]
    )

    # ========== SALUTATION ==========
    y = 320
    draw.text(
        (margin, y), 
        "To Whom It May Concern:", 
        fill=text_dark, 
        font=fonts["normal"]
    )

    # ========== TITLE ==========
    y = 410
    draw.rectangle(
        [(margin - 20, y - 10), (W - margin + 20, y + 60)],
        fill="#f3f4f6"
    )
    draw.text(
        (W/2, y + 25), 
        "CERTIFICATE OF EMPLOYMENT", 
        fill=primary_color, 
        font=fonts["title"], 
        anchor="mm"
    )

    # ========== BODY TEXT ==========
    y = 520

    # Calculate employment start date (1-5 years ago)
    years_employed = random.randint(1, 5)
    months_offset = random.randint(0, 11)
    start_date = datetime.now() - timedelta(days=years_employed*365 + months_offset*30)
    start_date_str = start_date.strftime("%B %d, %Y")

    # Position titles
    positions = [
        "Classroom Teacher",
        "Senior Teacher",
        "Lead Teacher",
        "Subject Specialist",
        "Department Chair"
    ]
    position = random.choice(positions)

    # Main certification paragraph
    body_paragraphs = [
        f"This letter serves to certify that {teacher_name} is currently employed with "
        f"{school_name} as a full-time {position} in the {department} Department.",

        f"The employee has been actively employed with our institution since {start_date_str} "
        f"and holds the employee identification number {emp_id}. {teacher_name} maintains "
        f"employment in good standing with our school district.",

        "This certification is being issued at the request of the employee for verification "
        "purposes and may be used for whatever legal purpose it may serve. Should you require "
        "additional information, please feel free to contact our Human Resources office."
    ]

    line_spacing = 38
    paragraph_spacing = 25

    for paragraph in body_paragraphs:
        # Wrap text to fit width
        wrapped_lines = textwrap.wrap(paragraph, width=75)

        for line in wrapped_lines:
            draw.text(
                (margin, y), 
                line, 
                fill=text_dark, 
                font=fonts["normal"]
            )
            y += line_spacing

        y += paragraph_spacing

    # ========== EMPLOYMENT DETAILS BOX ==========
    y += 10
    box_height = 220

    draw.rectangle(
        [(margin, y), (W-margin, y + box_height)],
        outline=primary_color,
        width=2
    )

    # Title bar
    draw.rectangle(
        [(margin, y), (W-margin, y + 45)],
        fill=primary_color
    )
    draw.text(
        (margin + 20, y + 10), 
        "EMPLOYMENT DETAILS", 
        fill="white", 
        font=fonts["heading"]
    )

    # Details rows
    details_y = y + 65
    row_spacing = 42

    details = [
        ("Employee Name:", teacher_name),
        ("Position:", position),
        ("Department:", department),
        ("Employment Status:", "Full-Time, Active"),
    ]

    for label, value in details:
        draw.text(
            (margin + 25, details_y), 
            label, 
            fill=text_light, 
            font=fonts["small"]
        )
        draw.text(
            (margin + 300, details_y), 
            value, 
            fill=text_dark, 
            font=fonts["large"]
        )
        details_y += row_spacing

    # ========== SIGNATURE SECTION ==========
    sig_y = H - 260

    draw.text(
        (margin, sig_y), 
        "Sincerely,", 
        fill=text_dark, 
        font=fonts["normal"]
    )

    # Signature line
    sig_line_y = sig_y + 90
    draw.line(
        [(margin, sig_line_y), (margin + 350, sig_line_y)], 
        fill=text_dark, 
        width=2
    )

    # Signatory names
    hr_directors = [
        "Elizabeth Martinez",
        "Robert Johnson",
        "Patricia Williams",
        "Michael Anderson",
        "Jennifer Thompson"
    ]

    signatory_name = random.choice(hr_directors)

    draw.text(
        (margin, sig_line_y + 15), 
        signatory_name, 
        fill=text_dark, 
        font=fonts["heading"]
    )
    draw.text(
        (margin, sig_line_y + 55), 
        "Director of Human Resources", 
        fill=text_light, 
        font=fonts["normal"]
    )

    # Contact info
    draw.text(
        (margin, sig_line_y + 95), 
        f"Email: hr@{school_name.lower().replace(' ', '')}.edu", 
        fill=text_light, 
        font=fonts["small"]
    )

    # ========== FOOTER ==========
    footer_y = H - 50
    draw.text(
        (W/2, footer_y), 
        "This is an official document | For verification purposes only", 
        fill=text_light, 
        font=fonts["tiny"], 
        anchor="mm"
    )

    print(f"✅ Generated Employment Letter for {teacher_name}")
    print(f"   Position: {position}")
    print(f"   Employment since: {start_date_str}")
    print(f"   Signed by: {signatory_name}")

    return img
