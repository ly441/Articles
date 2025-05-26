
import pytest
import psycopg2
from code_challenge.lib.models.article import Article
from code_challenge.lib.models.author import Author
from code_challenge.lib.models.magazine import Magazine


# Fixtures
@pytest.fixture(scope="module")
def db_connection():
    """Module-scoped database setup"""
    connection_params = {
        "dbname": "test_articles_db",
        "user": "postgres",  
        "password": "postgres",
        "host": "localhost",
        "port" : 5432
    }
    
    # Set connections for all models
    Article.set_connection(connection_params)
    Author.set_connection(connection_params)
    Magazine.set_connection(connection_params)

    # Create tables
    conn = psycopg2.connect(**connection_params)
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                bio TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS magazines (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,       
                author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
                magazine_id INTEGER REFERENCES magazines(id) ON DELETE SET NULL
            )
        """)
        conn.commit()
    
    yield conn
    
    # Teardown
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS articles, authors, magazines CASCADE")
        conn.commit()
    conn.close()

@pytest.fixture(autouse=True)
def clean_db(db_connection):
    """Clean and seed test data before each test"""
    with db_connection.cursor() as cursor:
        cursor.execute("TRUNCATE authors, magazines, articles RESTART IDENTITY CASCADE")
        
        # Insert test author
        cursor.execute("""
            INSERT INTO authors (name, bio)
            VALUES ('Test Author', 'Test Bio')
            RETURNING id
        """)
        author_id = cursor.fetchone()[0]
        
        # Insert test magazine
        cursor.execute("""
            INSERT INTO magazines (name, category)
            VALUES ('Test Magazine', 'Test Category')
            RETURNING id
        """)
        magazine_id = cursor.fetchone()[0]
        
        db_connection.commit()
    
    return {"author_id": author_id, "magazine_id": magazine_id}

# Tests
def test_article_creation(clean_db):
    article = Article(
        title="Test Article",
        content="Test Content",
        author_id=clean_db["author_id"],
        magazine_id=clean_db["magazine_id"]
    )
    assert article.title == "Test Article"
    assert article.author_id == clean_db["author_id"]

def test_save_and_retrieve(clean_db):
    article = Article(
        title="Save Test",
        content="Content",
        author_id=clean_db["author_id"],
        magazine_id=clean_db["magazine_id"]
    )
    article.save()
    
    retrieved = Article.find_by_id(article.id)
    assert retrieved.title == "Save Test"
    assert retrieved.author_id == clean_db["author_id"]

def test_find_by_title(clean_db):
    Article.create(
        title="Unique Title 123",
        content="Content",
        author_id=clean_db["author_id"],
        magazine_id=clean_db["magazine_id"]
    )
    
    results = Article.find_by_title("unique")
    assert len(results) == 1
    assert results[0].title == "Unique Title 123"

def test_find_by_author(clean_db):
    Article.create(
        title="Author Test",
        content="Content",
        author_id=clean_db["author_id"],
        magazine_id=clean_db["magazine_id"]
    )
    
    results = Article.find_by_author(clean_db["author_id"])
    assert len(results) == 1
    assert results[0].title == "Author Test"

def test_find_by_magazine(clean_db):
    Article.create(
        title="Magazine Test",
        content="Content",
        author_id=clean_db["author_id"],
        magazine_id=clean_db["magazine_id"]
    )
    
    results = Article.find_by_magazine(clean_db["magazine_id"])
    assert len(results) == 1
    assert results[0].title == "Magazine Test"

def test_article_update(clean_db):
    article = Article.create(
        title="Original Title",
        content="Content",
        author_id=clean_db["author_id"],
        magazine_id=clean_db["magazine_id"]
    )
    
    article.title = "Updated Title"
    article.save()
    
    updated = Article.find_by_id(article.id)
    assert updated.title == "Updated Title"

def test_article_delete(clean_db):
    article = Article.create(
        title="To Delete",
        content="Content",
        author_id=clean_db["author_id"],
        magazine_id=clean_db["magazine_id"]
    )
    
    article.delete()
    assert Article.find_by_id(article.id) is None

@pytest.mark.parametrize("title,content,author_id,magazine_id", [
    ("", "Content", 1, 1),
    ("Title", "", 1, 1),
    ("Title", "Content", 0, 1),
    ("Title", "Content", 1, 0),
])
def test_validation(title, content, author_id, magazine_id, clean_db):
    with pytest.raises(ValueError):
        Article(
            title=title,
            content=content,
            author_id=author_id,
            magazine_id=magazine_id
        )