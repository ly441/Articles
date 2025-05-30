
from code_challenge.lib.models.author import Author
from code_challenge.lib.models.magazine import Magazine
from code_challenge.lib.models.article import Article
from code_challenge.lib.controllers.db import add_author_with_articles
from code_challenge.lib.controllers.config import db_config
from code_challenge.lib.db.connection import get_connection
# Set the database connection parameters
Magazine.set_connection(db_config)
Author.set_connection(db_config)
Article.set_connection(db_config)
print(db_config)
Magazine.set_connection({
    "dbname": "articles_challenge",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
})
Author.set_connection({
    "dbname": "articles_challenge",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
})
Article.set_connection({
    "dbname": "articles_challenge",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
})


def cli():
    print("📚 Magazine Database CLI") 
    while True:
        print("\n1. Add author with articles")
        print("2. Find top publisher")
        print("3. Search articles by author")
        print("4. List all authors and their articles")
        print("5. Add magazine")
        print("6. List all magazines")
        print("7. Update magazine")
        print("8. Delete magazine")
        print("9. Add author")
        print("10. List all authors")
        print("11. Update author")
        print("12. Delete author")
        print("13. Add article")
        print("14. List all articles")
        print("15. Update article")
        print("16. Delete article")
        print("17. Exit")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            name = input("Author name: ").strip()
            bio = input("Author bio: ").strip()
            articles = []
            
            while True:
                title = input("Article title (q to finish): ").strip()
                if title.lower() == 'q':
                    break
                if any(a['title'].lower() == title.lower() for a in articles):
                    print("⚠️ Article with this title already added.")
                    continue
                content = input("Article content: ").strip()
                magazine_id = input("Magazine ID: ").strip()
                
                articles.append({
                    'title': title,
                    'content': content,
                    'magazine_id': magazine_id
                })
                print(f"✅ Added article: {title}")
            
            if add_author_with_articles(name, bio, articles):
                print("✅ Author and articles added successfully!")
            else:
                print("❌ Failed to add author and articles.")
        
        elif choice == "2":
            top_mag = Magazine.top_publisher()
            if top_mag:
                print(f"🏆 Top publisher: {top_mag.name}")
            else:
                print("No magazines found.")
        
        elif choice == "3":
            author_id = input("Author ID: ").strip()
            author = Author.find_by_id(author_id)
            if author:
                print(f"\n📝 Articles by {author.name}:")
                for article in author.articles():
                    mag = Magazine.find_by_id(article.magazine_id)
                    mag_name = mag.name if mag else "Unknown Magazine"
                    print(f"- {article.title} in {mag_name}")
            else:
                print("❌ Author not found.")
        
        elif choice == "4":
            authors = Author.get_all()
            if not authors:
                print("❌ No authors found.")
            else:
                for author in authors:
                    print(f"\n👤 {author.name} (ID: {author.id})")
                    articles = author.articles()
                    if not articles:
                        print("   - 📄 No articles found.")
                    else:
                        for article in articles:
                            print(f"   - 📄 {article.title}")
        
        elif choice == "5":
            name = input("Magazine name: ").strip()
            category = input("Magazine category: ").strip()
            description = input("Magazine description: ").strip()
            new_magazine = Magazine(name=name, category=category, description=description)
            new_magazine.save()
            print("✅ Magazine added successfully!")
        
        elif choice == "6":
            magazines = Magazine.get_all()
            if not magazines:
                print("❌ No magazines found.")
            else:
                for magazine in magazines:
                    print(f"\n📰 {magazine.name} (ID: {magazine.id})")
                    print(f"   - Category: {magazine.category}")
                    print(f"   - Description: {magazine.description}")
        
        elif choice == "7":
            mag_id = input("Magazine ID: ").strip()
            name = input("New magazine name: ").strip()
            description = input("New magazine description: ").strip()
            magazine = Magazine.find_by_id(mag_id)
            if magazine:
                magazine.name = name
                magazine.description = description
                magazine.save()
                print("✅ Magazine updated successfully!")
            else:
                print("❌ Magazine not found.")
        
        elif choice == "8":
            mag_id = input("Magazine ID: ").strip()
            magazine = Magazine.find_by_id(mag_id)
            if magazine:
                magazine.delete()
                print("✅ Magazine deleted successfully!")
            else:
                print("❌ Magazine not found.")
        
        elif choice == "9":
            name = input("Author name: ").strip()
            email = input("Author email: ").strip()
            bio = input("Author bio: ").strip()
            new_author = Author(name=name, email=email, bio=bio)
            new_author.save()
            print("✅ Author added successfully!")
        
        elif choice == "10":
            authors = Author.get_all()
            if not authors:
                print("❌ No authors found.")
            else:
                for author in authors:
                    print(f"\n👤 {author.name} (ID: {author.id})")
                    print(f"   - Email: {author.email}")
                    print(f"   - Bio: {author.bio}")
        
        elif choice == "11":
            author_id = input("Author ID: ").strip()
            name = input("New author name: ").strip()
            email = input("New author email: ").strip()
            bio = input("New author bio: ").strip()
            author = Author.find_by_id(author_id)
            if author:
                author.name = name
                author.email = email
                author.bio = bio
                author.save()
                print("✅ Author updated successfully!")
            else:
                print("❌ Author not found.")
        
        elif choice == "12":
            author_id = input("Author ID: ").strip()
            author = Author.find_by_id(author_id)
            if author:
                author.delete()
                print("✅ Author deleted successfully!")
            else:
                print("❌ Author not found.")
        
        elif choice == "13":
            title = input("Article title: ").strip()
            content = input("Article content: ").strip()
            author_id = input("Author ID: ").strip()
            magazine_id = input("Magazine ID: ").strip()
            new_article = Article(title=title, content=content, author_id=author_id, magazine_id=magazine_id)
            new_article.save()
            print("✅ Article added successfully!")
        
        elif choice == "14":
            articles = Article.get_all()
            if not articles:
                print("❌ No articles found.")
            else:
                for article in articles:
                    print(f"\n📄 {article.title} (ID: {article.id})")
                    print(f"   - Content: {article.content}")
                    print(f"   - Author ID: {article.author_id}")
                    print(f"   - Magazine ID: {article.magazine_id}")
        
        elif choice == "15":
            article_id = input("Article ID: ").strip()
            title = input("New article title: ").strip()
            content = input("New article content: ").strip()
            article = Article.find_by_id(article_id)
            if article:
                article.title = title
                article.content = content
                article.save()
                print("✅ Article updated successfully!")
            else:
                print("❌ Article not found.")
        
        elif choice == "16":
            article_id = input("Article ID: ").strip()
            article = Article.find_by_id(article_id)
            if article:
                article.delete()
                print("✅ Article deleted successfully!")
            else:
                print("❌ Article not found.")
        
        elif choice == "17":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice, try again.")

if __name__ == "__main__":
    cli()