# Import Flask modules
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, make_response
from flaskext.mysql import MySQL

# Create an object named app
app = Flask(__name__)

# Configure MySQL database
app.config['MYSQL_DATABASE_HOST'] = 'database.c1c8mokm63q3.us-east-1.rds.amazonaws.com'
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'dbpasword_1'
app.config['MYSQL_DATABASE_DB'] = 'bookstore_db'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql = MySQL()
mysql.init_app(app)
connection = mysql.connect()
connection.autocommit(True)
cursor = connection.cursor()

# Initialize the database
def init_bookstore_db():
    cursor.execute("SHOW TABLES LIKE 'books';")
    result = cursor.fetchone()
    if not result:
        books_table = """
        CREATE TABLE books(
        book_id INT NOT NULL AUTO_INCREMENT,
        title VARCHAR(100) NOT NULL,
        author VARCHAR(100),
        is_sold BOOLEAN NOT NULL DEFAULT 0,
        PRIMARY KEY (book_id)
        )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        data = """
        INSERT INTO books (title, author, is_sold)
        VALUES
            ("Where the Crawdads Sing", "Delia Owens", 1 ),
            ("The Vanishing Half: A Novel", "Brit Bennett", 0),
            ("1st Case", "James Patterson, Chris Tebbetts", 0);
        """
        cursor.execute(books_table)
        cursor.execute(data)

# Get all books
def get_all_books():
    query = "SELECT * FROM books;"
    cursor.execute(query)
    result = cursor.fetchall()
    books = [{'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])} for row in result]
    return books

# Find a book by ID
def find_book(book_id):
    query = "SELECT * FROM books WHERE book_id=%s;"
    cursor.execute(query, (book_id,))
    row = cursor.fetchone()
    if row:
        return {'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])}
    return None

# Insert a book
def insert_book(title, author):
    insert_query = "INSERT INTO books (title, author) VALUES (%s, %s);"
    cursor.execute(insert_query, (title, author))

# Update a book
def update_book(book):
    update_query = """
    UPDATE books
    SET title=%s, author=%s, is_sold=%s
    WHERE book_id=%s;
    """
    cursor.execute(update_query, (book['title'], book['author'], book['is_sold'], book['book_id']))

# Remove a book
def remove_book(book_id):
    delete_query = "DELETE FROM books WHERE book_id=%s;"
    cursor.execute(delete_query, (book_id,))

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for displaying all books
@app.route('/books')
def books_page():
    books = get_all_books()
    return render_template('books.html', books=books)

# Route for adding a new book
@app.route('/books/add', methods=['GET', 'POST'])
def add_book_page():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        insert_book(title, author)
        return redirect(url_for('books_page'))
    return render_template('add_book.html')

# Route for editing a book
@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book_page(book_id):
    book = find_book(book_id)
    if not book:
        abort(404)
    if request.method == 'POST':
        book['title'] = request.form['title']
        book['author'] = request.form['author']
        book['is_sold'] = int(request.form.get('is_sold', 0))
        update_book(book)
        return redirect(url_for('books_page'))
    return render_template('edit_book.html', book=book)

# Route for deleting a book
@app.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book_page(book_id):
    book = find_book(book_id)
    if book:
        remove_book(book_id)
    return redirect(url_for('books_page'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return make_response(render_template('404.html'), 404)

# Run the application
if __name__ == '__main__':
    init_bookstore_db()
    app.run(host='0.0.0.0', port=80)

