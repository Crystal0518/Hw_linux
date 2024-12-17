from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_cors import CORS
import pymysql
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='Ljw1213808',
        database='book',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 登录页面路由
@app.route('/login')
def login_page():
    return render_template('login.html')

# 登录API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                      (username, password))
        user = cursor.fetchone()

        if user:
            return jsonify({'message': '登录成功'})
        else:
            return jsonify({'message': '用户名或密码��误'}), 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': '登录失败，请稍后重试'}), 500
    finally:
        cursor.close()
        conn.close()



# 添加 index 路由
@app.route('/index')
def index_page():
    return render_template('index.html')

# 修改主页路由（可选）
@app.route('/')
def home():
    return redirect(url_for('login_page'))

# Add @login_required to protected routes
@app.route('/api/books', methods=['GET'])
def get_books():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    search_query = request.args.get('search', '')

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    offset = (page - 1) * page_size

    # 构建查询条件
    where_clause = ""
    if search_query:
        where_clause = f" WHERE title LIKE '%{search_query}%' OR author LIKE '%{search_query}%'"

    # 获取总记录数
    cursor.execute(f"SELECT COUNT(*) as total FROM books_info{where_clause}")
    total = cursor.fetchone()['total']

    # 替代方案：使用变量来生成序号
    cursor.execute("SET @row_number = %s", (offset,))
    query = f"""
        SELECT 
            book_id,
            title,
            author,
            publisher,
            publication_year,
            genre,
            language,
            @row_number:=@row_number+1 as id
        FROM books_info
        {where_clause}
        LIMIT {offset}, {page_size}
    """
    
    cursor.execute(query)
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        'data': books,
        'total': total
    })


# 删除图书
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM books_info WHERE book_id = %s", (book_id,))
        conn.commit()
        return jsonify({'message': '删除成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 更新图书信息
@app.route('/api/books/<int:book_id>', methods=['PUT'])

def update_book(book_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
            UPDATE books_info 
            SET title = %s, author = %s, publisher = %s, 
                publication_year = %s, genre = %s, language = %s
            WHERE book_id = %s
        """
        cursor.execute(sql, (
            data['title'],
            data['author'],
            data['publisher'],
            data['publication_year'],
            data['genre'],
            data['language'],
            book_id
        ))
        conn.commit()
        return jsonify({'message': '更新成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 添加图书
@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # 验证必填字段
    required_fields = ['title', 'author', 'publisher', 'publication_year', 'genre', 'language']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 是必填项'}), 400

    try:
        sql = """
            INSERT INTO books_info (
                title, author, publisher, 
                publication_year, genre, language
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data['title'],
            data['author'],
            data['publisher'],
            data['publication_year'],
            data['genre'],
            data['language']
        ))
        conn.commit()
        return jsonify({'message': '添加成功', 'book_id': cursor.lastrowid})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
