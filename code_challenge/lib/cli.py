# cli.py

from code_challenge.lib.models.author import Author
from code_challenge.lib.models.magazine import Magazine
from code_challenge.lib.models.article import Article
from code_challenge.lib.db import add_author_with_articles
def cli():
    print("📚 Magazine Database CLI")
    while True:
        print("\n1. Add author with articles")
        print("2. Find top publisher")
        print("3. Search articles by author")
        print("4. Exit")
        
        choice = input("Select an option: ")
        
        if choice == "1":
            name = input("Author name: ")
            bio = input("Author bio: ")
            articles = []
            while True:
                title = input("Article title (q to finish): ")
                if title.lower() == 'q':
                    break
                content = input("Article content: ")
                magazine_id = input("Magazine ID: ")
                articles.append({
                    'title': title,
                    'content': content,
                    'magazine_id': magazine_id
                })
            if add_author_with_articles(name, bio, articles):
                print("✅ Author and articles added successfully!")
                
        elif choice == "2":
            top_mag = Magazine.top_publisher()
            if top_mag:
                print(f"🏆 Top publisher: {top_mag.name}")
            else:
                print("No magazines found")
                
        elif choice == "3":
            author_id = input("Author ID: ")
            author = Author.find_by_id(author_id)
            if author:
                print(f"\nArticles by {author.name}:")
                for article in author.articles():
                    mag = Magazine.find_by_id(article.magazine_id)
                    print(f"- {article.title} in {mag.name}")
            else:
                print("Author not found")
                
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("Invalid choice, try again")

if __name__ == "__main__":
    cli()