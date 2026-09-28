"""Embed the existing Chinese copy in rendered HTML before publication.

Quarto remains the English source, and assets/i18n/zh.json remains the Chinese
source. CSS selects the language before first paint; no browser translation
request, page hiding, or view-transition support is needed.
"""

import hashlib
import json
import os
from pathlib import Path

from bs4 import BeautifulSoup


SITE = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
if not OUTPUT.is_absolute():
    OUTPUT = SITE / OUTPUT


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
    for element in soup.select(".pace-brand-tagline"):
        element.decompose()
    for element in soup.select(".pace-brand-main"):
        element.unwrap()

    # Keep the brand descriptor in the HTML before first paint, in both languages.
    brand = soup.select_one(".navbar-brand-container")
    brand["class"] = list(dict.fromkeys([*brand.get("class", []), "pace-brand-lockup"]))
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

    # Refresh cached CSS when previewing a changed header layout.
    css_version = hashlib.sha256((SITE / "pace-site.css").read_bytes()).hexdigest()[:12]
    for link in soup.select('link[rel="stylesheet"]'):
        href = link.get("href", "")
        if href.split("?", 1)[0].endswith("pace-site.css"):
            link["href"] = href.split("?", 1)[0] + "?v=" + css_version

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
