
from lib.db.connection import get_connection
from code-challenge.lib.models.magazine import Magazine


# Test the connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT NOW() as current_time;")
print(cursor.fetchone()) 
conn.close()

# Set up database connection
Magazine.set_connection({
    "dbname": "your_database",
    "user": "your_username",
    "password": "your_password",
    "host": "localhost"
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