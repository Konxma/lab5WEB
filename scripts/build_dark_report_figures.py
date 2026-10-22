"""Make dark report images in the style of the supplied request/response example."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report_docx" / "dark_figures"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = json.loads((ROOT / "evidence" / "api-results.json").read_text(encoding="utf-8"))

WIDTH = 1280
LEFT = 28
ROW = 32
FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 25)
FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 26)
BG = "#1e1e1e"
BAR = "#252526"
INK = "#d4d4d4"
MUTED = "#858585"
ACCENT = "#4ec9b0"
GOLD = "#d7ba7d"


def wrap_lines(lines, *, code=False):
    wrapped = []
    max_pixels = WIDTH - (LEFT + 60 if code else LEFT) - 42
    for entry in lines:
        number, line = entry if code else (None, entry)
        if not line:
            wrapped.append((number, ""))
            continue
        indent = len(line) - len(line.lstrip())
        continuation_indent = min(indent + 2, 10)
        first = True
        while FONT.getlength(line) > max_pixels:
            cut = len(line)
            while cut > 1 and FONT.getlength(line[:cut]) > max_pixels:
                cut -= 1
            space = line.rfind(" ", indent + 1, cut + 1)
            if space > indent:
                cut = space
            wrapped.append((number if first else None, line[:cut].rstrip()))
            line = " " * continuation_indent + line[cut:].lstrip()
            first = False
        wrapped.append((number if first else None, line))
    return wrapped


def panel(number, heading, lines, *, code=False):
    rows = wrap_lines(lines, code=code)
    height = max(190, 65 + len(rows) * ROW + 24)
    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, 47), fill=BAR)
    draw.text((LEFT, 10), heading, font=FONT_TITLE, fill="#ffffff")
    for index, (source_number, line) in enumerate(rows):
        y = 64 + index * ROW
        if code:
            if source_number is not None:
                draw.text((LEFT, y), f"{source_number:02}", font=FONT_SMALL, fill=MUTED)
            draw.text((LEFT + 60, y), line, font=FONT, fill=INK)
        else:
            color = GOLD if line.startswith(("GET ", "POST ", "HTTP ")) else INK
            draw.text((LEFT, y), line, font=FONT, fill=color)
    img.save(OUT / f"fig-{number:02}.png")


def wrap_half(lines):
    wrapped = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        while len(line) > 40:
            cut = line.rfind(" ", 8, 40)
            if cut < 8:
                cut = 40
            wrapped.append(line[:cut].rstrip())
            line = "  " + line[cut:].lstrip()
        wrapped.append(line)
    return wrapped


def api_panel(number, exchange):
    request = [
        f"> {exchange['method']} {exchange['route']} HTTP/1.1",
        "> Host: localhost:3000",
    ]
    if exchange["requestBody"] is not None:
        request.append("> Content-Type: application/json")
        request.append("")
        request.extend(json.dumps(exchange["requestBody"], ensure_ascii=False, indent=2).splitlines())
    response = [
        f"< HTTP/1.1 {exchange['status']}",
        "< Content-Type: application/json",
        "",
        *json.dumps(exchange["body"], ensure_ascii=False, indent=2).splitlines(),
    ]
    request, response = wrap_half(request), wrap_half(response)
    height = max(210, 65 + max(len(request), len(response)) * 30 + 24)
    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, 47), fill=BAR)
    draw.text((LEFT, 10), "requests.http / Response", font=FONT_TITLE, fill="#ffffff")
    draw.line((WIDTH // 2, 47, WIDTH // 2, height), fill="#414141", width=2)
    for index, line in enumerate(request):
        draw.text((22, 68 + index * 30), line, font=FONT_SMALL,
                  fill=GOLD if line.startswith(">") else INK)
    for index, line in enumerate(response):
        color = ACCENT if line.startswith("< HTTP/1.1 20") else "#f48771" if line.startswith("< HTTP/1.1 404") else INK
        draw.text((WIDTH // 2 + 22, 68 + index * 30), line, font=FONT_SMALL, fill=color)
    img.save(OUT / f"fig-{number:02}.png")


def source_lines(rel, first, last):
    lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    return list(enumerate(lines[first - 1:last], start=first))


def fact_path(rel):
    if not (ROOT / rel).is_file():
        raise FileNotFoundError(rel)
    return rel.replace("/", "\\")


startup = (ROOT / "evidence" / "startup.log").read_text(encoding="utf-8").splitlines()
startup = [line for line in startup if any(key in line for key in
           ("GadgetsModule", "OrdersModule", "SharedModule", "GadgetsService",
            "OrdersService", "successfully started"))]
panel(1, "Запуск застосунку: журнал NestJS", startup)

tree = [
    "src/",
    "  " + fact_path("src/app.module.ts").split("\\")[-1],
    "  gadgets/",
    "    " + fact_path("src/gadgets/gadgets.module.ts").split("\\")[-1],
    "    " + fact_path("src/gadgets/gadgets.controller.ts").split("\\")[-1],
    "    " + fact_path("src/gadgets/gadgets.service.ts").split("\\")[-1],
    "    dto/ (CreateGadgetDto, UpdateGadgetDto)",
    "  orders/",
    "    " + fact_path("src/orders/orders.module.ts").split("\\")[-1],
    "    " + fact_path("src/orders/orders.controller.ts").split("\\")[-1],
    "    " + fact_path("src/orders/orders.service.ts").split("\\")[-1],
    "  shared/",
    "    " + fact_path("src/shared/shared.module.ts").split("\\")[-1],
    "    " + fact_path("src/shared/slug.service.ts").split("\\")[-1],
    "    config/ (STORE_CONFIG, FEE_CALCULATOR)",
]
panel(2, "Структура файлів поточного проєкту", tree)

for number, rel, first, last in [
    (3, "src/app.module.ts", 1, 10),
    (4, "src/shared/shared.module.ts", 1, 12),
    (5, "src/shared/slug.service.ts", 11, 21),
    (6, "src/gadgets/gadgets.service.ts", 7, 19),
    (9, "src/shared/config/app-config.provider.ts", 1, 16),
    (10, "src/shared/config/fee-calculator.provider.ts", 1, 16),
    (11, "src/orders/orders.module.ts", 1, 12),
]:
    panel(number, rel, source_lines(rel, first, last), code=True)

for number, exchange in [(7, RESULTS[0]), (8, RESULTS[1]), (12, RESULTS[2]),
                         (13, RESULTS[3]), (14, RESULTS[4])]:
    api_panel(number, exchange)

panel(15, "Scope.REQUEST: ID двох запитів", [
    "GET /gadgets",
    "X-Request-Id: " + RESULTS[0]["requestId"],
    "X-Request-Trace-Match: " + RESULTS[0]["traceMatch"],
    "",
    "POST /gadgets",
    "X-Request-Id: " + RESULTS[1]["requestId"],
    "X-Request-Trace-Match: " + RESULTS[1]["traceMatch"],
])

test_log = (ROOT / "evidence" / "test-run.log").read_text(encoding="utf-8-sig").splitlines()
test_log = [line for line in test_log if line.startswith(("TAP", "# Subtest", "ok ", "# tests", "# pass", "# fail"))]
panel(16, "npm test: результат перевірки", test_log)

print(f"Created {len(list(OUT.glob('fig-*.png')))} figures from source and recorded runs")
