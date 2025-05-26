# lib/db/connection.py
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    conn = psycopg2.connect(
        dbname="articles_challenge",
        user="postgres",     
        password="lynn123",  
        host="localhost",
        port="5432"
    )
    conn.cursor_factory = RealDictCursor  
    return conn