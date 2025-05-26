
import unittest
import psycopg2
from psycopg2.extras import RealDictCursor
from lib.models.author import Author
from code_challenge.lib.models.article import Article
from code_challenge.lib.models.magazine import Magazine
import os

class TestArticle(unittest.TestCase):
    def test_something(self):
        self.assertTrue(True)
# Test Database Setup
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

@pytest.fixture(autouse=True)
def clean_tables(test_db):
    """Clean tables before each test"""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "articles_challenge"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost")
    )
    cursor = conn.cursor()
    
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
    conn.close()

# === Test Cases ===
def test_author_initialization():
    """Test Author class initialization"""
    author = Author("John Doe", "john@example.com")
    assert author.name == "John Doe"
    assert author.email == "john@example.com"
    assert author.id is None

def test_name_validation():
    """Test name validation"""
    with pytest.raises(ValueError, match="at least 2 characters"):
        Author("J", "john@example.com")
    
    with pytest.raises(ValueError):
        Author("", "john@example.com")

def test_email_validation():
    """Test email validation"""
    with pytest.raises(ValueError, match="Invalid email format"):
        Author("John Doe", "invalid-email")
    
    with pytest.raises(ValueError):
        Author("John Doe", "missing@dot")

def test_save_new_author():
    """Test saving a new author"""
    author = Author("New Author", "new@example.com")
    saved_author = author.save()
    
    assert saved_author.id is not None
    assert saved_author.name == "New Author"

def test_find_by_id():
    """Test finding author by ID"""
    author = Author.find_by_id(1)
    assert author is not None
    assert author.name == "Test Author"
    assert author.email == "test@example.com"

def test_find_by_name():
    """Test finding authors by name"""
    authors = Author.find_by_name("Test")
    assert len(authors) == 1
    assert authors[0].name == "Test Author"

def test_author_articles_relationship():
    """Test author-articles relationship"""
    author = Author.find_by_id(1)
    articles = author.articles()
    
    assert len(articles) == 1
    assert articles[0].title == "Test Article"

def test_duplicate_email():
    """Test duplicate email validation"""
    author = Author("Duplicate", "test@example.com")
    with pytest.raises(ValueError, match="already exists"):
        author.save()
        
def test_magazines_method(self):
    # Create second magazine
    magazine2 = Magazine.create("Tech Weekly", "Technology")
    Article.create("Python Tips", "Content", self.author.id, self.magazine.id)
    Article.create("Rust Guide", "Content", self.author.id, magazine2.id)
    
    magazines = self.author.magazines()
    self.assertEqual(len(magazines), 2)
    self.assertEqual({m.name for m in magazines}, {"Tech Today", "Tech Weekly"})

def test_most_prolific(self):
    author2 = Author.create("Jane Smith", "Writer")
    Article.create("Article 1", "Content", self.author.id, self.magazine.id)
    Article.create("Article 2", "Content", self.author.id, self.magazine.id)
    Article.create("Article 3", "Content", author2.id, self.magazine.id)
    
    prolific = Author.most_prolific()
    self.assertEqual(prolific.id, self.author.id)       