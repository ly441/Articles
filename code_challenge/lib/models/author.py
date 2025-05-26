
import psycopg2
from psycopg2 import IntegrityError
from datetime import datetime
from psycopg2.extras import DictCursor
from datetime import datetime
import os

class Author:
    def __init__(self, name, email, bio=None, id=None):
        self.id = id
        self.name = name
        self.email = email
        self.bio = bio
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    # === Validations ===
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        self._name = value.strip()
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format")
        self._email = value.lower().strip()
    
    @property
    def save(self):
        """Save the author to the database"""
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "articles_challenge"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost")
        )
        cursor = conn.cursor()
        
        try:
            if self.id is None:  # New author
                cursor.execute(
                    """
                    INSERT INTO authors (name, email, bio, created_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, created_at;
                    """,
                    (self.name, self.email, self.bio, self.created_at)
                )
                result = cursor.fetchone()
                self.id = result[0]
                self.created_at = result[1]
            else:  # Update existing
                cursor.execute(
                    """
                    UPDATE authors 
                    SET name = %s, email = %s, bio = %s
                    WHERE id = %s;
                    """,
                    (self.name, self.email, self.bio, self.id)
                )
            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
            raise ValueError("Email already exists in database")
        finally:
            conn.close()
        
        return self
    
    # === Query Methods ===
    @classmethod
    def find_by_id(cls, author_id):
        """Find author by ID"""
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "articles_challenge"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost")
        )
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute("SELECT * FROM authors WHERE id = %s;", (author_id,))
        result = cursor.fetchone()
        conn.close()
        
        return cls._create_from_db(result) if result else None
    
    @classmethod
    def find_by_name(cls, name):
        """Find authors by name (case-insensitive partial match)"""
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "articles_challenge"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost")
        )
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute("SELECT * FROM authors WHERE name ILIKE %s;", (f"%{name}%",))
        results = cursor.fetchall()
        conn.close()
        
        return [cls._create_from_db(row) for row in results]
    
    # === Relationship Methods ===
    def articles(self):
        """Get all articles by this author"""
        from .article import Article  # Avoid circular imports
        
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "articles_challenge"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost")
        )
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute(
            """
            SELECT * FROM articles 
            WHERE author_id = %s
            ORDER BY published_at DESC;
            """,
            (self.id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [Article._create_from_db(row) for row in results]
    
    # === Utility Methods ===
    @classmethod
    def _create_from_db(cls, db_row):
        """Create Author instance from database row"""
        return cls(
            id=db_row['id'],
            name=db_row['name'],
            email=db_row['email'],
            bio=db_row['bio'],
            created_at=db_row.get('created_at')
        )
    
    def to_dict(self):
        """Convert author to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    
    def articles(self):
        """Get all articles written by this author"""
        from article import Article
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM articles
                    WHERE author_id = %s
                """, (self.id,))
                return [Article(
                    row['title'],
                    row['content'],
                    row['author_id'],
                    row['magazine_id'],
                    row['id']
                ) for row in cursor.fetchall()]

    def magazines(self):
        """Find all magazines this author has contributed to"""
        from magazine import Magazine
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT m.* FROM magazines m
                    JOIN articles a ON m.id = a.magazine_id
                    WHERE a.author_id = %s
                """, (self.id,))
                return [Magazine(
                    row['name'],
                    row['category'],
                    row['id']
                ) for row in cursor.fetchall()]

    @classmethod
    def most_prolific(cls):
        """Find the author with the most articles"""
        from article import Article
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT author_id, COUNT(*) as article_count
                    FROM articles
                    GROUP BY author_id
                    ORDER BY article_count DESC
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    return cls.find_by_id(result['author_id'])
                return None
    def add_article(self,magazine,title):
        """Add an articles to this author"""
        from article import Article
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO articles (title, author_id, magazine_id)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """, (title, self.id, magazine.id))
                article_id = cursor.fetchone()[0]
                conn.commit()
                return Article(title=title, author_id=self.id, magazine_id=magazine.id, id=article_id)   
    @classmethod
    def topic_areas(self):
        """Get all unique topic areas from authors' bios"""
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT bio FROM authors
                    WHERE bio IS NOT NULL AND bio != '';
                """)
                bios = cursor.fetchall()
                topics = set()
                for bio in bios:
                    if bio[0]:
                        topics.update(bio[0].split(','))
                return [topic.strip() for topic in topics if topic.strip()]
            
def __repr__(self):
    return f"<Author {self.id}: {self.name}>"

