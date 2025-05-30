# config.py
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
database_url = urlparse(os.getenv("postgresql://postgres:postgres@localhost:5432/articles.db"))
db_config = {
    "dbname": os.getenv("DB_NAME", "articles_challenge"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "mysecretpassword"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432)
}