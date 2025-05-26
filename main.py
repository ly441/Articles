
from lib.db.connection import get_connection
from code_challenge.lib.models.magazine import Magazine
from code_challenge.lib.models.article import Article
from code_challenge.lib.models.author import Author
# Test database connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT NOW() as current_time;")
print(cursor.fetchone()) 
conn.close()

# Set up database connection
Magazine.set_connection({
    "dbname": "articles.db",
    "user": "postgress",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
})

# Create a new magazine
tech_mag = Magazine.create("Tech Insights", "Technology")

# Find a magazine by ID
found_mag = Magazine.find_by_id(tech_mag.id)
print(found_mag)  # <Magazine id=1 name='Tech Insights' category='Technology'>

# Find magazines by category
tech_mags = Magazine.find_by_category("Technology")
for mag in tech_mags:
    print(mag.name)

# Update a magazine
tech_mag.name = "Tech Insights Monthly"
tech_mag.save()

# Get all magazines
all_mags = Magazine.all()
print(f"Total magazines: {len(all_mags)}")

# Delete a magazine
tech_mag.delete()

# Set up database connection
Article.set_connection({
    "dbname": "articles.db",
    "user": "postgress",
    "password": "posgres",
    "host": "localhost",
    "port": 5432
})
Magazine.set_connection({
    "dbname": "articles.db",
    "user": "postgress",
    "password": "posgres",
    "host": "localhost",
    "port": 5432
})
Author.set_connection({
    "dbname": "articles.db",
    "user": "postgress",
    "password": "posgres",
    "host": "localhost",
    "port": 5432
})

# Create author and magazine
author = Author.create("lemayian olekolii", "Tech journalist","Violeta Kioki","motivation and inspiration")
magazine = Magazine.create("Tech Insights", "Technology","inspiration and motivation","emotional intelligence")

# Create a new article
article = Article.create(
    "The Future of AI",
    "Exploring the latest trends in artificial intelligence...",
    author.id,
    magazine.id
)

# Find articles by title
ai_articles = Article.find_by_title("AI")
for art in ai_articles:
    print(f"{art.title} by {art.author().name} in {art.magazine().name}")

# Update an article
article.title = "The Future of Artificial Intelligence"
article.save()

# Get all articles in a magazine
magazine_articles = Article.find_by_magazine_id(magazine.id)
print(f"Articles in {magazine.name}: {len(magazine_articles)}")

# Delete an article
article.delete()
# Configure database connection
db_config = {
    "dbname": "articles.db",
    "user": "postgress",
    "password": "space",
    "host": "localhost"
}

# Set connection for all classes
Article.set_connection(db_config)

# Create a new article
new_article = Article.create(
    title="Python Programming",
    content="All about Python...",
    author_id=1,  # Existing author ID
    magazine_id=1  # Existing magazine ID
)

# Find articles by title
python_articles = Article.find_by_title("python")
for article in python_articles:
    print(f"Found: {article.title}")

# Update an article
article = Article.find_by_id(1)
article.title = "Advanced Python Programming"
article.save()

# Delete an article
article.delete()

# Example usage
author = Author.find_by_id(1)
magazine = Magazine.find_by_id(1)

# Get author's topic areas
print(f"Author specializes in: {', '.join(author.topic_areas())}")

# Add new article
new_article = author.add_article(
    magazine=magazine,
    title="New Research Findings",
    content="Detailed analysis..."
)

# Get magazine statistics
print(f"Magazine titles: {magazine.article_titles()}")
print(f"Top contributors: {magazine.contributing_authors()}")