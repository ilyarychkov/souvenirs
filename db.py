import sqlite3
import os

# Определяем базовую директорию проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Инициализация БД
def init_db():
    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS Arts (
            Art_ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            ArtPhoto BLOB NOT NULL,
            Price INT NOT NULL,
            Width INT NOT NULL,
            Height INT NOT NULL,
            Artist_ID INT NOT NULL,
            Creation_year INT NOT NULL,
            Technique INT NOT NULL,
            Description TEXT,
            Sold BOOLEAN,
            Framing TEXT NOT NULL,
            FOREIGN KEY (Artist_ID) REFERENCES Artists(Artist_ID),
            FOREIGN KEY (Technique) REFERENCES Techniques(Technique_ID)
        )
    ''')          

    c.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            First_name TEXT NOT NULL,
            Last_name TEXT NOT NULL,
            Email TEXT NOT NULL,
            Password TEXT NOT NULL,
            Phone TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Artists (
            Artist_ID INT PRIMARY KEY,
            Name TEXT NOT NULL,
            ArtistPhoto BLOB NOT NULL,
            Birth_year INT,
            Bio TEXT
        )
    ''')

    c.execute('''              
        CREATE TABLE IF NOT EXISTS Techniques (
            Technique_ID INT PRIMARY KEY,
            Name TEXT NOT NULL
        )
    ''')

    c.execute('''  
        CREATE TABLE IF NOT EXISTS Themes (
            Theme_ID INT PRIMARY KEY,
            Name TEXT NOT NULL
        )
    ''')

    c.execute('''              
        CREATE TABLE IF NOT EXISTS Arts_themes (
            Art_theme_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Art_ID INT,
            Theme_ID INT,
            FOREIGN KEY (Art_ID) REFERENCES Arts(Art_ID),
            FOREIGN KEY (Theme_ID) REFERENCES Themes(Theme_ID)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Cart (
            Cart_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            User_ID INT,
            FOREIGN KEY (User_id) REFERENCES Users(User_ID)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Cart_items (
            Cart_item_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Cart_ID INT,
            Art_ID INT,
            FOREIGN KEY (Cart_ID) REFERENCES Cart(Cart_ID),
            FOREIGN KEY (Art_ID) REFERENCES Arts(Art_ID)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Favorites (
            Favorites_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            User_ID INT,
            Art_ID INT,
            FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
            FOREIGN KEY (Art_ID) REFERENCES Arts(Art_ID)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            Order_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            User_ID INT,
            User_Phone_number TEXT,
            Delivery_address TEXT,
            Total_amount INT,
            Order_date DATETIME,
            status CHECK(status IN ('Сборка заказа', 'В пути', 'Отменен')),
            FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS Order_items (
            Order_item_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Order_ID INT,
            Art_ID INT,
            FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID),
            FOREIGN KEY (Art_ID) REFERENCES Arts(Art_ID)
        )
    ''')

    conn.commit()
    conn.close()

def convertToBinaryData(filename):
    try:
        file_path = os.path.join(BASE_DIR, 'static', 'images', filename)
        with open(file_path, 'rb') as file:
            blobData = file.read()
        return blobData
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None

# Функция для вставки данных в таблицы
def insertData(table_name, **kwargs):
    try:
        conn = sqlite3.connect('arthaven.db')
        c = conn.cursor()

        # Проверка наличия изображения для преобразования в BLOB
        if 'ArtPhoto' in kwargs and kwargs['ArtPhoto']:
            kwargs['ArtPhoto'] = convertToBinaryData(kwargs['ArtPhoto'])

        if 'ArtistPhoto' in kwargs and kwargs['ArtistPhoto']:
            kwargs['ArtistPhoto'] = convertToBinaryData(kwargs['ArtistPhoto'])

        # Формирование запроса на вставку
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?' for _ in kwargs])
        sqlite_insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        # Выполнение запроса
        c.execute(sqlite_insert_query, tuple(kwargs.values()))
        conn.commit()
        print(f"Данные успешно вставлены в таблицу {table_name}")

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()

# Инициализация базы данных
init_db()

# Вставка данных в таблицы
insertData('Techniques', Technique_ID=1, Name='Холст, акрил')
insertData('Techniques', Technique_ID=2, Name='Холст, масло')
insertData('Techniques', Technique_ID=3, Name='Картон, масло')
insertData('Techniques', Technique_ID=4, Name='Дерево, масло')
insertData('Techniques', Technique_ID=5, Name='Холст, акрил, масло')
insertData('Techniques', Technique_ID=6, Name='Холст, темпера')
insertData('Techniques', Technique_ID=7, Name='Дерево, акрил')
insertData('Techniques', Technique_ID=8, Name='Бумага, акрил')
insertData('Techniques', Technique_ID=9, Name='Ткань, акрил')
insertData('Techniques', Technique_ID=10, Name='Бумага, масло')

# Таблица категорий
insertData('Themes', Theme_ID=1, Name='Украшение')
insertData('Themes', Theme_ID=2, Name='Сувенир')
insertData('Themes', Theme_ID=3, Name='Редкое')
insertData('Themes', Theme_ID=4, Name='Необычное')
insertData('Themes', Theme_ID=5, Name='Средневековье')
insertData('Themes', Theme_ID=6, Name='Прекрасное')
insertData('Themes', Theme_ID=7, Name='Подарок')
insertData('Themes', Theme_ID=8, Name='Интересное')
insertData('Themes', Theme_ID=9, Name='Магнит')
insertData('Themes', Theme_ID=10, Name='Дорогое')
insertData('Themes', Theme_ID=11, Name='Украшения')
insertData('Themes', Theme_ID=12, Name='Хорошая цена')
insertData('Themes', Theme_ID=13, Name='Хороший подарок')
insertData('Themes', Theme_ID=14, Name='Для девушки')
insertData('Themes', Theme_ID=15, Name='Для мужчины')
insertData('Themes', Theme_ID=16, Name='История')
insertData('Themes', Theme_ID=17, Name='Искусство')
insertData('Themes', Theme_ID=18, Name='Рукоделье')

# Таблица Городов
insertData('Artists', Artist_ID=1, Name='Санкт-Петербург', ArtistPhoto='питер.png', Birth_year=1703, 
           Bio='Санкт-Петербург – русский портовый город на побережье Балтийского моря, который в течение двух веков служил столицей Российской империи. Он был основан в 1703 году Петром I, которому воздвигнут знаменитый памятник "Медный всадник".')
insertData('Artists', Artist_ID=2, Name='Москва', ArtistPhoto='москва.png', Birth_year=1147, 
           Bio='Москва – столица России, многонациональный город на Москве-реке в западной части страны. В его историческом центре находится средневековая крепость Кремль – резиденция российского президента.')
insertData('Artists', Artist_ID=3, Name='Казань', ArtistPhoto='казань.png', Birth_year=1005, 
           Bio='Казань – город на юго-западе России, расположенный на берегах Волги и Казанки. В столице полуавтономной Республики Татарстан находится древний кремль – крепость, известная своими музеями и святыми местами.')
insertData('Artists', Artist_ID=4, Name='Челябинск', ArtistPhoto='челябинск.png', Birth_year=1736, 
           Bio='Челя́бинск — восьмой по численности населения город в Российской Федерации, административный центр Челябинской области, шестнадцатый по занимаемой площади городской округ.')
insertData('Artists', Artist_ID=5, Name='Новосибирск', ArtistPhoto='новосибирск.png', Birth_year=1893, 
           Bio='Новосибирск – российский город на реке Обь в юго-восточной части Западно-Сибирской равнины. Благодаря строительству Транссибирской магистрали с XIX века город постоянно рос и развивался. Об этом напоминает первый железнодорожный мост через реку Обь, который существует и сегодня.')

# Таблица Сувениров  
insertData('Arts', Art_ID=2, Name='Браслет Питер', ArtPhoto='браслетпитер.webp', Price=129, Width=1, Height=120, Artist_ID=1, Creation_year=2023, Technique=2, 
           Description='', Sold=False, Framing='Подрамник')
insertData('Arts_themes', Art_ID=2, Theme_ID=2)
insertData('Arts_themes', Art_ID=2, Theme_ID=11)
insertData('Arts_themes', Art_ID=2, Theme_ID=14)
insertData('Arts_themes', Art_ID=2, Theme_ID=12)
insertData('Arts', Art_ID=3, Name='Веер Санкт-Петербург', ArtPhoto='веерсанктпетербург.webp', Price=215, Width=1, Height=120, Artist_ID=1, Creation_year=2024, Technique=2, 
           Description='Т')