from sqlalchemy import text
from database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("MySQL connection successful!")
        print("Test result:", result.scalar())
except Exception as e:
    print("MySQL connection failed:", e)