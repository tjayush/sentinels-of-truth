import sqlite3

DATABASE_PATH = "database/truth.db"


def connect_db():

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
      
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim TEXT UNIQUE,
        status TEXT,
        confidence REAL,
        evidence TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flagged_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim TEXT,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    connection.commit()
    connection.close()


def insert_claim(claim, status, confidence, evidence):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO claims (claim, status, confidence, evidence)
    VALUES (?, ?, ?, ?)
    """, (claim, status, confidence, evidence))

    connection.commit()
    connection.close()


def insert_flagged_claim(claim, reason):
    
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO flagged_claims (claim, reason)
    VALUES (?, ?)
    """, (claim, reason))

    connection.commit()
    connection.close()


def get_all_claims():
  
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM claims ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]