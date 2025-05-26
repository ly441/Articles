
import pytest
import psycopg2
from code_challenge.lib.models.magazine import Magazine

# Fixtures
@pytest.fixture(scope="module")
def db_connection():
    """Module-scoped database connection and setup"""
    connection_params = {
        "dbname": "test_magazine_db",
        "user": "your_username",
        "password": "your_password",
        "host": "localhost"
    }
    Magazine.set_connection(connection_params)
    
    # Create tables
    conn = psycopg2.connect(**connection_params)
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS magazines (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL
            )
        """)
        conn.commit()
    yield conn
    # Teardown
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS magazines CASCADE")
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
    
    # Test name search
    tech_mags = Magazine.find_by_name("tech")
    assert len(tech_mags) == 2
    assert all("Tech" in mag.name for mag in tech_mags)
    
    # Test category search
    tech_category = Magazine.find_by_category("Technology")
    assert len(tech_category) == 2
    assert all(mag.category == "Technology" for mag in tech_category)

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