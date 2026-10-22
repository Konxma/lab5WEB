"""Render saved, unmodified console logs as readable report images."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
FONT = Path("C:/Windows/Fonts/consola.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/consolab.ttf")


def render(source: str, target: str, heading: str) -> None:
    lines = (EVIDENCE / source).read_text(encoding="utf-8-sig").splitlines()
    font = ImageFont.truetype(str(FONT), 22)
    bold = ImageFont.truetype(str(FONT_BOLD), 28)
    width = 1440
    row_height = 31
    height = max(420, 136 + len(lines) * row_height + 42)
    image = Image.new("RGB", (width, height), "#111a2b")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((30, 30, width - 30, height - 30), radius=18, fill="#172338", outline="#425674", width=2)
    draw.text((58, 55), heading, font=bold, fill="#f3f7ff")
    draw.line((56, 105, width - 56, 105), fill="#425674", width=2)
    for index, line in enumerate(lines):
        color = "#86e3b1" if "successfully started" in line or "pass 1" in line or line.startswith("ok ") else "#dce7f7"
        draw.text((58, 126 + index * row_height), line, font=font, fill=color)
    image.save(EVIDENCE / target)


render("startup.log", "00-startup.png", "Запуск NestJS: усі модулі ініціалізовано")
render("test-run.log", "06-tests.png", "Наскрізна перевірка: npm test")
