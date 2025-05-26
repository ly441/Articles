import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

class Magazine:
    _connection = None
    
    @classmethod
    def set_connection(cls, connection_params):
        """Set the database connection parameters for all Magazine instances."""
        cls._connection = connection_params

    def __init__(self, name, category, id=None):
        self.id = id
        self.name = name
        self.category = category
        self._validate()

    def _validate(self):
        """Validate the magazine attributes."""
        if not isinstance(self.name, str) or len(self.name) == 0:
            raise ValueError("Name must be a non-empty string")
        if len(self.name) > 100:
            raise ValueError("Name must be 100 characters or less")
        if not isinstance(self.category, str) or len(self.category) == 0:
            raise ValueError("Category must be a non-empty string")
        if len(self.category) > 50:
            raise ValueError("Category must be 50 characters or less")

    def save(self):
        """Save the magazine to the database."""
        self._validate()
        
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor() as cursor:
                if self.id is None:
                    # Insert new record
                    query = sql.SQL("""
                        INSERT INTO magazines (name, category)
                        VALUES (%s, %s)
                        RETURNING id
                    """)
                    cursor.execute(query, (self.name, self.category))
                    self.id = cursor.fetchone()[0]
                else:
                    # Update existing record
                    query = sql.SQL("""
                        UPDATE magazines
                        SET name = %s, category = %s
                        WHERE id = %s
                    """)
                    cursor.execute(query, (self.name, self.category, self.id))
    
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
    def create(cls, name, category):
        """Create and save a new magazine."""
        magazine = cls(name, category)
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
                    return cls(result['name'], result['category'], result['id'])
                return None

    @classmethod
    def find_by_name(cls, name):
        """Find magazines by name (case-insensitive partial match)."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("SELECT * FROM magazines WHERE LOWER(name) LIKE LOWER(%s)")
                cursor.execute(query, (f"%{name.lower()}%",))
                return [cls(row['name'], row['category'], row['id']) for row in cursor.fetchall()]

    @classmethod
    def find_by_category(cls, category):
        """Find magazines by exact category match."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("SELECT * FROM magazines WHERE category = %s")
                cursor.execute(query, (category,))
                return [cls(row['name'], row['category'], row['id']) for row in cursor.fetchall()]

    @classmethod
    def all(cls):
        """Get all magazines from the database."""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("SELECT * FROM magazines")
                cursor.execute(query)
                return [cls(row['name'], row['category'], row['id']) for row in cursor.fetchall()]

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
        return f"<Magazine id={self.id} name='{self.name}' category='{self.category}'>"
    def authors(self):
        """Get all authors who have written for this magazine"""
        from author import Author
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT a.* FROM authors a
                    JOIN articles ar ON a.id = ar.author_id
                    WHERE ar.magazine_id = %s
                """, (self.id,))
                return [Author(
                    row['name'],
                    row['bio'],
                    row['id']
                ) for row in cursor.fetchall()]

    @classmethod
    def find_with_multiple_authors(cls):
        """Find magazines with articles by at least 2 different authors"""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT m.* FROM magazines m
                    JOIN articles a ON m.id = a.magazine_id
                    GROUP BY m.id
                    HAVING COUNT(DISTINCT a.author_id) >= 2
                """)
                return [cls(
                    row['name'],
                    row['category'],
                    row['id']
                ) for row in cursor.fetchall()]

    def article_count(self):
        """Count the number of articles in this magazine"""
        with psycopg2.connect(**self._connection) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM articles
                    WHERE magazine_id = %s
                """, (self.id,))
                return cursor.fetchone()[0]

    @classmethod
    def all_article_counts(cls):
        """Count of articles in each magazine"""
        with psycopg2.connect(**cls._connection) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT m.id, m.name, COUNT(a.id) as article_count
                    FROM magazines m
                    LEFT JOIN articles a ON m.id = a.magazine_id
                    GROUP BY m.id
                """)
                return {row[1]: row[2] for row in cursor.fetchall()}

    