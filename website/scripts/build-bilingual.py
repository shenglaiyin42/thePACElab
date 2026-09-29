"""Embed the existing Chinese copy in rendered HTML before publication.

Quarto remains the English source, and assets/i18n/zh.json remains the Chinese
source. CSS selects the language before first paint; no browser translation
request, page hiding, or view-transition support is needed.
"""

import hashlib
import json
import os
from base64 import b64encode
from io import BytesIO
from pathlib import Path

import qrcode
from qrcode.image.svg import SvgPathImage
from bs4 import BeautifulSoup


SITE = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
PUBLIC_ORIGIN = "https://thepacelab.org"
if not OUTPUT.is_absolute():
    OUTPUT = SITE / OUTPUT


def language_pair(soup, english, chinese):
    wrapper = soup.new_tag("span")
    for language, label in (("en", english), ("zh", chinese)):
        span = soup.new_tag("span", attrs={"data-pace-copy": language})
        span.string = label
        wrapper.append(span)
    return wrapper


def qr_image(url):
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                         box_size=6, border=2)
    code.add_data(url)
    code.make(fit=True)
    output = BytesIO()
    code.make_image(image_factory=SvgPathImage).save(output)
    return "data:image/svg+xml;base64," + b64encode(output.getvalue()).decode("ascii")


def add_share_controls(soup, path, copy):
    page_name = path.stem
    has_poster = page_name == "index" or page_name.startswith("post-")
    page_path = "/" if page_name == "index" else f"/{page_name}.html"
    canonical = PUBLIC_ORIGIN + page_path
    english_title = soup.html["data-pace-title-en"].removesuffix(" – PACE Lab")
    chinese_title = "PACE Lab" if page_name == "index" else copy["title"]

    share = soup.new_tag("details", attrs={
        "class": "pace-share",
        "data-share-url": canonical,
        "data-share-title-en": english_title,
        "data-share-title-zh": chinese_title,
    })
    summary = soup.new_tag("summary")
    summary.append(language_pair(soup, "Share", "分享"))
    share.append(summary)
    menu = soup.new_tag("div", attrs={"class": "pace-share-menu"})
    for css_class, label in (("pace-share-x", "X / Twitter"),
                             ("pace-share-bluesky", "Bluesky")):
        link = soup.new_tag("a", href=canonical + "?lang=en", attrs={
            "class": css_class, "target": "_blank", "rel": "noopener noreferrer",
        })
        link.string = label
        menu.append(link)
    for css_class, english, chinese in (
        ("pace-share-native", "More options", "更多方式"),
        ("pace-share-copy", "Copy link", "复制链接"),
        ("pace-share-wechat", "WeChat / Moments", "微信 / 朋友圈"),
    ):
        button = soup.new_tag("button", type="button", attrs={"class": css_class})
        if css_class == "pace-share-native":
            button["hidden"] = ""
        button.append(language_pair(soup, english, chinese))
        menu.append(button)
    menu_status = soup.new_tag("p", attrs={
        "class": "pace-share-menu-status", "role": "status", "aria-live": "polite",
    })
    menu.append(menu_status)
    share.append(menu)

    if page_name.startswith("post-"):
        date = soup.select_one(".post-article .post-date")
        if date is None:
            raise ValueError(f"{path.name}: missing article date for share control")
        row = soup.new_tag("div", attrs={"class": "pace-post-meta"})
        date.wrap(row)
        row.append(share)
    else:
        share["class"] = ["pace-share", "pace-share-footer"]
        soup.select_one("#quarto-document-content").append(share)

    dialog = soup.new_tag("dialog", attrs={
        "class": "pace-share-dialog", "aria-labelledby": "pace-share-dialog-title",
    })
    close = soup.new_tag("button", type="button", attrs={
        "class": "pace-share-dialog-close", "aria-label": "Close / 关闭",
    })
    close.string = "×"
    dialog.append(close)
    heading = soup.new_tag("h2", id="pace-share-dialog-title")
    heading.append(language_pair(soup, "Share via WeChat", "分享到微信"))
    dialog.append(heading)
    intro = soup.new_tag("p")
    if has_poster:
        intro.append(language_pair(
            soup,
            "Save this poster to share in WeChat Moments. Its QR code opens this page.",
            "保存海报后可分享到朋友圈；扫码即可打开当前页面。",
        ))
    else:
        intro.append(language_pair(
            soup,
            "Scan the QR code with WeChat. On your phone, tap ··· and choose Share to Moments.",
            "用微信扫一扫打开页面，再点右上角「···」选择「分享到朋友圈」。",
        ))
    dialog.append(intro)
    if has_poster:
        for language in ("en", "zh"):
            image = soup.new_tag("img", attrs={
                "class": "pace-share-poster", "data-share-poster": language,
                "src": f"assets/share-posters/{page_name}-{language}.png",
                "alt": f"PACE Lab poster for the {language.upper()} page with a QR code",
                "width": "240", "height": "300",
            })
            dialog.append(image)
        poster_link = soup.new_tag("a", href=f"assets/share-posters/{page_name}-en.png", attrs={
            "class": "pace-share-poster-download",
            "data-poster-en": f"assets/share-posters/{page_name}-en.png",
            "data-poster-zh": f"assets/share-posters/{page_name}-zh.png",
            "download": f"PACE-Lab-{page_name}-en.png",
        })
        poster_link.append(language_pair(soup, "Download PNG poster", "下载 PNG 海报"))
        dialog.append(poster_link)
    else:
        for language in ("en", "zh"):
            image = soup.new_tag("img", attrs={
                "class": "pace-share-qr", "data-share-qr": language,
                "src": qr_image(canonical + f"?lang={language}"),
                "alt": f"QR code for the {language.upper()} page",
                "width": "192", "height": "192",
            })
            dialog.append(image)
    copy_button = soup.new_tag("button", type="button", attrs={
        "class": "pace-share-dialog-copy",
    })
    copy_button.append(language_pair(soup, "Copy this link", "复制当前页面链接"))
    dialog.append(copy_button)
    status = soup.new_tag("p", attrs={"class": "pace-share-status", "role": "status",
                                      "aria-live": "polite"})
    dialog.append(status)
    soup.body.append(dialog)


def add_pair(soup, element, translation):
    # Paragraph groupings can differ between the author's language drafts.
    block = isinstance(translation, dict) and translation.get("block", False)
    tag = "div" if block else "span"
    attrs = {"data-pace-block": "true"} if block else {}
    english = soup.new_tag(tag, attrs={**attrs, "data-pace-copy": "en", "lang": "en"})
    for child in list(element.contents):
        english.append(child.extract())
    chinese = soup.new_tag(tag, attrs={**attrs, "data-pace-copy": "zh", "lang": "zh-CN"})
    if isinstance(translation, str):
        chinese.string = translation
    elif isinstance(translation, dict) and isinstance(translation.get("html"), str):
        fragment = BeautifulSoup(translation["html"], "html.parser")
        for child in list(fragment.contents):
            chinese.append(child.extract())
    else:
        raise ValueError("Invalid translation: expected text or an HTML object")
    element.append(english)
    element.append(chinese)


def build_page(path, copy, navigation):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    # Quarto preview may rebuild one page at a time. Restore the English copy
    # before reprocessing any pages left over from an earlier render.
    for element in soup.select('[data-pace-copy="zh"]'):
        element.decompose()
    for element in soup.select('[data-pace-copy="en"]'):
        element.unwrap()
    for element in soup.select(".pace-language-item"):
        element.decompose()
    for element in soup.select(".pace-share, .pace-share-dialog"):
        element.decompose()
    for element in soup.select(".pace-post-meta"):
        element.unwrap()
    for element in soup.select(".pace-brand-tagline"):
        element.decompose()
    for element in soup.select(".pace-brand-main"):
        element.unwrap()

    # Keep the brand descriptor in the HTML before first paint, in both languages.
    brand = soup.select_one(".navbar-brand-container")
    brand["class"] = list(dict.fromkeys([*brand.get("class", []), "pace-brand-lockup"]))
    home_href = soup.select_one('.navbar-nav .nav-link')["href"]
    for link in brand.select("a.navbar-brand"):
        link["href"] = home_href
    main = soup.new_tag("div", attrs={"class": "pace-brand-main"})
    for element in list(brand.select(".navbar-brand")):
        main.append(element.extract())
    for whitespace in list(brand.find_all(string=True, recursive=False)):
        if not whitespace.strip():
            whitespace.extract()
    brand.append(main)
    tagline = soup.new_tag("div", attrs={"class": "pace-brand-tagline", "lang": "en"})
    for line in (
        "<strong>P</strong>athogen Dynamics, <strong>A</strong>nimal Movement,",
        "Global <strong>C</strong>hanges, and <strong>E</strong>cology",
    ):
        span = soup.new_tag("span")
        fragment = BeautifulSoup(line, "html.parser")
        for child in list(fragment.contents):
            span.append(child.extract())
        tagline.append(span)
        tagline.append("\n")
    brand.append(tagline)

    # Refresh cached header styles when the published layout changes.
    for link in soup.select('link[rel="stylesheet"]'):
        href = link.get("href", "").split("?", 1)[0]
        name = Path(href).name
        if name in {"pace-site.css", "navigation-stability-v4.css", "share-preview.css"}:
            css_version = hashlib.sha256((SITE / name).read_bytes()).hexdigest()[:12]
            link["href"] = href + "?v=" + css_version

    targets = []
    for selector, translation in copy["selectors"].items():
        matches = soup.select(selector)
        if len(matches) != 1:
            raise ValueError(f"{path.name}: {selector!r} matched {len(matches)} elements; expected one")
        targets.append((matches[0], translation))
    menu = soup.select(".navbar-nav .menu-text")
    if len(menu) != len(navigation):
        raise ValueError(f"{path.name}: unexpected navigation item count")
    for element in menu:
        english = element.get_text(strip=True)
        targets.append((element, navigation[english]))
    for element, translation in targets:
        add_pair(soup, element, translation)

    soup.html["data-pace-title-en"] = soup.title.get_text()
    soup.html["data-pace-title-zh"] = copy["title"] + " | PACE Lab"
    for element in soup.select(".publications-page ol"):
        element["lang"] = "en"

    nav = soup.select_one(".navbar-nav")
    item = soup.new_tag("li", attrs={"class": "nav-item pace-language-item"})
    button = soup.new_tag("button", attrs={
        "type": "button", "class": "pace-language-switch",
        "aria-pressed": "false", "aria-label": "Switch to Chinese",
    })
    button.string = "EN / 中文"
    item.append(button)
    nav.append(item)
    add_share_controls(soup, path, copy)
    return str(soup)


def main():
    translations = json.loads((SITE / "assets/i18n/zh.json").read_text(encoding="utf-8"))
    rendered = {}
    for name, copy in translations["pages"].items():
        path = OUTPUT / f"{name}.html"
        if not path.is_file():
            raise FileNotFoundError(f"Render the complete site first: missing {path}")
        rendered[path] = build_page(path, copy, translations["navigation"])
    # Validate every selector before updating any output file.
    for path, html in rendered.items():
        path.write_text(html, encoding="utf-8")
    print(f"Embedded English and Chinese copy in {len(rendered)} pages.")


if __name__ == "__main__":
    main()
