import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="articles.db",
        user="lynn kolii",
        password="space",
        host="localhost",
        port="5432"
    )
