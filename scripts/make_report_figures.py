"""Create report figures from the actual project files and captured HTTP results."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "assets"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = json.loads((ROOT / "evidence" / "api-results.json").read_text(encoding="utf-8"))
FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 21)
FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 19)
FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22)
BG = "#1e1e1e"
BAR = "#252526"
INK = "#d4d4d4"
MUTED = "#858585"
GREEN = "#4ec9b0"
GOLD = "#dcdcaa"


def code_lines(path, first=None, last=None):
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    start = 1 if first is None else first
    stop = len(lines) if last is None else last
    return [(i, lines[i - 1]) for i in range(start, min(stop, len(lines)) + 1)]


def code_figure(number, title, lines, width=1600):
    row = 30
    height = 70 + row * len(lines) + 28
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 52), fill=BAR)
    draw.text((26, 13), title, font=FONT_BOLD, fill="#ffffff")
    for position, (line_number, content) in enumerate(lines):
        y = 68 + position * row
        draw.text((25, y), f"{line_number:>3}", font=FONT_SMALL, fill=MUTED)
        color = GOLD if content.strip().startswith(("@", "export", "const ")) else INK
        draw.text((92, y), content.expandtabs(2), font=FONT, fill=color)
    image.save(OUT / f"fig-{number:02}.png")


def plain_figure(number, title, lines, width=1600, highlight=None):
    row = 31
    height = 70 + row * len(lines) + 28
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 52), fill=BAR)
    draw.text((26, 13), title, font=FONT_BOLD, fill="#ffffff")
    for position, line in enumerate(lines):
        color = GREEN if highlight and highlight in line else INK
        draw.text((28, 68 + position * row), line, font=FONT, fill=color)
    image.save(OUT / f"fig-{number:02}.png")


def api_figure(number, title, exchange, width=1600):
    request = [f"> {exchange['method']} {exchange['route']} HTTP/1.1", "> Host: localhost:3000"]
    if exchange["method"] == "POST":
        request.append("> Content-Type: application/json")
        request.append("")
        if exchange["label"] == "Створення гаджета":
            body = {"title": "Новий Смартфон", "price": 30000, "warrantyMonths": 12,
                    "cpu": "Snapdragon 8 Gen 3", "ramGb": 12}
        elif exchange["label"] == "Невідомий товар":
            body = {"productId": "99999", "quantity": 1, "customerEmail": "student@example.com"}
        else:
            body = {"productId": "3", "quantity": 2, "customerEmail": "student@example.com"}
        request.extend(json.dumps(body, ensure_ascii=False, indent=2).splitlines())
    response = [f"< HTTP/1.1 {exchange['status']}", "< Content-Type: application/json", ""]
    response.extend(json.dumps(exchange["body"], ensure_ascii=False, indent=2).splitlines())
    count = max(len(request), len(response))
    row = 29
    height = 75 + row * count + 30
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 52), fill=BAR)
    draw.text((26, 13), title, font=FONT_BOLD, fill="#ffffff")
    draw.line((width // 2, 52, width // 2, height), fill="#3a3a3a", width=2)
    for position, line in enumerate(request):
        draw.text((26, 72 + position * row), line, font=FONT_SMALL, fill=GOLD if line.startswith(">") else INK)
    for position, line in enumerate(response):
        color = GREEN if line.startswith("< HTTP/1.1 20") else "#f48771" if line.startswith("< HTTP/1.1 404") else INK
        draw.text((width // 2 + 28, 72 + position * row), line, font=FONT_SMALL, fill=color)
    image.save(OUT / f"fig-{number:02}.png")


plain_figure(1, "Terminal - npm start", (ROOT / "evidence" / "startup.log").read_text(encoding="utf-8").splitlines(), highlight="successfully started")
plain_figure(2, "Explorer - структура проєкту", [
    "lab5WEB", "  src", "    app.module.ts", "    gadgets", "      gadgets.module.ts", "      gadgets.controller.ts",
    "      gadgets.service.ts", "      gadget.entity.ts", "      dto / create-gadget.dto.ts", "    orders", "      orders.module.ts", "      orders.controller.ts",
    "      orders.service.ts", "    shared", "      shared.module.ts", "      slug.service.ts", "      config / request-id.service.ts",
    "  requests.http", "  test/api.test.js",
])
code_figure(3, "app.module.ts", code_lines("src/app.module.ts"))
code_figure(4, "shared.module.ts", code_lines("src/shared/shared.module.ts"))
code_figure(5, "slug.service.ts", code_lines("src/shared/slug.service.ts"))
code_figure(6, "gadgets.service.ts - OnModuleInit", code_lines("src/gadgets/gadgets.service.ts", 1, 29))
api_figure(7, "requests.http / Response", RESULTS[0])
api_figure(8, "requests.http / Response", RESULTS[1])
code_figure(9, "app-config.provider.ts - useValue", code_lines("src/shared/config/app-config.provider.ts"))
code_figure(10, "fee-calculator.provider.ts - useFactory", code_lines("src/shared/config/fee-calculator.provider.ts"))
code_figure(11, "orders.module.ts", code_lines("src/orders/orders.module.ts"))
api_figure(12, "requests.http / Response", RESULTS[2])
api_figure(13, "requests.http / Response", RESULTS[3])
api_figure(14, "requests.http / Response", RESULTS[4])
plain_figure(15, "Scope.REQUEST - заголовки двох запитів", [
    "GET /gadgets",
    f"X-Request-Id: {RESULTS[0]['requestId']}",
    f"X-Request-Trace-Match: {RESULTS[0]['traceMatch']}",
    "",
    "POST /gadgets",
    f"X-Request-Id: {RESULTS[1]['requestId']}",
    f"X-Request-Trace-Match: {RESULTS[1]['traceMatch']}",
])
plain_figure(16, "Terminal - npm test", (ROOT / "evidence" / "test-run.log").read_text(encoding="utf-8-sig").splitlines(), highlight="pass 1")
print("Created 16 figures from project files and recorded runs")
