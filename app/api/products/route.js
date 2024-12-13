import sqlite3 from 'sqlite3';
import path from 'path';

const dbPath = path.resolve('public', 'database.db');

const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE, (err) => {
  if (err) {
    console.error('Ошибка подключения к базе данных:', err.message);
  } else {
    console.log('Подключение к базе данных установлено');
  }
});

export async function GET(request) {
  const { searchParams } = new URL(request.url);

  const priceRange = searchParams.get('priceRange') || '';
  const category = searchParams.get('category') || '';

  let minPrice = 0;
  let maxPrice = Infinity;

  if (priceRange === 'low') {
    minPrice = 0;
    maxPrice = 5000;
  } else if (priceRange === 'medium') {
    minPrice = 5000;
    maxPrice = 20000;
  } else if (priceRange === 'high') {
    minPrice = 20000;
    maxPrice = Infinity; 
  }

  let query = `
    SELECT p.id, p.title, p.price, p.image_url, p.product_url, c.title AS category_title
    FROM products p
    JOIN product_categories pc ON p.id = pc.product_id
    JOIN categories c ON pc.category_id = c.id
    WHERE p.price BETWEEN ? AND ?`;

  let params = [minPrice, maxPrice];

  if (category) {
    query += ' AND c.title LIKE ?';
    params.push(`%${category}%`);
  }

  query += ' ORDER BY RANDOM() LIMIT 5';

  return new Promise((resolve, reject) => {
    db.all(query, params, (err, rows) => {
      if (err) {
        console.error('Ошибка при извлечении данных:', err);
        reject(new Error(`Ошибка при извлечении данных: ${err.message}`));
      } else if (rows.length === 0) {
        console.warn('Нет товаров, соответствующих запросу');
        resolve(
          new Response(JSON.stringify({ message: 'Товары не найдены' }), {
            status: 404,
            headers: {
              'Content-Type': 'application/json',
            },
          })
        );
      } else {
        resolve(
          new Response(JSON.stringify(rows), {
            status: 200,
            headers: {
              'Content-Type': 'application/json',
            },
          })
        );
      }
    });
  });
}
