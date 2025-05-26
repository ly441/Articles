import unittest
import psycopg2
from code_challenge.tests.test_article import Article

class TestArticle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up test database connection
        cls.connection_params = {
            "dbname": "test_db",
            "user": "postgres",
            "password": "yourpassword",
            "host": "localhost"
        }
        Article.set_connection(cls.connection_params)
        
        # Create test tables
        with psycopg2.connect(**cls.connection_params) as conn:
            with conn.cursor() as cursor:
                # Create authors table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS authors (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        bio TEXT
                    )
                """)
                # Create magazines table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS magazines (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        category VARCHAR(50) NOT NULL
                    )
                """)
                # Create articles table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        content TEXT NOT NULL,
                        author_id INTEGER REFERENCES authors(id),
                        magazine_id INTEGER REFERENCES magazines(id)
                    )
                """)
                conn.commit()

    def setUp(self):
        # Clear and seed test data
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE authors, magazines, articles RESTART IDENTITY CASCADE")
                
                # Insert test author
                cursor.execute("""
                    INSERT INTO authors (name, bio)
                    VALUES ('Test Author', 'Test Bio')
                    RETURNING id
                """)
                self.author_id = cursor.fetchone()[0]
                
                # Insert test magazine
                cursor.execute("""
                    INSERT INTO magazines (name, category)
                    VALUES ('Test Magazine', 'Test Category')
                    RETURNING id
                """)
                self.magazine_id = cursor.fetchone()[0]
                
                conn.commit()

    def test_article_creation(self):
        article = Article(
            title="Test Article",
            content="Test Content",
            author_id=self.author_id,
            magazine_id=self.magazine_id
        )
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.author_id, self.author_id)

    def test_save_and_retrieve(self):
        article = Article(
            title="Save Test",
            content="Content",
            author_id=self.author_id,
            magazine_id=self.magazine_id
        )
        article.save()
        
        retrieved = Article.find_by_id(article.id)
        self.assertEqual(retrieved.title, "Save Test")
        self.assertEqual(retrieved.author_id, self.author_id)

    def test_find_by_title(self):
        Article.create(
            title="Unique Title 123",
            content="Content",
            author_id=self.author_id,
            magazine_id=self.magazine_id
        )
        
        results = Article.find_by_title("unique")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Unique Title 123")

    def test_find_by_author(self):
        Article.create(
            title="Author Test",
            content="Content",
            author_id=self.author_id,
            magazine_id=self.magazine_id
        )
        
        results = Article.find_by_author(self.author_id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Author Test")

    def test_find_by_magazine(self):
        Article.create(
            title="Magazine Test",
            content="Content",
            author_id=self.author_id,
            magazine_id=self.magazine_id
        )
        
        results = Article.find_by_magazine(self.magazine_id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Magazine Test")

    def test_article_update(self):
        article = Article.create(
            title="Original Title",
            content="Content",
            author_id=self.author_id,
            magazine_id=self.magazine_id
        )
        
        article.title = "Updated Title"
        article.save()
        
        updated = Article.find_by_id(article.id)
        self.assertEqual(updated.title, "Updated Title")

    def test_article_delete(self):
        article = Article.create(
            title="To Delete",
            content="Content",
            author_id=self.author_id,
            magazine_id=self.magazine_id
        )
        
        article.delete()
        self.assertIsNone(Article.find_by_id(article.id))

    def test_validation(self):
        with self.assertRaises(ValueError):
            Article("", "Content", self.author_id, self.magazine_id)
        
        with self.assertRaises(ValueError):
            Article("Title", "", self.author_id, self.magazine_id)
            
        with self.assertRaises(ValueError):
            Article("Title", "Content", 0, self.magazine_id)
            
        with self.assertRaises(ValueError):
            Article("Title", "Content", self.author_id, 0)

    @classmethod
    def tearDownClass(cls):
        # Clean up test database
        with psycopg2.connect(**cls.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS articles, authors, magazines CASCADE")
                conn.commit()

if __name__ == "__main__":
    unittest.main()