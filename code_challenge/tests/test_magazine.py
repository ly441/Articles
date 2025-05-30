
import pytest
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from code_challenge.lib.models.magazine import Magazine

@pytest.fixture(scope="module")
def db_connection():
    # Set up the connection parameters for the test database
    Magazine.set_connection({
        "dbname": "test_articles_challenge",
        "user": "postgres",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": 5432
    })
    
    # Create the necessary tables for the test
    with psycopg2.connect(**Magazine._connection) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS magazines (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    description TEXT,
                    frequency VARCHAR(50) CHECK (frequency IN ('weekly', 'monthly', 'quarterly', 'yearly')),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    published_at TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(20) CHECK (status IN ('draft', 'published', 'archived')) DEFAULT 'draft',
                    author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
                    magazine_id INTEGER REFERENCES magazines(id) ON DELETE SET NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT title_min_length CHECK (length(title) >= 5),
                    CONSTRAINT content_min_length CHECK (length(content) >= 100)
                );
            """)
            conn.commit()
    yield
    # Drop the tables after the tests are done
    with psycopg2.connect(**Magazine._connection) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS articles CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS magazines CASCADE;")
            conn.commit()

def test_create_magazine(db_connection):
    magazine = Magazine.create("Tech Today", "Technology", "Daily updates on tech news")
    assert magazine.id is not None
    assert magazine.name == "Tech Today"
    assert magazine.category == "Technology"
    assert magazine.description == "Daily updates on tech news"

def test_find_magazine_by_id(db_connection):
    magazine = Magazine.create("Tech Today", "Technology", "Daily updates on tech news")
    found_magazine = Magazine.find_by_id(magazine.id)
    assert found_magazine.name == "Tech Today"
    assert found_magazine.category == "Technology"
    assert found_magazine.description == "Daily updates on tech news"

def test_find_magazine_by_name(db_connection):
    Magazine.create("Tech Today", "Technology", "Daily updates on tech news")
    magazines = Magazine.find_by_name("Tech Today")
    assert len(magazines) == 1
    assert magazines[0].name == "Tech Today"

def test_update_magazine(db_connection):
    magazine = Magazine.create("Tech Today", "Technology", "Daily updates on tech news")
    magazine.name = "Tech Tomorrow"
    magazine.description = "Weekly updates on tech trends"
    magazine.save()
    updated_magazine = Magazine.find_by_id(magazine.id)
    assert updated_magazine.name == "Tech Tomorrow"
    assert updated_magazine.description == "Weekly updates on tech trends"

def test_delete_magazine(db_connection):
    magazine = Magazine.create("Tech Today", "Technology", "Daily updates on tech news")
    magazine.delete()
    assert Magazine.find_by_id(magazine.id) is None

def test_top_publisher(db_connection):
    magazine1 = Magazine.create("Tech Today", "Technology", "Daily updates on tech news")
    magazine2 = Magazine.create("Science Weekly", "Science", "Weekly updates on science news")
    
    # Assuming you have a method to add articles to a magazine
    # Add more articles to magazine1 than magazine2
    # This is a placeholder for actual article creation logic
    # Article.create(magazine_id=magazine1.id, ...)
    
    top_publisher = Magazine.top_publisher()
    assert top_publisher.id == magazine1.id