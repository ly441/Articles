
import pytest
import psycopg2
import os
from code_challenge.lib.models.author import Author
from code_challenge.lib.models.article import Article
from code_challenge.lib.models.magazine import Magazine
from code_challenge.lib.db.connection import get_connection

# Fixtures
@pytest.fixture(scope="module")
def test_db():
    """Create test database structure"""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "articles_challenge"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost")
    )
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            bio TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS magazines (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            published_at TIMESTAMP WITH TIME ZONE,
            author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
            magazine_id INTEGER REFERENCES magazines(id) ON DELETE SET NULL       
        )
    """)
    
    conn.commit()
    conn.close()
    print("Test database structure created")
    yield

@pytest.fixture
def db_connection(test_db):
    """Database connection with clean state"""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "articles_challenge"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost")
    )
    cursor = conn.cursor()
    
    # Clean tables
    cursor.execute("TRUNCATE TABLE articles RESTART IDENTITY CASCADE")
    cursor.execute("TRUNCATE TABLE authors RESTART IDENTITY CASCADE")
    cursor.execute("TRUNCATE TABLE magazines RESTART IDENTITY CASCADE")
    
    # Add test data
    cursor.execute(
        "INSERT INTO authors (name, email, bio) VALUES (%s, %s, %s) RETURNING id",
        ("Test Author", "test@example.com", "Test Bio")
    )
    author_id = cursor.fetchone()[0]
    
    cursor.execute(
        "INSERT INTO magazines (name, category) VALUES (%s, %s) RETURNING id",
        ("Tech Today", "Technology")
    )
    magazine_id = cursor.fetchone()[0]
    
    cursor.execute(
        "INSERT INTO articles (title, content, author_id, magazine_id) VALUES (%s, %s, %s, %s)",
        ("Test Article", "Test Content", author_id, magazine_id)
    )
    
    conn.commit()
    yield conn
    conn.close





@pytest.fixture
def test_author(db_connection):
    author = Author(name="Test Author", email="test@example.com").save()
    assert author.id is not None
    return author

@pytest.fixture
def test_magazine(db_connection):
    """Fixture providing a test magazine"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO magazines (name, category)
            VALUES ('Tech Today', 'Technology')
            RETURNING id
        """)
        magazine_id = cursor.fetchone()[0]
        db_connection.commit()
    return magazine_id

