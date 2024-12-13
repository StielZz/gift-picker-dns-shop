CREATE TABLE categories (
    id TEXT PRIMARY KEY,              -- Идентификатор категории (UUID хранится как строка)
    parent_id TEXT,                   -- Идентификатор родительской категории (NULL для корневых категорий)
    title VARCHAR(255) NOT NULL,      -- Название категории
    level INT NOT NULL,               -- Уровень вложенности категории
	relative_url TEXT NOT NULL,       -- Относительный URL категории
    FOREIGN KEY (parent_id) REFERENCES categories(id)  -- Связь с родительской категорией
);

CREATE TABLE products (
    id TEXT PRIMARY KEY,              -- Идентификатор товара (UUID хранится как строка)
    title TEXT NOT NULL,              -- Название товара
    price INT NOT NULL,               -- Цена товара
    image_url TEXT NOT NULL,          -- Изображение продукта
    product_url TEXT NOT NULL         -- Ссылка на продукт
);

CREATE TABLE product_categories (
    product_id TEXT,                  -- Идентификатор товара (UUID), ссылается на таблицу products
    category_id TEXT,                 -- Идентификатор категории (UUID), ссылается на таблицу categories
    FOREIGN KEY (product_id) REFERENCES products(id),    -- Внешний ключ, ссылающийся на uuid товара в таблице products
    FOREIGN KEY (category_id) REFERENCES categories(id),  -- Внешний ключ, ссылающийся на uuid категории в таблице categories
    PRIMARY KEY (product_id, category_id)  -- Сочетание product_id и category_id уникально, создавая уникальную пару товара и категории
);