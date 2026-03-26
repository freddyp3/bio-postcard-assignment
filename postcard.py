from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

W, H = letter  # 612 x 792

DEEP_OCEAN = colors.HexColor("#0a1628")
MIDNIGHT = colors.HexColor("#0d1f3c")
TEAL = colors.HexColor("#00b4d8")
CYAN_LIGHT = colors.HexColor("#90e0ef")
SAND = colors.HexColor("#f5e6c8")
CORAL = colors.HexColor("#ff6b6b")
WHITE = colors.white
GOLD = colors.HexColor("#ffd166")

def draw_ocean_bg(c, x, y, w, h):
    # Deep gradient-like background using overlapping rects
    steps = 20
    for i in range(steps):
        t = i / steps
        r = 0.04 + t * 0.04
        g = 0.12 + t * 0.08
        b = 0.24 + t * 0.16
        c.setFillColorRGB(r, g, b)
        c.rect(x, y + (i/steps)*h, w, h/steps + 1, fill=1, stroke=0)

def draw_bubbles(c, x, y, w, h):
    import random
    random.seed(42)
    c.setStrokeColor(CYAN_LIGHT)
    c.setFillColorRGB(0.5, 0.9, 1.0, 0.15)
    for _ in range(18):
        bx = x + random.uniform(0.05, 0.95) * w
        by = y + random.uniform(0.05, 0.95) * h
        br = random.uniform(3, 10)
        c.setLineWidth(0.5)
        c.circle(bx, by, br, fill=1, stroke=1)

def draw_wavy_lines(c, x, y, w, h):
    c.setStrokeColor(colors.HexColor("#1a4a6e"))
    c.setLineWidth(0.8)
    import math
    for row in range(0, int(h), 18):
        p = c.beginPath()
        step = 8
        p.moveTo(x, y + row)
        for i in range(0, int(w) + 1, step):
            px = min(x + i, x + w)
            wave_y = y + row + math.sin((i + row) * 0.07) * 4
            p.lineTo(px, wave_y)
        c.drawPath(p, stroke=1, fill=0)

def draw_mimic_octopus(c, cx, cy, scale=1.0):
    """Mimic octopus with brown/cream striped banded arms like the real thing"""
    import math

    BROWN = colors.HexColor("#5c2d0e")
    CREAM = colors.HexColor("#e8c99a")
    DARK_BROWN = colors.HexColor("#3a1a06")
    MID_BROWN = colors.HexColor("#8b4513")

    def striped_arm(c, sx, sy, pts, arm_width, scale):
        """Draw a tapered arm with alternating brown/cream bands"""
        segs = len(pts) - 1
        for i in range(segs):
            x1, y1 = pts[i]
            x2, y2 = pts[i+1]
            t = i / segs
            w = arm_width * (1 - t * 0.75) * scale
            # alternate color
            fill = BROWN if i % 2 == 0 else CREAM
            c.setFillColor(fill)
            c.setStrokeColor(DARK_BROWN)
            c.setLineWidth(0.4 * scale)
            # draw as a short thick line segment
            angle = math.atan2(y2 - y1, x2 - x1)
            perp = angle + math.pi/2
            offx = math.cos(perp) * w
            offy = math.sin(perp) * w
            path = c.beginPath()
            path.moveTo(x1 + offx, y1 + offy)
            path.lineTo(x2 + offx, y2 + offy)
            path.lineTo(x2 - offx, y2 - offy)
            path.lineTo(x1 - offx, y1 - offy)
            path.close()
            c.drawPath(path, fill=1, stroke=1)

    def make_arm(cx, cy, angle_deg, length, curl, num_pts=12):
        pts = []
        angle = math.radians(angle_deg)
        for i in range(num_pts):
            t = i / (num_pts - 1)
            # curl increases along arm
            a = angle + math.radians(curl * t * t)
            r = length * t
            x = cx + math.cos(a) * r
            y = cy + math.sin(a) * r
            pts.append((x, y))
        return pts

    # 8 arms — spread evenly around body for visual balance
    # Right-side arms are shorter so they stay within the left panel
    arms = [
        (200, 55 * scale, -25),     # left-down
        (240, 52 * scale, 20),      # down-left
        (280, 45 * scale, 40),      # down
        (320, 35 * scale, 55),      # down-right (short)
        (160, 50 * scale, -40),     # up-left
        (120, 45 * scale, -60),     # up-left
        (70,  35 * scale, -50),     # up-right (short)
        (30,  30 * scale, 40),      # right (short)
    ]

    for angle_deg, length, curl in arms:
        pts = make_arm(cx, cy, angle_deg, length * scale, curl)
        striped_arm(c, cx, cy, pts, 4.5, scale)

    # Mantle (body) - elongated oval
    c.setFillColor(BROWN)
    c.setStrokeColor(DARK_BROWN)
    c.setLineWidth(1.2 * scale)
    # draw mantle as ellipse-like shape
    mantle_w = 18 * scale
    mantle_h = 24 * scale
    c.ellipse(cx - mantle_w, cy, cx + mantle_w, cy + mantle_h, fill=1, stroke=1)

    # Mantle spots/texture
    for (ox, oy, sr) in [(-5, 14, 3), (4, 18, 2.5), (-2, 8, 2)]:
        c.setFillColor(DARK_BROWN)
        c.circle(cx + ox*scale, cy + oy*scale, sr * scale, fill=1, stroke=0)

    # Cream band across mantle
    c.setFillColor(CREAM)
    c.setStrokeColor(DARK_BROWN)
    c.setLineWidth(0.5 * scale)
    c.ellipse(cx - mantle_w*0.7, cy + mantle_h*0.35, cx + mantle_w*0.7, cy + mantle_h*0.55, fill=1, stroke=1)

    # Eye (rectangular pupil like real octopus)
    c.setFillColor(CREAM)
    c.circle(cx + 7*scale, cy + 4*scale, 4*scale, fill=1, stroke=0)
    c.setFillColor(DARK_BROWN)
    c.circle(cx + 7*scale, cy + 4*scale, 2.5*scale, fill=1, stroke=0)
    # rectangular pupil
    c.setFillColor(colors.HexColor("#1a0a00"))
    c.rect(cx + 5.5*scale, cy + 3*scale, 3*scale, 1.5*scale, fill=1, stroke=0)

# FRONT
def draw_front(c):
    FX, FY = 36, H/2 + 20
    FW, FH = W - 72, H/2 - 56

    # Clip all ocean artwork to the panel boundary
    c.saveState()
    clip = c.beginPath()
    clip.rect(FX, FY, FW, FH)
    c.clipPath(clip, stroke=0, fill=0)

    draw_ocean_bg(c, FX, FY, FW, FH)
    draw_wavy_lines(c, FX, FY, FW, FH)
#    draw_bubbles(c, FX, FY, FW, FH)
    c.restoreState()

    # Border
    c.setStrokeColor(TEAL)
    c.setLineWidth(2.5)
    c.rect(FX, FY, FW, FH, fill=0, stroke=1)

    # Inner accent border
    c.setStrokeColor(colors.HexColor("#023e8a"))
    c.setLineWidth(1)
    c.rect(FX+6, FY+6, FW-12, FH-12, fill=0, stroke=1)

    # Octopus illustration - centered in left half of front panel
    oct_cx = FX + FW * 0.30
    oct_cy = FY + FH * 0.48
    draw_mimic_octopus(c, oct_cx, oct_cy, scale=1.5)

    # ── Right column text content ──
    rx = FX + FW * 0.54          # right column left edge (small margin from center)
    max_w = FW * 0.42            # text wrap width

    # "ORGANISM OF THE DAY" label
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(rx, FY + FH - 22, "ORGANISM OF THE DAY")

    # Divider line under label
    c.setStrokeColor(TEAL)
    c.setLineWidth(1)
    c.line(rx, FY + FH - 26, FX + FW - 16, FY + FH - 26)

    # Title
    c.setFillColor(SAND)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(rx, FY + FH - 54, "Mimic Octopus")

    # Scientific name
    c.setFillColor(CYAN_LIGHT)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(rx, FY + FH - 70, "Thaumoctopus mimicus")

    # Habitat tag — centered text
    hab_pill_w, hab_pill_h = 115, 14
    hab_y = FY + FH - 90
    c.setFillColor(colors.HexColor("#023e8a"))
    c.roundRect(rx, hab_y, hab_pill_w, hab_pill_h, 4, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(rx + hab_pill_w / 2, hab_y + (hab_pill_h - 7.5) / 2 + 1, "Indo-Pacific  |  Benthic Zone")

    # Fun facts section
    facts = [
        ("FACT 1", "ECOLOGY", "Chooses from its 15+ disguises based on the specific predator. For example, it mimics sea snakes to deter damselfish."),
        ("FACT 2", "ECOLOGY", "In 2011, researchers found the mimic octopus has its own copycat: the harlequin jawfish, which shadows the octopus and blends in with its arm coloring to avoid detection."),
        ("FACT 3", "EVOLUTION", "It also uses mimicry offensively to hunt. For example, it pretends to be a crab seeking a mate, then devours the deceived crab."),
    ]

    label_colors = {
        "ECOLOGY": colors.HexColor("#2ec4b6"),
        "EVOLUTION": colors.HexColor("#ff9f1c"),
    }

    fy = FY + FH - 114
    for title, tag, text in facts:
        # Fact number
        c.setFillColor(SAND)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(rx, fy, title)

        # Tag pill — centered text
        pill_x = rx + 38
        pill_w, pill_h = 52, 11
        pill_y = fy - 3
        pill_color = label_colors.get(tag, TEAL)
        c.setFillColor(pill_color)
        c.roundRect(pill_x, pill_y, pill_w, pill_h, 3, fill=1, stroke=0)
        c.setFillColor(DEEP_OCEAN)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(pill_x + pill_w / 2, pill_y + (pill_h - 6) / 2 + 1, tag)

        # Fact text (wrapped manually)
        c.setFillColor(WHITE)
        c.setFont("Helvetica", 7.5)
        words = text.split()
        line = ""
        line_y = fy - 14
        for word in words:
            test = line + word + " "
            if c.stringWidth(test, "Helvetica", 7.5) < max_w:
                line = test
            else:
                c.drawString(rx, line_y, line.strip())
                line_y -= 11
                line = word + " "
        if line:
            c.drawString(rx, line_y, line.strip())
            line_y -= 11

        fy = line_y - 12

    # "POSTCARD" label top-left
    c.setFillColor(colors.HexColor("#1a3a5c"))
    c.setFont("Helvetica-Bold", 7)
    c.drawString(FX + 12, FY + FH - 14, "POSTCARD  //  FRONT")


# BACK
def draw_back(c):
    BX, BY = 36, 28
    BW, BH = W - 72, H/2 - 56

    # Subtle background
    c.setFillColor(colors.HexColor("#f7f3ed"))
    c.rect(BX, BY, BW, BH, fill=1, stroke=0)

    # Texture lines (like aged paper) — inset so they don't touch the border
    c.setStrokeColor(colors.HexColor("#e8dfd0"))
    c.setLineWidth(0.4)
    margin = 4
    for i in range(margin, int(BH) - margin, 14):
        c.line(BX + margin, BY + i, BX + BW - margin, BY + i)

    # Main border
    c.setStrokeColor(colors.HexColor("#0a1628"))
    c.setLineWidth(2)
    c.rect(BX, BY, BW, BH, fill=0, stroke=1)

    # Center dividing line
    mid_x = BX + BW * 0.52
    c.setStrokeColor(colors.HexColor("#0a1628"))
    c.setLineWidth(1)
    c.line(mid_x, BY + 10, mid_x, BY + BH - 10)

    # ─ LEFT SIDE: message ─
    c.setFillColor(colors.HexColor("#0a1628"))
    c.setFont("Helvetica-Bold", 7)
    c.drawString(BX + 12, BY + BH - 18, "A NOTE FROM A BIOL 111 STUDENT:")

    c.setStrokeColor(colors.HexColor("#0a1628"))
    c.setLineWidth(0.5)
    c.line(BX + 12, BY + BH - 21, mid_x - 10, BY + BH - 21)

    msg = (
        "Hi! Did you know the mimic octopus can impersonate over 15 "
        "different dangerous marine species? It lives on exposed sandy "
        "seafloors with nowhere to hide, so it evolved the most creative "
        "defense in the ocean. Next time you feel unprepared for a "
        "challenge, just ask: WWMOD? (What Would Mimic Octopus Do?)"
    )
    c.setFont("Helvetica-Oblique", 8.5)
    c.setFillColor(colors.HexColor("#1a1a2e"))
    words = msg.split()
    line = ""
    ly = BY + BH - 38
    max_w = (mid_x - BX - 24)
    for word in words:
        test = line + word + " "
        if c.stringWidth(test, "Helvetica-Oblique", 8.5) < max_w:
            line = test
        else:
            c.drawString(BX + 12, ly, line.strip())
            ly -= 13
            line = word + " "
    if line:
        c.drawString(BX + 12, ly, line.strip())
        ly -= 13

    # Signature
    c.setFont("Helvetica-BoldOblique", 9)
    c.setFillColor(colors.HexColor("#0a1628"))
    c.drawString(BX + 12, ly - 8, "- Fredrik")

    # PS
    ps_text = (
        "P.S. Hey Professor Lynn, I am a computer science student and I created "
        "this postcard in code with a programming language called Python. The picture is "
        "digital but not from the internet, I created it myself! I have attached a link to my code "
        "in case you're curious :)."
    )
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.HexColor("#3a3a5c"))
    ps_words = ps_text.split()
    ps_line = ""
    ps_y = ly - 24
    ps_max_w = mid_x - BX - 24
    for word in ps_words:
        test = ps_line + word + " "
        if c.stringWidth(test, "Helvetica-Oblique", 7) < ps_max_w:
            ps_line = test
        else:
            c.drawString(BX + 12, ps_y, ps_line.strip())
            ps_y -= 10
            ps_line = word + " "
    if ps_line:
        c.drawString(BX + 12, ps_y, ps_line.strip())

    # ─ RIGHT SIDE: address + stamp ─
    # Stamp box top-right
    stamp_x = BX + BW - 60
    stamp_y = BY + BH - 58
    c.setFillColor(DEEP_OCEAN)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.5)
    c.rect(stamp_x, stamp_y, 48, 40, fill=1, stroke=1)

    # Maple leaf on stamp — coordinates from turtle graphics implementation
    # Source: https://stackoverflow.com/a/74275513 (CC BY-SA 4.0)
    # Turtle coords are already in standard Cartesian (Y-up), same as PDF
    leaf_pts = [
        (1, -3), (5, -4), (4, -3), (9, 1), (7, 2), (8, 5),
        (5, 4), (5, 5), (3, 4), (4, 9), (2, 7), (0, 10),
        (-2, 7), (-4, 8), (-3, 3), (-5, 6), (-5, 4), (-8, 5),
        (-7, 2), (-9, 1), (-4, -3), (-5, -4), (0, -3),
        (0, -7), (0, -6), (1, -3),
    ]
    leaf_cx = stamp_x + 24
    leaf_cy = stamp_y + 23
    ls = 1.45
    c.setFillColor(colors.HexColor("#ff0000"))
    c.setStrokeColor(colors.HexColor("#cc0000"))
    c.setLineWidth(0.3)
    p = c.beginPath()
    px0, py0 = leaf_pts[0]
    p.moveTo(leaf_cx + px0 * ls, leaf_cy + py0 * ls)
    for px, py in leaf_pts[1:]:
        p.lineTo(leaf_cx + px * ls, leaf_cy + py * ls)
    p.close()
    c.drawPath(p, fill=1, stroke=1)

    c.setFillColor(CYAN_LIGHT)
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(stamp_x + 24, stamp_y + 5, "CANADA")

    # "Please mail to:"
    c.setFillColor(colors.HexColor("#0a1628"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 12, BY + BH - 80, "Please mail to:")

    # Address lines
    c.setFont("Helvetica", 9)
    addr_lines = [
        "Professor & BIOL 111 Team",
        "Department of Biology",
        "University of British Columbia",
        "Vancouver, BC  B1O 1L1",
    ]
    ay = BY + BH - 98
    for line in addr_lines:
        c.drawString(mid_x + 12, ay, line)
        # underline
        lw = c.stringWidth(line, "Helvetica", 9)
        c.setStrokeColor(colors.HexColor("#aaa090"))
        c.setLineWidth(0.4)
        c.line(mid_x + 12, ay - 2, mid_x + 12 + max(lw, 140), ay - 2)
        ay -= 18

    # Return address
    c.setFillColor(colors.HexColor("#555"))
    c.setFont("Helvetica", 6.5)
    c.drawString(mid_x + 12, BY + 18, "From: Fredrik  |  BIOL 111 (S2026)")

    # "POSTCARD" label
    c.setFillColor(colors.HexColor("#aaa090"))
    c.setFont("Helvetica-Bold", 6)
    c.drawString(BX + 12, BY + 8, "POSTCARD  //  BACK")


# BUILD
c = canvas.Canvas("/Users/fredrikpettit/Documents/postcard/mimic_octopus_postcard.pdf", pagesize=letter)

draw_front(c)
draw_back(c)

c.save()
print("Done")