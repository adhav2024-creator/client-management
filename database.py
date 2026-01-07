import sqlite3
import pandas as pd

DB_FILE = "clients.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create the clients table
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  client_num TEXT,
                  name TEXT,
                  uen TEXT,
                  year_end TEXT,
                  status TEXT)''')
    conn.commit()
    conn.close()

def get_clients():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()
    return df

def add_client(num, name, uen, ye, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO clients (client_num, name, uen, year_end, status) VALUES (?,?,?,?,?)",
              (num, name, uen, ye, status))
    conn.commit()
    conn.close()

def delete_client(client_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
def update_client(client_id, num, name, uen, month, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''UPDATE clients 
                 SET client_num=?, name=?, uen=?, year_end=?, status=? 
                 WHERE id=?''',
              (num, name, uen, month, status, client_id))
    conn.commit()
    conn.close()