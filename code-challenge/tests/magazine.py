import unittest
import psycopg2
from magazine import Magazine

class TestMagazine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up test database connection
        cls.connection_params = {
            "dbname": "test_magazine_db",
            "user": "your_username",
            "password": "your_password",
            "host": "localhost"
        }
        Magazine.set_connection(cls.connection_params)
        
        # Create test tables
        with psycopg2.connect(**cls.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS magazines (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        category VARCHAR(50) NOT NULL
                    )
                """)
                conn.commit()

    def setUp(self):
        # Clear magazines table before each test
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE magazines RESTART IDENTITY CASCADE")
                conn.commit()

    def test_initialization_and_validation(self):
        # Test valid initialization
        mag = Magazine("Tech Today", "Technology")
        self.assertEqual(mag.name, "Tech Today")
        self.assertEqual(mag.category, "Technology")
        
        # Test invalid name
        with self.assertRaises(ValueError):
            Magazine("", "Technology")
        with self.assertRaises(ValueError):
            Magazine(None, "Technology")
        with self.assertRaises(ValueError):
            Magazine("A" * 101, "Technology")
            
        # Test invalid category
        with self.assertRaises(ValueError):
            Magazine("Tech Today", "")
        with self.assertRaises(ValueError):
            Magazine("Tech Today", None)
        with self.assertRaises(ValueError):
            Magazine("Tech Today", "A" * 51)

    def test_save_and_find_by_id(self):
        # Test save new magazine
        mag = Magazine("Science Weekly", "Science")
        mag.save()
        self.assertIsNotNone(mag.id)
        
        # Test find by id
        found_mag = Magazine.find_by_id(mag.id)
        self.assertEqual(found_mag.name, "Science Weekly")
        self.assertEqual(found_mag.category, "Science")
        self.assertEqual(found_mag.id, mag.id)
        
        # Test update
        mag.name = "Science Monthly"
        mag.save()
        updated_mag = Magazine.find_by_id(mag.id)
        self.assertEqual(updated_mag.name, "Science Monthly")

    def test_find_by_name_and_category(self):
        # Create test data
        Magazine.create("Tech Today", "Technology")
        Magazine.create("Tech Weekly", "Technology")
        Magazine.create("Science News", "Science")
        
        # Test find by name
        tech_mags = Magazine.find_by_name("tech")
        self.assertEqual(len(tech_mags), 2)
        self.assertTrue(all("Tech" in mag.name for mag in tech_mags))
        
        # Test find by category
        tech_category = Magazine.find_by_category("Technology")
        self.assertEqual(len(tech_category), 2)
        self.assertTrue(all(mag.category == "Technology" for mag in tech_category))

    def test_delete(self):
        mag = Magazine.create("Fashion Monthly", "Fashion")
        mag_id = mag.id
        self.assertIsNotNone(Magazine.find_by_id(mag_id))
        
        mag.delete()
        self.assertIsNone(mag.id)
        self.assertIsNone(Magazine.find_by_id(mag_id))

    def test_all(self):
        self.assertEqual(len(Magazine.all()), 0)
        
        Magazine.create("Mag 1", "Cat 1")
        Magazine.create("Mag 2", "Cat 2")
        
        all_mags = Magazine.all()
        self.assertEqual(len(all_mags), 2)
        self.assertEqual({mag.name for mag in all_mags}, {"Mag 1", "Mag 2"})

    @classmethod
    def tearDownClass(cls):
        # Clean up test database
        with psycopg2.connect(**cls.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS magazines CASCADE")
                conn.commit()

if __name__ == "__main__":
    unittest.main()