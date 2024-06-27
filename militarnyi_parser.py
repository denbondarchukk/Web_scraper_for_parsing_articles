# Імпорт необхідних бібліотек
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Створення словника для позначення українських місяців англійськими варіантами
month_map = {
    'Січня': 'January',
    'Лютого': 'February',
    'Березня': 'March',
    'Квітня': 'April',
    'Травня': 'May',
    'Червня': 'June',
    'Липня': 'July',
    'Серпня': 'August',
    'Вересня': 'September',
    'Жовтня': 'October',
    'Листопада': 'November',
    'Грудня': 'December'
}


def parse_date(date_text):
    # Заміна українських назв місяців на англійські
    for ukr_month, eng_month in month_map.items():
        date_text = date_text.replace(ukr_month, eng_month)
    # Переведення текстової дати в об'єкт datetime
    return datetime.strptime(date_text, '%d %B, %Y')


def parse_article(url):
    response = requests.get(url)
    if response.status_code == 200:
        # Парсимо вміст сторінки за допомогою BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        # Знаходимо всі елементи за двома необхідними класами
        article_items = soup.find_all('div', class_='article-item article-item--wide js-filtered-item all reference')
        article_items_front = soup.find_all('div',
                                            class_='article-item article-item--wide js-filtered-item all reference article-item--front')
        all_articles = article_items_front + article_items

        for i, article_item in enumerate(all_articles, 1):
            # Знаходимо перший тег <a> і отримуємо значення атрибуту href
            a_tag = article_item.find('a')
            href_value = a_tag.get('href')
            # Отримуємо URL нової сторінки
            new_response = requests.get(href_value)
            if new_response.status_code == 200:
                new_soup = BeautifulSoup(new_response.text, 'html.parser')
                # Отримуємо елемент з датою публікації
                date_element = new_soup.find('span', class_='post-info__date')
                date_text = date_element.text.strip()
                article_date = parse_date(date_text)
                # Перевірка чи стаття опублікована після 24 лютого 2022 року
                if article_date < datetime(2022, 2, 24):
                    return True
                # Знаходимо всі параграфи (тег <p>) на новій сторінці
                paragraphs = new_soup.find_all('p')
                # Створюємо назву файлу на основі дати публікації
                filename = article_date.strftime('%Y-%m-%d_{i}.txt').format(i=i)
                # Записуємо текст параграфів у текстовий файл
                with open(filename, 'w', encoding='utf-8') as file:
                    # Спочатку знаходимо і записуємо заголовок статті
                    article_title = new_soup.find('h1', class_='post-banner__title')
                    if article_title:
                        file.write(f'{article_title.get_text()}\n')
                    for paragraph in paragraphs:
                        if paragraph.get('class') == ['title', 'title--main']:
                            continue  # Пропускаємо слово "блоги" на початку тексту
                        elif paragraph.find_parent('div', class_='donate'):
                            break
                        else:
                            paragraph_text = paragraph.get_text()
                            file.write(f'{paragraph_text} \n')
            else:
                print(f'Помилка запиту: {new_response.status_code}')
    else:
        print(f'Помилка запиту: {response.status_code}')
    return False


# URL для парсингу
base_url = 'https://mil.in.ua/uk/articles/'
# Початкове значення номеру веб-сторінки
page_number = 1
# Парсимо статті доки не знайдемо статтю опубліковану до 24 лютого 2022 року
found_recent_article = False
while not found_recent_article:
    url = f'{base_url}?page={page_number}&type=all'
    found_recent_article = parse_article(url)
    page_number += 1
