"""Create bilingual, 1080x1350 WeChat Moments posters from site copy.

Run from a Python environment with scripts/poster-requirements.txt installed.
The output is static so ordinary GitHub Pages visitors need no image service.
"""

import json
import re
from datetime import date
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont


SITE = Path(__file__).resolve().parents[1]
DESTINATION = SITE / "assets/share-posters"
TRANSLATIONS = json.loads((SITE / "assets/i18n/zh.json").read_text(encoding="utf-8"))
SIZE = (1080, 1350)
PAPER = "#fffdf7"
INK = "#171716"
SOFT = "#484a43"
MOSS = "#6c745f"
RULE = "#d8dcd0"
LATIN = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
LATIN_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
CHINESE = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")


def font(size, language="en", bold=False):
    if language == "zh":
        return ImageFont.truetype(str(CHINESE), size, index=1 if bold else 0)
    return ImageFont.truetype(str(LATIN_BOLD if bold else LATIN), size)


def lines(draw, text, face, max_width, language):
    # Keep embedded Latin terms (for example HPAI and agent-based) intact.
    words = (re.findall(r"[A-Za-z0-9]+(?:[-–][A-Za-z0-9]+)*|[^\x00-\x7f]|\s+|.", text)
             if language == "zh" else text.split())
    output = []
    current = ""
    for word in words:
        candidate = (current + word) if language == "zh" else (current + " " + word).strip()
        if current and draw.textlength(candidate, font=face) > max_width:
            output.append(current.rstrip())
            current = word.lstrip()
        else:
            current = candidate
    if current:
        output.append(current.rstrip())
    return output


def wrapped(draw, text, x, y, width, face, leading, language, fill=INK):
    for line in lines(draw, text, face, width, language):
        draw.text((x, y), line, font=face, fill=fill, anchor="lt")
        y += leading
    return y


def curated_lines(draw, text, requested, x, y, face, leading, fill=INK):
    # Curated breaks prevent isolated Chinese characters or split English terms.
    if "".join(requested) != text:
        raise ValueError("Poster line breaks no longer match the page copy")
    for line in requested:
        if draw.textlength(line, font=face) > SIZE[0] - x - 72:
            raise ValueError(f"Poster line is too wide: {line}")
        draw.text((x, y), line, font=face, fill=fill, anchor="lt")
        y += leading
    return y


def frontmatter_title(path):
    contents = path.read_text(encoding="utf-8")
    match = re.search(r'^title: "([^"]+)"$', contents, re.MULTILINE)
    if not match:
        raise ValueError(f"Missing page title: {path}")
    return match.group(1)


def page_date(path):
    contents = path.read_text(encoding="utf-8")
    match = re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', contents)
    if not match:
        raise ValueError(f"Missing publication date: {path}")
    return date.fromisoformat(match.group(1))


def qr_for(url):
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=4)
    code.add_data(url)
    code.make(fit=True)
    return code.make_image(fill_color=INK, back_color="white").convert("RGB").resize(
        (208, 208), Image.Resampling.NEAREST
    )


def poster(page, language, title, description=None, published=None):
    canvas = Image.new("RGB", SIZE, PAPER)
    draw = ImageDraw.Draw(canvas)

    # A very faint echo of the existing homepage flyway network, never a text layer.
    network = Image.open(SITE / "assets/backgrounds/flyway-network.png").convert("RGBA")
    network.thumbnail((560, 850), Image.Resampling.LANCZOS)
    alpha = network.getchannel("A").point(lambda value: round(value * 0.18))
    network.putalpha(alpha)
    canvas.paste(network, (SIZE[0] - network.width + 90, 222), network)
    draw = ImageDraw.Draw(canvas)

    logo = Image.open(SITE / "assets/logo-concepts/pace-logo-official-v2.png").convert("RGBA")
    logo.thumbnail((145, 145), Image.Resampling.LANCZOS)
    canvas.paste(logo, (72, 55), logo)
    draw.text((236, 95), "PACE Lab", font=font(55, bold=True), fill=INK, anchor="lt")
    draw.line((72, 226, 1008, 226), fill=RULE, width=2)

    eyebrow = "研究动态" if language == "zh" else "RESEARCH STORY"
    if page == "index":
        eyebrow = "研究团队" if language == "zh" else "RESEARCH GROUP"
    draw.text((76, 279), eyebrow, font=font(30, language, bold=True), fill=MOSS, anchor="lt")

    title_size = 73 if language == "en" else 66
    if page == "index":
        title_size = 88
    title_language = "en" if page == "index" else language
    title_breaks = {
        "post-hpai-waterbirds": ["从一群水鸟中，我们能看出", "什么 HPAI 风险信息？"],
        "post-landscape-migration-avian-influenza": ["景观变化如何重塑", "迁徙与禽流感风险"],
    }
    if language == "zh" and page in title_breaks:
        title_y = curated_lines(draw, title, title_breaks[page], 72, 353,
                                font(title_size, language, bold=True), title_size + 17)
    else:
        title_y = wrapped(draw, title, 72, 353, 930, font(title_size, title_language, bold=True),
                          title_size + 17, title_language)

    if page == "index":
        tagline = ("病原体动态、动物迁移、全球变化与生态过程。" if language == "zh" else
                   "Pathogen Dynamics, Animal Movement, Global Changes, and Ecology.")
        tagline_y = wrapped(draw, tagline, 76, title_y + 40, 920,
                            font(39 if language == "zh" else 41, language), 61, language, SOFT)
        draw.line((76, tagline_y + 27, 184, tagline_y + 27), fill=MOSS, width=4)
        if language == "zh":
            curated_lines(draw, description, [
                "我们团队擅长运用统计模型、网络分析和机器学习等",
                "定量分析方法，结合个体基础模型（agent-based model）",
                "和箱式模型（compartment model）等机理模型，",
                "研究不同尺度上的传染病传播动态。",
            ], 76, tagline_y + 70, font(30, language), 52, SOFT)
        else:
            wrapped(draw, description, 76, tagline_y + 70, 914,
                    font(33), 52, language, SOFT)
    else:
        date_label = (f"{published.year} 年 {published.month} 月 {published.day} 日" if language == "zh"
                      else f"{published:%B} {published.day}, {published.year}")
        draw.text((76, title_y + 43), date_label, font=font(32, language), fill=MOSS, anchor="lt")
        draw.line((76, title_y + 114, 190, title_y + 114), fill=MOSS, width=4)

    # High-contrast, quiet footer keeps the QR usable in a saved/compressed image.
    draw.rounded_rectangle((72, 1045, 1008, 1279), radius=18,
                           fill="#ffffff", outline=RULE, width=2)
    qr = qr_for("https://thepacelab.org/" + ("" if page == "index" else f"{page}.html") +
                f"?lang={language}")
    canvas.paste(qr, (780, 1058))
    callout = ("扫码浏览网站" if language == "zh" and page == "index" else
               "扫码阅读文章" if language == "zh" else
               "Scan to visit the site" if page == "index" else "Scan to read the post")
    draw.text((102, 1090), callout, font=font(37, language, bold=True), fill=INK, anchor="lt")
    draw.text((102, 1164), "thepacelab.org", font=font(30), fill=SOFT, anchor="lt")
    draw.text((102, 1218), "PACE Lab", font=font(25, bold=True), fill=MOSS, anchor="lt")

    DESTINATION.mkdir(parents=True, exist_ok=True)
    output = DESTINATION / f"{page}-{language}.png"
    canvas.save(output, optimize=True)
    return output


def main():
    home_zh = TRANSLATIONS["pages"]["index"]["selectors"][".home-simple > p"]
    home_en = ("Our team combines quantitative analyses, including statistical modeling, "
               "network analysis, and machine learning, with mechanistic approaches, "
               "particularly agent-based and compartment models, to understand infectious "
               "disease transmission in wildlife across scales.")
    home_source = (SITE / "index.qmd").read_text(encoding="utf-8")
    if home_en not in home_source:
        raise ValueError("Homepage English copy changed; update the poster generator before regenerating")
    generated = [poster("index", "en", "PACE Lab", home_en),
                 poster("index", "zh", "PACE Lab", home_zh)]
    for name in ("post-hpai-waterbirds", "post-landscape-migration-avian-influenza"):
        source = SITE / f"{name}.qmd"
        published = page_date(source)
        generated.append(poster(name, "en", frontmatter_title(source), published=published))
        generated.append(poster(name, "zh", TRANSLATIONS["pages"][name]["title"],
                                published=published))
    for path in generated:
        print(path.relative_to(SITE))


if __name__ == "__main__":
    main()
