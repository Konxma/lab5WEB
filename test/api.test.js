const { test } = require('node:test');
const assert = require('node:assert/strict');
require('reflect-metadata');
const { ValidationPipe } = require('@nestjs/common');
const { NestFactory } = require('@nestjs/core');
const { AppModule } = require('../dist/app.module');

test('повний сценарій каталогу, замовлень і request scope', async () => {
  const app = await NestFactory.create(AppModule, { logger: false });
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }));
  await app.listen(0);
  const base = `http://127.0.0.1:${app.getHttpServer().address().port}`;
  const json = { 'content-type': 'application/json' };

  try {
    const seededResponse = await fetch(`${base}/clothes`);
    assert.equal(seededResponse.status, 200);
    const seeded = await seededResponse.json();
    assert.equal(seeded.length, 2);
    assert.equal(seeded[0].slug, 'kurtka-zymova');

    const createdResponse = await fetch(`${base}/clothes`, {
      method: 'POST', headers: json,
      body: JSON.stringify({ title: 'Черевики Trail 2', category: 'Взуття', price: 1499.5 }),
    });
    assert.equal(createdResponse.status, 201);
    const created = await createdResponse.json();
    assert.equal(created.slug, 'cherevyky-trail-2');

    const firstList = await fetch(`${base}/clothes?search=Trail&limit=1`);
    assert.equal(firstList.status, 200);
    assert.equal((await firstList.json()).length, 1);
    assert.notEqual(firstList.headers.get('x-request-id'), seededResponse.headers.get('x-request-id'));
    assert.equal(firstList.headers.get('x-request-trace-match'), 'true');

    const orderResponse = await fetch(`${base}/orders`, {
      method: 'POST', headers: json,
      body: JSON.stringify({ productId: created.id, quantity: 2, customerEmail: 'student@example.com' }),
    });
    assert.equal(orderResponse.status, 201);
    const order = await orderResponse.json();
    assert.equal(order.subtotal, 2999);
    assert.equal(order.taxAmount, 599.8);
    assert.equal(order.total, 3598.8);
    assert.equal(order.currency, 'UAH');
    assert.equal(order.productSlug, created.slug);
    assert.equal(orderResponse.headers.get('x-request-trace-match'), 'true');

    const missingResponse = await fetch(`${base}/orders`, {
      method: 'POST', headers: json,
      body: JSON.stringify({ productId: 'missing', quantity: 1, customerEmail: 'student@example.com' }),
    });
    assert.equal(missingResponse.status, 404);

    const ordersResponse = await fetch(`${base}/orders`);
    const orders = await ordersResponse.json();
    assert.equal(orders.length, 1);
    assert.equal(orders[0].orderId, order.orderId);

    const invalidResponse = await fetch(`${base}/orders`, {
      method: 'POST', headers: json,
      body: JSON.stringify({ productId: created.id, quantity: 0, customerEmail: 'bad' }),
    });
    assert.equal(invalidResponse.status, 400);

    const updateResponse = await fetch(`${base}/clothes/${created.id}`, {
      method: 'PATCH', headers: json,
      body: JSON.stringify({ title: 'Кросівки Trail 2' }),
    });
    assert.equal(updateResponse.status, 200);
    assert.equal((await updateResponse.json()).slug, 'krosivky-trail-2');

    const deleteResponse = await fetch(`${base}/clothes/${created.id}`, { method: 'DELETE' });
    assert.equal(deleteResponse.status, 204);
    assert.equal((await fetch(`${base}/clothes/${created.id}`)).status, 404);
  } finally {
    await app.close();
  }
});
