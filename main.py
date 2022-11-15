import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_tables, Publisher, Shop, Book, Stock, Sale
import json
import os


def find_book_sold(name):

    '''Функция осуществляет SELECT запрос в базу данных по имени автора
    
    книги. Выводит на печать название книги, название магазина, 
    
    цена книги, дата продажи. На вход принимает имя автора.
    
    '''
    n = [0, 0, 0]

    request = session.query(
        Book.title, 
        Shop.name, 
        Sale.price, 
        Sale.date_sale
    ).join(Publisher).join(Stock).join(Shop).join(Sale).filter(
        Publisher.name == name
        )

    #определение максимальной длины каждого элемента
    for i in request.all():
        if len(str(i.title)) > n[0]:
            n[0] = len(str(i.title))
        if len(str(i.name)) > n[1]:
            n[1] = len(str(i.name))
        if len(str(i.price)) > n[2]:
            n[2] = len(str(i.price))

    for i in request.all():
        book = str(i.title).ljust(n[0], " ")
        shop = str(i.name).ljust(n[1], " ")
        price = str(i.price).ljust(n[2], " ")
        date = str(i.date_sale).partition('T')[0]
        print(f'{book} | {shop} | {price} | {date}')

def download_json():

    '''Функция загружает файл json с данными и вносит изменения 
    
    в текущую базу согласно моделей.
    
    '''

    with open('fixtures/db_test.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for record in data:
        model = {
            'publisher': Publisher,
            'shop': Shop,
            'book': Book,
            'stock': Stock,
            'sale': Sale,
        }.get(record['model'])
        session.add(model(id=record['pk'], **record['fields']))


if __name__ == '__main__':
    
    # получение персональных данных для подключения 
    with open(os.getenv('SQL_Alchemy'), 'r') as file:
        for i in json.load(file):
            if i['type'] == 'postgresql':
                sql = i['fields']
                break

    DSN = f'''{sql["driver"]}://{sql["login"]}:{sql["password"]}@{sql["server"]}:{sql["port"]}/{sql["title_datebase"]}''' 

    # создание объекта engine который может подключаться к БД:
    engine = sqlalchemy.create_engine(DSN)

    # создание таблиц базы данных согласно моделей
    create_tables(engine)

    # создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()

    # наполнение базы данных
    download_json()

    author ='O’Reilly'
    print(f'Автор {author}:')
    find_book_sold(author)

    author = input('Введите имя автора: ')
    find_book_sold(author)

    session.commit()