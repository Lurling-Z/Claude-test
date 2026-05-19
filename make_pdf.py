# -*- coding: utf-8 -*-
"""Professional IELTS Writing Template PDF Generator - Yuanxuetong"""
import json
import os
from fpdf import FPDF

_DIR = os.path.dirname(os.path.abspath(__file__))

FONT_R = "/tmp/fonts/NotoSansSC-Regular.ttf"
FONT_B = "/tmp/fonts/NotoSansSC-Bold.ttf"
LOGO = os.path.join(_DIR, "cover-page/yuanxuetong-logo.png")
OUTPUT = os.path.join(_DIR, "yuanxuetong-ielts-writing-templates.pdf")

with open(os.path.join(_DIR, "pdf_data.json"), "r", encoding="utf-8") as f:
    DATA = json.load(f)

# --- Color Palette ---
BRAND_DARK = (10, 54, 92)
BRAND = (15, 76, 129)
BRAND_LIGHT = (220, 235, 248)
ACCENT = (230, 57, 70)
ACCENT_LIGHT = (255, 240, 241)
GOLD = (212, 175, 55)
SOFT_BG = (247, 249, 252)
CARD_BG = (250, 251, 253)
TEXT_C = (31, 41, 55)
SUB_C = (107, 114, 128)
WHITE = (255, 255, 255)
LINE_C = (220, 225, 232)
SUCCESS = (16, 185, 129)


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("CN", "", FONT_R)
        self.add_font("CN", "B", FONT_B)
        self.set_auto_page_break(auto=True, margin=18)
        self._is_cover = True

    def header(self):
        if self._is_cover:
            return
        # Top brand bar
        self.set_fill_color(*BRAND_DARK)
        self.rect(0, 0, 210, 8, style="F")
        # Gold accent line
        self.set_fill_color(*GOLD)
        self.rect(0, 8, 210, 0.6, style="F")
        # Header text
        self.set_font("CN", "B", 7.5)
        self.set_text_color(*WHITE)
        self.set_xy(12, 1.8)
        self.cell(0, 4.5, "\u6e0a\u5b66\u901a \u00b7 \u96c5\u601d\u5199\u4f5c\u6a21\u677f\u5408\u96c6", align="L")
        self.set_font("CN", "", 7.5)
        self.set_xy(12, 1.8)
        self.cell(0, 4.5, "\u516c\u4f17\u53f7 / \u5c0f\u7ea2\u4e66\uff1a\u6e0a\u5b66\u901a\u676d\u5dde", align="R")
        self.set_text_color(*TEXT_C)
        self.set_y(12)

    def footer(self):
        if self._is_cover:
            return
        self.set_y(-14)
        # Footer line
        self.set_draw_color(*LINE_C)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(2)
        self.set_font("CN", "", 7)
        self.set_text_color(*SUB_C)
        self.cell(0, 5, "\u7b2c %d \u9875" % self.page_no(), align="L")
        self.set_xy(self.l_margin, self.get_y())
        self.cell(0, 5, "\u6e0a\u5b66\u901a\u676d\u5dde \u00b7 \u96c5\u601d\u6559\u7814\u7ec4 \u00b7 \u4ec5\u9650\u5185\u90e8\u4f7f\u7528", align="R")

    def draw_rounded_rect(self, x, y, w, h, r, fill_color=None, border_color=None, left_accent=None):
        """Draw a rectangle with optional colored left border accent."""
        if fill_color:
            self.set_fill_color(*fill_color)
            self.rect(x, y, w, h, style="F")
        if left_accent:
            self.set_fill_color(*left_accent)
            self.rect(x, y, 3, h, style="F")
        if border_color:
            self.set_draw_color(*border_color)
            self.rect(x, y, w, h, style="D")

    def section_divider(self, text):
        self.ln(6)
        y = self.get_y()
        # Full width gradient bar
        self.set_fill_color(*BRAND_DARK)
        self.rect(10, y, 190, 11, style="F")
        # Gold left accent
        self.set_fill_color(*GOLD)
        self.rect(10, y, 4, 11, style="F")
        # Text
        self.set_font("CN", "B", 11.5)
        self.set_text_color(*WHITE)
        self.set_xy(18, y + 2)
        self.cell(0, 7, text)
        self.set_text_color(*TEXT_C)
        self.set_y(y + 15)

    def h2(self, text):
        self.ln(5)
        y = self.get_y()
        # Left accent bar
        self.set_fill_color(*BRAND)
        self.rect(10, y, 3, 8, style="F")
        self.set_font("CN", "B", 12.5)
        self.set_text_color(*BRAND_DARK)
        self.set_xy(16, y)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*TEXT_C)
        self.ln(2)

    def sub_text(self, text):
        self.set_x(16)
        self.set_font("CN", "", 9)
        self.set_text_color(*SUB_C)
        self.multi_cell(178, 4.8, text)
        self.set_text_color(*TEXT_C)
        self.ln(4)

    def template_card(self, t):
        """Draw a professional template card with background and left accent."""
        # Estimate height - if near bottom, new page
        if self.get_y() > 215:
            self.add_page()

        card_x = 12
        card_w = 186
        pad = 5
        content_w = card_w - pad * 2 - 3  # account for left accent

        # --- Measure content height by drawing invisibly ---
        start_y = self.get_y()

        # We'll draw content first, then overlay background behind it
        # fpdf2 doesn't support z-ordering, so we draw background first with estimated height
        # Estimate: title(7) + scene(10) + sentence(12) + how(15) + example(15) + pitfall(10) + spacing = ~75
        # Better: draw to temp, measure, then draw for real

        # Save position
        sy = self.get_y()

        # --- Draw the card background ---
        # First pass: estimate height
        self.set_font("CN", "", 9)
        lines_scene = len(t["scene"]) // 42 + 1
        lines_sent = len(t["sentence"]) // 38 + 1
        lines_how = len(t["how"]) // 42 + 1
        lines_ex = len(t["example"]) // 42 + 1
        lines_pit = len(t["pitfall"]) // 42 + 1
        est_h = 8 + lines_scene*5 + 3 + lines_sent*5.5 + 3 + lines_how*5 + 3 + lines_ex*5 + 3 + lines_pit*5 + 8
        est_h = max(est_h, 55)

        if sy + est_h > 275:
            self.add_page()
            sy = self.get_y()

        # Draw card background
        self.draw_rounded_rect(card_x, sy, card_w, est_h, 2, fill_color=CARD_BG, border_color=LINE_C, left_accent=BRAND)

        # --- Number badge ---
        badge_x = card_x + 6
        badge_y = sy + 3
        self.set_fill_color(*BRAND)
        self.rect(badge_x, badge_y, 18, 7, style="F")
        self.set_font("CN", "B", 8)
        self.set_text_color(*WHITE)
        self.set_xy(badge_x, badge_y + 0.5)
        self.cell(18, 6, "No.%s" % t["num"], align="C")

        # Title next to badge
        self.set_font("CN", "B", 11)
        self.set_text_color(*BRAND_DARK)
        self.set_xy(badge_x + 21, badge_y + 0.5)
        self.cell(0, 6, t["title"])
        self.set_y(sy + 12)

        # Scene
        self.set_x(card_x + pad + 3)
        self.set_font("CN", "", 8.5)
        self.set_text_color(*SUB_C)
        self.multi_cell(content_w, 4.5, "\u9002\u7528\u573a\u666f\uff1a" + t["scene"])
        self.ln(2)

        # Sentence highlight box
        sent_y = self.get_y()
        self.set_fill_color(*BRAND_LIGHT)
        sent_lines = len(t["sentence"]) // 36 + 1
        self.rect(card_x + pad + 3, sent_y, content_w, sent_lines * 5.5 + 4, style="F")
        self.set_xy(card_x + pad + 5, sent_y + 2)
        self.set_font("CN", "B", 9.5)
        self.set_text_color(*BRAND_DARK)
        self.multi_cell(content_w - 4, 5.5, t["sentence"])
        self.ln(2)

        # How to use
        self.set_x(card_x + pad + 3)
        self.set_font("CN", "B", 8.5)
        self.set_text_color(*ACCENT)
        self.cell(18, 4.5, "\u600e\u4e48\u7528\uff1a")
        self.set_font("CN", "", 8.5)
        self.set_text_color(*TEXT_C)
        self.set_x(card_x + pad + 3)
        self.multi_cell(content_w, 4.5, "\u600e\u4e48\u7528\uff1a" + t["how"])
        self.ln(1.5)

        # Example
        self.set_x(card_x + pad + 3)
        self.set_font("CN", "", 8.5)
        self.set_text_color(*SUB_C)
        self.multi_cell(content_w, 4.5, "\u586b\u7a7a\u793a\u8303\uff1a" + t["example"])
        self.ln(1.5)

        # Pitfall with warning color
        self.set_x(card_x + pad + 3)
        self.set_font("CN", "B", 8.5)
        self.set_text_color(*ACCENT)
        pit_y = self.get_y()
        # Small warning background
        self.set_fill_color(*ACCENT_LIGHT)
        pit_lines = len(t["pitfall"]) // 42 + 1
        self.rect(card_x + pad + 3, pit_y, content_w, pit_lines * 4.5 + 3, style="F")
        self.set_xy(card_x + pad + 5, pit_y + 1)
        self.set_font("CN", "", 8.5)
        self.multi_cell(content_w - 4, 4.5, "\u26a0 " + t["pitfall"])

        # Update position to end of card
        actual_end = self.get_y() + 4
        card_actual_h = actual_end - sy
        # Redraw border to correct height
        self.set_draw_color(*LINE_C)
        self.rect(card_x, sy, card_w, card_actual_h, style="D")
        # Redraw left accent to correct height
        self.set_fill_color(*BRAND)
        self.rect(card_x, sy, 3, card_actual_h, style="F")

        self.set_y(actual_end + 4)
        self.set_text_color(*TEXT_C)



def build():
    pdf = PDF()
    pdf.set_margin(10)
    pdf.l_margin = 10
    pdf.r_margin = 10

    # ============================================================
    # COVER PAGE
    # ============================================================
    pdf.add_page()
    pdf._is_cover = True

    # Full-page background
    pdf.set_fill_color(*BRAND_DARK)
    pdf.rect(0, 0, 210, 297, style="F")

    # Decorative top band
    pdf.set_fill_color(*GOLD)
    pdf.rect(0, 0, 210, 3, style="F")

    # Logo
    pdf.image(LOGO, x=55, y=30, w=100)

    # Main title
    pdf.set_y(80)
    pdf.set_font("CN", "B", 32)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 16, "\u96c5\u601d\u5199\u4f5c\u6a21\u677f\u5408\u96c6", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("CN", "", 13)
    pdf.set_text_color(*GOLD)
    pdf.cell(0, 8, "IELTS Writing Template Collection", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Subtitle line
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("CN", "", 11)
    pdf.set_text_color(200, 210, 225)
    pdf.cell(0, 7, "23 \u4e2a\u9ad8\u9891\u53e5\u578b  |  \u6309\u529f\u80fd\u5206\u7c7b  |  \u9644\u4f7f\u7528\u573a\u666f\u4e0e\u8e29\u5751\u63d0\u793a", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)

    # Cover info box
    box_x, box_w = 35, 140
    box_y = pdf.get_y()
    pdf.set_fill_color(20, 65, 105)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.6)
    pdf.rect(box_x, box_y, box_w, 58, style="FD")
    pdf.set_line_width(0.2)

    pdf.set_xy(box_x + 10, box_y + 7)
    pdf.set_font("CN", "B", 10.5)
    pdf.set_text_color(*GOLD)
    pdf.cell(0, 6, "\u8c01\u9002\u5408\u7528\u8fd9\u4efd\u8d44\u6599\uff1a", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    items = [
        "\u96c5\u601d\u5199\u4f5c\u5361\u5728 5.5-6\uff0c\u60f3\u51b2 6.5 \u4ee5\u4e0a",
        "\u5927\u4f5c\u6587\u4e0d\u77e5\u9053\u600e\u4e48\u5f00\u5934\u3001\u4e3e\u4f8b\u3001\u6536\u5c3e",
        "\u5c0f\u4f5c\u6587\u4e00\u4e0a\u6765\u5c31\u5806\u6570\u636e\uff0c\u5206\u6570\u4e0a\u4e0d\u53bb",
        "\u6a21\u677f\u80cc\u4e86\u4e00\u5806\uff0c\u5957\u4e0a\u53bb\u8fd8\u662f\u6ca1\u903b\u8f91",
    ]
    pdf.set_font("CN", "", 10)
    pdf.set_text_color(200, 215, 230)
    for item in items:
        pdf.set_x(box_x + 12)
        pdf.cell(0, 7.5, "\u00bb  " + item, new_x="LMARGIN", new_y="NEXT")

    # Footer on cover
    pdf.set_y(255)
    pdf.set_font("CN", "", 9)
    pdf.set_text_color(150, 165, 180)
    pdf.cell(0, 5, "\u6574\u7406\uff1a\u6e0a\u5b66\u901a\u676d\u5dde \u00b7 \u96c5\u601d\u6559\u7814\u7ec4", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "2025 \u66a8\u671f\u7248  |  \u4ec5\u9650\u5185\u90e8\u5b66\u5458\u4f7f\u7528", align="C", new_x="LMARGIN", new_y="NEXT")

    # Bottom gold bar
    pdf.set_fill_color(*GOLD)
    pdf.rect(0, 294, 210, 3, style="F")

    # ============================================================
    # TABLE OF CONTENTS
    # ============================================================
    pdf._is_cover = False
    pdf.add_page()

    pdf.set_font("CN", "B", 18)
    pdf.set_text_color(*BRAND_DARK)
    pdf.cell(0, 10, "\u76ee\u5f55  CONTENTS", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 80, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(8)

    toc_items = [
        ("\u5199\u5728\u524d\u9762 \u00b7 \u6a21\u677f\u600e\u4e48\u7528\u624d\u6709\u5206", ""),
        ("", ""),
        ("PART 1  \u5927\u4f5c\u6587\uff08Task 2\uff09", "20 \u53e5"),
        ("    \u4e00\u3001\u8ba9\u6b65\u6bb5\u5f00\u5934", "No.1 - No.4, No.24"),
        ("    \u4e8c\u3001\u4e3e\u4f8b\u5c55\u5f00", "No.5 - No.8, No.25-26"),
        ("    \u4e09\u3001\u5bf9\u6bd4\u8f6c\u6298", "No.9 - No.11, No.27-28"),
        ("    \u56db\u3001\u7ed3\u5c3e\u89c2\u70b9\u91cd\u7533", "No.12 - No.14, No.29"),
        ("    \u4e94\u3001\u4e3b\u4f53\u6bb5\u4e3b\u9898\u53e5", "No.34 - No.35"),
        ("", ""),
        ("PART 2  \u5c0f\u4f5c\u6587\uff08Task 1\uff09", "9 \u53e5"),
        ("    \u516d\u3001\u603b\u4f53\u8d8b\u52bf / \u6982\u8ff0\u53e5", "No.15 - No.18, No.30"),
        ("    \u4e03\u3001\u7ec6\u8282\u63cf\u8ff0", "No.19 - No.23, No.31-33"),
        ("", ""),
        ("PART 3  \u9ad8\u5206\u8bcd\u6c47\u5347\u7ea7\u8868", "15 \u7ec4\u9ad8\u9891\u66ff\u6362"),
        ("PART 4  \u4e94\u5927\u8bdd\u9898\u9ad8\u5206\u642d\u914d", "30+ \u5730\u9053\u8868\u8fbe"),
        ("PART 5  \u70ed\u95e8\u8bdd\u9898\u8bba\u70b9\u5e93", "5 \u5927\u8bdd\u9898 \u00d7 \u6b63\u53cd\u5404 3 \u4e2a\u8bba\u70b9"),
        ("PART 6  7\u5206 vs 5.5\u5206 \u5b9e\u4f8b\u5bf9\u6bd4", "4 \u4e2a\u8bc4\u5206\u7ef4\u5ea6"),
        ("PART 7  \u5199\u5b8c\u524d\u7684\u68c0\u67e5\u6e05\u5355", "12 \u6761\u81ea\u67e5\u9879"),
    ]

    for title, detail in toc_items:
        if not title:
            pdf.ln(3)
            continue
        if title.startswith("PART") or title.startswith("\u5199\u5728"):
            pdf.set_font("CN", "B", 11)
            pdf.set_text_color(*BRAND_DARK)
        elif title.startswith("    "):
            pdf.set_font("CN", "", 10)
            pdf.set_text_color(*TEXT_C)
        else:
            pdf.set_font("CN", "", 10)
            pdf.set_text_color(*TEXT_C)

        pdf.cell(130, 7.5, title)
        if detail:
            pdf.set_font("CN", "", 9)
            pdf.set_text_color(*SUB_C)
            pdf.cell(0, 7.5, detail, align="R")
        pdf.ln(7.5)

    # ============================================================
    # INTRO PAGE
    # ============================================================
    pdf.add_page()

    # Section header with decorative element
    pdf.set_font("CN", "B", 18)
    pdf.set_text_color(*BRAND_DARK)
    pdf.cell(0, 10, "\u5199\u5728\u524d\u9762", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CN", "", 11)
    pdf.set_text_color(*SUB_C)
    pdf.cell(0, 6, "\u6a21\u677f\u600e\u4e48\u7528\u624d\u6709\u5206", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    pdf.line(10, pdf.get_y(), 60, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(8)

    pdf.set_font("CN", "", 10)
    pdf.set_text_color(*TEXT_C)
    intro_lines = [
        "\u6a21\u677f\u80fd\u5e2e\u4f60\u6491\u4f4f\u7ed3\u6784\uff0c\u8ba9\u4f60\u5199\u4f5c\u65f6\u4e0d\u4f1a\u5361\u58f3\u3002\u4f46\u5206\u6570\u80fd\u4e0d\u80fd\u4e0a\u53bb\uff0c\u8fd8\u662f\u770b\u4f60\u5f80\u7a7a\u91cc\u586b\u7684\u5185\u5bb9\u6709\u6ca1\u6709\u903b\u8f91\u3002",
        "",
        "\u540c\u4e00\u4e2a While it is true that ___ \uff0c\u6709\u4eba\u586b\u8fdb\u53bb\u80fd\u62ff 7\uff0c\u6709\u4eba\u586b\u8fdb\u53bb\u8fd8\u662f 5.5\uff0c\u5dee\u8ddd\u5168\u5728\u4e2d\u95f4\u90a3\u6bb5\u8bdd\u8bb2\u6e05\u695a\u4e86\u6ca1\u6709\u3002",
        "",
        "\u5efa\u8bae\u4f60\u8fd9\u6837\u7528\u8fd9\u4efd\u8d44\u6599\uff1a",
    ]
    for line in intro_lines:
        if line:
            pdf.multi_cell(0, 5.8, line)
        else:
            pdf.ln(3)
    pdf.ln(6)

    # Steps with numbered circles
    steps = [
        "\u5148\u6309\u529f\u80fd\u627e\u5230\u5bf9\u5e94\u6a21\u677f\uff08\u8ba9\u6b65 / \u4e3e\u4f8b / \u8f6c\u6298 / \u7ed3\u5c3e / \u8d8b\u52bf / \u5bf9\u6bd4\uff09",
        "\u770b\u2018\u600e\u4e48\u7528\u2019\u548c\u2018\u586b\u7a7a\u793a\u8303\u2019\uff0c\u7406\u89e3\u8fd9\u4e00\u53e5\u7684\u903b\u8f91\u4f5c\u7528",
        "\u7528\u81ea\u5df1\u7684\u8bdd\u9898\u586b\u7a7a 3 \u6b21\uff0c\u5efa\u7acb\u808c\u8089\u8bb0\u5fc6",
        "\u5199\u5b8c\u68c0\u67e5\uff1a\u6a21\u677f\u586b\u8fdb\u53bb\u4e4b\u540e\uff0c\u610f\u601d\u6709\u6ca1\u6709\u8d70\u6837",
    ]
    for i, s in enumerate(steps, 1):
        y = pdf.get_y()
        # Number circle
        cx, cy = 16, y + 3.5
        pdf.set_fill_color(*BRAND)
        pdf.ellipse(cx - 3.5, cy - 3.5, 7, 7, style="F")
        pdf.set_font("CN", "B", 8)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(cx - 3.5, cy - 2.5)
        pdf.cell(7, 5, str(i), align="C")
        # Step text
        pdf.set_font("CN", "", 10)
        pdf.set_text_color(*TEXT_C)
        pdf.set_xy(24, y)
        pdf.multi_cell(170, 6, s)
        pdf.ln(3)

    pdf.ln(6)

    # Warning box - professional style
    wy = pdf.get_y()
    pdf.set_fill_color(*ACCENT_LIGHT)
    pdf.rect(12, wy, 186, 34, style="F")
    pdf.set_fill_color(*ACCENT)
    pdf.rect(12, wy, 3, 34, style="F")

    pdf.set_xy(20, wy + 5)
    pdf.set_font("CN", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 5.5, "\u26a0  \u4f7f\u7528\u63d0\u9192", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CN", "", 9.5)
    pdf.set_text_color(*TEXT_C)
    warns = [
        "\u4e0d\u8981\u6574\u6bb5\u7167\u642c\u6a21\u677f\uff0c\u8003\u5b98\u4f1a\u8bc6\u522b",
        "\u4e00\u7bc7\u5927\u4f5c\u6587\u7528 2-3 \u4e2a\u6a21\u677f\u5c31\u591f\u4e86\uff0c\u8fc7\u591a\u53cd\u800c\u6263\u5206",
        "\u6a21\u677f\u662f\u9aa8\u67b6\uff0c\u8bba\u70b9\u548c\u4f8b\u5b50\u624d\u662f\u8089\uff0c\u4e24\u4e2a\u90fd\u5f97\u7ec3",
    ]
    for w in warns:
        pdf.set_x(20)
        pdf.cell(0, 6, "\u2022  " + w, new_x="LMARGIN", new_y="NEXT")

    # ============================================================
    # PART 1: TASK 2
    # ============================================================
    pdf.add_page()
    pdf.section_divider("PART 1  |  \u5927\u4f5c\u6587\uff08Task 2\uff09")

    sections = [
        ("concession", "\u4e00\u3001\u8ba9\u6b65\u6bb5\u5f00\u5934",
         "\u5148\u627f\u8ba4\u5bf9\u65b9\u6709\u9053\u7406\uff0c\u518d\u628a\u91cd\u5fc3\u62c9\u56de\u81ea\u5df1\u7684\u89c2\u70b9\u3002\u8003\u5b98\u5728 CC\uff08\u8fde\u8d2f\u8854\u63a5\uff09\u4e00\u9879\u5f88\u770b\u91cd\u8fd9\u79cd\u5904\u7406\u3002"),
        ("example", "\u4e8c\u3001\u4e3e\u4f8b\u5c55\u5f00",
         "\u89e3\u51b3\u2018\u5199\u5b8c for example \u5c31\u5361\u4f4f\u2019\u7684\u95ee\u9898\u3002\u4f8b\u5b50\u5199\u5b8c\u4e4b\u540e\u5fc5\u987b\u56de\u6263\u89c2\u70b9\uff0c\u4e0d\u80fd\u8ba9\u8003\u5b98\u81ea\u5df1\u731c\u3002"),
        ("contrast", "\u4e09\u3001\u5bf9\u6bd4\u8f6c\u6298",
         "\u4e2d\u95f4\u6bb5\u4e07\u80fd\u8fc7\u6e21\u3002\u8003\u5b98\u7279\u522b\u770b\u91cd long-term / short-term \u8fd9\u79cd\u65f6\u95f4\u7ef4\u5ea6\u7684\u8bba\u8bc1\u3002"),
        ("conclusion", "\u56db\u3001\u7ed3\u5c3e\u89c2\u70b9\u91cd\u7533",
         "\u7ed3\u5c3e\u4e0d\u8981\u518d\u5199 In conclusion, I think... \u8fd9\u79cd\u5c0f\u5b66\u4f5c\u6587\u5473\u7684\u5f00\u5934\u3002"),
        ("topic_sentence", "\u4e94\u3001\u4e3b\u4f53\u6bb5\u4e3b\u9898\u53e5",
         "\u6bcf\u6bb5\u5f00\u5934\u7684\u7b2c\u4e00\u53e5\u5176\u5b9e\u662f\u62c9\u5206\u6700\u9ad8\u7684\u4f4d\u7f6e\u3002\u4ece\u7ecf\u6d4e / \u793e\u4f1a / \u73af\u5883 \u7b49\u4e0d\u540c\u89d2\u5ea6\u5207\u5165\uff0c\u80fd\u8ba9\u4f5c\u6587\u8d70\u5411\u7acb\u523b\u660e\u6717\u3002"),
    ]

    for cat_key, title, desc in sections:
        pdf.h2(title)
        pdf.sub_text(desc)
        for t in DATA["templates"]:
            if t["category"] == cat_key:
                pdf.template_card(t)

    # ============================================================
    # PART 2: TASK 1
    # ============================================================
    pdf.add_page()
    pdf.section_divider("PART 2  |  \u5c0f\u4f5c\u6587\uff08Task 1\uff09")

    sections2 = [
        ("task1_overview", "\u516d\u3001\u603b\u4f53\u8d8b\u52bf / \u6982\u8ff0\u53e5",
         "\u5c0f\u4f5c\u6587\u4e00\u4e0a\u6765\u4e0d\u8981\u5806\u6570\u636e\u3002\u5148\u7528\u4e00\u53e5\u6982\u62ec\u5168\u5c40\u8d8b\u52bf\uff0c\u8003\u5b98\u5728\u7b2c\u4e00\u773c\u5c31\u7ed9\u4f60 TR\uff08\u4efb\u52a1\u56de\u5e94\uff09\u7684\u5206\u3002"),
        ("task1_detail", "\u4e03\u3001\u5c0f\u4f5c\u6587 \u00b7 \u7ec6\u8282\u63cf\u8ff0",
         "\u4e2d\u95f4\u6bb5\u62c9\u5206\u5173\u952e\u3002\u627e\u51fa\u53cd\u5dee\u6700\u5927\u3001\u6700\u6709\u4fe1\u606f\u91cf\u7684\u5bf9\u6bd4\uff0c\u518d\u5c55\u5f00\u3002"),
    ]

    for cat_key, title, desc in sections2:
        pdf.h2(title)
        pdf.sub_text(desc)
        for t in DATA["templates"]:
            if t["category"] == cat_key:
                pdf.template_card(t)

    # ============================================================
    # PART 3: VOCABULARY UPGRADE TABLE
    # ============================================================
    pdf.add_page()
    pdf.section_divider("PART 3  |  \u9ad8\u5206\u8bcd\u6c47\u5347\u7ea7\u8868")
    pdf.ln(2)

    pdf.set_font("CN", "", 9.5)
    pdf.set_text_color(*TEXT_C)
    pdf.multi_cell(0, 5.2,
        "\u96c5\u601d\u5199\u4f5c\u8003\u5b98\u4f1a\u5728\u51e0\u79d2\u5185\u8bc6\u522b\u51fa\u4f60\u662f\u4e0d\u662f\u91cd\u590d\u4f7f\u7528\u57fa\u7840\u8bcd\u3002"
        "\u4e0b\u9762\u8fd9 15 \u7ec4\u9ad8\u9891\u66ff\u6362\u5efa\u8bae\u80cc\u4e0b\u6765\u3002\u4e2d\u7ea7\u8bcd\u6c47\u9002\u7528\u4e8e\u6240\u6709\u573a\u5408\uff0c\u9ad8\u7ea7\u8bcd\u6c47\u9009\u6027\u4f7f\u7528\uff083-5 \u4e2a/\u7bc7\u5373\u53ef\uff09\u3002")
    pdf.ln(5)

    # Table header
    th_y = pdf.get_y()
    pdf.set_fill_color(*BRAND_DARK)
    pdf.rect(12, th_y, 186, 8, style="F")
    pdf.set_font("CN", "B", 9.5)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(14, th_y + 1.5)
    pdf.cell(28, 5, "\u57fa\u7840\u8bcd")
    pdf.cell(50, 5, "\u4e2d\u7ea7\u66ff\u6362")
    pdf.cell(54, 5, "\u9ad8\u7ea7\u66ff\u6362")
    pdf.cell(50, 5, "\u4f7f\u7528\u63d0\u793a")
    pdf.set_y(th_y + 9)

    # Table rows
    pdf.set_text_color(*TEXT_C)
    for i, row in enumerate(DATA["vocab_upgrade"]):
        ry = pdf.get_y()
        if ry > 270:
            pdf.add_page()
            ry = pdf.get_y()
        # Alternating row background
        if i % 2 == 0:
            pdf.set_fill_color(*SOFT_BG)
            pdf.rect(12, ry, 186, 7.5, style="F")
        pdf.set_xy(14, ry + 1.5)
        pdf.set_font("CN", "B", 9)
        pdf.set_text_color(*ACCENT)
        pdf.cell(28, 5, row["basic"])
        pdf.set_font("CN", "", 9)
        pdf.set_text_color(*TEXT_C)
        pdf.cell(50, 5, row["level1"])
        pdf.set_font("CN", "B", 9)
        pdf.set_text_color(*BRAND)
        pdf.cell(54, 5, row["level2"])
        pdf.set_font("CN", "", 8.5)
        pdf.set_text_color(*SUB_C)
        pdf.cell(50, 5, row["note"])
        pdf.set_y(ry + 7.5)
    pdf.ln(4)

    # ============================================================
    # PART 4: COLLOCATIONS
    # ============================================================
    pdf.add_page()
    pdf.section_divider("PART 4  |  \u4e94\u5927\u8bdd\u9898\u9ad8\u5206\u642d\u914d")
    pdf.ln(2)

    pdf.set_font("CN", "", 9.5)
    pdf.set_text_color(*TEXT_C)
    pdf.multi_cell(0, 5.2,
        "\u4e0b\u9762\u8fd9\u4e9b\u662f\u96c5\u601d\u5199\u4f5c\u4e94\u5927\u70ed\u95e8\u8bdd\u9898\u4e0b\u7684\u9ad8\u5206\u8868\u8fbe\u3002"
        "\u80cc\u8bf5\u662f\u4e00\u56de\u4e8b\uff0c\u80fd\u5728\u4f5c\u6587\u4e2d\u51c6\u786e\u7528\u51fa\u624d\u7b97\u771f\u638c\u63e1\u3002\u5efa\u8bae\u6bcf\u4e2a\u8bdd\u9898\u81f3\u5c11\u8bb0\u4f4f 3-4 \u4e2a\u3002")
    pdf.ln(5)

    coll_colors = [BRAND, (59, 130, 246), (139, 92, 246), SUCCESS, (245, 158, 11)]
    for idx, group in enumerate(DATA["collocations"]):
        if pdf.get_y() > 235:
            pdf.add_page()
        c = coll_colors[idx % len(coll_colors)]
        gy = pdf.get_y()
        # Category header
        pdf.set_fill_color(*c)
        pdf.rect(12, gy, 186, 8, style="F")
        pdf.set_font("CN", "B", 10)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(16, gy + 1.5)
        pdf.cell(0, 5, group["category"])
        pdf.set_y(gy + 9)

        # Two-column layout for items
        items = group["items"]
        col_w = 92
        for i in range(0, len(items), 2):
            iy = pdf.get_y()
            pdf.set_font("CN", "", 9)
            pdf.set_text_color(*TEXT_C)
            pdf.set_xy(14, iy)
            pdf.multi_cell(col_w, 5, "\u2022 " + items[i])
            end1 = pdf.get_y()
            if i + 1 < len(items):
                pdf.set_xy(14 + col_w + 2, iy)
                pdf.multi_cell(col_w, 5, "\u2022 " + items[i + 1])
                end2 = pdf.get_y()
                pdf.set_y(max(end1, end2))
            else:
                pdf.set_y(end1)
        pdf.ln(4)

    # ============================================================
    # PART 5: TOPIC ARGUMENT BANK
    # ============================================================
    pdf.add_page()
    pdf.section_divider("PART 5  |  \u70ed\u95e8\u8bdd\u9898\u8bba\u70b9\u5e93")
    pdf.ln(2)

    pdf.set_font("CN", "", 9.5)
    pdf.set_text_color(*TEXT_C)
    pdf.multi_cell(0, 5.2,
        "\u96c5\u601d\u5199\u4f5c\u5361\u4f4f\u7684\u4e00\u5927\u539f\u56e0\u662f\u201c\u4e0d\u77e5\u9053\u8be5\u8bb2\u4ec0\u4e48\u201d\u3002"
        "\u4e0b\u9762\u8fd9\u4e9b\u8bba\u70b9\u6db5\u76d6\u4e94\u5927\u9ad8\u9891\u8bdd\u9898\uff0c\u4e0d\u8981\u80cc\u53e5\u5b50\uff0c\u80cc\u601d\u8def\u3002\u5230\u8003\u573a\u4e0a\u6839\u636e\u9898\u76ee\u9009\u5408\u9002\u7684\u8bba\u70b9\u5957\u8fdb\u53bb\u5373\u53ef\u3002")
    pdf.ln(5)

    for idx, topic in enumerate(DATA["topic_bank"]):
        if pdf.get_y() > 215:
            pdf.add_page()
        ty = pdf.get_y()
        # Topic title with badge
        pdf.set_fill_color(*BRAND_DARK)
        pdf.rect(12, ty, 186, 8, style="F")
        pdf.set_fill_color(*GOLD)
        pdf.rect(12, ty, 4, 8, style="F")
        pdf.set_font("CN", "B", 10.5)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(20, ty + 1.5)
        pdf.cell(0, 5, "\u8bdd\u9898 %d  |  %s" % (idx + 1, topic["topic"]))
        pdf.set_y(ty + 10)

        # FOR arguments
        fy = pdf.get_y()
        pdf.set_fill_color(220, 252, 231)  # green tint
        h_for = len(topic["for_args"]) * 6 + 8
        pdf.rect(12, fy, 92, h_for, style="F")
        pdf.set_fill_color(*SUCCESS)
        pdf.rect(12, fy, 3, h_for, style="F")
        pdf.set_font("CN", "B", 9.5)
        pdf.set_text_color(*SUCCESS)
        pdf.set_xy(18, fy + 1.5)
        pdf.cell(0, 5, "\u2713 \u652f\u6301\u8bba\u70b9")
        pdf.set_font("CN", "", 8.5)
        pdf.set_text_color(*TEXT_C)
        pdf.set_y(fy + 7)
        for arg in topic["for_args"]:
            pdf.set_x(18)
            pdf.multi_cell(82, 5, "\u00b7 " + arg)

        # AGAINST arguments
        ay = fy
        pdf.set_fill_color(254, 226, 226)  # red tint
        h_ag = len(topic["against_args"]) * 6 + 8
        pdf.rect(106, ay, 92, h_ag, style="F")
        pdf.set_fill_color(*ACCENT)
        pdf.rect(106, ay, 3, h_ag, style="F")
        pdf.set_font("CN", "B", 9.5)
        pdf.set_text_color(*ACCENT)
        pdf.set_xy(112, ay + 1.5)
        pdf.cell(0, 5, "X \u53cd\u5bf9\u8bba\u70b9")
        pdf.set_font("CN", "", 8.5)
        pdf.set_text_color(*TEXT_C)
        pdf.set_y(ay + 7)
        for arg in topic["against_args"]:
            pdf.set_x(112)
            pdf.multi_cell(82, 5, "\u00b7 " + arg)

        pdf.set_y(max(fy + h_for, ay + h_ag) + 5)

    # ============================================================
    # PART 6: 7分 vs 5.5分
    # ============================================================
    pdf.add_page()
    pdf.section_divider("PART 6  |  7\u5206 vs 5.5\u5206  \u5b9e\u4f8b\u5bf9\u6bd4")
    pdf.ln(2)

    pdf.set_font("CN", "", 9.5)
    pdf.set_text_color(*TEXT_C)
    pdf.multi_cell(0, 5.2,
        "\u540c\u6837\u7684\u9898\u76ee\uff0c5.5 \u5206\u548c 7 \u5206\u5230\u5e95\u5dee\u5728\u54ea\u91cc\uff1f"
        "\u4e0b\u9762\u4ece\u96c5\u601d\u5b98\u65b9\u8bc4\u5206\u7684\u56db\u4e2a\u7ef4\u5ea6\uff0c\u6bcf\u4e2a\u90fd\u7ed9\u4f60\u4e00\u4e2a\u771f\u5b9e\u5bf9\u6bd4\u3002\u770b\u5b8c\u4f60\u5c31\u4f1a\u77e5\u9053\u81ea\u5df1\u54ea\u91cc\u53ef\u4ee5\u5feb\u901f\u63d0\u5206\u3002")
    pdf.ln(5)

    for idx, comp in enumerate(DATA["score_comparison"]):
        if pdf.get_y() > 215:
            pdf.add_page()
        cy = pdf.get_y()
        # Dimension title
        pdf.set_fill_color(*BRAND)
        pdf.rect(12, cy, 186, 7.5, style="F")
        pdf.set_font("CN", "B", 10.5)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(16, cy + 1.2)
        pdf.cell(0, 5, comp["dimension"])
        pdf.set_y(cy + 9)

        # Low score example
        ly = pdf.get_y()
        pdf.set_fill_color(254, 226, 226)
        # Estimate height
        low_lines = len(comp["low"]) // 75 + 1
        h_low = low_lines * 5 + 8
        pdf.rect(12, ly, 186, h_low, style="F")
        pdf.set_fill_color(*ACCENT)
        pdf.rect(12, ly, 3, h_low, style="F")
        pdf.set_font("CN", "B", 9)
        pdf.set_text_color(*ACCENT)
        pdf.set_xy(18, ly + 1.5)
        pdf.cell(0, 5, "5.5\u5206\u5199\u6cd5\uff1a")
        pdf.set_font("CN", "", 9)
        pdf.set_text_color(*TEXT_C)
        pdf.set_xy(18, ly + 7)
        pdf.multi_cell(176, 5, comp["low"])
        end_low = pdf.get_y() + 2

        # High score example
        hy = end_low
        pdf.set_fill_color(220, 252, 231)
        high_lines = len(comp["high"]) // 75 + 1
        h_high = high_lines * 5 + 8
        pdf.rect(12, hy, 186, h_high, style="F")
        pdf.set_fill_color(*SUCCESS)
        pdf.rect(12, hy, 3, h_high, style="F")
        pdf.set_font("CN", "B", 9)
        pdf.set_text_color(*SUCCESS)
        pdf.set_xy(18, hy + 1.5)
        pdf.cell(0, 5, "7\u5206\u5199\u6cd5\uff1a")
        pdf.set_font("CN", "", 9)
        pdf.set_text_color(*TEXT_C)
        pdf.set_xy(18, hy + 7)
        pdf.multi_cell(176, 5, comp["high"])
        end_high = pdf.get_y() + 2

        # Key takeaway
        ky = end_high
        pdf.set_fill_color(*BRAND_LIGHT)
        key_lines = len(comp["key"]) // 75 + 1
        h_key = key_lines * 5 + 8
        pdf.rect(12, ky, 186, h_key, style="F")
        pdf.set_fill_color(*BRAND)
        pdf.rect(12, ky, 3, h_key, style="F")
        pdf.set_font("CN", "B", 9)
        pdf.set_text_color(*BRAND_DARK)
        pdf.set_xy(18, ky + 1.5)
        pdf.cell(0, 5, "\u62c9\u5206\u5173\u952e\uff1a")
        pdf.set_font("CN", "", 9)
        pdf.set_text_color(*TEXT_C)
        pdf.set_xy(18, ky + 7)
        pdf.multi_cell(176, 5, comp["key"])
        pdf.ln(6)

    # ============================================================
    # PART 7: CHECKLIST
    # ============================================================
    pdf.add_page()
    pdf.section_divider("PART 7  |  \u5199\u5b8c\u524d\u7684\u68c0\u67e5\u6e05\u5355")
    pdf.ln(2)

    pdf.set_font("CN", "B", 13)
    pdf.set_text_color(*BRAND_DARK)
    pdf.cell(0, 8, "\u5199\u4f5c\u771f\u6b63\u8981\u7ec3\u7684\uff0c\u662f\u68c0\u67e5\u80fd\u529b\u3002", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("CN", "", 9.5)
    pdf.set_text_color(*TEXT_C)
    pdf.multi_cell(0, 5.2,
        "\u4e0b\u9762\u8fd9 12 \u4e2a\u95ee\u9898\uff0c\u5efa\u8bae\u5199\u5b8c\u4e4b\u540e\u9010\u6761\u8fc7\u4e00\u904d\u3002"
        "\u524d\u671f\u53ef\u80fd\u8981\u82b1 5-8 \u5206\u949f\uff0c\u7b49\u6210\u4e60\u60ef\u4e4b\u540e 2 \u5206\u949f\u5c31\u80fd\u626b\u5b8c\u3002")
    pdf.ln(6)

    chk_colors = [BRAND, (59, 130, 246), (139, 92, 246), SUCCESS]
    for idx, chk in enumerate(DATA["checklist"]):
        y = pdf.get_y()
        c = chk_colors[idx % len(chk_colors)]

        # Category header with colored bar
        pdf.set_fill_color(*c)
        pdf.rect(12, y, 186, 7.5, style="F")
        pdf.set_font("CN", "B", 9.5)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(16, y + 1)
        pdf.cell(0, 5.5, chk["category"])
        pdf.set_y(y + 9)

        # Items
        pdf.set_font("CN", "", 9.5)
        pdf.set_text_color(*TEXT_C)
        for item in chk["items"]:
            iy = pdf.get_y()
            # Checkbox
            pdf.set_draw_color(*c)
            pdf.rect(16, iy + 0.5, 4, 4, style="D")
            pdf.set_x(23)
            pdf.cell(0, 5.5, item, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

    # ============================================================
    # FINAL PAGE
    # ============================================================
    pdf.ln(6)
    fy = pdf.get_y()
    if fy > 220:
        pdf.add_page()
        fy = pdf.get_y() + 5

    # Final professional box
    pdf.set_fill_color(*SOFT_BG)
    pdf.set_draw_color(*BRAND)
    pdf.set_line_width(0.5)
    pdf.rect(12, fy, 186, 40, style="FD")
    pdf.set_fill_color(*BRAND)
    pdf.rect(12, fy, 3, 40, style="F")
    pdf.set_line_width(0.2)

    pdf.set_xy(20, fy + 6)
    pdf.set_font("CN", "B", 11)
    pdf.set_text_color(*BRAND_DARK)
    pdf.cell(0, 6, "\u6700\u540e\u4e00\u53e5\u8bdd\u9001\u7ed9\u4f60\uff1a", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("CN", "", 10)
    pdf.set_text_color(*TEXT_C)
    pdf.set_x(20)
    pdf.multi_cell(172, 5.8,
        "\u6a21\u677f\u8ba9\u4f60\u5199\u5f97\u5feb\uff0c\u903b\u8f91\u8ba9\u4f60\u5199\u5f97\u7a33\u3002"
        "\u60f3\u4ece 5.5 \u8d70\u5230 6.5\uff0c\u628a\u8fd9\u4efd\u8d44\u6599\u91cc\u7684 23 \u53e5\u8bdd\u7ec3\u5230\u80fd\u95ed\u7740\u773c\u775b\u586b\u7a7a\uff0c"
        "\u518d\u52a0\u4e0a\u6bcf\u5468 2 \u7bc7\u88ab\u6279\u6539\u8fc7\u7684\u4f5c\u6587\uff0c\u4e00\u4e2a\u66a8\u5047\u5c31\u80fd\u770b\u5230\u53d8\u5316\u3002")

    pdf.set_y(fy + 50)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.3)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(6)

    pdf.set_font("CN", "", 9.5)
    pdf.set_text_color(*SUB_C)
    pdf.cell(0, 5, "\u6e0a\u5b66\u901a\u676d\u5dde \u00b7 \u96c5\u601d\u6559\u7814\u7ec4", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "\u60f3\u8981\u4f5c\u6587\u4eba\u5de5\u6279\u6539 / \u5165\u8425\u524d\u8bca\u65ad / \u66a8\u671f\u5c01\u95ed\u8425\u8be6\u60c5", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CN", "B", 9.5)
    pdf.set_text_color(*BRAND)
    pdf.cell(0, 5, "\u53ef\u5728\u5c0f\u7ea2\u4e66\u79c1\u4fe1\u6211\u4eec  @\u6e0a\u5b66\u901a\u676d\u5dde", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.output(OUTPUT)
    print("OK:", OUTPUT)


if __name__ == "__main__":
    build()
