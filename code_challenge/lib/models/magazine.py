
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

class Magazine:
    _connection = None
    
    @classmethod
    def set_connection(cls, conn_params):
        if isinstance(conn_params, dict):
            cls._connection = conn_params
        else:
            raise ValueError("Connection must be a dict of parameters")
    
    def __init__(self, name, category, description=None, id=None):
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self._validate()

    def _validate(self):
        """Validate the magazine attributes."""
        if not isinstance(self.name, str) or len(self.name) == 0:
            raise ValueError("Name must be a non-empty string")
        if len(self.name) > 255:
            raise ValueError("Name must be 255 characters or less")
        if not isinstance(self.category, str) or len(self.category) == 0:
            raise ValueError("Category must be a non-empty string")
        if len(self.category) > 255:
            raise ValueError("Category must be 255 characters or less")
        if self.description is not None and not isinstance(self.description, str):
            raise ValueError("Description must be a string or None")

    def save(self):
        """Save the magazine to the database."""
        self._validate()
        
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor() as cursor:
                if self.id is None:
                    # Insert new record
                    query = sql.SQL("""
                        INSERT INTO magazines (name, category, description)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """)
                    cursor.execute(query, (self.name, self.category, self.description))
                    self.id = cursor.fetchone()[0]
                else:
                    # Update existing record
                    query = sql.SQL("""
                        UPDATE magazines
                        SET name = %s, category = %s, description = %s
                        WHERE id = %s
                    """)
                    cursor.execute(query, (self.name, self.category, self.description, self.id))
    
    def delete(self):
        """Delete the magazine from the database."""
        if self.id is None:
            raise ValueError("Cannot delete a magazine that hasn't been saved to the database")
            
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor() as cursor:
                query = sql.SQL("DELETE FROM magazines WHERE id = %s")
                cursor.execute(query, (self.id,))
                self.id = None

    @classmethod
    def create(cls, name, category, description=None):
        """Create and save a new magazine."""
        magazine = cls(name, category, description)
        magazine.save()
        return magazine

    @classmethod
    def find_by_id(cls, id):
        """Find a magazine by its ID."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("SELECT * FROM magazines WHERE id = %s")
                cursor.execute(query, (id,))
                result = cursor.fetchone()
                if result:
                    return cls(result['name'], result['category'], result['description'], result['id'])
                return None

    @classmethod
    def find_by_name(cls, name):
        """Find magazines by name (case-insensitive partial match)."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("SELECT * FROM magazines WHERE LOWER(name) LIKE LOWER(%s)")
                cursor.execute(query, (f"%{name.lower()}%",))
                return [cls(row['name'], row['category'], row['description'], row['id']) for row in cursor.fetchall()]

    @classmethod
    def find_by_category(cls, category):
        """Find magazines by exact category match."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("SELECT * FROM magazines WHERE category = %s")
                cursor.execute(query, (category,))
                return [cls(row['name'], row['category'], row['description'], row['id']) for row in cursor.fetchall()]

    @classmethod
    def get_all(cls):
        """Get all magazines from the database."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("SELECT * FROM magazines")
                cursor.execute(query)
                return [cls(row['name'], row['category'], row['description'], row['id']) for row in cursor.fetchall()]

    @classmethod
    def top_publisher(cls):
        """Find the magazine with the most articles."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("""
                    SELECT magazine_id, COUNT(*) as article_count
                    FROM articles
                    GROUP BY magazine_id
                    ORDER BY article_count DESC
                    LIMIT 1
                """)
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    return cls.find_by_id(result['magazine_id'])
                return None

    def articles(self):
        """Get all articles associated with this magazine."""
        from article import Article  # Avoid circular imports
        return Article.find_by_magazine_id(self.id)

    def contributors(self):
        """Get all authors who have written for this magazine."""
        from author import Author  # Avoid circular imports
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("""
                    SELECT DISTINCT authors.* 
                    FROM authors
                    JOIN articles ON authors.id = articles.author_id
                    WHERE articles.magazine_id = %s
                """)
                cursor.execute(query, (self.id,))
                return [Author(row['name'], row['bio'], row['id']) for row in cursor.fetchall()]
            
    def __repr__(self):
        return f"<Magazine id={self.id} name='{self.name}' category='{self.category}' description='{self.description}'>"