import pytest
import psycopg2

@pytest.fixture(scope="session")
def db_connection():
    """Session-wide test database connection"""
    # Connect to dedicated test database
    conn = psycopg2.connect(
        dbname="articles_test",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
    
    # Create fresh tables
    with conn.cursor() as cur:
        with open("schema.sql") as f:
            cur.execute(f.read())
        conn.commit()
    
    yield conn
    
    # Cleanup after all tests
    with conn.cursor() as cur:
        cur.execute("DROP TABLE articles, authors, magazines CASCADE;")
    conn.close()

@pytest.fixture(autouse=True)
def clean_tables(db_connection):
    """Clean data between tests"""
    yield
    with db_connection.cursor() as cur:
        cur.execute("TRUNCATE authors, magazines, articles RESTART IDENTITY CASCADE;")
    db_connection.commit()