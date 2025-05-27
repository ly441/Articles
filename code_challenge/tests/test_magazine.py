
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from code_challenge.lib.models.magazine import Magazine
from code_challenge.lib.models.author import Author
from code_challenge.lib.models.article import Article

# Fixtures
@pytest.fixture(scope="module")
def db_connection():
    """Module-scoped database connection and setup"""
    connection_params = {
        "dbname": "test_magazine_db",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432
    }
    Magazine.set_connection(connection_params)
    
    # Create tables
    conn = psycopg2.connect(**connection_params)
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS magazines (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                bio TEXT
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
        print("Test database structure created")
    yield conn
    # Teardown
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS articles CASCADE")
        cursor.execute("DROP TABLE IF EXISTS authors CASCADE")
        cursor.execute("DROP TABLE IF EXISTS magazines CASCADE")
        conn.commit()
    conn.close()
    print("Test database structure dropped")
    


@pytest.fixture
def test_author(db_connection):
    """Fixture providing a test author"""
    author = Author(name="Test Author", email="test@example.com").save()
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

# Tests
def test_initialization_and_validation():
    # Valid initialization
    mag = Magazine("Tech Today", "Technology")
    assert mag.name == "Tech Today"
    assert mag.category == "Technology"
    
    # Invalid name tests
    with pytest.raises(ValueError):
        Magazine("", "Technology")
    with pytest.raises(ValueError):
        Magazine(None, "Technology")
    with pytest.raises(ValueError):
        Magazine("A" * 101, "Technology")
    
    # Invalid category tests
    with pytest.raises(ValueError):
        Magazine("Tech Today", "")
    with pytest.raises(ValueError):
        Magazine("Tech Today", None)
    with pytest.raises(ValueError):
        Magazine("Tech Today", "A" * 51)

def test_save_and_find_by_id(db_connection):
    # Create and save
    mag = Magazine("Science Weekly", "Science")
    mag.save()
    assert mag.id is not None
    
    # Find by ID
    found_mag = Magazine.find_by_id(mag.id)
    assert found_mag.name == "Science Weekly"
    assert found_mag.category == "Science"
    assert found_mag.id == mag.id
    
    # Update and verify
    mag.name = "Science Monthly"
    mag.save()
    updated_mag = Magazine.find_by_id(mag.id)
    assert updated_mag.name == "Science Monthly"

def test_find_by_name_and_category(db_connection):
    # Setup test data
    Magazine.create("Tech Today", "Technology")
    Magazine.create("Tech Weekly", "Technology")
    Magazine.create("Science News", "Science")







def test_author(db_connection):
    author = Author(name="Test Author", email="test_author@example.com").save()
    assert author.id is not None
    return author

@pytest.fixture
def test_author(db_connection):
    """Fixture providing a test author"""
    author = Author(name="Test Author", email="test@example.com").save()
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


def test_delete(db_connection):
    mag = Magazine.create("Fashion Monthly", "Fashion")
    mag_id = mag.id
    assert Magazine.find_by_id(mag_id) is not None
    
    mag.delete()
    assert mag.id is None
    assert Magazine.find_by_id(mag_id) is None



