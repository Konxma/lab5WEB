const fs = require('node:fs');
const path = require('node:path');
require('reflect-metadata');
const { ValidationPipe } = require('@nestjs/common');
const { NestFactory } = require('@nestjs/core');
const { AppModule } = require('../dist/app.module');

const evidenceDir = path.join(__dirname, '..', 'evidence');
fs.mkdirSync(evidenceDir, { recursive: true });
const logLines = [];
const logger = Object.fromEntries(
  ['log', 'error', 'warn', 'debug', 'verbose', 'fatal'].map((level) => [
    level,
    (message, context = '') => logLines.push(`[${level.toUpperCase()}] [${context}] ${message}`),
  ]),
);

async function main() {
  const app = await NestFactory.create(AppModule, { logger });
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }));
  await app.listen(0);
  const base = `http://127.0.0.1:${app.getHttpServer().address().port}`;
  const exchanges = [];

  async function send(label, method, route, data) {
    const response = await fetch(base + route, {
      method,
      headers: data === undefined ? {} : { 'content-type': 'application/json' },
      body: data === undefined ? undefined : JSON.stringify(data),
    });
    const body = await response.json();
    const record = {
      label, method, route, status: response.status,
      requestId: response.headers.get('x-request-id'),
      traceMatch: response.headers.get('x-request-trace-match'),
      body,
    };
    exchanges.push(record);
    return record;
  }

  try {
    await send('Початковий каталог', 'GET', '/clothes');
    const created = await send('Створення товару', 'POST', '/clothes', {
      title: 'Черевики Trail 2', category: 'Взуття', price: 1499.5,
    });
    await send('Оформлення замовлення', 'POST', '/orders', {
      productId: created.body.id, quantity: 2, customerEmail: 'student@example.com',
    });
    await send('Невідомий товар', 'POST', '/orders', {
      productId: 'missing', quantity: 1, customerEmail: 'student@example.com',
    });
    await send('Список замовлень', 'GET', '/orders');
    await send('Каталог після запитів', 'GET', '/clothes');
    fs.writeFileSync(path.join(evidenceDir, 'api-results.json'), JSON.stringify(exchanges, null, 2) + '\n');
    fs.writeFileSync(path.join(evidenceDir, 'startup.log'), logLines.join('\n') + '\n');
    console.log(`Збережено ${exchanges.length} HTTP-обмінів і ${logLines.length} повідомлень запуску.`);
    console.log(`Статуси: ${exchanges.map((x) => x.status).join(', ')}`);
    if (logLines.some((line) => line.startsWith('[ERROR]'))) process.exitCode = 1;
  } finally {
    await app.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
