
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
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

def test_most_prolific(db_connection):
    """Test finding most prolific author"""
    # Create test authors
    author1 = Author(name="Anita", email="anita@gmail.com").save()
    author2 = Author(name="Builder", email="builder@gmail.com").save()
    
    # Create articles
    with db_connection.cursor() as cursor:
        # Author 1: 3 articles
        cursor.execute("""
            INSERT INTO articles (title, author_id, magazine_id)
            VALUES (%s, %s, %s),
                   (%s, %s, %s),
                   (%s, %s, %s)
        """, (
            "Art 1", author1.id, 1,
            "Art 2", author1.id, 1,
            "Art 3", author1.id, 1
        ))
        
        # Author 2: 2 articles
        cursor.execute("""
            INSERT INTO articles (title, author_id, magazine_id)
            VALUES (%s, %s, %s),
                   (%s, %s, %s)
        """, (
            "Art 4", author2.id, 1,
            "Art 5", author2.id, 1
        ))
        db_connection.commit()
    
    prolific = Author.most_prolific()
    assert prolific.id == author1.id


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

def test_magazines_method(db_connection, test_author, test_magazine):
    """Test author's magazines relationship"""
    # Create article linking author and magazine
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO articles (title, author_id, magazine_id)
            VALUES ('Test Article', %s, %s)
        """, (test_author.id, test_magazine))
        db_connection.commit()
    
    magazines = test_author.magazines()
    assert len(magazines) == 1
    assert magazines[0].name == "Tech Today"

