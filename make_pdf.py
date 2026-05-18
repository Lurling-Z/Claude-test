# -*- coding: utf-8 -*-
import json
from fpdf import FPDF

FONT_R = "/tmp/fonts/NotoSansSC-Regular.ttf"
FONT_B = "/tmp/fonts/NotoSansSC-Bold.ttf"
OUTPUT = "projects/sandbox/Claude-test/yuanxuetong-ielts-writing-templates.pdf"

with open("projects/sandbox/Claude-test/pdf_data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

# Colors
BRAND = (15, 76, 129)
ACCENT = (230, 57, 70)
SOFT_BG = (244, 246, 249)
TEXT_C = (31, 41, 55)
SUB_C = (107, 114, 128)
WHITE = (255, 255, 255)
LINE_C = (209, 213, 219)


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("CN", "", FONT_R)
        self.add_font("CN", "B", FONT_B)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_fill_color(*BRAND)
            self.rect(0, 0, 210, 7, style="F")
            self.set_font("CN", "B", 8)
            self.set_text_color(*WHITE)
            self.set_xy(10, 1.5)
            self.cell(0, 4, "\u6e0a\u5b66\u901a \u00b7 \u96c5\u601d\u5199\u4f5c\u6a21\u677f\u5408\u96c6", align="L")
            self.set_font("CN", "", 8)
            self.set_xy(10, 1.5)
            self.cell(0, 4, "\u516c\u4f17\u53f7 / \u5c0f\u7ea2\u4e66\uff1a\u6e0a\u5b66\u901a\u676d\u5dde", align="R")
            self.set_text_color(*TEXT_C)
            self.set_y(10)

    def footer(self):
        self.set_y(-12)
        self.set_font("CN", "", 7.5)
        self.set_text_color(*SUB_C)
        self.cell(0, 8, "\u7b2c %d \u9875    |    \u6e0a\u5b66\u901a \u00b7 \u96c5\u601d\u66a8\u671f\u5c01\u95ed\u8425" % self.page_no(), align="C")

    def section_divider(self, text):
        self.ln(4)
        self.set_fill_color(*BRAND)
        self.set_font("CN", "B", 12)
        self.set_text_color(*WHITE)
        x = self.get_x()
        self.cell(0, 9, "  " + text, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*TEXT_C)
        self.ln(4)

    def h2(self, text):
        self.ln(4)
        self.set_font("CN", "B", 13)
        self.set_text_color(*BRAND)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*TEXT_C)
        self.ln(1)

    def sub_text(self, text):
        self.set_font("CN", "", 9)
        self.set_text_color(*SUB_C)
        self.multi_cell(0, 5, text)
        self.set_text_color(*TEXT_C)
        self.ln(3)

    def template_card(self, t):
        # Check if we need a new page (estimate card height ~60mm)
        if self.get_y() > 230:
            self.add_page()

        x0 = self.get_x()
        y0 = self.get_y()
        w = 190

        # Draw card content first to measure height
        self.set_x(x0 + 3)

        # Title
        self.set_font("CN", "B", 11)
        self.set_text_color(*BRAND)
        self.cell(0, 6, "%s. %s" % (t["num"], t["title"]), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        # Scene
        self.set_x(x0 + 3)
        self.set_font("CN", "", 9)
        self.set_text_color(*SUB_C)
        self.multi_cell(w - 6, 4.5, "\u9002\u7528\u573a\u666f\uff1a" + t["scene"])
        self.ln(1)

        # Sentence
        self.set_x(x0 + 3)
        self.set_font("CN", "B", 10)
        self.set_text_color(*BRAND)
        self.multi_cell(w - 6, 5, t["sentence"])
        self.ln(1)

        # How to use
        self.set_x(x0 + 3)
        self.set_font("CN", "", 9)
        self.set_text_color(*TEXT_C)
        self.multi_cell(w - 6, 4.5, "\u600e\u4e48\u7528\uff1a" + t["how"])
        self.ln(1)

        # Example
        self.set_x(x0 + 3)
        self.set_text_color(*SUB_C)
        self.multi_cell(w - 6, 4.5, "\u586b\u7a7a\u793a\u8303\uff1a" + t["example"])
        self.ln(1)

        # Pitfall
        self.set_x(x0 + 3)
        self.set_text_color(*ACCENT)
        self.multi_cell(w - 6, 4.5, "\u5bb9\u6613\u8e29\u7684\u5751\uff1a" + t["pitfall"])

        y1 = self.get_y()
        self.set_text_color(*TEXT_C)

        # Draw background rectangle
        self.set_fill_color(*SOFT_BG)
        self.set_draw_color(*LINE_C)
        # Use rect behind the content (we draw it after measuring)
        # Actually fpdf draws on top, so we need a different approach
        # Let's just add spacing
        self.ln(5)
        # Draw a subtle line separator
        self.set_draw_color(*LINE_C)
        self.line(self.l_margin, self.get_y(), self.l_margin + w, self.get_y())
        self.ln(4)


def build():
    pdf = PDF()
    pdf.set_margin(10)
    pdf.l_margin = 10
    pdf.r_margin = 10

    # === COVER PAGE ===
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("CN", "B", 28)
    pdf.set_text_color(*BRAND)
    pdf.cell(0, 14, "\u96c5\u601d\u5199\u4f5c\u6a21\u677f\u5408\u96c6", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("CN", "", 12)
    pdf.set_text_color(*SUB_C)
    pdf.cell(0, 8, "23 \u4e2a\u9ad8\u9891\u53e5\u578b \uff5c \u6309\u529f\u80fd\u5206\u7c7b \uff5c \u9644\u4f7f\u7528\u573a\u666f\u4e0e\u8e29\u5751\u63d0\u793a", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)

    # Cover box
    pdf.set_fill_color(*SOFT_BG)
    pdf.set_draw_color(*BRAND)
    bx = 30
    bw = 150
    by = pdf.get_y()
    pdf.rect(bx, by, bw, 50, style="FD")
    pdf.set_xy(bx + 8, by + 6)
    pdf.set_font("CN", "B", 10.5)
    pdf.set_text_color(*TEXT_C)
    pdf.cell(0, 6, "\u8c01\u9002\u5408\u7528\u8fd9\u4efd\u8d44\u6599\uff1a", new_x="LMARGIN", new_y="NEXT")
    items = [
        "\u00b7 \u96c5\u601d\u5199\u4f5c\u5361\u5728 5.5-6\uff0c\u60f3\u51b2 6.5 \u4ee5\u4e0a",
        "\u00b7 \u5927\u4f5c\u6587\u4e0d\u77e5\u9053\u600e\u4e48\u5f00\u5934\u3001\u4e3e\u4f8b\u3001\u6536\u5c3e",
        "\u00b7 \u5c0f\u4f5c\u6587\u4e00\u4e0a\u6765\u5c31\u5806\u6570\u636e\uff0c\u5206\u6570\u4e0a\u4e0d\u53bb",
        "\u00b7 \u6a21\u677f\u80cc\u4e86\u4e00\u5806\uff0c\u5957\u4e0a\u53bb\u8fd8\u662f\u6ca1\u903b\u8f91",
    ]
    pdf.set_font("CN", "", 10)
    for item in items:
        pdf.set_x(bx + 8)
        pdf.cell(0, 6.5, item, new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(by + 60)
    pdf.ln(20)
    pdf.set_font("CN", "", 9)
    pdf.set_text_color(*SUB_C)
    pdf.cell(0, 5, "\u6574\u7406\uff1a\u6e0a\u5b66\u901a\u676d\u5dde \u00b7 \u96c5\u601d\u6559\u7814\u7ec4", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "\u4ec5\u9650\u5b66\u5458\u5185\u90e8\u4f7f\u7528\uff0c\u8bf7\u52ff\u5916\u4f20", align="C", new_x="LMARGIN", new_y="NEXT")

    # === INTRO PAGE ===
    pdf.add_page()
    pdf.set_font("CN", "B", 20)
    pdf.set_text_color(*BRAND)
    pdf.cell(0, 10, "\u5199\u5728\u524d\u9762 \u00b7 \u6a21\u677f\u600e\u4e48\u7528\u624d\u6709\u5206", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

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
            pdf.multi_cell(0, 5.5, line)
        else:
            pdf.ln(3)
    pdf.ln(4)

    steps = [
        "1. \u5148\u6309\u529f\u80fd\u627e\u5230\u5bf9\u5e94\u6a21\u677f\uff08\u8ba9\u6b65 / \u4e3e\u4f8b / \u8f6c\u6298 / \u7ed3\u5c3e / \u8d8b\u52bf / \u5bf9\u6bd4\uff09",
        "2. \u770b\u2018\u600e\u4e48\u7528\u2019\u548c\u2018\u586b\u7a7a\u793a\u8303\u2019\uff0c\u7406\u89e3\u8fd9\u4e00\u53e5\u7684\u903b\u8f91\u4f5c\u7528",
        "3. \u7528\u81ea\u5df1\u7684\u8bdd\u9898\u586b\u7a7a 3 \u6b21\uff0c\u5efa\u7acb\u808c\u8089\u8bb0\u5fc6",
        "4. \u5199\u5b8c\u68c0\u67e5\uff1a\u6a21\u677f\u586b\u8fdb\u53bb\u4e4b\u540e\uff0c\u610f\u601d\u6709\u6ca1\u6709\u8d70\u6837",
    ]
    for s in steps:
        pdf.set_font("CN", "B", 10)
        pdf.set_text_color(*ACCENT)
        pdf.cell(6, 6, s[0:2])
        pdf.set_font("CN", "", 10)
        pdf.set_text_color(*TEXT_C)
        pdf.multi_cell(0, 6, s[2:])
        pdf.ln(1)

    pdf.ln(6)
    # Warning box
    pdf.set_fill_color(255, 245, 245)
    pdf.set_draw_color(*ACCENT)
    wy = pdf.get_y()
    pdf.rect(10, wy, 190, 30, style="FD")
    pdf.set_xy(14, wy + 4)
    pdf.set_font("CN", "B", 10)
    pdf.set_text_color(*TEXT_C)
    pdf.cell(0, 5.5, "\u63d0\u9192\u4e00\u4e0b\uff1a", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CN", "", 9.5)
    warns = [
        "\u00b7 \u4e0d\u8981\u6574\u6bb5\u7167\u642c\u6a21\u677f\uff0c\u8003\u5b98\u4f1a\u8bc6\u522b",
        "\u00b7 \u4e00\u7bc7\u5927\u4f5c\u6587\u7528 2-3 \u4e2a\u6a21\u677f\u5c31\u591f\u4e86\uff0c\u8fc7\u591a\u53cd\u800c\u6263\u5206",
        "\u00b7 \u6a21\u677f\u662f\u9aa8\u67b6\uff0c\u8bba\u70b9\u548c\u4f8b\u5b50\u624d\u662f\u8089\uff0c\u4e24\u4e2a\u90fd\u5f97\u7ec3",
    ]
    for w in warns:
        pdf.set_x(14)
        pdf.cell(0, 5.5, w, new_x="LMARGIN", new_y="NEXT")

    # === PART 1 ===
    pdf.add_page()
    pdf.section_divider("PART 1 \uff5c \u5927\u4f5c\u6587\uff08Task 2\uff09")

    sections = [
        ("concession", "\u4e00\u3001\u8ba9\u6b65\u6bb5\u5f00\u5934",
         "\u5148\u627f\u8ba4\u5bf9\u65b9\u6709\u9053\u7406\uff0c\u518d\u628a\u91cd\u5fc3\u62c9\u56de\u81ea\u5df1\u7684\u89c2\u70b9\u3002\u8003\u5b98\u5728 CC\uff08\u8fde\u8d2f\u8854\u63a5\uff09\u4e00\u9879\u5f88\u770b\u91cd\u8fd9\u79cd\u5904\u7406\u3002"),
        ("example", "\u4e8c\u3001\u4e3e\u4f8b\u5c55\u5f00",
         "\u89e3\u51b3\u2018\u5199\u5b8c for example \u5c31\u5361\u4f4f\u2019\u7684\u95ee\u9898\u3002\u4f8b\u5b50\u5199\u5b8c\u4e4b\u540e\u5fc5\u987b\u56de\u6263\u89c2\u70b9\uff0c\u4e0d\u80fd\u8ba9\u8003\u5b98\u81ea\u5df1\u731c\u3002"),
        ("contrast", "\u4e09\u3001\u5bf9\u6bd4\u8f6c\u6298",
         "\u4e2d\u95f4\u6bb5\u4e07\u80fd\u8fc7\u6e21\u3002\u8003\u5b98\u7279\u522b\u770b\u91cd long-term / short-term \u8fd9\u79cd\u65f6\u95f4\u7ef4\u5ea6\u7684\u8bba\u8bc1\u3002"),
        ("conclusion", "\u56db\u3001\u7ed3\u5c3e\u89c2\u70b9\u91cd\u7533",
         "\u7ed3\u5c3e\u4e0d\u8981\u518d\u5199 In conclusion, I think... \u8fd9\u79cd\u5c0f\u5b66\u4f5c\u6587\u5473\u7684\u5f00\u5934\u3002"),
    ]

    for cat_key, title, desc in sections:
        pdf.h2(title)
        pdf.sub_text(desc)
        for t in DATA["templates"]:
            if t["category"] == cat_key:
                pdf.template_card(t)

    # === PART 2 ===
    pdf.add_page()
    pdf.section_divider("PART 2 \uff5c \u5c0f\u4f5c\u6587\uff08Task 1\uff09")

    sections2 = [
        ("task1_overview", "\u4e94\u3001\u603b\u4f53\u8d8b\u52bf / \u6982\u8ff0\u53e5",
         "\u5c0f\u4f5c\u6587\u4e00\u4e0a\u6765\u4e0d\u8981\u5806\u6570\u636e\u3002\u5148\u7528\u4e00\u53e5\u6982\u62ec\u5168\u5c40\u8d8b\u52bf\uff0c\u8003\u5b98\u5728\u7b2c\u4e00\u773c\u5c31\u7ed9\u4f60 TR\uff08\u4efb\u52a1\u56de\u5e94\uff09\u7684\u5206\u3002"),
        ("task1_detail", "\u516d\u3001\u5c0f\u4f5c\u6587 \u00b7 \u7ec6\u8282\u63cf\u8ff0",
         "\u4e2d\u95f4\u6bb5\u62c9\u5206\u5173\u952e\u3002\u627e\u51fa\u53cd\u5dee\u6700\u5927\u3001\u6700\u6709\u4fe1\u606f\u91cf\u7684\u5bf9\u6bd4\uff0c\u518d\u5c55\u5f00\u3002"),
    ]

    for cat_key, title, desc in sections2:
        pdf.h2(title)
        pdf.sub_text(desc)
        for t in DATA["templates"]:
            if t["category"] == cat_key:
                pdf.template_card(t)

    # === PART 3: CHECKLIST ===
    pdf.add_page()
    pdf.section_divider("PART 3 \uff5c \u5199\u5b8c\u524d\u7684\u68c0\u67e5\u6e05\u5355")

    pdf.set_font("CN", "B", 13)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 8, "\u5199\u4f5c\u771f\u6b63\u8981\u7ec3\u7684\uff0c\u662f\u68c0\u67e5\u80fd\u529b\u3002", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("CN", "", 10)
    pdf.set_text_color(*TEXT_C)
    pdf.multi_cell(0, 5.5,
        "\u4e0b\u9762\u8fd9 12 \u4e2a\u95ee\u9898\uff0c\u5efa\u8bae\u4f60\u5199\u5b8c\u4e4b\u540e\u9010\u6761\u8fc7\u4e00\u904d\u3002"
        "\u524d\u671f\u53ef\u80fd\u8981\u82b1 5-8 \u5206\u949f\uff0c\u7b49\u6210\u4e60\u60ef\u4e4b\u540e 2 \u5206\u949f\u5c31\u80fd\u626b\u5b8c\u3002")
    pdf.ln(6)

    for chk in DATA["checklist"]:
        pdf.set_font("CN", "B", 11)
        pdf.set_text_color(*ACCENT)
        pdf.cell(0, 7, chk["category"], new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("CN", "", 9.5)
        pdf.set_text_color(*TEXT_C)
        for item in chk["items"]:
            pdf.cell(0, 6, "[ ]  " + item, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # Final box
    pdf.ln(8)
    pdf.set_fill_color(*SOFT_BG)
    pdf.set_draw_color(*BRAND)
    fy = pdf.get_y()
    pdf.rect(10, fy, 190, 35, style="FD")
    pdf.set_xy(16, fy + 5)
    pdf.set_font("CN", "B", 10.5)
    pdf.set_text_color(*TEXT_C)
    pdf.cell(0, 6, "\u6700\u540e\u4e00\u53e5\u8bdd\u9001\u7ed9\u4f60\uff1a", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CN", "", 10)
    pdf.set_x(16)
    pdf.multi_cell(170, 5.5,
        "\u6a21\u677f\u8ba9\u4f60\u5199\u5f97\u5feb\uff0c\u903b\u8f91\u8ba9\u4f60\u5199\u5f97\u7a33\u3002"
        "\u60f3\u4ece 5.5 \u8d70\u5230 6.5\uff0c\u628a\u8fd9\u4efd\u8d44\u6599\u91cc\u7684 23 \u53e5\u8bdd\u7ec3\u5230\u80fd\u95ed\u7740\u773c\u775b\u586b\u7a7a\uff0c"
        "\u518d\u52a0\u4e0a\u6bcf\u5468 2 \u7bc7\u88ab\u6279\u6539\u8fc7\u7684\u4f5c\u6587\uff0c\u4e00\u4e2a\u66a8\u5047\u5c31\u80fd\u770b\u5230\u53d8\u5316\u3002")

    pdf.set_y(fy + 45)
    pdf.set_font("CN", "", 9)
    pdf.set_text_color(*SUB_C)
    pdf.cell(0, 5, "\u2014\u2014", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "\u6e0a\u5b66\u901a\u676d\u5dde \u00b7 \u96c5\u601d\u6559\u7814\u7ec4", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "\u60f3\u8981\u4f5c\u6587\u4eba\u5de5\u6279\u6539 / \u5165\u8425\u524d\u8bca\u65ad / \u66a8\u671f\u5c01\u95ed\u8425\u8be6\u60c5\uff0c\u53ef\u5728\u5c0f\u7ea2\u4e66\u79c1\u4fe1\u6211\u4eec\u3002", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.output(OUTPUT)
    print("OK:", OUTPUT)


if __name__ == "__main__":
    build()
