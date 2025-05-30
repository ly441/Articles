import psycopg2

# Connection config — change to match your setup
DB_NAME = "articles_test"
DB_USER = "postgres"
DB_PASSWORD = "postgres"  # 🔐 Replace with your real password
DB_HOST = "localhost"
DB_PORT = "5432"

def init_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Example SQL table creation — adjust based on your schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS authors (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            author_id INTEGER REFERENCES authors(id)
        );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tables created successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    init_db()
