
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from code_challenge.lib.models.author import Author
from code_challenge.lib.models.article import Article
from code_challenge.lib.models.magazine import Magazine


# Fixtures
@pytest.fixture(scope="module")
def test_db():
    """Create test database structure"""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "articles_challenge"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost")
    )
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authors (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            bio TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            published_at TIMESTAMP WITH TIME ZONE,
            author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

@pytest.fixture
def db_connection(test_db):
    """Database connection with clean state"""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "articles_challenge"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost")
    )
    cursor = conn.cursor()
    
    # Clean tables
    cursor.execute("TRUNCATE TABLE articles RESTART IDENTITY CASCADE")
    cursor.execute("TRUNCATE TABLE authors RESTART IDENTITY CASCADE")
    
    # Add test data
    cursor.execute(
        "INSERT INTO authors (name, email, bio) VALUES (%s, %s, %s) RETURNING id",
        ("Test Author", "test@example.com", "Test Bio")
    )
    author_id = cursor.fetchone()[0]
    
    cursor.execute(
        "INSERT INTO articles (title, content, author_id) VALUES (%s, %s, %s)",
        ("Test Article", "Test Content", author_id)
    )
    
    conn.commit()
    yield conn
    conn.close()

@pytest.fixture
def test_author(db_connection):
    """Fixture providing a test author"""
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM authors LIMIT 1")
        return Author(**cursor.fetchone())

@pytest.fixture
def test_article(db_connection):
    """Fixture providing a test article"""
    with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM articles LIMIT 1")
        return Article(**cursor.fetchone())

# Test Cases
def test_author_initialization():
    """Test Author class initialization"""
    author = Author("John Doe", "john@example.com")
    assert author.name == "John Doe"
    assert author.email == "john@example.com"
    assert author.id is None

@pytest.mark.parametrize("name,email", [
    ("J", "john@example.com"),
    ("", "john@example.com")
])
def test_name_validation(name, email):
    """Test name validation"""
    with pytest.raises(ValueError, match="at least 2 characters"):
        Author(name, email)

@pytest.mark.parametrize("email", [
    "invalid-email",
    "missing@dot"
])
def test_email_validation(email):
    """Test email validation"""
    with pytest.raises(ValueError, match="Invalid email format"):
        Author("John Doe", email)

def test_save_new_author(db_connection):
    """Test saving a new author"""
    author = Author("New Author", "new@example.com")
    saved_author = author.save()
    
    assert saved_author.id is not None
    assert saved_author.name == "New Author"

def test_find_by_id(test_author):
    """Test finding author by ID"""
    found = Author.find_by_id(test_author.id)
    assert found.name == "Test Author"
    assert found.email == "test@example.com"

def test_find_by_name():
    """Test finding authors by name"""
    Author("Search Test", "search@test.com").save()
    results = Author.find_by_name("Test")
    assert len(results) == 1
    assert results[0].name == "Search Test"

def test_author_articles_relationship(test_author, test_article):
    """Test author-articles relationship"""
    articles = test_author.articles()
    assert len(articles) == 1
    assert articles[0].title == "Test Article"

def test_duplicate_email(test_author):
    """Test duplicate email validation"""
    with pytest.raises(ValueError, match="already exists"):
        Author("Duplicate", test_author.email).save()

def test_magazines_method(db_connection, test_author):
    """Test author's magazines relationship"""
    # Create test magazines
    magazine1 = Magazine.create("Tech Today", "Technology")
    magazine2 = Magazine.create("Tech Weekly", "Technology")
    
    # Create articles
    Article.create("Python Tips", "Content", test_author.id, magazine1.id)
    Article.create("Rust Guide", "Content", test_author.id, magazine2.id)
    
    magazines = test_author.magazines()
    assert len(magazines) == 2
    assert {m.name for m in magazines} == {"Tech Today", "Tech Weekly"}

def test_most_prolific(db_connection):
    """Test finding most prolific author"""
    # Create test authors
    author1 = Author("Author 1", "author1@test.com").save()
    author2 = Author("Author 2", "author2@test.com").save()
    
    # Create articles
    Article.create("Article 1", "Content", author1.id, 1)
    Article.create("Article 2", "Content", author1.id, 1)
    Article.create("Article 3", "Content", author1.id, 1)
    Article.create("Article 4", "Content", author2.id, 1)
    
    prolific = Author.most_prolific()
    assert prolific.id == author1.id