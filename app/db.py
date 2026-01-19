import sqlite3

def get_db():
    conn = sqlite3.connect("users.db", timeout=10)
    conn.row_factory = sqlite3.Row
    return conn



def create_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()
    

def create_property_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            title TEXT,
            type TEXT,
            price INTEGER,
            description TEXT,
            image TEXT,
            contact_number TEXT,
            status TEXT DEFAULT 'available',
            deal_type TEXT,
            state TEXT,
            city TEXT,
            area TEXT
        )
    """)
    conn.commit()
    conn.close()

