import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create the user table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def add_user(name, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Insert the new user into the database
    c.execute('INSERT INTO users (name, password) VALUES (?, ?)', (name, password))

    conn.commit()
    conn.close()

def get_user(name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Get the user from the database
    c.execute('SELECT * FROM users WHERE name=?', (name,))
    user = c.fetchone()

    conn.close()

    return user
