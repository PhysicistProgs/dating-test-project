import urllib
from django.core.files import File
import requests
from bs4 import BeautifulSoup
from .models import Category, Product


def parse_category(url, parent_category=None):
    """
    Рекурсивно парсит категории, пока не дойдет до той, у которой нет подкатегории
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='html.parser')
    if soup.find(class_='Subcategory__title-container'):
        cat_name = soup.find(class_='Subcategory__title-container').find('h1').text.strip()
        new_cat = Category.objects.create(parent=parent_category, name=cat_name, url=url)
    else:
        parent_cat_name = soup.find('h1').text.strip()
        parent_cat = Category.objects.create(name=parent_cat_name, parent=parent_category, url=url)
        for category in soup.find_all('a', class_='CatalogCategoryMenu__category'):
            parse_category(category['href'], parent_cat)


def parse_categories():
    """
    Парсит категории со всего сайта
    """
    url = 'https://www.citilink.ru/catalog/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='html.parser')
    category_blocks = soup.find_all(name='ul', class_='CatalogLayout__item', )
    for category in category_blocks:
        link = category.find('a')['href']
        print(f'Ссылка следующего перехода {link}')
        parse_category(link, )


def parse_page_products(url):
    """
    Парсит страницу товаров и возвращает список ссылок на товары
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text,  features='html.parser')
    possible_products = soup.find_all('a')
    products = []
    for product in possible_products:
        url = product.get('href')
        print(f'possible url: {url}')
        if url and 'citilink.ru/product' in url:
            print(f'url: {url}')
            products.append(url.rstrip('/otzyvy/'))
    input('urls ended')
    return products


def parse_product(url):
    """
    Парсит страницу продукта: возвращает имя, цену и ссылку на изображение
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='html.parser')
    try:
        name = soup.find('h1').text.strip()
        price = soup.find('span', class_='ProductHeader__price-default_current-price '
                                         'js--ProductHeader__price-default_current-price').text.strip()
        image_link = soup.find('img', class_='PreviewList__image Image')['src']
    except (AttributeError, KeyError):
        return None, 1, 1
    return name, int(price.replace(' ', '')), image_link


def set_image(url, product):
    """
    Устанавливает у объекта продукта изображение
    На выход принимает ссылку на изображение и сам продукт.
    """
    img = urllib.request.urlopen(url)
    filepath = '/home/andreygl/Documents/Coding/apptrix_test_task/dating_project/products'
    with open(filepath + 'tmp_img.jpeg', 'wb') as f:
        f.write(img.read())
    with open(filepath + 'tmp_img.jpeg', 'rb') as f:
        image_file = File(f)
        product.image = image_file
        product.save()


def create_products():
    """
    Запускаем парсинг и создание продуктов из категорий,
    которые на данный момент есть в базе.
    При пустой базе необходимо для начала спарсить категории (функция parse_categories)
    """
    qs = Category.objects.all()
    for cat in qs:
        if not cat.get_children():
            products = parse_page_products(cat.url)
            for product in products:
                name, price, image_link = parse_product(product)
                if not name:
                    continue
                product = Product.objects.create(name=name, price=price, category=cat,)
                set_image(image_link, product)
