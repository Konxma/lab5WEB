"""Make legible report figures directly from current source and recorded HTTP runs."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report_docx" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = json.loads((ROOT / "evidence" / "api-results.json").read_text(encoding="utf-8"))

WIDTH = 1200
LEFT = 64
ROW = 37
FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 27)
FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 24)
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 31)
BG = "#ffffff"
BAR = "#eaf1f8"
INK = "#172433"
MUTED = "#627387"
ACCENT = "#175fa8"


def wrap_lines(lines, *, code=False):
    wrapped = []
    max_pixels = WIDTH - (LEFT + 60 if code else LEFT) - 42
    for entry in lines:
        number, line = entry if code else (None, entry)
        if not line:
            wrapped.append((number, ""))
            continue
        indent = len(line) - len(line.lstrip())
        first = True
        while FONT.getlength(line) > max_pixels:
            cut = len(line)
            while cut > 1 and FONT.getlength(line[:cut]) > max_pixels:
                cut -= 1
            space = line.rfind(" ", indent + 1, cut + 1)
            if space > indent:
                cut = space
            wrapped.append((number if first else None, line[:cut].rstrip()))
            line = " " * (indent + 2) + line[cut:].lstrip()
            first = False
        wrapped.append((number if first else None, line))
    return wrapped


def panel(number, heading, lines, *, code=False):
    rows = wrap_lines(lines, code=code)
    height = max(250, 116 + len(rows) * ROW + 36)
    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH - 1, height - 1), outline="#cbd7e2", width=2)
    draw.rectangle((0, 0, WIDTH, 78), fill=BAR)
    draw.rectangle((0, 0, 9, height), fill=ACCENT)
    draw.text((LEFT, 20), heading, font=FONT_TITLE, fill=INK)
    for index, (source_number, line) in enumerate(rows):
        y = 105 + index * ROW
        if code:
            if source_number is not None:
                draw.text((LEFT, y), f"{source_number:02}", font=FONT_SMALL, fill=MUTED)
            draw.text((LEFT + 60, y), line, font=FONT, fill=INK)
        else:
            color = ACCENT if line.startswith(("GET ", "POST ", "HTTP ", "PASS")) else INK
            draw.text((LEFT, y), line, font=FONT, fill=color)
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

catalog = RESULTS[0]
panel(7, "GET /gadgets   HTTP 200", [
    "Відповідь сервера, основні поля:",
    *[f"id={item['id']} | {item['title']} | slug={item['slug']} | "
      f"price={item['price']} UAH" for item in catalog["body"]],
    "Кількість початкових гаджетів: " + str(len(catalog["body"])),
])

created = RESULTS[1]
panel(8, "POST /gadgets   HTTP 201", [
    "Запит: title=Новий Смартфон, price=30000, warrantyMonths=12,",
    "cpu=Snapdragon 8 Gen 3, ramGb=12",
    "",
    "Відповідь сервера:",
    *json.dumps(created["body"], ensure_ascii=False, indent=2).splitlines(),
])

order = RESULTS[2]
picked = {key: order["body"][key] for key in
          ("productId", "productTitle", "unitPrice", "quantity", "subtotal",
           "taxAmount", "total", "currency")}
panel(12, "POST /orders   HTTP 201", [
    "Запит: productId=3, quantity=2, customerEmail=student@example.com",
    "",
    "Відповідь сервера, суми замовлення:",
    *json.dumps(picked, ensure_ascii=False, indent=2).splitlines(),
])

missing = RESULTS[3]
panel(13, "POST /orders   HTTP 404", [
    "Запит: productId=99999, quantity=1",
    "",
    "Відповідь сервера:",
    *json.dumps(missing["body"], ensure_ascii=False, indent=2).splitlines(),
])

orders = RESULTS[4]
panel(14, "GET /orders   HTTP 200", [
    "Збережених замовлень: " + str(len(orders["body"])),
    "",
    "Перше замовлення, основні поля:",
    *json.dumps({key: orders["body"][0][key] for key in
                 ("productTitle", "quantity", "subtotal", "taxAmount", "total", "currency")},
                ensure_ascii=False, indent=2).splitlines(),
])

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
