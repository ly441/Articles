import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

class Article:
    _connection = None
    
    @classmethod
    def set_connection(cls, connection_params):
        """Set the database connection parameters for all Article instances."""
        cls._connection = connection_params

    def __init__(self, title, content, author_id, magazine_id, id=None):
        self.id = id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.magazine_id = magazine_id
        self._validate()

    def _validate(self):
        """Validate the article attributes."""
        if not isinstance(self.title, str) or len(self.title) == 0:
            raise ValueError("Title must be a non-empty string")
        if len(self.title) > 255:
            raise ValueError("Title must be 255 characters or less")
        if not isinstance(self.content, str) or len(self.content) == 0:
            raise ValueError("Content must be a non-empty string")
        if not isinstance(self.author_id, int) or self.author_id <= 0:
            raise ValueError("Author ID must be a positive integer")
        if not isinstance(self.magazine_id, int) or self.magazine_id <= 0:
            raise ValueError("Magazine ID must be a positive integer")

    def save(self):
        """Save the article to the database."""
        self._validate()
        
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor() as cursor:
                if self.id is None:
                    # Insert new record
                    query = """
                        INSERT INTO articles (title, content, author_id, magazine_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """
                    cursor.execute(query, (self.title, self.content, self.author_id, self.magazine_id))
                    self.id = cursor.fetchone()[0]
                else:
                    # Update existing record
                    query = """
                        UPDATE articles
                        SET title = %s, content = %s, author_id = %s, magazine_id = %s
                        WHERE id = %s
                    """
                    cursor.execute(query, (self.title, self.content, self.author_id, self.magazine_id, self.id))
    
    def delete(self):
        """Delete the article from the database."""
        if self.id is None:
            raise ValueError("Cannot delete an article that hasn't been saved to the database")
            
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor() as cursor:
                query = "DELETE FROM articles WHERE id = %s"
                cursor.execute(query, (self.id,))
                self.id = None

    @classmethod
    def create(cls, title, content, author_id, magazine_id):
        """Create and save a new article."""
        article = cls(title, content, author_id, magazine_id)
        article.save()
        return article

    @classmethod
    def find_by_id(cls, id):
        """Find an article by its ID."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = "SELECT * FROM articles WHERE id = %s"
                cursor.execute(query, (id,))
                result = cursor.fetchone()
                if result:
                    return cls(
                        result['title'],
                        result['content'],
                        result['author_id'],
                        result['magazine_id'],
                        result['id']
                    )
                return None

    @classmethod
    def find_by_title(cls, title):
        """Find articles by title (case-insensitive partial match)."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = "SELECT * FROM articles WHERE LOWER(title) LIKE LOWER(%s)"
                cursor.execute(query, (f"%{title.lower()}%",))
                return [
                    cls(
                        row['title'],
                        row['content'],
                        row['author_id'],
                        row['magazine_id'],
                        row['id']
                    ) for row in cursor.fetchall()
                ]

    @classmethod
    def find_by_author(cls, author_id):
        """Find articles by author ID."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = "SELECT * FROM articles WHERE author_id = %s"
                cursor.execute(query, (author_id,))
                return [
                    cls(
                        row['title'],
                        row['content'],
                        row['author_id'],
                        row['magazine_id'],
                        row['id']
                    ) for row in cursor.fetchall()
                ]

    @classmethod
    def find_by_magazine(cls, magazine_id):
        """Find articles by magazine ID."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = "SELECT * FROM articles WHERE magazine_id = %s"
                cursor.execute(query, (magazine_id,))
                return [
                    cls(
                        row['title'],
                        row['content'],
                        row['author_id'],
                        row['magazine_id'],
                        row['id']
                    ) for row in cursor.fetchall()
                ]

    @classmethod
    def all(cls):
        """Get all articles from the database."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM articles")
                return [
                    cls(
                        row['title'],
                        row['content'],
                        row['author_id'],
                        row['magazine_id'],
                        row['id']
                    ) for row in cursor.fetchall()
                ]

    def get_author(self):
        """Get the author of this article."""
        from author import Author  # Avoid circular imports
        return Author.find_by_id(self.author_id)

    def get_magazine(self):
        """Get the magazine this article belongs to."""
        from magazine import Magazine  # Avoid circular imports
        return Magazine.find_by_id(self.magazine_id)

    def __repr__(self):
        return f"<Article id={self.id} title='{self.title}' author_id={self.author_id} magazine_id={self.magazine_id}>"