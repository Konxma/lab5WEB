const { test } = require('node:test');
const assert = require('node:assert/strict');
require('reflect-metadata');
const { ValidationPipe } = require('@nestjs/common');
const { NestFactory } = require('@nestjs/core');
const { AppModule } = require('../dist/app.module');

test('API гаджетів із практичної №4 та модулі практичної №5', async () => {
  const app = await NestFactory.create(AppModule, { logger: false });
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));
  await app.listen(0);
  const base = `http://127.0.0.1:${app.getHttpServer().address().port}`;
  const json = { 'content-type': 'application/json' };
  try {
    assert.equal(await (await fetch(base)).text(), 'Hello World!');
    const seededResponse = await fetch(`${base}/gadgets`);
    assert.equal(seededResponse.status, 200);
    assert.equal(seededResponse.headers.get('x-api-version'), '1.0');
    assert.equal(seededResponse.headers.get('x-service-status'), 'operational');
    const seeded = await seededResponse.json();
    assert.equal(seeded.length, 2);
    assert.equal(seeded[0].id, '1');
    assert.equal(seeded[0].slug, 'noutbuk-pro-16');

    const filteredResponse = await fetch(`${base}/gadgets?search=Pro&limit=1`);
    assert.equal(filteredResponse.status, 200);
    assert.equal((await filteredResponse.json()).length, 1);
    assert.notEqual(filteredResponse.headers.get('x-request-id'), seededResponse.headers.get('x-request-id'));
    assert.equal(filteredResponse.headers.get('x-request-trace-match'), 'true');

    const createdResponse = await fetch(`${base}/gadgets`, {
      method: 'POST', headers: json,
      body: JSON.stringify({ title: 'Новий Смартфон', price: 30000, warrantyMonths: 12,
        cpu: 'Snapdragon 8 Gen 3', ramGb: 12 }),
    });
    assert.equal(createdResponse.status, 201);
    const created = await createdResponse.json();
    assert.equal(created.id, '3');
    assert.equal(created.slug, 'novyy-smartfon');
    assert.equal(created.warrantyMonths, 12);

    const orderResponse = await fetch(`${base}/orders`, {
      method: 'POST', headers: json,
      body: JSON.stringify({ productId: created.id, quantity: 2, customerEmail: 'student@example.com' }),
    });
    assert.equal(orderResponse.status, 201);
    const order = await orderResponse.json();
    assert.equal(order.subtotal, 60000);
    assert.equal(order.taxAmount, 12000);
    assert.equal(order.total, 72000);
    assert.equal(order.currency, 'UAH');
    assert.equal(order.productSlug, created.slug);
    assert.equal(orderResponse.headers.get('x-request-trace-match'), 'true');

    const missingResponse = await fetch(`${base}/orders`, {
      method: 'POST', headers: json,
      body: JSON.stringify({ productId: '99999', quantity: 1, customerEmail: 'student@example.com' }),
    });
    assert.equal(missingResponse.status, 404);
    const orders = await (await fetch(`${base}/orders`)).json();
    assert.equal(orders.length, 1);
    assert.equal(orders[0].orderId, order.orderId);
    const invalidResponse = await fetch(`${base}/orders`, {
      method: 'POST', headers: json,
      body: JSON.stringify({ productId: created.id, quantity: 0, customerEmail: 'bad' }),
    });
    assert.equal(invalidResponse.status, 400);

    const updateResponse = await fetch(`${base}/gadgets/${created.id}`, {
      method: 'PATCH', headers: json,
      body: JSON.stringify({ title: 'Смартфон Pro', price: 42000 }),
    });
    assert.equal(updateResponse.status, 200);
    const updated = await updateResponse.json();
    assert.equal(updated.slug, 'smartfon-pro');
    assert.equal(updated.price, 42000);
    assert.equal(updated.cpu, 'Snapdragon 8 Gen 3');
    assert.equal((await fetch(`${base}/gadgets?limit=0`)).status, 400);
    const deleteResponse = await fetch(`${base}/gadgets/${created.id}`, { method: 'DELETE' });
    assert.equal(deleteResponse.status, 204);
    assert.equal((await fetch(`${base}/gadgets/${created.id}`)).status, 404);
  } finally {
    await app.close();
  }
});
