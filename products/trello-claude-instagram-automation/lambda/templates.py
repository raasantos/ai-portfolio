"""
templates.py — brand-agnostic Instagram post image templates (6 layouts).
This module is the single source of truth for what each template needs as input.
Designed to be imported directly by the Lambda handler.

Fonts: this repo ships NO font files and picks none for you — bring your own
and drop them in fonts/ (see fonts/README.md). In Lambda, system fonts are NOT
present — the .otf/.ttf files must be bundled in the deployment package (or a
Lambda Layer). The four FONT_* env vars below point at four weights of a
single typeface; override them to match whatever files you actually placed in
fonts/, or point separate vars at genuinely different typefaces if you want a
mixed look.

Branding: set BRAND_NAME (all-caps eyebrow/wordmark text, e.g. "YOUR BRAND")
and BRAND_HANDLE (footer text, e.g. "@yourbrand") as environment variables.
Both default to obvious placeholders so a misconfigured deploy is visible in
the rendered image instead of failing silently.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (138, 138, 138)
BORDER_GREY = (42, 42, 42)
MARGIN = 90

BRAND_NAME = os.environ.get("BRAND_NAME", "YOUR BRAND")
BRAND_HANDLE = os.environ.get("BRAND_HANDLE", "@yourbrand")

# Resolved relative to this file so it works both locally and in Lambda
# (Lambda always extracts the deployment zip to /var/task, so this becomes
# /var/task/fonts/ automatically — no hardcoded absolute path needed).
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"

# Four weights used across the templates: a heavy/black weight for large
# display headlines and big numbers, a bold weight for the quote template,
# a semibold for tags/eyebrows, and a medium weight for body/subtext/footer.
# Defaults name generic roles, not a specific typeface — point them at
# whatever files you place in fonts/.
FONT_BLACK = os.environ.get("FONT_BLACK", "Display-Black.otf")
FONT_BOLD = os.environ.get("FONT_BOLD", "Display-Bold.otf")
FONT_SEMIBOLD = os.environ.get("FONT_SEMIBOLD", "Text-SemiBold.otf")
FONT_MEDIUM = os.environ.get("FONT_MEDIUM", "Text-Medium.otf")


def _font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def F_DISPLAY_BLACK(s): return _font(FONT_BLACK, s)
def F_DISPLAY_BOLD(s):  return _font(FONT_BOLD, s)
def F_SEMIBOLD(s):      return _font(FONT_SEMIBOLD, s)
def F_MEDIUM(s):         return _font(FONT_MEDIUM, s)


def wrap_text(draw, text, fnt, max_width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), test, font=fnt)
            if bbox[2] - bbox[0] <= max_width or not current:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(draw, lines, fnt, center_x, start_y, line_height, fill=WHITE, align="center", left_x=None):
    y = start_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        w = bbox[2] - bbox[0]
        x = center_x - w / 2 if align == "center" else left_x
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def letterspace_draw(draw, text, fnt, x, y, fill, tracking):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        bbox = draw.textbbox((0, 0), ch, font=fnt)
        cx += (bbox[2] - bbox[0]) + tracking
    return cx


def _tracked_width(draw, text, fnt, tracking):
    return sum((draw.textbbox((0, 0), c, font=fnt)[2] - draw.textbbox((0, 0), c, font=fnt)[0]) + tracking for c in text) - tracking


def _wordmark_footer(d, rule=True):
    if rule:
        rule_y = H - MARGIN - 50
        d.line([(MARGIN, rule_y), (W - MARGIN, rule_y)], fill=BORDER_GREY, width=2)
        y = rule_y + 18
    else:
        y = H - MARGIN - 30
    wm_font = F_MEDIUM(22)
    wm_text = BRAND_HANDLE
    bbox = d.textbbox((0, 0), wm_text, font=wm_font)
    w = bbox[2] - bbox[0]
    d.text((W / 2 - w / 2, y), wm_text, font=wm_font, fill=GREY)


# ---------------------------------------------------------------------------
# TEMPLATE: hook_simples — fields: {"headline": str}
# ---------------------------------------------------------------------------
def hook_simples(headline):
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    letterspace_draw(d, BRAND_NAME, F_SEMIBOLD(26), MARGIN, MARGIN, GREY, tracking=4)
    rule_y = MARGIN + 50
    d.line([(MARGIN, rule_y), (MARGIN + 110, rule_y)], fill=WHITE, width=2)
    headline_font = F_DISPLAY_BLACK(92)
    max_w = W - 2 * MARGIN
    lines = wrap_text(d, headline, headline_font, max_w)
    line_h = 100
    total_h = line_h * len(lines)
    start_y = (H - total_h) / 2
    draw_multiline(d, lines, headline_font, W / 2, start_y, line_h, WHITE, align="center")
    return img


# ---------------------------------------------------------------------------
# TEMPLATE: quote — fields: {"quote": str, "attribution": str}
# ---------------------------------------------------------------------------
def quote(quote, attribution):
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    letterspace_draw(d, BRAND_NAME, F_SEMIBOLD(26), MARGIN, MARGIN, GREY, tracking=4)
    rule_y = MARGIN + 50
    d.line([(MARGIN, rule_y), (MARGIN + 110, rule_y)], fill=WHITE, width=2)
    d.text((MARGIN - 8, 220), "\u201C", font=F_DISPLAY_BLACK(140), fill=BORDER_GREY)
    quote_font = F_DISPLAY_BOLD(72)
    max_w = W - 2 * MARGIN
    lines = wrap_text(d, quote, quote_font, max_w)
    line_h = 82
    total_h = line_h * len(lines)
    start_y = (H - total_h) / 2
    draw_multiline(d, lines, quote_font, W / 2, start_y, line_h, WHITE, align="center")
    attr_font = F_MEDIUM(28)
    bbox = d.textbbox((0, 0), attribution, font=attr_font)
    w = bbox[2] - bbox[0]
    d.text((W / 2 - w / 2, start_y + total_h + 40), attribution, font=attr_font, fill=GREY)
    return img


# ---------------------------------------------------------------------------
# TEMPLATE: framed — fields: {"headline": str}
# ---------------------------------------------------------------------------
def framed(headline):
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    inset, bl, stroke = 50, 55, 3
    for x, y, dx, dy in [(inset, inset, 1, 1), (W - inset, inset, -1, 1),
                         (inset, H - inset, 1, -1), (W - inset, H - inset, -1, -1)]:
        d.line([(x, y), (x + dx * bl, y)], fill=WHITE, width=stroke)
        d.line([(x, y), (x, y + dy * bl)], fill=WHITE, width=stroke)
    headline_font = F_DISPLAY_BLACK(86)
    max_w = W - 2 * (inset + 70)
    lines = wrap_text(d, headline, headline_font, max_w)
    line_h = 94
    total_h = line_h * len(lines)
    start_y = (H - total_h) / 2 - 20
    draw_multiline(d, lines, headline_font, W / 2, start_y, line_h, WHITE, align="center")
    wm_font = F_SEMIBOLD(24)
    wm_text = BRAND_NAME
    tracked_w = _tracked_width(d, wm_text, wm_font, 4)
    letterspace_draw(d, wm_text, wm_font, W / 2 - tracked_w / 2, H - inset - 50, GREY, tracking=4)
    return img


# ---------------------------------------------------------------------------
# TEMPLATE: left_editorial — fields: {"headline": str}
# ---------------------------------------------------------------------------
def left_editorial(headline):
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    wm_font = F_SEMIBOLD(24)
    wm_text = BRAND_NAME
    tracked_w = _tracked_width(d, wm_text, wm_font, 3)
    letterspace_draw(d, wm_text, wm_font, W - MARGIN - tracked_w, MARGIN, GREY, tracking=3)
    headline_font = F_DISPLAY_BLACK(96)
    max_w = W - 2 * MARGIN - 40
    lines = wrap_text(d, headline, headline_font, max_w)
    line_h = 104
    total_h = line_h * len(lines)
    start_y = H * 0.55 - total_h / 2
    d.rectangle([MARGIN, start_y + 6, MARGIN + 6, start_y + total_h - 18], fill=WHITE)
    draw_multiline(d, lines, headline_font, None, start_y, line_h, WHITE, align="left", left_x=MARGIN + 40)
    return img


# ---------------------------------------------------------------------------
# TEMPLATE: tag_headline — fields: {"tag": str, "headline": str, "subtext": str|None}
# ---------------------------------------------------------------------------
def tag_headline(tag, headline, subtext=None):
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    tag_font = F_SEMIBOLD(24)
    tracked_w = _tracked_width(d, tag, tag_font, 3)
    pad_x, pad_y = 22, 14
    tag_w, tag_h = tracked_w + pad_x * 2, 24 + pad_y * 2
    d.rectangle([MARGIN, MARGIN, MARGIN + tag_w, MARGIN + tag_h], outline=WHITE, width=2)
    letterspace_draw(d, tag, tag_font, MARGIN + pad_x, MARGIN + pad_y - 2, WHITE, tracking=3)

    headline_font = F_DISPLAY_BLACK(84)
    max_w = W - 2 * MARGIN
    lines = wrap_text(d, headline, headline_font, max_w)
    line_h = 92
    total_h = line_h * len(lines)

    sub_font = F_MEDIUM(38)
    sub_lines = wrap_text(d, subtext, sub_font, max_w) if subtext else []
    sub_line_h = 50
    sub_total_h = sub_line_h * len(sub_lines) + (30 if sub_lines else 0)

    start_y = (H - (total_h + sub_total_h)) / 2 + 20
    end_y = draw_multiline(d, lines, headline_font, W / 2, start_y, line_h, WHITE, align="center")
    if sub_lines:
        draw_multiline(d, sub_lines, sub_font, W / 2, end_y + 30, sub_line_h, GREY, align="center")

    _wordmark_footer(d)
    return img


# ---------------------------------------------------------------------------
# TEMPLATE: tag_stat — fields: {"tag": str, "big_number": str, "label": str}
# ---------------------------------------------------------------------------
def tag_stat(tag, big_number, label):
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    tag_font = F_SEMIBOLD(24)
    tracked_w = _tracked_width(d, tag, tag_font, 3)
    pad_x, pad_y = 22, 14
    tag_w, tag_h = tracked_w + pad_x * 2, 24 + pad_y * 2
    d.rectangle([MARGIN, MARGIN, MARGIN + tag_w, MARGIN + tag_h], outline=WHITE, width=2)
    letterspace_draw(d, tag, tag_font, MARGIN + pad_x, MARGIN + pad_y - 2, WHITE, tracking=3)

    num_font = F_DISPLAY_BLACK(150 if len(big_number) > 8 else 220)
    bbox = d.textbbox((0, 0), big_number, font=num_font)
    num_h = bbox[3] - bbox[1]
    num_y = H * 0.38
    draw_multiline(d, [big_number], num_font, W / 2, num_y, num_h + 20, WHITE, align="center")

    label_font = F_MEDIUM(36)
    max_w = W - 2 * MARGIN
    lines = wrap_text(d, label, label_font, max_w)
    # Pillow draws from the ascender line, so the glyph's real bottom is at
    # num_y + bbox[3] — not num_y + num_h. Measuring off the ink height alone
    # loses the whole ascender gap (~51px at 220pt) and the label collides with
    # the number.
    label_y = num_y + bbox[3] + 50
    draw_multiline(d, lines, label_font, W / 2, label_y, 48, GREY, align="center")

    _wordmark_footer(d)
    return img


# Registry the Lambda dispatches on — key is the "template" value sent in the request
TEMPLATES = {
    "hook_simples": hook_simples,
    "quote": quote,
    "framed": framed,
    "left_editorial": left_editorial,
    "tag_headline": tag_headline,
    "tag_stat": tag_stat,
}

# Reference only (not enforced at runtime) — required fields per template,
# for validation and for writing the Claude prompt correctly.
FIELD_SCHEMA = {
    "hook_simples": ["headline"],
    "quote": ["quote", "attribution"],
    "framed": ["headline"],
    "left_editorial": ["headline"],
    "tag_headline": ["tag", "headline"],       # subtext optional
    "tag_stat": ["tag", "big_number", "label"],
}
