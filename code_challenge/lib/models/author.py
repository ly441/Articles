
import psycopg2
from psycopg2 import IntegrityError
from psycopg2.extras import DictCursor
from datetime import datetime


class Author:
    _connection = {
        "dbname": "articles_challenge",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432
    }

    def __init__(self, name, email, bio=None, id=None, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.bio = bio
        self.created_at = created_at

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', email='{self.email}')>"

    @classmethod
    def set_connection(cls, conn_params):
        if isinstance(conn_params, dict):
            cls._connection = conn_params
        else:
            raise ValueError("Connection must be a dict of parameters")

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

    def save(self):
        """Save the author to the database"""
        conn = psycopg2.connect(**self._connection)
        cursor = conn.cursor()
        
        try:
            if self.id is None:  # New author
                cursor.execute(
                    """
                    INSERT INTO authors (name, email, bio, created_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, created_at;
                    """,
                    (self.name, self.email, self.bio, self.created_at or datetime.utcnow())
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
        except IntegrityError:
            conn.rollback()
            raise ValueError("Email already exists in database")
        finally:
            conn.close()
        
        return self

    # === Query Methods ===
    @classmethod
    def find_by_id(cls, author_id):
        """Find author by ID"""
        conn = psycopg2.connect(**cls._connection)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute("SELECT * FROM authors WHERE id = %s;", (author_id,))
        result = cursor.fetchone()
        conn.close()
        
        return cls._create_from_db(result) if result else None

    @classmethod
    def find_by_name(cls, name):
        """Find authors by name (case-insensitive partial match)"""
        conn = psycopg2.connect(**cls._connection)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute("SELECT * FROM authors WHERE name ILIKE %s;", (f"%{name}%",))
        results = cursor.fetchall()
        conn.close()
        
        return [cls._create_from_db(row) for row in results]

    # === Relationship Methods ===
    def articles(self):
        """Get all articles by this author"""
        from .article import Article  # Avoid circular imports
        
        conn = psycopg2.connect(**self._connection)
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

    def magazines(self):
        """Find all magazines this author has contributed to"""
        from .magazine import Magazine  # Avoid circular imports
        
        conn = psycopg2.connect(**self._connection)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute(
            """
            SELECT DISTINCT m.* FROM magazines m
            JOIN articles a ON m.id = a.magazine_id
            WHERE a.author_id = %s
            """,
            (self.id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [Magazine._create_from_db(row) for row in results]

    @classmethod
    def most_prolific(cls):
        """Find the author with the most articles"""
        conn = psycopg2.connect(**cls._connection)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute(
            """
            SELECT author_id, COUNT(*) as article_count
            FROM articles
            GROUP BY author_id
            ORDER BY article_count DESC
            LIMIT 1
            """
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return cls.find_by_id(result['author_id'])
        return None

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
        
    @classmethod
    def get_all(cls):
        conn = psycopg2.connect(**cls._connection)
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT * FROM authors")
        authors = cursor.fetchall()
        conn.close()
        return [cls._create_from_db(row) for row in authors]

    @classmethod
    def add_author(cls, name, email, bio=None):
        """Add a new author to the database and return the author with their assigned ID"""
        new_author = cls(name=name, email=email, bio=bio)
        saved_author = new_author.save()
        return saved_author