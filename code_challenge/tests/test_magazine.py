
import pytest
import psycopg2
from code_challenge.lib.models.magazine import Magazine
from code_challenge.lib.models.author import Author


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
        conn.commit()
    yield conn
    # Teardown
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS magazines CASCADE")
        cursor.execute("DROP TABLE IF EXISTS authors CASCADE")
        cursor.execute("DROP TABLE IF EXISTS articles CASCADE")
        conn.commit()
    conn.close()

@pytest.fixture(autouse=True)
def clean_db(db_connection):
    """Clean database before each test"""
    with db_connection.cursor() as cursor:
        cursor.execute("TRUNCATE magazines RESTART IDENTITY CASCADE")
        db_connection.commit()

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

def test_save_and_find_by_id():
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

def test_find_by_name_and_category():
    # Setup test data
    Magazine.create("Tech Today", "Technology")
    Magazine.create("Tech Weekly", "Technology")
    Magazine.create("Science News", "Science")

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

def test_most_prolific(db_connection, test_magazine):
    """Test finding most prolific author"""
    
    author1 = Author(name="Author 1", email="author1@test.com").save()
    author2 = Author(name="Author 2", email="author2@test.com").save()
    
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
        

def test_author(db_connection):
    author = Author(name="Test Author", email="test_author@example.com").save()
    return author

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

def test_delete():
    mag = Magazine.create("Fashion Monthly", "Fashion")
    mag_id = mag.id
    assert Magazine.find_by_id(mag_id) is not None
    
    mag.delete()
    assert mag.id is None
    assert Magazine.find_by_id(mag_id) is None

def test_all():
    assert len(Magazine.all()) == 0
    
    Magazine.create("Mag 1", "Cat 1")
    Magazine.create("Mag 2", "Cat 2")
    
    all_mags = Magazine.all()
    assert len(all_mags) == 2
    assert {mag.name for mag in all_mags} == {"Mag 1", "Mag 2"}