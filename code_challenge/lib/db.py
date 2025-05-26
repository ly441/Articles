# db.py
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from code_challenge.config import db_config

class Transaction:
    def __init__(self):
        self.conn = psycopg2.connect(**db_config)
        self.cursor = self.conn.cursor()
        
    def __enter__(self):
        self.conn.autocommit = False
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()

def add_author_with_articles(author_name, bio, articles_data):
    """
    Add an author and their articles in a single transaction
    articles_data: list of dicts with 'title', 'content', and 'magazine_id'
    """
    try:
        with Transaction() as cursor:
            # Insert author
            cursor.execute(
                """INSERT INTO authors (name, bio) 
                VALUES (%s, %s) RETURNING id""",
                (author_name, bio)
            )
            author_id = cursor.fetchone()[0]
            
            # Insert articles
            for article in articles_data:
                cursor.execute(
                    """INSERT INTO articles 
                    (title, content, author_id, magazine_id)
                    VALUES (%s, %s, %s, %s)""",
                    (article['title'], article['content'], 
                     author_id, article['magazine_id'])
                )
        return True
    except Exception as e:
        print(f"Transaction failed: {str(e)}")
        return False