"""Extract only the shared diagram, excluding the incomplete embedded caption.

Run with the bundled workspace Python and Pillow. The English and Chinese
Word files contain pixel-identical diagram areas; both originals stay intact.
"""

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageChops


FOLDER = Path(__file__).resolve().parent
WEBSITE = FOLDER.parents[1] / "website"
SOURCE = {
    "en": FOLDER / "Climate_Change_Bird_Migration_HPAI_Research_Story_Draft.docx",
    "zh": FOLDER / "Climate_Change_Bird_Migration_HPAI_Research_Story_Chinese.docx",
}
OUTPUT = WEBSITE / "assets/posts/climate-change-bird-migration-hpai-figure.png"
DIAGRAM_BOX = (86, 92, 1290, 460)


def diagram(path):
    with ZipFile(path) as document:
        source = Image.open(BytesIO(document.read("word/media/image1.png"))).convert("RGB")
        if source.width != 1350 or source.height < DIAGRAM_BOX[3]:
            raise ValueError(f"Unexpected figure dimensions in {path.name}: {source.size}")
        return source.crop(DIAGRAM_BOX)


english = diagram(SOURCE["en"])
chinese = diagram(SOURCE["zh"])
if ImageChops.difference(english, chinese).getbbox() is not None:
    raise ValueError("The English and Chinese diagram areas are no longer identical")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
english.save(OUTPUT, optimize=True)
print(f"Saved {OUTPUT.relative_to(WEBSITE)} ({english.width} × {english.height})")
