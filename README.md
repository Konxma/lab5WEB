# Практична робота №5 — продовження API гаджетів

Основою є код з `C:\Users\vadim\Desktop\lab4web\online-store`: маршрут `/gadgets`, DTO з полями `title`, `price`, `warrantyMonths`, `cpu`, `ramGb`, запити пошуку, перегляду, створення, часткового оновлення та видалення. На основі цього ресурсу виконано завдання практичної №5: модулі, спільні провайдери, замовлення, `OnModuleInit` та область видимості `REQUEST`.

**Особливість вихідної папки:** у ній є `GadgetsController` і DTO, але немає імпортованого ними `gadgets.service.ts`. Сервіс відновлено за контрактом контролера й `requests.http`. Два початкові гаджети додано для завдання №5; вони не є відтворенням невідомих вихідних даних роботи №4. Оригінальну папку не змінено.

Готовий [звіт PDF](report/Практична_робота_5_Ткаченко_ВМ.pdf), [запити REST Client](requests.http) та [відповіді для захисту](DEFENSE.md).

## Запуск і перевірка

Потрібні Node.js 20+ і npm. Перевірено на Node.js 22.23.3.

```bash
npm ci
npm run build
npm start
```

Сервер працює на `http://localhost:3000`. Для наскрізної перевірки: `npm test`. Дані зберігаються в пам’яті й скидаються після перезапуску.

## Структура

```text
src/
  app.module.ts       # збирає модулі
  home/               # збережений GET / з роботи №4
  gadgets/            # DTO, контролер і сервіс гаджетів
  orders/             # замовлення, перевірка товару та розрахунок податку
  shared/             # SlugService, конфігурація, фабрика, RequestIdService
requests.http         # ручні перевірки API
test/api.test.js      # наскрізна перевірка
evidence/             # реальні відповіді API та журнали запуску
report/               # звіт за зразком
```

`GadgetsModule` експортує `GadgetsService`, а `OrdersModule` імпортує його для перевірки `productId` і ціни. `SharedModule` експортує `SlugService`, `STORE_CONFIG` через `useValue`, `FEE_CALCULATOR` через `useFactory` та сервіси трасування запитів. `GadgetsService` додає два гаджети в `onModuleInit`; `OrdersService` повідомляє про готовність. `RequestIdService` має `Scope.REQUEST`: заголовки `X-Request-Id` та `X-Request-Trace-Match` показують окремий ID кожного HTTP-запиту.

## API

| Метод | Маршрут | Результат |
|---|---|---|
| `GET` | `/` | `Hello World!` з роботи №4 |
| `GET` | `/gadgets` | Каталог, `search` і `limit`; заголовки `X-API-Version` та `X-Service-Status` |
| `GET` | `/gadgets/:id` | Гаджет або `404` |
| `POST` | `/gadgets` | Новий гаджет з автоматичним `slug`, `201` |
| `PATCH` | `/gadgets/:id` | Часткове оновлення, перерахунок `slug` після зміни назви |
| `DELETE` | `/gadgets/:id` | Видалення, `204` |
| `POST` | `/orders` | Замовлення, податок та сума, `201`; невідомий гаджет — `404` |
| `GET` | `/orders` | Список замовлень |

Тіло створення гаджета відповідає DTO практичної №4:

```json
{ "title": "Новий Смартфон", "price": 30000, "warrantyMonths": 12, "cpu": "Snapdragon 8 Gen 3", "ramGb": 12 }
```

Після чистого запуску цей гаджет отримує `id: "3"`. При замовленні двох одиниць `subtotal = 60000`, `taxAmount = 12000`, `total = 72000 UAH`. Помилки в тілах запитів повертають `400` через `ValidationPipe`.

## Результат перевірки

`npm test`: **1 тест пройшов, 0 помилок**. Перевірено маршрути роботи №4, пошук, початкові дані, slug, створення замовлення, податок, `400`, `404`, редагування, видалення та окремі Request ID. Запис фактичних запитів є в [api-results.json](evidence/api-results.json), а журнал запуску — у [startup.log](evidence/startup.log).
