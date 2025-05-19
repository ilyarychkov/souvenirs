from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import base64


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

app.secret_key = 'mySuperSecretKey123!'


# Функция для форматирования цены
def format_price(price):
    return f"{price:,.0f}".replace(',', '.')

# Регистрация пользовательского фильтра
app.jinja_env.filters['format_price'] = format_price


@app.route('/', methods=['GET'])
def main():
    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    c.execute('SELECT Art_ID, Name, ArtPhoto FROM Arts WHERE Sold = False ORDER BY RANDOM() LIMIT 1')
    banner_art = c.fetchone()

    c.execute('''SELECT a.Art_ID, a.Name, a.ArtPhoto, a.Price, a.Height, a.Width, ar.Name AS Author, a.Artist_ID 
        FROM Arts a
        JOIN Artists ar ON a.Artist_ID = ar.Artist_ID WHERE Sold = False ORDER BY a.Art_ID DESC
        LIMIT 4
    ''')
    popular_arts = c.fetchall()

    c.execute('''SELECT a.Art_ID, a.Name, a.ArtPhoto, a.Price, a.Height, a.Width, ar.Name AS Author, a.Artist_ID
        FROM Arts a
        JOIN Artists ar ON a.Artist_ID = ar.Artist_ID WHERE Sold = False ORDER BY RANDOM()
        LIMIT 20
    ''')
    rec_arts = c.fetchall()

    conn.close()

    return render_template('main.html', banner_art=banner_art, popular_arts=popular_arts, rec_arts=rec_arts)



@app.route('/arts-catalog', methods=['GET', 'POST'])
def artCatalog():
    sort_type = request.args.get('sort', 'popular')
    name_filter = request.args.get('name', '')
    
    # Получение параметра фильтрации по цене
    price_from = request.args.get('price_from', type=float)
    price_to = request.args.get('price_to', type=float)
    # Преобразование в целые числа
    price_from = int(price_from) if price_from is not None else None
    price_to = int(price_to) if price_to is not None else None

    is_sold = request.args.get('sold') 
    author = request.args.get('author', '')
    technique = request.args.getlist('technique')  
    theme = request.args.getlist('theme')  # Получение списка тем

    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    # Определение SQL-запроса в зависимости от выбранной сортировки
    order_by = {
        'popular': 'Art_ID DESC',
        'price-acs': 'Price ASC',
        'price-desc': 'Price DESC',
        'new-to-old': 'Creation_year DESC',
        'old-to-new': 'Creation_year ASC',
    }.get(sort_type, 'Art_ID ASC')

    # Начало SQL-запроса
    query = f"""
        SELECT a.Art_ID, a.Name, a.ArtPhoto, a.Price, a.Height, a.Width, ar.Name AS Author 
        FROM Arts a
        JOIN Artists ar ON a.Artist_ID = ar.Artist_ID 
        WHERE 1=1  -- Начинаем с условного выражения
    """
    conditions = []
    parameters = []

    if name_filter:
        conditions.append("a.Name LIKE ? COLLATE NOCASE")
        parameters.append('%' + name_filter + '%')


    if price_from is not None:
        conditions.append("a.Price >= ?")
        parameters.append(price_from)

    if price_to is not None:
        conditions.append("a.Price <= ?")
        parameters.append(price_to)

    if author:
        conditions.append("ar.Name LIKE ? COLLATE NOCASE")
        parameters.append('%' + author + '%')

    if technique:
        techniques_placeholder = ', '.join(['?'] * len(technique))
        conditions.append(f"a.Technique IN ({techniques_placeholder})")
        parameters.extend(technique)

    if theme:
        themes_placeholder = ', '.join(['?'] * len(theme))
        conditions.append(f"a.Theme IN ({themes_placeholder})")
        parameters.extend(theme)

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += f" ORDER BY {order_by}"

    c.execute(query, parameters)
    arts = c.fetchall()
    conn.close()

    return render_template('arts-catalog.html', arts=arts, sort_type=sort_type,
                           name_filter=name_filter, price_from=price_from, price_to=price_to,
                           author=author, technique=technique, theme=theme)



@app.route('/art')
def art():
    art_id = int(request.args.get('id'))
    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    user_id = session.get('user_id')
    in_cart = False
    is_favorite = False

    if user_id:
        # Находим Cart_ID для текущего пользователя
        c.execute('SELECT Cart_ID FROM Cart WHERE User_ID = ?', (user_id,))
        cart = c.fetchone()
        cart = int(cart[0]) # tuple в int

        c.execute('SELECT Art_ID FROM Cart_items WHERE Cart_ID = ? AND Art_ID = ?', (cart, art_id))
        res = c.fetchone()
        if res is not None:
            in_cart = res[0] > 0 
        else:
            in_cart = False 

        # Обработка наличия избранном
        c.execute('SELECT COUNT(*) FROM Favorites WHERE User_ID = ? AND Art_ID = ?', (user_id, art_id))
        is_favorite = c.fetchone()[0] > 0
    

    
    c.execute("""
        SELECT a.Art_ID, a.Name, a.ArtPhoto, a.Price, a.Height, a.Width, ar.Artist_ID, ar.Name AS Author, a.Creation_year, a.Description, a.Framing, t.Name AS Technique 
        FROM Arts a 
        JOIN Artists ar ON a.Artist_ID = ar.Artist_ID 
        LEFT JOIN Techniques t ON a.Technique = t.Technique_ID
        WHERE a.Art_ID = ?
    """, (art_id,))

    art_details = c.fetchone()

   
    c.execute('''SELECT Artist_ID, Name, ArtistPhoto, Birth_year, Bio FROM Artists WHERE Artist_ID = ?''', (art_details[6],))
    artist = c.fetchone()  
    
    artist_photo_b64 = base64.b64encode(artist[2]).decode('utf-8')
    artist = artist[:2] + (artist_photo_b64,) + artist[3:]

    
    themes = []
    if art_details:
        c.execute("""
            SELECT th.Name FROM Themes th
            JOIN Arts_themes at ON th.Theme_ID = at.Theme_ID
            WHERE at.Art_ID = ?
        """, (art_id,))

        themes = [row[0] for row in c.fetchall()]  
        # Преобразуем BLOB в Base64
        art_photo_b64 = base64.b64encode(art_details[2]).decode('utf-8')
        art_details = art_details[:2] + (art_photo_b64,) + art_details[3:]

       
        author_name = artist[1]
        c.execute("""
            SELECT COUNT(*) FROM Arts WHERE Artist_ID = (
                SELECT Artist_ID FROM Artists WHERE Name = ?
            )
        """, (author_name,))
        author_count = c.fetchone()[0]

        
        c.execute("""
            SELECT th.Name FROM Themes th
            JOIN Arts_themes at ON th.Theme_ID = at.Theme_ID
            JOIN Arts a ON a.Art_ID = at.Art_ID
            WHERE a.Artist_ID = (
                SELECT Artist_ID FROM Artists WHERE Name = ?
            )
            GROUP BY th.Name
            LIMIT 5
        """, (author_name,))
        author_themes = [row[0] for row in c.fetchall()]

        
        additional_themes_count = len(author_themes) - 5 if len(author_themes) > 5 else 0

       
        c.execute("""
            SELECT a.Art_ID, a.ArtPhoto FROM Arts a WHERE a.Artist_ID = (
                SELECT Artist_ID FROM Artists WHERE Name = ?
            ) LIMIT 5
        """, (author_name,))

        
        author_arts = [{'id': row[0], 'photo': base64.b64encode(row[1]).decode('utf-8')} for row in c.fetchall()]

        
        c.execute('''
            SELECT 
                art.Art_ID,
                art.Name,
                art.ArtPhoto
            FROM 
                Arts art
            WHERE 
                art.Artist_ID = ?
            LIMIT 5
        ''', (artist[0],))

    conn.close()

    return render_template('art.html', art=art_details, themes=themes, author_avatar=art_details[2], 
                           author_count=author_count, artist=artist, author_themes=author_themes, 
                           additional_themes_count=additional_themes_count, author_arts=author_arts, 
                           in_cart=in_cart, is_favorite=is_favorite)



@app.route('/artists-catalog', methods=['GET'])
def artistsCatalog():
    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    
    selected_themes = request.args.getlist('themes')  
    sort_by = request.args.get('sort_by', 'popular')   
    artist_name = request.args.get('artist_name', '')  

   
    sql = '''
        SELECT 
            a.Artist_ID, 
            a.Name AS artist_name,
            a.ArtistPhoto AS artist_photo,
            COUNT(art.Art_ID) AS artwork_count
        FROM 
            Artists a
        LEFT JOIN 
            Arts art ON a.Artist_ID = art.Artist_ID
    '''

  
    if artist_name:
        sql += ' WHERE a.Name LIKE ?'
        artist_name = f'%{artist_name}%'  
        params = [artist_name]
    else:
        params = []


    if selected_themes:
        if not artist_name:
            sql += ' WHERE '
        else:
            sql += ' AND '
        
        sql += '''
            a.Artist_ID IN (
                SELECT 
                    art.Artist_ID 
                FROM 
                    Arts art
                JOIN 
                    Arts_themes at ON art.Art_ID = at.Art_ID
                JOIN 
                    Themes t ON at.Theme_ID = t.Theme_ID
                WHERE 
                    t.Name IN ({})
            )
        '''.format(', '.join(['?'] * len(selected_themes)))

        params.extend(selected_themes)

  
    if sort_by == 'popular':
        sql += ' GROUP BY a.Artist_ID ORDER BY artwork_count DESC'
    elif sort_by == 'new-to-old':
        sql += ' GROUP BY a.Artist_ID ORDER BY a.Artist_ID DESC'  # По ID (предполагаем, что ID = Creation Date)
    elif sort_by == 'old-to-new':
        sql += ' GROUP BY a.Artist_ID ORDER BY a.Artist_ID ASC'

    c.execute(sql, params)
    artists = c.fetchall()

   
    artist_data = []
    for artist in artists:
        artist_id = artist[0]
        artist_name = artist[1]
        artist_photo = artist[2]
        artwork_count = artist[3]

        
        c.execute('''
            SELECT 
                art.Art_ID,
                art.Name,
                art.ArtPhoto
            FROM 
                Arts art
            WHERE 
                art.Artist_ID = ?
            LIMIT 5
        ''', (artist_id,))
        
        artworks = c.fetchall()
        
        
        c.execute('''
            SELECT DISTINCT
                t.Name 
            FROM 
                Themes t
            JOIN 
                Arts_themes at ON at.Theme_ID = t.Theme_ID
            JOIN 
                Arts art ON at.Art_ID = art.Art_ID
            WHERE 
                art.Artist_ID = ?
        ''', (artist_id,))
        
        themes = c.fetchall()
        remaining_themes_count = max(0, len(themes) - 5)
        
        
        themes_list = [theme[0] for theme in themes]

        artist_data.append({
            'artist_id': artist_id,
            'artist_name': artist_name,
            'artist_photo': artist_photo,
            'artwork_count': artwork_count,
            'themes': themes_list[:5],
            'remaining_themes_count': remaining_themes_count,
            'artworks': artworks
        })

    conn.close()

    return render_template('artists-catalog.html', artists=artist_data, selected_themes=selected_themes, artist_name=artist_name, sort_by=sort_by)



@app.route('/artist')
def artist():
    artist_id = request.args.get('id')  
    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

  
    c.execute('''SELECT Artist_ID, Name, ArtistPhoto, Birth_year, Bio FROM Artists WHERE Artist_ID = ?''', (artist_id,))
    artist = c.fetchone()  

    
    c.execute('''SELECT a.Art_ID, a.Name, a.ArtPhoto, a.Price, a.Width, a.Height, a.Description 
                 FROM Arts a 
                 WHERE a.Artist_ID = ?''', (artist_id,))
    arts = c.fetchall()  

    
    c.execute('''
        SELECT DISTINCT
            t.Name 
        FROM 
            Themes t
        JOIN 
            Arts_themes at ON at.Theme_ID = t.Theme_ID
        JOIN 
            Arts art ON at.Art_ID = art.Art_ID
        WHERE 
            art.Artist_ID = ?
    ''', (artist_id,))
    
    themes = c.fetchall()
    themes_list = [theme[0] for theme in themes]

    conn.close()

    return render_template('artist.html', artist=artist, arts=arts, themes_list=themes_list)


# Страница КОРЗИНЫ
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        return place_order()  # Обработка оформления заказа

    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    user_id = session['user_id']  # Получаем User_ID из сессии

    
    c.execute('''
        SELECT a.Art_ID, a.Name, a.Price, a.ArtPhoto FROM Cart_items ci
        JOIN Cart c ON ci.Cart_ID = c.Cart_ID
        JOIN Arts a ON ci.Art_ID = a.Art_ID
        WHERE c.User_ID = ?
    ''', (user_id,))
    
    cart_arts = c.fetchall()  # Получаем все товары в корзине
    
    total_price = sum(art[2] for art in cart_arts)  # Итоговая цена товаров в корзине

    # Преобразуем BLOB в Base64
    for idx, art in enumerate(cart_arts):
        art_photo_b64 = base64.b64encode(art[3]).decode('utf-8')  # Преобразуем BLOB в Base64
        cart_arts[idx] = art[:3] + (art_photo_b64,)  # Заменяем на закодированное изображение

    conn.close()

    return render_template('cart.html', cart_arts=cart_arts, total_price=total_price)

def place_order():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401  # Проверка авторизации

    user_id = session['user_id']
    user_phone = request.form.get('user_phone')
    delivery_address = request.form.get('delivery_address')
    
    # Получаем текущее время
    order_date = datetime.now()

    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    # Получаем текущую корзину пользователя
    c.execute('''
        SELECT ci.Art_ID, a.Price FROM Cart_items ci
        JOIN Cart c ON ci.Cart_ID = c.Cart_ID
        JOIN Arts a ON ci.Art_ID = a.Art_ID
        WHERE c.User_ID = ?
    ''', (user_id,))
    
    cart_items = c.fetchall()  # Получаем все товары в корзине

    if not cart_items:
        flash('Корзина пуста', 'error')
        return redirect(url_for('cart'))

    # Подсчитываем общую сумму
    total_amount = sum(item[1] for item in cart_items)

    # Вставляем новую запись в таблицу Orders
    c.execute('''
        INSERT INTO Orders (User_ID, User_Phone_number, Delivery_address, Total_amount, Order_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, user_phone, delivery_address, total_amount, order_date, 'Сборка заказа'))
    
    order_id = c.lastrowid  # Получаем ID нового заказа

    # Добавляем элементы заказа в таблицу Order_items
    for item in cart_items:
        c.execute('''
            INSERT INTO Order_items (Order_ID, Art_ID)
            VALUES (?, ?)
        ''', (order_id, item[0]))  # item[0] — это Art_ID
    
    # Очищаем корзину
    c.execute('DELETE FROM Cart_items WHERE Cart_ID = (SELECT Cart_ID FROM Cart WHERE User_ID = ?)', (user_id,))

    conn.commit()
    conn.close()

    flash('Ваш заказ успешно оформлен!', 'success')
    return redirect(url_for('main')) 


# Удаление товара из корзины
@app.route('/cart/delete/<int:art_id>', methods=['POST'])
def delete_from_cart(art_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401  # Проверка на авторизацию

    user_id = session['user_id']

    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    # Удаляем элемент из Cart_arts
    c.execute('''
        DELETE FROM Cart_items 
        WHERE Art_ID = ? AND Cart_ID = (SELECT Cart_ID FROM Cart WHERE User_ID = ?)
    ''', (art_id, user_id))
    
    conn.commit()
    conn.close()

    return jsonify({'success': True})


# Добавление товара в корзину
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    art_id = request.json.get('artId')

    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401  # Проверка на авторизацию

    user_id = session['user_id']  # Получаем User_ID из сессии

    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    # Находим Cart_ID для текущего пользователя
    c.execute('SELECT Cart_ID FROM Cart WHERE User_ID = ?', (user_id,))
    cart = c.fetchone()

    if cart:
        cart_id = cart[0]
        
        # Проверяем, есть ли уже этот элемент в корзине
        c.execute('SELECT COUNT(*) FROM Cart_items WHERE Cart_ID = ? AND Art_ID = ?', (cart_id, art_id))
        item_exists = c.fetchone()[0]

        if item_exists > 0:
            return jsonify({'error': 'Item already in cart'}), 409  # Конфликт, элемент уже в корзине

        # Добавляем элемент в корзину
        c.execute('INSERT INTO Cart_items (Cart_ID, Art_ID) VALUES (?, ?)', (cart_id, art_id))
        conn.commit()

        response = {'status': 'success', 'message': 'Item added to cart'}
    else:
        response = {'error': 'Cart not found'}

    conn.close()
    return jsonify(response)


# Добавление в избранное
@app.route('/api/favorites/add', methods=['POST'])
def add_to_favorites():
    art_id = request.json.get('artId')

    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401  # Проверка на авторизацию

    user_id = session.get('user_id')  # Получаем user_id из сессии

    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    # Проверяем, есть ли уже этот элемент в избранном
    c.execute('SELECT COUNT(*) FROM Favorites WHERE User_ID = ? AND Art_ID = ?', (user_id, art_id))
    item_exists = c.fetchone()[0]

    if item_exists > 0:
        # Удаляем элемент из избранного
        c.execute('DELETE FROM Favorites WHERE User_ID = ? AND Art_ID = ?', (user_id, art_id))
        conn.commit()
        response = {'status': 'success', 'message': 'Item deleted from favorites'}
    else:
        # Добавляем элемент в избранное
        c.execute('INSERT INTO Favorites (User_ID, Art_ID) VALUES (?, ?)', (user_id, art_id))
        conn.commit()
        response = {'status': 'success', 'message': 'Item added to favorites'}

    conn.close()
    return jsonify(response)


# страница ИЗБРАННОГО
@app.route('/favorites', methods=['GET'])
def favorites():
    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    user_id = session['user_id']  # Получаем User_ID из сессии

    # Получаем избранные картины текущего пользователя
    c.execute('SELECT Art_ID FROM Favorites WHERE User_ID = ?', (user_id,))
    
    fav_arts = c.fetchall()  # Получаем все картины в избранном

    # Извлекаем Art_ID из кортежа
    art_ids = [art[0] for art in fav_arts]  # Преобразуем в плоский список

    if not art_ids:  # Если нет избранных картин
        conn.close()
        return render_template('favorites.html', fav_arts=[])

    # Преобразуем список в строку для использования в IN-запросе
    placeholders = ', '.join('?' for _ in art_ids)

    c.execute(f"""
        SELECT a.Art_ID, a.Name, a.ArtPhoto, a.Price, a.Height, a.Width, ar.Artist_ID, ar.Name AS Author
        FROM Arts a
        JOIN Artists ar ON a.Artist_ID = ar.Artist_ID 
        WHERE a.Art_ID IN ({placeholders})
    """, art_ids)

    fav_arts = c.fetchall()

    # Преобразуем BLOB в Base64
    for idx, art in enumerate(fav_arts):
        # Убедимся, что art[2] — это фактически изображение в формате BLOB
        art_photo = art[2]  # измените индекс в зависимости от вашего SQL запроса
        if isinstance(art_photo, bytes):
            art_photo_b64 = base64.b64encode(art_photo).decode('utf-8')  # Преобразуем BLOB в Base64
            fav_arts[idx] = art[:2] + (art_photo_b64,) + art[3:]  # Заменяем на закодированное изображение
        else:
            # Обработка случая, когда art[2] не является байтовым объектом
            print(f"Неверный тип данных для art[2]: {type(art_photo)}")  # Для отладки
            fav_arts[idx] = art[:2] + (None,) + art[3:]  # Заменяем изображение на None

    conn.close()

    return render_template('favorites.html', fav_arts=fav_arts)


# Страница ВХОДА
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('login.html', email=email)

        conn = sqlite3.connect('arthaven.db')
        c = conn.cursor()

        # Поиск пользователя по email
        c.execute('SELECT User_ID, Password FROM Users WHERE Email = ?', (email,))
        user = c.fetchone()

        if user and check_password_hash(user[1], password):  # Проверяем пароль
            session['user_id'] = user[0]  # Сохраняем User_ID в сессии
            flash('Успешный вход!', 'success')
            return redirect(url_for('main'))
        else:
            flash('Неправильный email или пароль', 'error')
            return render_template('login.html', email=email)

        conn.close()
        
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем email из сессии
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('main'))


# Страница РЕГИСТРАЦИИ
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['name']
        last_name = request.form['surname']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        conn = sqlite3.connect('arthaven.db')
        c = conn.cursor()

        try:
            # Вставка нового пользователя в таблицу Users
            c.execute('INSERT INTO Users (First_name, Last_name, Email, Password) VALUES (?, ?, ?, ?)', 
                      (first_name, last_name, email, password))
            conn.commit()
            
            # Получаем User_ID последнего добавленного пользователя
            user_id = c.lastrowid
            
            # Создание корзины для нового пользователя
            c.execute('INSERT INTO Cart (User_ID) VALUES (?)', (user_id,))
            conn.commit()

            flash('Регистрация прошла успешно! Пожалуйста, войдите в свою учетную запись.', 'success')
            return redirect(url_for('login'))  # перенаправление на страницу входа
        except sqlite3.IntegrityError:
            flash('Email уже существует', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')


# Создание корзины для пользователя при регистрации
def create_cart_for_user(user_id):
    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()
    
    # Создание новой корзины для пользователя
    c.execute('INSERT INTO Cart (User_ID) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        phone = request.form['phone']

        c.execute('''
            UPDATE Users
            SET First_name = ?, Last_name = ?, Email = ?, Phone = ?
            WHERE User_ID = ?
        ''', (name, surname, email, phone, user_id))
        conn.commit()

    # Получение данных пользователя
    c.execute('SELECT First_name, Last_name, Email, Password, Phone FROM Users WHERE User_ID = ?', (user_id,))
    user = c.fetchone()

    # Получение всех заказов пользователя, включая отменённые
    c.execute('''
        SELECT Order_ID, Total_amount, Order_date, Delivery_address, Status FROM Orders
        WHERE User_ID = ? ORDER BY Order_date DESC
    ''', (user_id,))
    orders_raw = c.fetchall()

    orders = {}
    for order in orders_raw:
        order_id, total, date, address, status = order
        c.execute('''
            SELECT a.Art_ID, a.ArtPhoto FROM Order_items oi
            JOIN Arts a ON oi.Art_ID = a.Art_ID
            WHERE oi.Order_ID = ?
        ''', (order_id,))
        items = [{'id': row[0], 'image': base64.b64encode(row[1]).decode('utf-8')} for row in c.fetchall()]

        orders[order_id] = {
            'total_amount': total,
            'order_date': date,
            'delivery_address': address,
            'status': status,
            'art_items': items
        }

    conn.close()
    return render_template('profile.html', user=user, orders=orders)



@app.template_filter('b64encode')
def b64encode(data):
    if data and isinstance(data, bytes):
        try:
            encoded = base64.b64encode(data).decode('utf-8')
            return "data:image/png;base64," + encoded
        except Exception as e:
            print(f"Error encoding image: {e}")
    else:
        print("Data is not valid for encoding:", data)
    return ""

@app.route('/order/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'user_id' not in session:
        return jsonify(success=False, error='Пользователь не авторизован'), 401

    conn = sqlite3.connect('arthaven.db')
    c = conn.cursor()

    # Проверим, принадлежит ли заказ текущему пользователю
    c.execute('SELECT User_ID FROM Orders WHERE Order_ID = ?', (order_id,))
    result = c.fetchone()
    if result is None:
        conn.close()
        return jsonify(success=False, error='Заказ не найден'), 404

    if result[0] != session['user_id']:
        conn.close()
        return jsonify(success=False, error='Нет доступа к заказу'), 403

    # Удалим связанные записи из Order_items
    c.execute('DELETE FROM Order_items WHERE Order_ID = ?', (order_id,))

    # Удалим сам заказ
    c.execute('DELETE FROM Orders WHERE Order_ID = ?', (order_id,))

    conn.commit()
    conn.close()

    return jsonify(success=True, message='Заказ полностью удалён')





@socketio.on('message')
def handle_message(data):
    print('Received message: ' + data)


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@app.errorhandler(500)
def internal_error(error):
    return "500 Internal Server Error", 500


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)