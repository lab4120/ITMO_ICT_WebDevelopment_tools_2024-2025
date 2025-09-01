import os
from dotenv import load_dotenv

print("Current working directory:", os.getcwd())
print(".env file exists:", os.path.exists('.env'))

# Load environment variables from .env file
result = load_dotenv('.env')
print("load_dotenv result:", result)

# Access environment variables
db_url = os.getenv('DB_ADMIN')
print(f"Database URL: {db_url}")

# Debug: print all environment variables
print("All environment variables:")
for key, value in os.environ.items():
    if 'DB' in key:
        print(f"  {key}: {value}")

# Example of using the database URL in your application
if db_url:
    print("Database connection configured successfully!")
else:
    print("Warning: Database URL not found in environment variables")
