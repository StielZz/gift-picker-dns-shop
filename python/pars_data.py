import requests
import sqlite3
import json



def get_db_connection():
    """
    Открывает соединение с базой данных.

    :return: Соединение и курсор.
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    return conn, cursor


def get_categories(city_id="30b7c1ea-03fb-11dc-95ee-00151716f9f5", max_menu_level=6):
    """
    Получает категории с сайта DNS по указанным параметрам.
    
    :param city_id: Идентификатор города (по умолчанию Владивосток).
    :param max_menu_level: Максимальный уровень вложенности меню.
    :return: Список категорий.
    :raises ValueError: Если данные не найдены или произошла ошибка при обработке ответа от API.
    :raises requests.RequestException: Если произошла ошибка при выполнении запроса к API.
    """
    url = f"https://restapi.dns-shop.ru/v1/get-menu?maxMenuLevel={max_menu_level}"

    headers = {
        "Cityid": city_id,  
        "Origin": "https://www.dns-shop.ru",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    if response.status_code == 200:
        try:
            categories = response.json().get("data", None)
            if categories is None:
                raise ValueError("Ошибка: Отсутствуют данные о категориях в ответе")
            return categories
        except (KeyError, ValueError) as e:
            raise ValueError(f"Ошибка в обработке данных: {e}")
    else:
        raise ValueError(f"Ошибка {response.status_code}: {response.text}")


def get_categories_with_levels(categories, level=0, parent_id=None):
    """
    Рекурсивная функция для получения категорий с уровнями вложенности.

    :param categories: Список категорий.
    :param level: Текущий уровень вложенности.
    :param parent_id: ID родительской категории.
    :return: Список категорий с уровнями вложенности и родительским ID.
    :raises ValueError: Если в категории отсутствуют обязательные поля.
    """
    result = []
    
    for category in categories:
        try:
            category_id = category["id"]
            category_name = category["title"]
            category_url = category["url"]
            if category["childs"]:
                category_childs = True
            else:
                category_childs = False
        except KeyError as e:
            raise ValueError(f"Отсутствует обязательное поле: {e.args[0]} в категории: {category}")

        if not category_id or category_id == "markdown":
            continue

        result.append({
            'level': level,
            'title': category_name,
            'id': category_id,
            'url': category_url,
            'parent_id': parent_id,
            'childs': category_childs
        })

        if "childs" in category and category["childs"]:
            result.extend(get_categories_with_levels(category["childs"], level + 1, category_id))

    return result


def insert_category_to_db(category, conn, cursor):
    """
    Функция для вставки категории в базу данных.
    
    :param category: Словарь, содержащий данные категории.
    :param conn: Соединение базы данных.
    :param cursor: Курсор базы данных.
    :raises Exception: Если произошла ошибка при вставке данных в бд.
    """
    try:
        cursor.execute('''
            INSERT INTO categories (id, parent_id, title, level, relative_url) 
            VALUES (?, ?, ?, ?, ?)
        ''', (category['id'], category['parent_id'], category['title'], category['level'], category['url']))

        conn.commit()

    except Exception as e:
        raise Exception(f"Ошибка при вставке категории {category['title']}: {str(e)}")
    

def get_products_by_category(category):
    """
    Получает список UUID продуктов для заданной категории.
    
    :param category: Словарь, содержащий данные категории.
    :return: Список UUID продуктов.
    :raises Exception: Если произошла ошибка при запросе или обработке данных.
    """

    category_url = category['url']

    page = 1
    url = f"https://www.dns-shop.ru{category_url}?p={page}"

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        'Referer': f"https://www.dns-shop.ru{url}",
        'x-csrf-token': 'HT-Kx3W2obf-LdctPMrIemnWp30LJUG1MW2xOZlpiIJSce_0A__L3cp0lGVonq8tPonSCGBGBuNeD9ha4Qu65w==',
    }

    cookies = {
        '_csrf': 'd2591f3c4912f741f5863f9ebb46a89df79b2bc39232ac2b5e49d85a473b0842a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22ONe3vIjj4YCHTTgWW_uukcGVobicxb2e%22%3B%7D',
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies)
        response.raise_for_status()

        inline_js = response.json()["assets"]["inlineJs"]

        for _, value in inline_js.items():
            if value.startswith("window.AjaxState.register"):
                json_data = value[len("window.AjaxState.register("):-2]
                extracted_json = json.loads(json_data)

                for section in extracted_json:
                    if section[0].get("type") == "avails-container":
                        return [item["data"]["product"] for item in section[1]]

    except requests.RequestException as e:
        raise Exception(f"Ошибка запроса: {e}")
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        raise Exception(f"Ошибка обработки данных: {e}")


def get_products_info(products_uuid):
    """
    Получает информацию о продуктах по списку UUID.
    
    :param product_uuids: Список UUID продуктов.
    :return: Список с информацией о продуктах.
    :raises Exception: Если произошла ошибка при запросе или обработке данных.
    """

    url = "https://www.dns-shop.ru/ajax-state/product-buy/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        'X-Requested-With': 'XMLHttpRequest',
        'content-type': 'application/x-www-form-urlencoded',
    }

    # В id обязательный символ '-'
    containers = [{"id": f"product-{i+1}", "data": {"id": product_id}} for i, product_id in enumerate(products_uuid)]
    
    data = {
        "type": "product-buy",
        "containers": containers
    }

    try:
        response = requests.post(url, headers=headers, data={'data': json.dumps(data)})
        response.raise_for_status()

        products_data = response.json()["data"]["states"]
        return products_data

    except requests.RequestException as e:
        raise Exception(f"Ошибка запроса: {e}")
    except (KeyError, json.JSONDecodeError) as e:
        raise Exception(f"Ошибка обработки данных: {e}")
   
    
def insert_product_to_db(product, conn, cursor, image_url, product_url):
    """
    Функция для вставки продукта в базу данных.
    
    :param product: Словарь, содержащий данные продукта.
    :param conn: Соединение базы данных.
    :param cursor: Курсор базы данных.
    :param image_url: URL изображения продукта.
    :param product_url: URL на продукт.
    :raises Exception: Если произошла ошибка при вставке данных в бд.
    """
    try:
        cursor.execute('''SELECT COUNT(*) FROM products WHERE id = ?''', (product["data"]['id'],))
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute(''' 
                INSERT INTO products (id, title, price, image_url, product_url) 
                VALUES (?, ?, ?, ?, ?)
            ''', (product["data"]['id'], product["data"]['name'], product["data"]['price']['current'], image_url, product_url))

            conn.commit()
        else:
            print(f"Продукт с id {product['data']['id']} уже существует в базе.")

    except Exception as e:
        raise Exception(f"Ошибка при вставке товара {product['data']['name']}: {str(e)}")


def insert_product_category_relation(product_id, category_id, conn, cursor):
    """
    Функция для вставки связи между продуктом и категорией в базу данных.
    
    :param product_id: Идентификатор товара.
    :param category_id: Идентификатор категории.
    :param conn: Соединение базы данных.
    :param cursor: Курсор базы данных.
    :raises Exception: Если произошла ошибка при вставке данных в бд.
    """
    try:
        cursor.execute(''' 
            INSERT INTO product_categories (product_id, category_id) 
            VALUES (?, ?)
        ''', (product_id, category_id))

        conn.commit()

    except Exception as e:
        raise Exception(f"Ошибка при вставке связи товара {product_id} и категории {category_id}: {str(e)}")


def get_product_images(product_ids):
    """
    Получает изображения для списка продуктов по их UUID.
    
    :param product_ids: Список UUID продуктов.
    :return: Словарь с UUID продуктов и соответствующими изображениями.
    :raises Exception: Если произошла ошибка при запросе или обработке данных.
    """
    url = "https://www.dns-shop.ru/catalog/product/get-images/"

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        'X-Requested-With': 'XMLHttpRequest',
        'content-type': 'application/x-www-form-urlencoded',
    }

    data = {
        "ids": product_ids
    }

    try:
        response = requests.post(url, headers=headers, data={'ids': json.dumps(data['ids'])})
        response.raise_for_status()

        product_images = response.json()["data"]

        return product_images

    except requests.RequestException as e:
        raise Exception(f"Ошибка запроса: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        raise Exception(f"Ошибка обработки данных: {e}")


def get_product_url(product_uuid): # Очень сильно замедляет парсер тк 1 запрос 1 продукт есть вариант можно переделать но времени нет
    """
    Функция для получения URL продукта по его UUID.
    
    :param product_uuid: UUID продукта.
    :return: URL продукта.
    :raises Exception: Если произошла ошибка при запросе или обработке данных.
    """
    url = f"https://www.dns-shop.ru/product/microdata/{product_uuid}/"
    
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        'Referer': f"https://www.dns-shop.ru{url}",
        'x-csrf-token': 'HT-Kx3W2obf-LdctPMrIemnWp30LJUG1MW2xOZlpiIJSce_0A__L3cp0lGVonq8tPonSCGBGBuNeD9ha4Qu65w==',
    }

    cookies = {
        '_csrf': 'd2591f3c4912f741f5863f9ebb46a89df79b2bc39232ac2b5e49d85a473b0842a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22ONe3vIjj4YCHTTgWW_uukcGVobicxb2e%22%3B%7D',
    }

    data = {
        "product_id": product_uuid
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data) 
        response.raise_for_status()

        url = response.json()["data"]["offers"]["url"]
        return url  

    except requests.RequestException as e:
        raise Exception(f"Ошибка запроса: {e}")
    

conn, cursor = get_db_connection()

categories = get_categories()
categorized_data = get_categories_with_levels(categories)

for index, category in enumerate(categorized_data):
    print(index, category)
    insert_category_to_db(category, conn, cursor)

    if not category["childs"]:
        products_uuid = get_products_by_category(category)
        if products_uuid is None:
            print(f"Ошибка: Не удалось получить UUID продуктов для категории {category['title']}")
            continue

        products_info = get_products_info(products_uuid)
        if not products_info:
            print(f"Ошибка: Не удалось получить данные о продуктах для категории {category['title']}")
            continue 
        
        products_image = get_product_images(products_uuid)
        if not products_info:
            print(f"Ошибка: Не удалось получить изображение о продуктах для категории {category['title']}")
            continue 

        for product in products_info:
            try:
                image_url = products_image[product["data"]['id']][0]
                product_url = get_product_url(product["data"]['id'])
                insert_product_to_db(product, conn, cursor, image_url, product_url)
                insert_product_category_relation(product["data"]['id'], category['id'], conn, cursor)
            except:
                print(f"Изображение для продукта {product['data']['id']} не найдено, пропускаем.")
            