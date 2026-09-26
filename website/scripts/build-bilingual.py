"""Embed the existing Chinese copy in rendered HTML before publication.

Quarto remains the English source, and assets/i18n/zh.json remains the Chinese
source. CSS selects the language before first paint; no browser translation
request, page hiding, or view-transition support is needed.
"""

import json
import os
from pathlib import Path

from bs4 import BeautifulSoup


SITE = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
if not OUTPUT.is_absolute():
    OUTPUT = SITE / OUTPUT


def add_pair(soup, element, translation):
    english = soup.new_tag("span", attrs={"data-pace-copy": "en", "lang": "en"})
    for child in list(element.contents):
        english.append(child.extract())
    chinese = soup.new_tag("span", attrs={"data-pace-copy": "zh", "lang": "zh-CN"})
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
