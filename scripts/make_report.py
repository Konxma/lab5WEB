"""Generate the submission PDF from verified project evidence."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
REPORT_DIR = ROOT / "report"
REPORT_DIR.mkdir(exist_ok=True)
OUTPUT = REPORT_DIR / "Практична_робота_5_Ткаченко_ВМ.pdf"

pdfmetrics.registerFont(TTFont("ArialUA", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("ArialUABold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFontFamily("ArialUA", normal="ArialUA", bold="ArialUABold")

NAVY = colors.HexColor("#173252")
BLUE = colors.HexColor("#285b92")
LIGHT = colors.HexColor("#eaf1f8")
INK = colors.HexColor("#243347")

styles = {
    "normal": ParagraphStyle("normal", fontName="ArialUA", fontSize=10.8, leading=15.8,
                             textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7),
    "small": ParagraphStyle("small", fontName="ArialUA", fontSize=9.4, leading=13.7,
                            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=5),
    "h1": ParagraphStyle("h1", fontName="ArialUABold", fontSize=17, leading=22,
                         textColor=NAVY, spaceAfter=13),
    "h2": ParagraphStyle("h2", fontName="ArialUABold", fontSize=12.2, leading=17,
                         textColor=BLUE, spaceBefore=10, spaceAfter=7),
    "caption": ParagraphStyle("caption", fontName="ArialUA", fontSize=9.1, leading=12,
                              alignment=TA_CENTER, textColor=INK, spaceBefore=5, spaceAfter=15),
    "center": ParagraphStyle("center", fontName="ArialUA", fontSize=12, leading=18,
                             alignment=TA_CENTER, textColor=INK),
    "cover": ParagraphStyle("cover", fontName="ArialUABold", fontSize=18, leading=25,
                            alignment=TA_CENTER, textColor=NAVY),
    "table": ParagraphStyle("table", fontName="ArialUA", fontSize=9.2, leading=12.2,
                            textColor=INK),
}


def p(text, kind="normal"):
    return Paragraph(text, styles[kind])


def bullet(text):
    return p("• " + text)


def fig(filename, caption, max_width=500, max_height=420):
    image_path = EVIDENCE / filename
    source = ImageReader(str(image_path))
    width, height = source.getSize()
    factor = min(max_width / width, max_height / height)
    picture = Image(str(image_path), width=width * factor, height=height * factor)
    picture.hAlign = "CENTER"
    return [picture, p(escape(caption), "caption")]


def question(number, title, answer):
    return [p(f"{number}. {escape(title)}", "h2"), p(escape(answer), "small")]


story = []

# 1. Титульна сторінка за наданим зразком.
story += [Spacer(1, 55),
          p("МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ", "center"),
          p("ПРИРОДНИЧО-ГУМАНІТАРНИЙ ФАХОВИЙ КОЛЕДЖ<br/>ДВНЗ «УЖГОРОДСЬКИЙ УНІВЕРСИТЕТ»", "center"),
          Spacer(1, 95),
          p("«РОЗРОБКА WEB-ЗАСТОСУВАНЬ»", "cover"),
          Spacer(1, 16),
          p("ЗВІТ З ПРАКТИЧНОЇ РОБОТИ № 5", "cover"),
          p("Модульна архітектура та ін’єкція залежностей у NestJS", "center"),
          Spacer(1, 104)]
cover_details = Table([
    ["Виконав:", "Ткаченко В. М., студент курсу КН-41"],
    ["Перевірив:", "викл. Верещагін О. О."],
], colWidths=[95, 335])
cover_details.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "ArialUA"),
    ("FONTSIZE", (0, 0), (-1, -1), 11),
    ("LEADING", (0, 0), (-1, -1), 16),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
]))
story += [cover_details, Spacer(1, 117), p("УЖГОРОД – 2026", "center"), PageBreak()]

# 2. Постановка та архітектура.
story += [p("Тема, мета і постановка задачі", "h1"),
          p("<b>Тема:</b> модульна архітектура та ін’єкція залежностей у NestJS."),
          p("<b>Мета:</b> розділити серверний застосунок на функціональні та спільний модулі; "
            "опанувати імпорт і експорт провайдерів, стратегії useValue та useFactory, хук "
            "OnModuleInit і область видимості Scope.REQUEST."),
          p("<b>Варіант 3:</b> інтернет-магазин одягу та взуття. Основний ресурс — clothes; "
            "модуль, сутність і сервіс — ClothesModule, ClothingEntity, ClothesService."),
          p("Структура застосунку", "h2")]
rows = [
    [p("Модуль", "table"), p("Призначення", "table"), p("Зв’язки", "table")],
    [p("ClothesModule", "table"), p("CRUD каталогу; початкові товари; генерація slug", "table"), p("Імпортує SharedModule; експортує ClothesService", "table")],
    [p("OrdersModule", "table"), p("Створення й перегляд замовлень; розрахунок вартості", "table"), p("Імпортує ClothesModule і SharedModule", "table")],
    [p("SharedModule", "table"), p("SlugService, конфігурація, податок, request ID", "table"), p("Експортує сервіси і токени", "table")],
]
table = Table(rows, colWidths=[112, 192, 175], repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c9d5e2")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story += [table, Spacer(1, 14),
          p("AppModule містить лише імпорти трьох модулів. Контролери і сервіси ресурсів "
            "зареєстровано у власних модулях. OrdersModule отримує доступ до каталогу лише "
            "через експортований ClothesService — це демонструє інкапсуляцію провайдерів."),
          p("Середовище: Node.js 22.23.3, npm 12.2.0, TypeScript, NestJS. Сховище даних — "
            "in-memory; після перезапуску застосунку воно очищується."), PageBreak()]

# 3. Хід роботи за трьома рівнями.
story += [p("Хід роботи", "h1"),
          p("Рівень 1. Ізоляція каталогу та спільний модуль", "h2"),
          bullet("Створено ClothesModule з ClothesController і ClothesService. Реалізовано маршрути "
                 "GET, POST, PATCH, DELETE та DTO з перевіркою вхідних даних."),
          bullet("SlugService транслітерує кирилицю, прибирає сторонні символи та формує "
                 "slug у нижньому регістрі. Наприклад: «Черевики Trail 2» → "
                 "«cherevyky-trail-2»."),
          bullet("ClothesService впроваджує SlugService через конструктор та записує slug під час "
                 "створення або перейменування товару."),
          p("Рівень 2. Замовлення та кастомні провайдери", "h2"),
          bullet("OrdersModule імпортує ClothesModule і викликає ClothesService.findOne(productId). "
                 "За відсутності товару повертається 404 Not Found."),
          bullet("STORE_CONFIG створено через useValue: назва магазину, валюта UAH, податок 20%. "
                 "FEE_CALCULATOR створено через useFactory з inject: [STORE_CONFIG]."),
          bullet("OrdersService отримує токени через @Inject(), обчислює subtotal, taxAmount і total, "
                 "зберігає замовлення у пам’яті."),
          p("Приклад перевіреного розрахунку: 1499,50 × 2 = 2999,00 грн; податок 20% = "
            "599,80 грн; усього = 3598,80 грн."),
          p("Рівень 3. Життєвий цикл, scope і тестування", "h2"),
          bullet("OnModuleInit каталогу додає два початкові товари й повідомляє про ініціалізацію. "
                 "OrdersService повідомляє про готовність приймати замовлення."),
          bullet("RequestIdService має Scope.REQUEST. Заголовок X-Request-Id змінюється між "
                 "запитами, а X-Request-Trace-Match: true підтверджує спільний екземпляр "
                 "у контролері та сервісі в межах одного запиту."),
          bullet("Створено requests.http і наскрізний HTTP-тест для позитивних та негативних "
                 "сценаріїв. Застосунок успішно збирається; тест завершується без помилок."),
          PageBreak()]

# 4–7. Фактичні знімки роботи.
story += [p("Результати запуску та каталогу", "h1")]
story += fig("00-startup.png", "Рис. 1 – Успішний запуск AppModule, SharedModule, ClothesModule й OrdersModule; помилок немає.", 500, 315)
story += fig("01-catalog.png", "Рис. 2 – GET /clothes: два початкові товари, додані через OnModuleInit.", 500, 315)
story += [PageBreak(), p("Створення товару й замовлення", "h1")]
story += fig("02-product.png", "Рис. 3 – POST /clothes: статус 201 Created і автоматично створений slug.", 500, 255)
story += fig("03-order.png", "Рис. 4 – POST /orders: актуальна ціна, кількість, податок і загальна сума.", 500, 315)
story += [PageBreak(), p("Обробка помилки та список замовлень", "h1")]
story += fig("04-not-found.png", "Рис. 5 – POST /orders з невідомим productId повертає 404 Not Found.", 500, 285)
story += fig("05-orders.png", "Рис. 6 – GET /orders повертає збережене замовлення.", 500, 340)
story += [PageBreak(), p("Наскрізна перевірка і область видимості", "h1")]
story += fig("06-tests.png", "Рис. 7 – Збірка TypeScript і наскрізний тест: 1 пройшов, 0 помилок.", 500, 350)
story += [p("Порівняння фактичних заголовків X-Request-Id у збережених результатах "
            "показало різні UUID для послідовних HTTP-запитів. Значення "
            "X-Request-Trace-Match дорівнює true: RequestIdService і RequestTraceService "
            "бачать той самий екземпляр у межах запиту. Усі три товари залишились у "
            "каталозі після створення замовлення, оскільки дані зберігає singleton-сервіс."),
          p("Тест додатково перевірив некоректні DTO (400), пошук, часткове оновлення, "
            "видалення (204) та подальший 404 для видаленого товару."), PageBreak()]

# 8–9. Контрольні питання.
story += [p("Відповіді на контрольні питання", "h1")]
story += question(1, "Що таке Feature Module і Shared Module?",
                  "Feature Module об’єднує контролери й провайдери однієї предметної області, "
                  "наприклад каталогу або замовлень. Shared Module містить повторно використовувані "
                  "сервіси та експортує їх іншим модулям.")
story += question(2, "Як працює інкапсуляція провайдерів?",
                  "Провайдер доступний у модулі, де його оголошено. Інший модуль може його "
                  "впровадити після експорту провайдера з першого модуля та імпорту цього модуля. "
                  "Без експорту NestJS не зможе розв’язати залежність і повідомить про помилку запуску.")
story += question(3, "Чим відрізняються useClass, useValue та useFactory?",
                  "useClass створює екземпляр класу; useValue повертає готове значення, наприклад "
                  "конфігурацію; useFactory викликає функцію, яка може динамічно сформувати провайдер "
                  "на основі інших залежностей.")
story += question(4, "Для чого потрібен @Inject()?",
                  "Декоратор явно задає токен провайдера. Він потрібен для рядкових або символьних "
                  "токенів, інтерфейсів і типів, яких немає під час виконання JavaScript, тому NestJS "
                  "не може визначити провайдер лише за типом параметра конструктора.")
story += [PageBreak(), p("Контрольні питання (продовження)", "h1")]
story += question(5, "Як працює масив inject у useFactory?",
                  "NestJS знаходить провайдери за токенами в масиві inject і передає їх значення "
                  "до фабричної функції в тому самому порядку. У проєкті STORE_CONFIG є аргументом "
                  "фабрики FEE_CALCULATOR.")
story += question(6, "Що таке життєвий цикл та коли працює OnModuleInit?",
                  "Життєвий цикл охоплює створення, ініціалізацію та завершення компонентів. "
                  "OnModuleInit викликається після розв’язання залежностей модуля. У ньому доречні "
                  "початкове завантаження даних, підготовка кешу й коротка діагностика готовності.")
story += question(7, "Чим відрізняються Scope.DEFAULT, REQUEST і TRANSIENT?",
                  "DEFAULT зазвичай створює один екземпляр провайдера на час роботи застосунку. "
                  "REQUEST створює окремий екземпляр для кожного запиту й повторно використовує "
                  "його в тому самому контексті. TRANSIENT створює окремий екземпляр для кожного "
                  "споживача провайдера.")
story += question(8, "Що таке циклічна залежність і як допомагає forwardRef()?",
                  "Цикл виникає, коли модуль або провайдер A залежить від B, а B — від A. "
                  "forwardRef(() => B) відкладає розв’язання посилання до часу, коли обидві сторони "
                  "відомі контейнеру NestJS. Краще спочатку перевірити архітектуру і, за можливості, "
                  "винести спільну логіку в окремий модуль.")
story += [p("Висновок", "h2"),
          p("Створено модульний REST API для магазину одягу й взуття. Реалізовано міжмодульне "
            "впровадження залежностей, кастомні провайдери конфігурації та податку, "
            "OnModuleInit і Scope.REQUEST. Фактичні HTTP-запити підтвердили коректне створення "
            "товарів і замовлень, обробку помилок та збереження стану між запитами. "
            "Наскрізний тест пройшов без помилок."),
          p("Джерела: умова практичної роботи №5; документація NestJS (docs.nestjs.com).", "small")]


def footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor("#c9d5e2"))
        canvas.line(55, 48, A4[0] - 55, 48)
        canvas.setFont("ArialUA", 9)
        canvas.setFillColor(colors.HexColor("#61748d"))
        canvas.drawString(55, 34, "Практична робота №5 • Ткаченко В. М.")
        canvas.drawRightString(A4[0] - 55, 34, str(doc.page))
    canvas.restoreState()


document = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4, rightMargin=55, leftMargin=55,
    topMargin=52, bottomMargin=62, title="Практична робота №5 — Ткаченко В. М.",
    author="Ткаченко В. М.",
)
document.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
