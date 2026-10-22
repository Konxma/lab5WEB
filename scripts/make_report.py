"""Build a seven-page PDF following the supplied practical-work report layout."""

from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "report" / "Практична_робота_5_Ткаченко_ВМ.pdf"
ASSETS = ROOT / "report" / "assets"
WIDTH, HEIGHT = A4
LEFT = 71
RIGHT = 43
TEXT_WIDTH = WIDTH - LEFT - RIGHT

pdfmetrics.registerFont(TTFont("TimesUA", "C:/Windows/Fonts/times.ttf"))
pdfmetrics.registerFont(TTFont("TimesUABold", "C:/Windows/Fonts/timesbd.ttf"))


def centered(c, text, y, bold=False, size=14):
    c.setFont("TimesUABold" if bold else "TimesUA", size)
    c.drawCentredString(WIDTH / 2, y, text)


def wrap(text, font="TimesUA", size=14, width=TEXT_WIDTH):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if pdfmetrics.stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(c, text, x, y, *, width=TEXT_WIDTH, leading=20, bold=False, centered_text=False):
    font = "TimesUABold" if bold else "TimesUA"
    c.setFont(font, 14)
    for line in wrap(text, font, 14, width):
        if centered_text:
            c.drawCentredString(x + width / 2, y, line)
        else:
            c.drawString(x, y, line)
        y -= leading
    return y


def figure(c, number, caption, y, max_height):
    path = ASSETS / f"fig-{number:02}.png"
    with Image.open(path) as image:
        pixel_width, pixel_height = image.size
    scale = min(TEXT_WIDTH / pixel_width, max_height / pixel_height)
    draw_width = pixel_width * scale
    draw_height = pixel_height * scale
    x = LEFT + (TEXT_WIDTH - draw_width) / 2
    image_bottom = y - draw_height
    c.drawImage(str(path), x, image_bottom, width=draw_width, height=draw_height, mask="auto")
    y = image_bottom - 17
    y = paragraph(c, f"Рис. {number} – {caption}", LEFT, y, centered_text=True, leading=18)
    return y - 13


CAPTIONS = {
    1: "Запуск NestJS-застосунку без помилок.",
    2: "Структура модулів проєкту.",
    3: "Імпорт GadgetsModule, OrdersModule і SharedModule в AppModule.",
    4: "Реєстрація та експорт провайдерів у SharedModule.",
    5: "Реалізація генерації slug у SlugService.",
    6: "Початкові гаджети та OnModuleInit у GadgetsService.",
    7: "Отримання каталогу після ініціалізації (200 OK).",
    8: "Створення товару з автоматичною генерацією slug (201 Created).",
    9: "Конфігураційний провайдер STORE_CONFIG за стратегією useValue.",
    10: "Фабричний провайдер FEE_CALCULATOR за стратегією useFactory.",
    11: "Імпорт GadgetsModule та SharedModule в OrdersModule.",
    12: "Створення замовлення: вартість і податок (201 Created).",
    13: "Обробка неіснуючого productId (404 Not Found).",
    14: "Перегляд оформлених замовлень (200 OK).",
    15: "Новий Request ID для кожного HTTP-запиту.",
    16: "Наскрізне тестування без помилок.",
}


c = canvas.Canvas(str(OUTPUT), pagesize=A4)
c.setTitle("Практична робота №5 — Ткаченко В. М.")
c.setAuthor("Ткаченко В. М.")

# Сторінка 1: титулка повторює розташування блоків у зразку.
centered(c, "МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ", 775)
centered(c, "ПРИРОДНИЧО-ГУМАНІТАРНИЙ ФАХОВИЙ КОЛЕДЖ ДВНЗ", 750)
centered(c, "«УЖГОРОДСЬКИЙ УНІВЕРСИТЕТ»", 725)
centered(c, "«РОЗРОБКА WEB-ЗАСТОСУВАНЬ»", 531)
centered(c, "ПРАКТИЧНА РОБОТА №5", 506)
c.setFont("TimesUA", 14)
for line, y in [
    ("Виконав:", 421), ("Ткаченко В.М.", 398), ("студент курсу КН-41", 375),
    ("Перевірив:", 331), ("викл. Верещагін О.О.", 308),
]:
    c.drawRightString(WIDTH - RIGHT, y, line)
centered(c, "УЖГОРОД – 2026", 72)
c.showPage()

# Сторінка 2: тільки тема, мета та варіант, як у зразку.
y = 761
y = paragraph(c, "Тема: Модульна архітектура та ін’єкція залежностей у NestJS", LEFT, y)
y -= 6
y = paragraph(c, "Мета: Опанувати поділ NestJS-застосунку на функціональні й спільний модулі, "
              "міжмодульну ін’єкцію залежностей, кастомні провайдери та життєвий цикл компонентів.", LEFT, y)
y -= 6
y = paragraph(c, "Ресурс з практичної роботи №4: гаджети, маршрут /gadgets", LEFT, y)
y -= 6
paragraph(c, "У вихідній папці були контролер і DTO гаджетів, але бракувало файла "
          "gadgets.service.ts. Сервіс відновлено за маршрутами та прикладами HTTP-запитів.", LEFT, y)
c.showPage()

# Сторінки 3–7: послідовні скриншоти з підписами.
centered(c, "Хід роботи", 770)
y = 742
for number, limit in [(1, 142), (2, 179), (3, 131)]:
    y = figure(c, number, CAPTIONS[number], y, limit)
c.showPage()

y = 779
for number, limit in [(4, 147), (5, 160), (6, 205)]:
    y = figure(c, number, CAPTIONS[number], y, limit)
c.showPage()

y = 779
for number, limit in [(7, 197), (8, 166), (9, 142)]:
    y = figure(c, number, CAPTIONS[number], y, limit)
c.showPage()

y = 779
for number, limit in [(10, 128), (11, 113), (12, 178), (13, 110)]:
    y = figure(c, number, CAPTIONS[number], y, limit)
c.showPage()

y = 779
for number, limit in [(14, 162), (15, 95), (16, 148)]:
    y = figure(c, number, CAPTIONS[number], y, limit)
y -= 2
c.setFont("TimesUABold", 14)
c.drawString(LEFT, y, "Висновок")
y -= 23
paragraph(c, "У ході практичної роботи продовжено REST API магазину гаджетів "
          "на NestJS. Реалізовано GadgetsModule, OrdersModule і SharedModule, генерацію slug, "
          "провайдери useValue та useFactory, хук OnModuleInit і Scope.REQUEST. Перевірено "
          "створення товарів і замовлень, розрахунок податку та обробку помилки 404. "
          "Застосунок успішно запускається, наскрізний тест проходить без помилок.", LEFT, y, leading=18)
c.showPage()

c.save()
print(OUTPUT)
