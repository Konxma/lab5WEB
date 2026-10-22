// Optional evidence generator. Set PLAYWRIGHT_MODULE to a local Playwright installation.
const fs = require('node:fs');
const path = require('node:path');
require('reflect-metadata');
const { ValidationPipe } = require('@nestjs/common');
const { NestFactory } = require('@nestjs/core');
const { AppModule } = require('../dist/app.module');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');

const evidenceDir = path.join(__dirname, '..', 'evidence');
fs.mkdirSync(evidenceDir, { recursive: true });

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);
}

async function main() {
  const app = await NestFactory.create(AppModule, { logger: false });
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));
  await app.listen(0);
  const base = `http://127.0.0.1:${app.getHttpServer().address().port}`;
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 760 }, deviceScaleFactor: 1 });

  async function capture(filename, title, method, route, payload) {
    const response = await fetch(base + route, {
      method,
      headers: payload === undefined ? {} : { 'content-type': 'application/json' },
      body: payload === undefined ? undefined : JSON.stringify(payload),
    });
    const result = await response.json();
    const status = `${response.status} ${response.statusText}`;
    const req = payload === undefined ? '' : JSON.stringify(payload, null, 2);
    const body = JSON.stringify(result, null, 2);
    await page.setContent(`<!doctype html><html lang="uk"><meta charset="utf-8"><style>
      * { box-sizing: border-box; } body { margin: 0; padding: 36px 48px; background: #f3f6fb; color: #16263d; font: 20px Arial, sans-serif; }
      h1 { margin: 0 0 28px; font-size: 30px; } .bar { background: #16263d; color: #fff; padding: 16px 20px; border-radius: 12px 12px 0 0; font: 18px Consolas, monospace; }
      .status { color: ${response.ok ? '#91e5b0' : '#ffb4a8'}; float: right; } .card { background: white; border: 1px solid #d9e1ed; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 28px #182f4a18; }
      .section { padding: 16px 20px; border-top: 1px solid #e1e6ee; } .label { font-size: 15px; font-weight: bold; color: #52647e; margin-bottom: 8px; }
      pre { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; font: 17px/1.43 Consolas, monospace; color: #172c4a; }
    </style><body><h1>${escapeHtml(title)}</h1><div class="card"><div class="bar">${escapeHtml(method)} ${escapeHtml(route)}<span class="status">${escapeHtml(status)}</span></div>
      ${req ? `<div class="section"><div class="label">Тіло запиту</div><pre>${escapeHtml(req)}</pre></div>` : ''}
      <div class="section"><div class="label">Відповідь сервера</div><pre>${escapeHtml(body)}</pre></div>
      <div class="section"><div class="label">Заголовки</div><pre>X-Request-Id: ${escapeHtml(response.headers.get('x-request-id'))}\nX-Request-Trace-Match: ${escapeHtml(response.headers.get('x-request-trace-match'))}</pre></div>
    </div></body></html>`);
    await page.screenshot({ path: path.join(evidenceDir, filename), fullPage: true });
    return result;
  }

  try {
    await capture('01-catalog.png', 'Початковий каталог: OnModuleInit', 'GET', '/clothes');
    const product = await capture('02-product.png', 'Створення товару та slug', 'POST', '/clothes', {
      title: 'Черевики Trail 2', category: 'Взуття', price: 1499.5,
    });
    await capture('03-order.png', 'Замовлення: ціна, податок, підсумок', 'POST', '/orders', {
      productId: product.id, quantity: 2, customerEmail: 'student@example.com',
    });
    await capture('04-not-found.png', 'Перевірка помилки 404', 'POST', '/orders', {
      productId: 'missing', quantity: 1, customerEmail: 'student@example.com',
    });
    await capture('05-orders.png', 'Список оформлених замовлень', 'GET', '/orders');
    console.log('Збережено 5 знімків реальних HTTP-відповідей.');
  } finally {
    await browser.close();
    await app.close();
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
