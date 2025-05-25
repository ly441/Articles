
from lib.db.connection import get_connection
from psycopg2 import IntegrityError
from datetime import datetime
from psycopg2.extras import RealDictCursor
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
    
    # === Database Methods ===
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
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