from lib.db.connection import get_connection

# Test the connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT NOW() as current_time;")
print(cursor.fetchone()) 
conn.close()