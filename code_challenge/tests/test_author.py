
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
    with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM authors LIMIT 1")
        return Author(**cursor.fetchone())

@pytest.fixture
def test_article(db_connection):
    """Fixture providing a test article"""
    with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM articles LIMIT 1")
        row = cursor.fetchone()
        return Article(**row)


# Test Cases
def test_author_initialization():
    """Test Author class initialization"""
    author = Author("Josephine Doeller", "josephine@example.com")
    assert author.name == "Josephine Doeller"
    assert author.email == "josephine@example.com"
    assert author.id is None

@pytest.mark.parametrize("name,email", [
    ("J", "josephine@example.com"),
    ("", "josephine@example.com")
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
        Author("Josephine Doeller", email)

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

# tests/test_author.py
def test_author_articles_relationship(db_connection, magazine):
    author = Author(name="Test", email="test@example.com").save()
    
    with db_connection.cursor() as cur:
        cur.execute("""
            INSERT INTO articles (title, author_id, magazine_id)
            VALUES ('Test Article', %s, %s)
        """, (author.id, magazine))
        db_connection.commit()
    
    assert len(author.articles()) == 1

def test_duplicate_email(test_author):
    """Test duplicate email validation"""
    with pytest.raises(ValueError, match="already exists"):
        Author("Duplicate", test_author.email).save()


def test_magazines_method(db_connection, test_author, test_magazine):
    """Test author's magazines relationship"""
    magazine1 = Magazine.create("Tech Today", "Technology")
    magazine2 = Magazine.create("Tech Weekly", "Technology")
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO articles (title, author_id, magazine_id)
            VALUES ('Test Article', %s, %s)
        """, (test_author.id, test_magazine))
        db_connection.commit()
    
    magazines = test_author.magazines()
    assert len(magazines) == 1
    assert magazines[0].name == "Tech Today"
    
    # Create articles
    Article.create("Python Tips", "Content", test_author.id, magazine1.id)
    Article.create("Rust Guide", "Content", test_author.id, magazine2.id)
    
    magazines = test_author.magazines()
    assert len(magazines) == 2
    assert {m.name for m in magazines} == {"Tech Today", "Tech Weekly"}

def test_save_new_author(db_connection):
    """Test saving a new author to the database"""
    # Setup
    Author.set_connection(db_connection)
    
    # Test
    author = Author(name="Test Author", email="test@example.com")
    saved_author = author.save()
    
    # Assert
    assert saved_author.id is not None
    assert saved_author.created_at is not None    

def test_most_prolific(db_connection, test_magazine):
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
            "Art 1", author1.id, test_magazine,
            "Art 2", author1.id, test_magazine,
            "Art 3", author1.id, test_magazine
        ))
        
        # Author 2: 2 articles
        cursor.execute("""
            INSERT INTO articles (title, author_id, magazine_id)
            VALUES (%s, %s, %s),
                   (%s, %s, %s)
        """, (
            "Art 4", author2.id, test_magazine,
            "Art 5", author2.id, test_magazine
        ))
        db_connection.commit()
    
    prolific = Author.most_prolific()
    assert prolific.id == author1.id

    # Create articles
    Article.create("Article 1", "Content", author1.id, 1)
    Article.create("Article 2", "Content", author1.id, 1)
    Article.create("Article 3", "Content", author1.id, 1)
    Article.create("Article 4", "Content", author2.id, 1)

@pytest.fixture
def test_magazine(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO magazines (name, category)
            VALUES ('Tech Today', 'Technology')
            RETURNING id
        """)
        magazine_id = cursor.fetchone()[0]
        db_connection.commit()
    return magazine_id

def test_save_new_author(db_connection):
    """Test saving new author"""
    Author.set_connection(db_connection)
    author = Author(name="Unique Author", email="unique@test.com")
    saved_author = author.save()
    assert saved_author.id is not None

def test_find_by_name():
    """Test name search"""
    Author.set_connection(db_connection)
    Author(name="Search Test", email="search@test.com").save()
    results = Author.find_by_name("search")
    assert len(results) == 1  # Ensure test isolation

def test_author_articles_relationship(db_connection, test_author, test_magazine):
    # Create valid article
    with db_connection.cursor() as cur:
        cur.execute("""
            INSERT INTO articles 
            (title, content, author_id, magazine_id)
            VALUES (%s, %s, %s, %s)
        """, (
            "Valid Article Title",  # 20 characters
            "This is a valid article content that meets the 50 character minimum requirement.",  # 72 chars
            test_author,
            test_magazine
        ))
        db_connection.commit()
    
    # Test relationship
    author = Author.find_by_id(test_author)
    assert len(author.articles()) == 1


    prolific = Author.most_prolific()
    assert prolific.id == author.id